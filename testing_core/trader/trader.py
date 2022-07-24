import asyncio
import logging
from typing import Callable, Coroutine

from testing_core import enums
from testing_core.communicator.aeron_communicator import Communicator, AeronCommunicator
from testing_core.config import Configuration
from testing_core.enums import OrderType, OrderSide
from testing_core.formatter.formatter import Formatter
from testing_core.models.balance import Balance
from testing_core.models.message import Message, Balances
from testing_core.models.orderbook import Orderbook
from testing_core.order.order import OrderData, Order
from testing_core.order.order_fabric import OrderFabric
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.store.state_orders import OrdersState
from testing_core.utils import get_uuid

logger = logging.getLogger(__name__)

class Trader(object):
    """
    Класс для управления ордерами и хранения актуального баланса.
    Создает, хранит, отменяет и обновляет ордера. Отвечает за исполнение команд и взаимодействие с гейтом.
    Использует класс-communicator для взаимодействия с гейтом. Обрабатывает полученные сообщения, в том числе ошибки.
    """
    _orders_state: OrdersState
    _balances_state: BalancesState
    _orderbook_state: OrderbookState
    _communicator: Communicator
    _formatter: Formatter

    _order_error_callback: Callable[[OrderData], None]
    _order_closed_callback: Callable[[OrderData], None]

    def __init__(self,
                 config: Configuration,
                 order_error_callback: Callable[[OrderData], None] = None,
                 order_closed_callback: Callable[[OrderData], None] = None,
                 communicator: Communicator = None,
                 ):
        """
        Класс для управления ордерами и хранения актуального баланса.

        :param communicator: Коммуникатор для связи с гейтом. Должен реализовывать интерфейс Communicator
        :param order_error_callback: Функция обратного вызова для ошибок по ордерам. Опционально.
        :param order_closed_callback: Функция обратного вызова для исполненных ордеров на бирже. Опционально.
        """
        if communicator is None:
            communicator = AeronCommunicator(config=config,
                                             orderbook_handler=self._handle_orderbook,
                                             balance_handler=self._handle_balances,
                                             core_input_handler=self._handle_core_input)
        self._communicator = communicator
        self._orders_state = OrdersState()
        self._balances_state = BalancesState()
        self._orderbook_state = OrderbookState()
        self._order_fabric = OrderFabric(
            place_function=self.place_orders,
            request_update_function=self.request_update_orders,
            cancel_function=self.cancel_orders,
        )
        self._formatter = Formatter(
            exchange=config.exchange_id,
            instance=config.instance,
            algo=config.instance,
            node=config.node.value
        )

        self._order_error_callback = order_error_callback
        self._order_closed_callback = order_closed_callback

    def create_order(
            self,
            symbol: str,
            order_type: OrderType,
            side: OrderSide,
            price: float,
            amount: float,
            id_prefix: str = '',
            id_postfix: str = ''
    ) -> Order:
        """
        Создать ордер и разместить его на бирже
        :param symbol: символ валютной пары;
        :param order_type: тип ордера, например limit или market;
        :param side: сторона ордера, buy или sell;
        :param price: цена ордера, обязательно для всех типов ордеров (для market тоже);
        :param amount: объем ордера;
        :return: созданный ордер
        :param id_prefix: префикс для id, опционально;
        :param id_postfix: постфикс для id, опционально;
        :return: созданный ордер
        """
        order = self.create_unplaced_order(
            symbol=symbol,
            order_type=order_type,
            side=side,
            price=price,
            amount=amount,
            id_prefix=id_prefix,
            id_postfix=id_postfix,
        )

        # размещение ордера на бирже
        order.place()

        return order

    def create_unplaced_order(
            self,
            symbol: str,
            order_type: OrderType,
            side: OrderSide,
            price: float,
            amount: float,
            id_prefix: str = '',
            id_postfix: str = ''
    ):
        """
        Создать ордер без размещения на бирже (можно разместить позднее);
        :param symbol: символ валютной пары;
        :param order_type: тип ордера, например limit или market;
        :param side: сторона ордера, buy или sell;
        :param price: цена ордера, обязательно для всех типов ордеров (для market тоже);
        :param amount: объем ордера;
        :return: созданный ордер
        :param id_prefix: префикс для id, опционально;
        :param id_postfix: постфикс для id, опционально;
        :return: созданный ордер
        """
        # Создаю core order id
        core_order_id = get_uuid(prefix=id_prefix, postfix=id_postfix)

        # создаю ордер
        order = self._order_fabric.create_order(
            core_order_id=core_order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            price=price,
            amount=amount
        )

        # добавляю ордер в хранилище ордеров
        self._orders_state.add_order(order=order)

        return order

    @property
    def balances(self) -> dict[str: Balance]:
        """
        Получить текущие балансы по аккаунту.
        :return: текущие балансы
        """
        return self._balances_state.balances

    @property
    def orderbooks(self) -> dict[str, Orderbook]:
        """
        Получить актуальный ордербук.
        :return: актуальный ордербук
        """
        return self._orderbook_state.orderbooks

    def cancel_all_orders(self) -> None:
        """
        Отменить все открытые ордера на бирже.
        """
        command = self._formatter.format_command(
            action=enums.Action.CANCEL_ALL_ORDERS,
            data=None
        )
        self._communicator.publish(command)

    def place_orders(self, *orders: OrderData) -> None:
        """
        Разместить ордера на бирже (создать ордер на бирже).
        :param orders: ордера, который нужно разместить на бирже (один или несколько);
        :return: None
        """
        command = self._formatter.format_create_orders(*orders)
        self._communicator.publish(message=command)

    def cancel_orders(self, *orders: OrderData) -> None:
        """
        Отменить ордера на бирже.
        :param orders: ордера, который нужно отменить (один или несколько)
        :return: None
        """
        command = self._formatter.format_cancel_orders(*orders)
        self._communicator.publish(message=command)

    def request_update_orders(self, *orders: OrderData) -> None:
        """
        Запросить обновление ордеров. Обновление будет получено не сразу.
        :param orders: один или несколько ордеров.
        :return: None
        """
        command = self._formatter.format_get_orders(*orders)
        self._communicator.publish(message=command)

    def request_update_balances(self, assets: list[str]) -> None:
        """
        Запросить обновление баланса. Обновление будет получено не сразу.
        :param assets: список ассетов.
        :return: None
        """
        command = self._formatter.format_get_balance(assets=assets)
        self._communicator.publish(message=command)

    def _update_orders(self, orders: list[OrderData]) -> None:
        """
        Обновить данные по ордерам.
        :param orders: список данных по ордерам.
        :return: None
        """
        self._orders_state.update(orders=orders)

    def _handle_core_input(self, message: Message) -> None:
        """
        Обработчик сообщений канала core_input
        :param message: сообщение, полученное в канал
        :return: None
        """
        match message.event:
            case enums.Event.ERROR:
                logger.warning(f'Received message of error: {message}')
            case enums.Event.DATA:
                if isinstance(message.data, list) and message.data:
                    logger.warning(f'Received orders: {message.data}')
                    self._update_orders(orders=message.data)
                else:
                    logger.error(f'Unexpected type of data: {message}')
            case _:
                logger.warning(f'Unexpected event in message: {message}')

    def _handle_orderbook(self, message: Message) -> None:
        """
        Обработчик сообщений канала orderbooks
        :param message: сообщение, полученное в канал
        :return: None
        """
        match message.event:
            case enums.Event.ERROR:
                logger.warning(f'Received message of error: {message}')
            case enums.Event.DATA:
                if isinstance(message.data, Orderbook):
                    self._orderbook_state.update(orderbook=message.data)
                else:
                    logger.error(f'Unexpected type of data: {message}')
            case _:
                logger.warning(f'Unexpected event in message: {message}')

    def _handle_balances(self, message: Message) -> None:
        """
        Обработчик сообщений канала balances
        :param message: сообщение, полученное в канал
        :return: None
        """
        match message.event:
            case enums.Event.ERROR:
                logger.warning(f'Received message of error: {message}')
            case enums.Event.DATA:
                if isinstance(message.data, Balances):
                    self._balances_state.update(balances=message.data.assets)
                else:
                    logger.error(f'Unexpected type of data: {message}')
            case _:
                logger.warning(f'Unexpected event in message: {message}')

    async def handle_subscriptions_loop(self):
        while True:
            self._communicator.check_to_new_messages()
            await asyncio.sleep(0.000001)

    def get_loop(self) -> Coroutine:
        return self.handle_subscriptions_loop()





