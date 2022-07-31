import asyncio
import random

from testing_core import enums
from testing_core.exceptions import InsufficientBalance
from testing_core.order.order import Order
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class BalancesTesting(Strategy):
    """
    Стратегия тестирования корректного получения балансов
    Целью данной стратегии будет проверка правильности постановки балансов ядру.

    1. Через API проверяем действительный баланс, т.е. проверяем это не используя гейт.
    2. создаем 1 ордер и проверяем что гейт отправит нам измененный баланс, и поле used будет не нулевым у соот-го ассета.
    3. ждем пока ордер исполнится (т.е. надо поставить маркет ордер) и проверяем что поле used баланса определенного ассета
    стало нулевым, а активный баланс изменился.

    Проделываем пункты 1-3 с несколькими ассетами одновременно.

    4. ставим ордер так что бы он не мог быстро исполнится, немного ждем, далее отменяем ордер и проверяем
    чтобы поле used снова стало 0.0
    5. в структуре стакана есть `timestamp`, это время события на бирже, и гейт должен присывать последовательные
    балансы, т.е. если пришел баланс с запоздавшими данными это критическа ошибка. Время должно рости линейно.
    """
    name = 'Balances Testing'

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

        self.logger.info('2. Создаем лимитный ордер на случайном маркете. '
                         'Цена подбирается таким образом, чтобы ордер быстро исполнился. ')
        self.logger.info('3. Жду от гейта статусы об открытии, затем о закрытии. ')
        self.logger.info('4. Шаги 2 и 3 повторяются 10 раз.')
        is_successful_limit_orders = await self.execute_10_orders('limit', balances, orderbooks)
        if not is_successful_limit_orders:
            return

        self.logger.info('5. Создаю рычночный ордер на случайном маркете. ')
        self.logger.info('6. Жду от гейта статусы об открытии, затем о закрытии. ')
        self.logger.info('7. Шаги 5 и 6 повторяются 10 раз.')
        is_successful_market_orders = await self.execute_10_orders('market', balances, orderbooks)
        if not is_successful_market_orders:
            return

        self.logger.info('8. Отправляю команду гейту, в которой есть лимитные и рыночные ордера одновременно.')
        orders = [self.get_order('limit', orderbooks, balances), self.get_order('market', orderbooks, balances)]
        for order in orders:
            order.place()
        executing_sleeping_time = 0
        while orders[0].state != enums.OrderState.CLOSED and orders[1].state != enums.OrderState.CLOSED:
            await asyncio.sleep(0.1)
            executing_sleeping_time += 0.1
            if executing_sleeping_time >= 30:
                self.logger.critical(
                    f'TEST FAILED. Не удалось исполнить ордера {orders}')
                return

        self.logger.info('SUCCESS. Тест успешно пройден.')
        return

    async def execute_10_orders(self, order_type, balances, orderbooks):
        orders = [self.get_order(order_type=order_type, orderbooks=orderbooks, balances=balances) for _ in range(10)]
        for i, order in enumerate(orders):
            self.logger.info(f'Выставление ордера {i}')
            order.place()
            placing_sleeping_time = 0
            while order.state == enums.OrderState.PLACING:
                await asyncio.sleep(0.1)
                placing_sleeping_time += 0.1
                if placing_sleeping_time >= 5:
                    self.logger.critical(
                        f'TEST FAILED. Не удалось создать ордер {order}')
                    return False
            executing_sleeping_time = 0
            while order.state == enums.OrderState.OPEN:
                await asyncio.sleep(0.1)
                executing_sleeping_time += 0.1
                if executing_sleeping_time >= 30:
                    self.logger.critical(
                        f'TEST FAILED. Не удалось исполнить ордер {order}')
                    return False
            self.logger.info(f'Исполнен ордер {i}')
        return True

    @staticmethod
    def check_balances_to_free(balances: BalancesState) -> bool:
        for asset, balance in balances.items():
            if balance.used != 0:
                return False
        return True

    def get_order(self, order_type: str, orderbooks: OrderbookState, balances: BalancesState) -> Order:
        """
        Создаем ордер из случайного маркета
        :param order_type:
        :param orderbooks:
        :param balances:
        :return:
        """
        shuffled_markets = list(self.markets.items())
        random.shuffle(shuffled_markets)
        for symbol, market in shuffled_markets:
            market_price = (orderbooks[symbol].bids[0][0] + orderbooks[symbol].asks[0][0]) / 2
            if market.limits.cost.min is not None:
                amount = market.limits.cost.min / market_price * 1.1
            else:
                amount = market.limits.amount.min * market_price * 1.1
            if balances[market.base_asset].free > amount:
                price = market_price
                return self.trader.create_unplaced_order(
                    symbol=symbol,
                    order_type=order_type,
                    side='sell',
                    price=price,
                    amount=amount
                )
            elif balances[market.quote_asset].free > amount:
                price = market_price
                return self.trader.create_unplaced_order(
                    symbol='BTC/USDT',
                    order_type=order_type,
                    side='buy',
                    price=price,
                    amount=amount
                )
        raise InsufficientBalance

