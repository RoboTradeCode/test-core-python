import asyncio
import copy

from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class OrderbookTesting(Strategy):
    """
    Стратегия для тестирования корректного получения ордербуков.
    В данной стратегии надо проверить работу гейта в следующем:

    1. что данные вообще приходят, что они меняются
    2. нету больших задержек в передаче данных.
    3. в структуре стакана есть timestamp, это время события на бирже, и гейт должен присывать последовательные
    ордербуки, т.е. если пришел ордербук с запоздавшими данными это критическа ошибка. Время должно рости
    """
    name = 'Orderbook Testing'

    async def strategy(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        """
        Стратегия для быстрого тестирования гейта.
        :param trader:
        :param orderbooks:
        :param balances:
        :return:
        """

        self.logger.info('1. Отменяем все ордера и запрашиваем баланс.')
        trader.cancel_all_orders()
        trader.request_update_balances(assets=self.assets)

        self.logger.info('Жду баланс и ордербуки...')
        # проверяю наличие балансов, а также проверяю с помощью множеств, что для каждого маркета пришел ордербук
        while balances or \
                set(orderbooks.orderbooks.keys()).intersection(self.markets.keys()) != set(self.markets.keys()):
            await asyncio.sleep(0.1)
        self.logger.info(f'Текущий ордербук: {orderbooks}')

        self.logger.info('1. Проверяю, что ордербуки приходят и меняются')
        current_orderbook = copy.deepcopy(orderbooks.orderbooks)
        sleeping_time = 0
        while current_orderbook == orderbooks.orderbooks:
            await asyncio.sleep(0.1)
            sleeping_time += 0.1
            if sleeping_time >= 5:
                self.logger.critical(
                    f'TEST FAILED. Ордербуки не обновились в течение 5 секунд.')
                return

        self.logger.info('2. Проверяю на задержки в передаче данных.')
        symbol = list(orderbooks.orderbooks.keys())[0]
        last_update_timestamp = copy.deepcopy(orderbooks[symbol].timestamp)
        updates_count = 0
        for _ in range(250):
            if last_update_timestamp != orderbooks[symbol].timestamp:
                updates_count += 1
                last_update_timestamp = copy.deepcopy(orderbooks.last_update_timestamp)
            await asyncio.sleep(0.01)
        if updates_count < 5:
                self.logger.critical(
                    f'TEST FAILED. Обнаружены задержки в получении ордербуков. Причиной может быть '
                    f'низковолатильный актив (использовался {symbol}, медленное интернет-соединение гейта '
                    f'либо программные ошибки в гейте.')
                return

        self.logger.info('3. Проверяю, что гейт присылает ордербуки с последовательным timestamp')
        for _ in range(100):
            if last_update_timestamp != orderbooks[symbol].timestamp:
                if not last_update_timestamp > orderbooks[symbol].timestamp:
                    self.logger.critical(
                        f'TEST FAILED. Ордербуки пришли не в правильно порядке по timestamp (у ордербука, '
                        f'который пришел в ядро позже, ордербук меньше, чем у предыдущего).')
                    return
                last_update_timestamp = copy.deepcopy(orderbooks[symbol].timestamp)

        self.logger.info('SUCCESS. Тест успешно пройден.')
        return