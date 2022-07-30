from testing_core.models.orderbook import Orderbook
from testing_core.utils import get_micro_timestamp


class OrderbookState(object):
    """
    Класс для хранения актуального ордербука.
    """
    orderbooks: dict[str, Orderbook] = {}
    last_update_timestamp: int

    def update(self, orderbook: Orderbook):
        """
        Обновить ордербук.

        :param orderbook: актуальный ордербук.
        """
        self.orderbooks[orderbook.symbol] = orderbook
        self.last_update_timestamp = get_micro_timestamp()

    def __getitem__(self, symbol: str) -> Orderbook:
        """
        Получить ордербук по символу.
        :param symbol: символ торговой пары;
        :return: Orderbook ордербук
        """
        return self.orderbooks.get(symbol)

    def __iter__(self):
        return self.orderbooks.__iter__()

    def __repr__(self):
        return self.orderbooks.__repr__()

    def __bool__(self):
        return self.orderbooks == {}
