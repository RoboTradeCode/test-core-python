import asyncio
import random

from testing_core import enums
from testing_core.exceptions import InsufficientBalance
from testing_core.order.order import Order
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class OrderCreatingTesting(Strategy):
    """
    Стратегия тестирования корректного создания ордеров

    1. Отменяем все ордера и запрашиваем баланс.
    2. Создаем лимитный ордер на случайном маркете. Цена подбирается таким образом, чтобы ордер быстро исполнился.
    3. Жду от гейта статусы об открытии, затем о закрытии.
    4. Шаги 2 и 3 повторяются 10 раз.
    5. Создаю рычночный ордер на случайном маркете.
    6. Жду от гейта статусы об открытии, затем о закрытии.
    7. Шаги 5 и 6 повторяются 10 раз.
    8. Отправляю команду гейту, в которой есть лимитные и рыночные ордера одновременно.

    Причины, по которым тестирование может быть провалено:
    - некорректная работа гейта;
    - нехватка баланса на бирже;
    - проблемы с доступом к бирже со стороны гейта;
    - неправильно настроенная конфигурация (каналы aeron, ассеты и т.п.);
    """
    name = 'Order Creating Testing'

    async def execute(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
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
        # небольшая задержка, чтобы успела исполниться команда cancel_all_orders
        await asyncio.sleep(0.5)

        self.logger.info('Жду баланс и ордербуки...')
        # проверяю наличие балансов, а также проверяю с помощью множеств, что для каждого маркета пришел ордербук
        while balances or \
                set(orderbooks.orderbooks.keys()).intersection(self.markets.keys()) != set(self.markets.keys()):
            await asyncio.sleep(0.1)

        self.logger.info('2. Создаем лимитный ордер на случайном маркете. '
                         'Цена подбирается таким образом, чтобы ордер быстро исполнился. ')
        self.logger.info('3. Жду от гейта статусы об открытии, затем о закрытии. Статус должен приходить за 5 секунд.')
        self.logger.info('4. Шаги 2 и 3 повторяются 10 раз.')
        is_successful_limit_orders = await self.execute_10_orders('limit', balances, orderbooks)
        if not is_successful_limit_orders:
            return

        self.logger.info('5. Создаю рычночный ордер на случайном маркете. ')
        self.logger.info('6. Жду от гейта статусы об открытии, затем о закрытии. Статус должен приходить за 5 секунд.')
        self.logger.info('7. Шаги 5 и 6 повторяются 10 раз.')
        is_successful_market_orders = await self.execute_10_orders('market', balances, orderbooks)
        if not is_successful_market_orders:
            return

        self.logger.info('8. Отправляю команду гейту, в которой есть лимитные и рыночные ордера одновременно. '
                         'Ожидание 5 секунд')
        orders = [self.get_order('limit', orderbooks, balances), self.get_order('market', orderbooks, balances)]
        for order in orders:
            order.place()
        executing_sleeping_time = 0
        while orders[0].state != enums.OrderState.CLOSED and orders[1].state != enums.OrderState.CLOSED:
            await asyncio.sleep(0.1)
            executing_sleeping_time += 0.1
            if executing_sleeping_time >= 5:
                self.logger.critical(
                    f'TEST FAILED. Не удалось исполнить ордера {orders} за 5 секунд')
                return

        self.logger.info('SUCCESS. Тест успешно пройден.')
        return

    async def execute_10_orders(self, order_type, balances, orderbooks):
        orders = [self.get_order(order_type=order_type, orderbooks=orderbooks, balances=balances) for _ in range(10)]
        for i, order in enumerate(orders):
            self.logger.info(f'Выставление ордера {i}')
            order.place()
            # после выстваления ордера жду 5 секунд, периодически проверяю ордер
            placing_sleeping_time = 0
            while order.state == enums.OrderState.PLACING:
                await asyncio.sleep(0.1)
                placing_sleeping_time += 0.1
                if placing_sleeping_time >= 5:
                    self.logger.critical(
                        f'TEST FAILED. Не удалось создать ордер {order} в течение 5 секунд.')
                    return False
            executing_sleeping_time = 0
            while order.state == enums.OrderState.OPEN:
                await asyncio.sleep(0.1)
                executing_sleeping_time += 0.1
                if executing_sleeping_time >= 30:
                    self.logger.critical(
                        f'TEST FAILED. Не удалось исполнить ордер {order} в течение 30 секунд. Возможно, маркет'
                        f' {order.symbol} слишком волатильный или низколиквидный')
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
            amount = 0
            if market.limits.cost.min is not None:
                # умножаю на коэффициент, чтобы объем был немного больше минимального
                amount = market.limits.cost.min / market_price * 1.1
            if market.limits.cost.min is None or amount < market.limits.amount.min:
                # умножаю на коэффициен, чтобы объем был немного больше минимального
                amount = market.limits.amount.min * 1.1
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
                    symbol=symbol,
                    order_type=order_type,
                    side='buy',
                    price=price,
                    amount=amount
                )
        raise InsufficientBalance
