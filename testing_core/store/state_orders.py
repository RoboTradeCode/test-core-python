import logging

from testing_core import enums
from testing_core.models.message import OrderId
from testing_core.order.order import Order, OrderData, OrderUpdatable

logger = logging.getLogger(__name__)

class OrdersState(object):
    """
    Класс для хранения и обновления состояний ордеров
    """
    def __init__(self):
        self._orders: dict[str: OrderUpdatable] = {}

    def add_order(self, *orders: OrderUpdatable):
        """
        Добавить новый ордер. Если ордер уже существует, он будет обновлен.

        :param order: ордер, который нужно добавить;
        """
        for order in orders:
            self._orders[order.core_order_id] = order

    def remove_order(self, order: OrderData) -> bool:
        """
        Удалить ордер из хранимых ордеров;

        :param order: ордер, который нужно удалить;
        :return: False если ордера не было среди хранимых. True если ордер был успешно удален.
        """
        if order.core_order_id in self._orders:
            del self._orders[order.core_order_id]
            return True
        return False

    def update(self, orders: list[OrderData]):
        """
        Обновить данные по ордерам. Обновляет только те ордера, которые есть среди хранимых.

        :param orders: список из данных по ордерам;
        """
        for order_data in orders:
            if order := self._orders.get(order_data.core_order_id):
                order.update(order_data=order_data)
            else:
                logger.warning(f'Unknown order with id: {order_data.core_order_id}')

    def set_orders_state(self, *orders: OrderData | OrderId, state: enums.OrderState) -> None:
        """
        Установить новое состояние для одного или нескольких ордеров:
        :param orders: ордера, которым нужно обновить состояние:
        :param state: новое состояние
        """
        for order_data in orders:
            if order := self._orders.get(order_data.core_order_id):
                order.state = state

    def reset(self):
        """
        Сбросить состояние: Удалить все хранимые ордера.
        """
        self._orders.clear()

    @property
    def orders(self):
        """Получить копию ордеров, хранимых в экземпляре."""
        return self._orders.copy()

