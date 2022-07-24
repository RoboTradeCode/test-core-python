from testing_core.models.orderbook import Orderbook


class OrderbookState(object):
    """
    Класс для хранения актуального ордербука.
    """
    orderbooks: dict[str, Orderbook]

    def update(self, orderbook: Orderbook):
        """
        Обновить ордербук.

        :param orderbook: актуальный ордербук.
        """
        self.orderbooks[orderbook.symbol] = orderbook
