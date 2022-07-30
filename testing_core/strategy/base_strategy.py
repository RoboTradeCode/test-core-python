import logging
from abc import ABC, abstractmethod

from testing_core.config import Market
from testing_core.models.balance import Balance
from testing_core.models.orderbook import Orderbook
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.trader.trader import Trader


class Strategy(ABC):
    name: str

    def __init__(self, trader: Trader, markets: dict[str, Market], assets: list[str]):
        self.trader = trader

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s:%(filename)s:%(levelname)s %(message)s')
        self.logger = logging.getLogger(self.name)
        self.markets = markets
        self.assets = assets

    @abstractmethod
    async def strategy(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        ...

    def __repr__(self):
        return f'Strategy {self.name}. {self.description}'


