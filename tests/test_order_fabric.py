import copy
from unittest import TestCase

from testing_core.order.order import OrderData
from testing_core.order.order_fabric import OrderFabric
from tests.data.config_for_tests import markets_1
from tests.data.orders import order_1


def empty_func(_: OrderData):
    return None


class TestOrderFabric(TestCase):
    def setUp(self):
        self.order_fabric = OrderFabric(
            markets=markets_1,
            place_function=empty_func,
            request_update_function=empty_func,
            cancel_function=empty_func
        )

    def test_truncate_if_valid(self):
        order = copy.deepcopy(order_1)
        self.assertEqual(self.order_fabric.truncate_values_to_increment(order), order_1)

    def test_no_truncate_if_valid(self):
        order = copy.deepcopy(order_1)
        order.amount = 1.1234566778
        order.price = 15234.543253452
        self.assertNotEqual(self.order_fabric.truncate_values_to_increment(order), order_1)

    def test_check_order_to_limits_true(self):
        order = copy.deepcopy(order_1)
        self.assertTrue(self.order_fabric.check_order_to_limits(order))

    def test_check_order_to_limits_false(self):
        order = copy.deepcopy(order_1)
        order.amount = 1e-04
        order.price = 0.0001
        self.assertFalse(self.order_fabric.check_order_to_limits(order))
