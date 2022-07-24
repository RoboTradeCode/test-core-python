import asyncio
import time
from unittest import TestCase

from aeron import Subscriber

from testing_core.communicator.aeron_communicator import AeronCommunicator
from testing_core.models.message import Message
from tests.data.config_for_tests import config_1, aeron_channels
from tests.data.core_commands import command_get_balance_1

# todo придумать, как написать тесты для этого класса

class TestAeronCommunicator(TestCase):
    def _orderbook_handler(self, message: Message):
        self.orderbooks.append(message)

    def _balances_handler(self, message: Message):
        self.balances.append(message)

    def _core_input_handler(self, message: Message):
        self.core_input.append(message)

    def _gate_input_handler(self, message_as_str: str):
        self.gate_input.append(message_as_str)

    def setUp(self) -> None:
        self.orderbooks = []
        self.balances = []
        self.core_input = []
        self.gate_input = []
        self.communicator = AeronCommunicator(
            config=config_1,
            orderbook_handler=self._orderbook_handler,
            balance_handler=self._balances_handler,
            core_input_handler=self._core_input_handler
        )

    def test_publish(self):
        """Тест на публикацию сообщения"""
        subscriber = Subscriber(self._gate_input_handler,
                                aeron_channels.gate_input.channel,
                                aeron_channels.gate_input.stream_id
                                )
        # loop = asyncio.get_event_loop()
        # loop.create_task(self.communicator.publish(message=command_get_balance_1))
        #
        # time.sleep(1)
        # subscriber.poll()
        # self.assertTrue(self.gate_input)

    def test_publish_command(self):
        """Тест на отправку сообщения в канал команд"""
        self.fail()

    def test_publish_error(self):
        """Тест на отправку сообщения в канал ошибок"""
        self.fail()

    def test__handler(self):
        """Тест на начальную обработку и перенаправление дальше"""
        self.fail()

    def test__handler_matching(self):
        """Тест на выбор дальнейшего обработчика для данных"""
        self.fail()

    def test__handle_no_subscriber(self):
        self.fail()

    def test__match_action_to_handler(self):
        """Тест на матчинг действий и обработчиков"""
        self.fail()

    def test_check_to_new_messages(self):
        """Тест на проверку новых сообщений"""
        self.fail()

    def test_send_repeating(self):
        """Тест на повторную отправку сообщений, если не удалось отправить"""

    def test_no_subscriber(self):
        """Тест на обработку случая, когда нет подписчика"""
