import asyncio
import unittest

import pytest
import ujson
from aeron import Subscriber, Publisher

from testing_core import enums
from testing_core.models.message import Message, GateOrderInfo
from testing_core.trader.trader import Trader
from testing_core.utils import get_micro_timestamp, get_uuid
from tests.data.balances import balances_2, balances_missing_usdt_1
from tests.data.config_for_tests import config_1, aeron_channels_1, config_2, aeron_channels_2
from tests.data.invalid_messages import *
from tests.data.orderbooks import orderbook_1_message, orderbook_4_message

# @pytest.mark.skip()
from tests.data.orders import order_message_str_1


class TestCore(unittest.IsolatedAsyncioTestCase):
    """
    Проверка работы trader при неожиданной и неправильной работе гейта. Ядро должно обрабатывать кейсы без ошибок и
    по возможности логгировать неожиданное поведение.
    При тестировании происходит полная имитация работы гейта и класса Trader, с использованием aeron
    """
    def setUp(self):
        self.trader = Trader(config=config_2)
        self.gate_input = []

        self.core_input_publisher = Publisher(aeron_channels_2.core_input.channel, aeron_channels_2.core_input.stream_id)
        self.orderbook_publisher = Publisher(aeron_channels_2.orderbooks.channel, aeron_channels_2.orderbooks.stream_id)
        self.balance_publisher = Publisher(aeron_channels_2.balances.channel, aeron_channels_2.balances.stream_id)

        self.gate_input_subscriber = Subscriber(self.gate_input.append,
                                                aeron_channels_2.gate_input.channel,
                                                aeron_channels_2.gate_input.stream_id
                                                )
        loop = asyncio.get_event_loop()
        self.trader_loop_task = loop.create_task(self.trader.handle_subscriptions_loop())

        self.orderbook_publisher.offer(orderbook_1_message.json())

    def tearDown(self) -> None:
        self.trader_loop_task.cancel()

    async def test_invalid_format(self):
        """
        Приходящие сообщения не соответствуют формату
        """
        self.core_input_publisher.offer(invalid_order_message_1)
        self.core_input_publisher.offer(invalid_order_message_2)
        self.core_input_publisher.offer(invalid_order_message_3)
        self.core_input_publisher.offer(invalid_order_message_4)

        self.balance_publisher.offer(invalid_balance_message_1)

        self.orderbook_publisher.offer(invalid_orderbook_message_1)
        self.orderbook_publisher.offer(invalid_orderbook_message_2)
        self.orderbook_publisher.offer(invalid_orderbook_message_2)
        # подождать, чтобы были получены и обработаны сообщения
        await asyncio.sleep(0.1)

    async def test_invalid_order_id(self):
        """
        Ордер пришел не с тем id
        """
        order = self.trader.create_order(
            symbol='BTC/USDT',
            order_type=enums.OrderType.LIMIT,
            side=enums.OrderSide.BUY,
            price=1000.132,
            amount=20.1,
            id_prefix='test_prefix|',
            id_postfix='|test_postfix'
        )
        await asyncio.sleep(0.1)
        self.gate_input_subscriber.poll()
        message = Message(**ujson.loads(self.gate_input[0]))
        message.node = enums.Node.GATE
        message.timestamp = get_micro_timestamp()
        message.event = enums.Event.DATA
        message.data = GateOrderInfo(
            id='12343211234',
            client_order_id='1234123412341234_another_id',
            symbol='BTC/USDT',
            type=enums.OrderType.LIMIT,
            side=enums.OrderSide.BUY,
            price=1000.132,
            amount=20.1,
            status=enums.GateOrderStatus.OPEN,
            filled=0,
            timestamp=get_micro_timestamp(),
            info=None
        )
        self.core_input_publisher.offer(message.json())

    def test_different_response_event_id(self):
        """
        Event id команды и ответ отличаются
        """
        self.trader.request_update_balances(assets=['BTC', 'ETH'])
        self.gate_input_subscriber.poll()
        message = Message(**ujson.loads(self.gate_input[0]))
        message.event = get_uuid()
        message.node = enums.Node.GATE
        message.timestamp = get_micro_timestamp()
        message.event = enums.Event.DATA
        message.data = balances_2
        self.core_input_publisher.offer(message.json())

    async def test_unknown_order(self):
        """
        Пришел неизвестный ордер
        """
        self.core_input_publisher.offer(order_message_str_1)
        await asyncio.sleep(0.2)

    async def test_unwanted_orderbook(self):
        """
        Пришел ордербук по символу, который не нужен
        """
        self.orderbook_publisher.offer(orderbook_4_message.json())
        await asyncio.sleep(0.2)

    @pytest.mark.skip('Not implemented')
    async def test_broken_cancel_orders(self):
        """
        Ордер не отменяется командой cancel_orders
        """
        self.assertEqual(True, False)

    @pytest.mark.skip('Not implemented')
    def test_broken_cancel_all_orders(self):
        """
        Не отменяются все ордера командой cancel_all_orders
        """
        self.assertEqual(True, False)

    def test_missing_assets_in_get_balances(self):
        """
        Отсутствуют балансы по запрошенным ассетам get_balance
        """
        self.trader.request_update_balances(assets=['BTC', 'ETH', 'USDT'])
        self.gate_input_subscriber.poll()
        message = Message(**ujson.loads(self.gate_input[0]))
        message.node = enums.Node.GATE
        message.timestamp = get_micro_timestamp()
        message.event = enums.Event.DATA
        message.data = balances_missing_usdt_1
        self.core_input_publisher.offer(message.json())

    @pytest.mark.skip('Long wait and useless test')
    async def test_no_response(self):
        """
        Нет ответа на команду - ожидается ошибка или корректное исполнение
        """
        self.trader.request_update_balances(assets=['BTC', 'ETH', 'USDT'])
        self.gate_input_subscriber.poll()
        await asyncio.sleep(6)


if __name__ == '__main__':
    unittest.main()
