import logging
import time
from abc import ABC, abstractmethod
from typing import Callable

import ujson
from aeron import Publisher, Subscriber, AeronPublicationNotConnectedError, AeronPublicationError, \
    AeronPublicationAdminActionError
from pydantic import ValidationError
from ujson import JSONDecodeError

from testing_core import enums
from testing_core.config import CoreAeronChannels, Configuration
from testing_core.enums import Action
from testing_core.exceptions import UnexpectedAction
from testing_core.formatter.formatter import Formatter
from testing_core.models.balance import Balance
from testing_core.models.message import Message
from testing_core.models.orderbook import Orderbook
from testing_core.order.order import OrderData

logger = logging.getLogger(__name__)


class Communicator(ABC):
    @abstractmethod
    def handle_new_messages(self):
        """
        Проверка на наличие новых сообщений
        """
        pass

    @abstractmethod
    def publish(self, message: Message):
        """
        Отправка сообщения ядру и/или лог-серверу. Ошибки при передаче будут логгированы. Если передача не удалась,
        будут совершены повторные попытки (кроме ордер-бука, он не имеет повторных попыток).
        """
        # отправлять сообщение, пока не будет успешно
        pass


class AeronCommunicator(Communicator):
    """Класс для отправки и получения сообщений по Aeron"""
    _gate_input: Publisher
    _core_input: Subscriber
    _orderbooks: Subscriber
    _balances: Subscriber
    _logs: Publisher

    _channels: CoreAeronChannels

    _order_handler: Callable[[OrderData], None]
    _orderbook_handler: Callable[[Orderbook], None]
    _balance_handler: Callable[[dict[str, Balance]], None]

    # время последнего лога сообщения "not connected to a subscriber"
    _last_log_time: time = 0
    # список actions, которые не имеют подписчиков (в классе происходит разделение подписчиков по actions)
    _events_without_subscriber: list[Action] = []

    _formatter: Formatter

    def __init__(self,
                 config: Configuration,
                 orderbook_handler: Callable[[Message], None],
                 balance_handler: Callable[[Message], None],
                 core_input_handler: Callable[[Message], None]
                 ):
        """Класс для отправки и получения сообщений по Aeron;

        :param config: конфигурация гейта;
        :param orderbook_handler: callback-функция, которая вызывается с сообщением из канала orderbooks;
        :param balance_handler: callback-функция, которая вызывается с сообщением из канала balances;
        :param core_input_handler: callback-функция, которая вызывается с сообщением из канала core_input;
        """
        self._node = config.node
        self._channels = config.aeron_channels
        self._no_subscriber_log_frequency = config.no_subscriber_log_delay

        # создаю aeron publishers, aeron subscribers
        self._init_channels()

        # обработчики сообщений для подписок
        self._orderbook_handler: Callable[[Message], None] = orderbook_handler
        self._balance_handler: Callable[[Message], None] = balance_handler
        self._core_input_handler: Callable[[Message], None] = core_input_handler

        # объект для форматирования сообщений
        self._formatter = Formatter(
            exchange=config.exchange_id,
            instance=config.instance,
            algo=config.instance,
            node=config.node.value
        )

    def _init_channels(self):
        """
        Создать каналы для публикации и получения сообщений.
        """
        # publishers - каналы для отправки сообщений
        self._logs = Publisher(self._channels.logs.channel, self._channels.logs.stream_id)
        self._gate_input = Publisher(self._channels.gate_input.channel, self._channels.gate_input.stream_id)
        # subscribers - каналы для чтения сообщений (подписки)
        self._orderbooks = Subscriber(self._handler, self._channels.orderbooks.channel,
                                      self._channels.orderbooks.stream_id)
        self._balances = Subscriber(self._handler, self._channels.balances.channel, self._channels.balances.stream_id)
        self._core_input = Subscriber(self._handler, self._channels.core_input.channel,
                                      self._channels.core_input.stream_id)

    def handle_new_messages(self) -> None:
        """
        Проверка на наличие новых сообщений
        """
        self._orderbooks.poll()
        self._balances.poll()
        self._core_input.poll()

    def publish(self, message: Message) -> None:
        """
        Отправка сообщения ядру и/или лог-серверу. Ошибки при передаче будут логгированы. Если передача не удалась,
        будут совершены повторные попытки.
        :param message: сообщение, которое нужно отправить
        """
        # отправлять сообщение, пока не будет успешно
        is_successful = False
        num_of_retries = 0
        while not is_successful and num_of_retries < 5:

            try:
                is_successful = self._try_to_publish(message)

            # обработка случая, когда нет подписчика
            except AeronPublicationNotConnectedError:
                self._handle_no_subscriber(message)
                break
            # обработка случая admin actin (сообщение будет отправлено снова)
            except AeronPublicationAdminActionError:
                continue
            # обработка прочих ошибок aeron
            except AeronPublicationError as e:
                logger.warning(f'Error on aeron publishing: {e}')
                break
            # обработка неожиданного action
            except UnexpectedAction:
                logger.error(f'Unexpected action in message: {message}')

    def _handler(self, message_as_str: str):
        """Форматирование сообщения, отправка на лог-сервер, передача callback-функции"""
        logger.debug(f'Received message on aeron: {message_as_str}')
        try:
            # парсинг сообщения
            message_as_dict = ujson.loads(message_as_str)
            message = Message(**message_as_dict)

            handler = self._match_action_to_handler(message=message)
            handler(message)

            # НЕ РЕАЛИЗОВАНО
            # Отправка команды на log server
            # message_to_log = formatted_message
            # message_to_log.node = self._node
            # self._logs.offer(message_to_log.json())

        except JSONDecodeError:
            logger.error(f'Failed to parse json: {message_as_str}')
            message_error = self._formatter.format_error(
                action=None,
                message='Failed to handle command',
                event_id=None,
                data=message_as_str
            )
            self.publish(message_error)
        except ValidationError as exception:
            logger.error(f'Invalid format of message: {message_as_str}, exception: {exception}')
            message_error = self._formatter.format_error(
                action=None,
                message='Failed to handle command',
                event_id=None,
                data=message_as_str
            )
            self.publish(message_error)
        except Exception as e:
            logger.error(f'Failed to handle message. Exception: {e}.\n Faulty message: {message_as_str}', exc_info=True)
            message_error = self._formatter.format_error(
                action=None,
                message='Failed to handle command',
                event_id=None,
                data=message_as_str
            )
            self.publish(message_error)

    def _try_to_publish(self, message: Message) -> bool:
        """
        Попытка найти нужного publisher и отправить сообщение.
        :param message: сообщение, которое нужно отправить;
        :return: True, если успешно
        """
        message_json = message.json()
        if message.event == enums.Event.COMMAND:
            self._gate_input.offer(message_json)
        elif message.event == enums.Event.ERROR:
            self._logs.offer(message_json)
        return True

    def _handle_no_subscriber(self, message):
        """
        Обработка случая, когда нет подписчика (нужно логгировать сообщение, но не писать лог слишком часто)
        """
        if (time.time() - self._last_log_time) > self._no_subscriber_log_frequency:
            self._last_log_time = time.time()
            self._events_without_subscriber.clear()

        if message.event not in self._events_without_subscriber:
            self._events_without_subscriber.append(message.event)
            logger.warning(f'Event {message.event.value} not have a subscriber.')

    def _match_action_to_handler(self, message: Message) -> Callable[[Message], None]:
        """
        Определить, какой обработчик нужно использовать для сообщения.
        :param message: сообщение, для которого нужно выбрать обработчик;
        :return: функция для обработки сообщения
        """
        match message.action:
            case Action.ORDERBOOK_UPDATE:
                handler = self._orderbook_handler
            case Action.CREATE_ORDERS | Action.CANCEL_ORDERS | \
                 Action.CANCEL_ALL_ORDERS | Action.GET_ORDERS | Action.ORDERS_UPDATE:
                handler = self._core_input_handler
            case Action.GET_BALANCE | Action.BALANCE_UPDATE:
                handler = self._balance_handler
            case _:
                raise UnexpectedAction
        return handler
