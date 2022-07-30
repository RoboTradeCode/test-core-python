import copy
from unittest import TestCase

from testing_core.store.state_orders import OrdersState
from tests.data.orders import *


class TestOrdersState(TestCase):
    def setUp(self) -> None:
        self.orders_state = OrdersState()
        self.orders_state.add_order(order=copy.deepcopy(order_1))
        self.orders_state.add_order(order=copy.deepcopy(order_2))

    def tearDown(self) -> None:
        self.orders_state.reset()

    def test_reset(self):
        self.orders_state.reset()
        self.assertEqual(self.orders_state.orders, {})

    def test_add_order(self):
        self.orders_state.add_order(order=order_3)
        self.assertTrue(self.orders_state.orders[order_3.core_order_id] == order_3)
        self.assertTrue(len(self.orders_state.orders.values()) == 3)

    def test_remove_order(self):
        self.orders_state.remove_order(order=order_1)
        self.assertEqual(self.orders_state.orders, {order_2.core_order_id: order_2})

    def test_update_one_order(self):
        self.orders_state.update(orders=[order_1_update])
        updated_orders = {
            order_1.core_order_id: order_1_updated,
            order_2.core_order_id: order_2
        }
        self.assertEqual(self.orders_state.orders, updated_orders)

    def test_update_two_orders(self):
        self.orders_state.add_order(order_3)
        self.orders_state.update(orders=[order_1_update, order_2_update])
        updated_orders = {
            order_1.core_order_id: order_1_updated,
            order_2.core_order_id: order_2_updated,
            order_3.core_order_id: order_3
        }
        self.assertEqual(self.orders_state.orders, updated_orders)
