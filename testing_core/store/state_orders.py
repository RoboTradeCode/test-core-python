from testing_core.order.order import Order, OrderData, OrderUpdatable


class OrdersState(object):
    """
    Класс для хранения и обновления состояний ордеров
    """
    _orders: dict[str: OrderUpdatable] = {}

    def add_order(self, order: OrderUpdatable):
        """
        Добавить новый ордер.

        :param order: ордер, который нужно добавить;
        """
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

    def reset(self):
        """
        Сбросить состояние: Удалить все хранимые ордера.
        """
        self._orders.clear()

    @property
    def orders(self):
        """Получить копию ордеров, хранимых в экземпляре."""
        return self._orders.copy()

