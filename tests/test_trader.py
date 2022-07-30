import copy
from unittest import TestCase

import pytest

from testing_core import enums
from testing_core.order.order import Order
from testing_core.trader.trader import Trader
from tests.communicator_mock import CommunicatorMock
from tests.data.balances import balances_1_message, balances_1, balances_2_message, balances_3_total
from tests.data.config_for_tests import config_1, config_2
from tests.data.error_messages import error_from_gate_1
from tests.data.orderbooks import orderbook_1_message, orderbook_1, orderbook_2_message, orderbook_3_message, \
    orderbook_2, orderbook_3
from tests.data.orders import order_1, order_2, order_2_update_message, order_2_updated, order_4


class TestTrader(TestCase):
    def setUp(self):
        self.communicator_mock = CommunicatorMock()
        self.trader = Trader(config=config_2,
                             communicator=self.communicator_mock)
        self.communicator_mock.set_handlers(
            orderbook_handler=self.trader._handle_orderbook,
            balance_handler=self.trader._handle_balances,
            core_input_handler=self.trader._handle_core_input
        )

    def _check_order_1(self, order_to_checking: Order):
        self.assertEqual(order_to_checking.type, enums.OrderType.LIMIT, 'Invalid order type')
        self.assertEqual(order_to_checking.side, enums.OrderSide.BUY, 'Invalid order side')
        self.assertEqual(order_to_checking.price, 1000.132, 'Invalid order price')
        self.assertEqual(order_to_checking.amount, 20.1, 'Invalid order amount')

    def test_create_order(self):
        """
        Тест на создание ордера - обработка аргументов и отправление команды в коммуникатор
        """
        order = copy.deepcopy(self.trader.create_order(
            symbol='BTC/USDT',
            order_type=enums.OrderType.LIMIT,
            side=enums.OrderSide.BUY,
            price=1000.132,
            amount=20.1,
            id_prefix='test_prefix|',
            id_postfix='|test_postfix'
        ))
        self.assertTrue(order.core_order_id.startswith('test_prefix|'), 'Invalid prefix')
        self.assertTrue(order.core_order_id.endswith('|test_postfix'), 'Invalid postfix')
        self._check_order_1(order_to_checking=order)

    def test_create_placed_order(self):
        """
        Тест на создание ордера - обработка аргументов и отправление ордера в коммуникатор
        """
        self.trader.create_order(
            symbol='BTC/USDT',
            order_type=enums.OrderType.LIMIT,
            side=enums.OrderSide.BUY,
            price=1000.132,
            amount=20.1,
            id_prefix='test_prefix|',
            id_postfix='|test_postfix'
        )
        order = self.communicator_mock.published_messages[0].data[0]
        self._check_order_1(order_to_checking=order)

    def test_get_balances(self):
        """
        Тест, что класс предоставляет доступ к текущим балансам
        """
        self.communicator_mock.balances_queue.append(copy.deepcopy(balances_1_message))
        self.communicator_mock.handle_new_messages()
        self.assertEqual(self.trader.balances.balances, balances_1['assets'], 'Balances is not equal.')

    def test_balances_updating(self):
        """
        Тест, что балансы обновляются
        """
        self.communicator_mock.balances_queue.append(copy.deepcopy(balances_1_message))
        self.communicator_mock.handle_new_messages()
        self.communicator_mock.balances_queue.append(copy.deepcopy(balances_2_message))
        self.communicator_mock.handle_new_messages()
        self.assertEqual(self.trader.balances.balances, balances_3_total['assets'], 'Balances is not equal.')

    def test_get_orderbooks(self):
        """
        Тест, что класс предоставляет доступ к ордербукам
        """
        self.communicator_mock.orderbooks_queue.append(copy.deepcopy(orderbook_1_message))
        self.communicator_mock.handle_new_messages()
        self.assertEqual(self.trader.orderbooks['BTC/USDT'], orderbook_1, 'Orderbooks is not equal.')

    def test_orderbooks_updating(self):
        """
        Тест, что ордербуки обновляются
        """
        self.communicator_mock.orderbooks_queue.append(copy.deepcopy(orderbook_1_message))
        self.communicator_mock.handle_new_messages()
        self.communicator_mock.orderbooks_queue.append(copy.deepcopy(orderbook_3_message))
        self.communicator_mock.handle_new_messages()
        self.communicator_mock.orderbooks_queue.append(copy.deepcopy(orderbook_2_message))
        self.communicator_mock.handle_new_messages()
        self.assertEqual(self.trader.orderbooks['BTC/USDT'], orderbook_2, 'Orderbooks is not equal.')
        self.assertEqual(self.trader.orderbooks['ETH/USDT'], orderbook_3, 'Orderbooks is not equal.')

    def test_cancel_all_orders(self):
        """
        Тест отправления команды на отмену всех ордеров
        """
        self.trader.cancel_all_orders()
        self.assertEqual(self.communicator_mock.published_messages[0].action, enums.Action.CANCEL_ALL_ORDERS)

    def test_place_order(self):
        """
        Тест функции для отправления команды на создание ордеров коммуникатору
        """
        order_copy = copy.deepcopy(order_1)
        self.trader.place_orders(order_copy)
        order = copy.deepcopy(self.communicator_mock.published_messages[0].data[0])
        self.assertTrue(order.client_order_id.startswith('test_prefix|'), 'Invalid prefix')
        self.assertTrue(order.client_order_id.endswith('|test_postfix'), 'Invalid postfix')
        self._check_order_1(order_to_checking=order)

    def test_cancel_orders(self):
        """
        Тест отправки команды на отмену ордеров
        """
        order = copy.deepcopy(order_1)
        self.trader.cancel_orders(order)
        message = self.communicator_mock.published_messages[0]
        self.assertEqual(message.action, enums.Action.CANCEL_ORDERS)
        self.assertEqual(message.data[0].client_order_id, order.core_order_id)
        self.assertEqual(message.data[0].symbol, order.symbol)

    def test_request_update_orders(self):
        """
        Тест функции запроса статуса ордера (команда должна быть отправлена в коммуникатор)
        """
        order = copy.deepcopy(order_1)
        self.trader.request_update_orders(order)
        message = self.communicator_mock.published_messages[0]
        self.assertEqual(message.action, enums.Action.GET_ORDERS)
        self.assertEqual(message.data[0].client_order_id, order.core_order_id)
        self.assertEqual(message.data[0].symbol, order.symbol)

    def test_request_update_balances(self):
        """
        Тест функции запроса актуального баланса (команда должна быть отправлена в коммуникатор)
        """
        self.trader.request_update_balances(config_1.assets)
        message = self.communicator_mock.published_messages[0]
        self.assertEqual(message.action, enums.Action.GET_BALANCE)
        self.assertEqual(message.data, config_1.assets)

    def test_update_orders(self):
        """
        Тест правильной обработки обновлений ордеров
        """
        order = copy.deepcopy(order_2)
        self.trader.add_orders(order)
        self.communicator_mock.core_input_queue.append(order_2_update_message)
        self.communicator_mock.handle_new_messages()
        self.assertEqual(order, order_2_updated)

    @pytest.mark.skip('Error codes is not implemented in current version of trade system.')
    def test_handle_core_input(self):
        """
        Тест обработки сообщений в канал core_input
        """
        order = copy.deepcopy(order_4)
        self.trader.add_orders(order)
        self.assertEqual(order.state, enums.OrderState.UNPLACED)
        self.trader.place_orders(order)
        self.assertEqual(order.state, enums.OrderState.PLACING)
        self.communicator_mock.core_input_queue.append(error_from_gate_1)
        self.communicator_mock.handle_new_messages()
        self.assertEqual(order.state, enums.OrderState.ERROR)
