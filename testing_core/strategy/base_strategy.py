from abc import ABC, abstractmethod

from testing_core.trader.trader import Trader


class Strategy(ABC):
    name: str
    description: str

    def __init__(self, trader: Trader):
        self.trader = trader

    @abstractmethod
    async def execute(self):
        ...

    def __repr__(self):
        return f'Strategy {self.name}. {self.description}'


