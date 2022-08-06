import asyncio
import time
from unittest import TestCase

from aeron import Subscriber, Publisher

from testing_core.communicator.aeron_communicator import AeronCommunicator
from testing_core.models.message import Message
from tests.data.config_for_tests import config_1, aeron_channels_1
from tests.data.core_commands import command_get_balance_1

# todo придумать, как написать тесты для этого класса
from tests.data.error_messages import error_message_1
from tests.data.orderbooks import orderbook_1, orderbook_1_message


class TestAeronCommunicator(TestCase):
    def setUp(self) -> None:
        self.orderbooks = []
        self.balances = []
        self.core_input = []
        self.gate_input = []
        self.logs = []
        self.communicator = AeronCommunicator(
            config=config_1,
            orderbook_handler=self.orderbooks.append,
            balance_handler=self.balances.append,
            core_input_handler=self.core_input.append
        )

    def test_publish(self):
        """
        Тест на публикацию сообщения
        """
        subscriber = Subscriber(self.gate_input.append,
                                aeron_channels_1.gate_input.channel,
                                aeron_channels_1.gate_input.stream_id
                                )
        self.communicator.publish(message=command_get_balance_1)
        time.sleep(0.1)
        subscriber.poll()
        self.assertTrue(self.gate_input)

    def test_publish_command(self):
        """
        Тест на отправку сообщения в канал команд
        """
        subscriber = Subscriber(self.gate_input.append,
                                aeron_channels_1.gate_input.channel,
                                aeron_channels_1.gate_input.stream_id
                                )
        self.communicator.publish(message=command_get_balance_1)
        time.sleep(0.2)
        subscriber.poll()
        self.assertEqual(self.gate_input[0], command_get_balance_1.json())

    def test_publish_error(self):
        """
        Тест на отправку сообщения в канал ошибок
        """
        subscriber = Subscriber(self.logs.append,
                                aeron_channels_1.logs.channel,
                                aeron_channels_1.logs.stream_id
                                )
        self.communicator.publish(message=error_message_1)
        time.sleep(0.2)
        subscriber.poll()
        self.assertEqual(self.logs, [error_message_1.json()])

    def test__handler_matching(self):
        """
        Тест на выбор дальнейшего обработчика для данных и правильную передачу данных в него
        """
        publisher = Publisher(aeron_channels_1.orderbooks.channel, aeron_channels_1.orderbooks.stream_id)
        publisher.offer(orderbook_1_message.json())
        time.sleep(0.1)
        self.communicator.handle_new_messages()
        self.assertEqual(self.orderbooks, [orderbook_1_message])

    def test_no_subscriber(self):
        """
        Тест на обработку отсутствия подписчика
        """
        self.communicator.publish(message=command_get_balance_1)
        time.sleep(0.1)
        self.assertEqual(self.logs, [])