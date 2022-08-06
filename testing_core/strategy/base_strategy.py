import logging
from abc import ABC, abstractmethod

from testing_core.config import Market
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.trader.trader import Trader


class Strategy(ABC):
    """
    Абстрактный класс, реализации которого пишет пользователь (алготрейдер).
    В его реализациях будет описан алгоритм торговой стратегии, который использует Trader
    для получения данных и выставления ордеров.

    Doc-string реализации будет выводиться в логи, поэтому рекомендуется кратко описать стратегию.
    """
    # имя стратегии
    name: str

    def __init__(self, trader: Trader, markets: dict[str, Market], assets: list[str]):
        # trader предназначен для взаимодействия с биржей через гейт
        self.trader = trader

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s:%(filename)s:%(levelname)s %(message)s')

        self.logger = logging.getLogger(self.name)
        # список маркетов биржи, с которыми может взаимодействовать стратегия
        self.markets = markets
        # список ассетов, с которыми может взаимодействовать стратегия (должно соотноситься с markets)
        self.assets = assets

    @abstractmethod
    async def execute(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        """
        Запустить стратегию (если это не тестирующая стратегия, то внутри должен быть бесконечный цикл).
        :param trader: объект Trader, предназначенный для взаимодействия с биржей через гейт;
        :param orderbooks: объект, дает доступ к ордербукам, динамически их обновляет;
        :param balances: объект, дает доступ к балансам, динамически их обновляет;
        """
        ...

    def __repr__(self):
        return f'Strategy {self.name}. {self.__doc__}'


