import asyncio
import copy
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
    Стратегия тестирования обновлений баланса

    1. Отменяю все ордера и запрашиваю баланс.
    2. Случайным образом выбираю рынок, выставляю по нему ордер, повторяю 5 раз. При выставлении баланс
    должен изменяться и приходить в течении 0.5 секунды
    3. Отменяю ордера, созданные на шаге 2. Баланс должен изменяться и приходить в течении 0.5 секунды.
    """
    name = 'Balances Testing'

    async def execute(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        """
        Стратегия для быстрого тестирования гейта.
        :param trader:
        :param orderbooks:
        :param balances:
        :return:
        """
        self.logger.info('1. Отменяю все ордера и запрашиваю баланс.')
        trader.cancel_all_orders()
        trader.request_update_balances(assets=self.assets)
        # небольшая задержка, чтобы успела исполниться команда cancel_all_orders
        await asyncio.sleep(0.5)

        self.logger.info('Жду баланс и ордербуки...')
        # проверяю наличие балансов, а также проверяю с помощью множеств, что для каждого маркета пришел ордербук
        while balances or \
                set(orderbooks.orderbooks.keys()).intersection(self.markets.keys()) != set(self.markets.keys()):
            await asyncio.sleep(0.1)

        self.logger.info('2. Случайным образом выбираю рынок, выставляю по нему ордер, повторяю 5 раз. При '
                         'выставлении баланс должен изменяться и приходить в течении 0.5 секунды')
        orders = [self.get_order(order_type='limit', orderbooks=orderbooks, balances=balances) for _ in range(5)]
        last_balances = copy.deepcopy(balances)
        for order in orders:
            order.place()
            while order.state == enums.OrderState.PLACING:
                await asyncio.sleep(0.01)
            if order.state == enums.OrderState.ERROR:
                self.logger.critical(f'TEST FAILED. Не удалось выставить ордер. Пожалуйста, запустите тестирование'
                                     f'order-creating, чтобы проверить выставление ордеров.')
            await asyncio.sleep(0.5)
            if balances == last_balances:
                self.logger.critical(f'TEST FAILED. Баланс по символу {order.symbol} не обновился в '
                                     f'течение 0.5 секунды. Текущий баланс: {balances}\n'
                                     f'Баланс до отмены ордера: {last_balances}')
            last_balances = copy.deepcopy(balances)

        self.logger.info('3. Отменяю ордера, созданные на шаге 2. '
                         'Баланс должен изменяться и приходить в течении 0.5 секунды.')
        for order in orders:
            order.cancel()
            while order.state != enums.OrderState.CANCELED:
                await asyncio.sleep(0.01)
            if order.state == enums.OrderState.ERROR:
                self.logger.critical(f'TEST FAILED. Не удалось отменить ордер. Пожалуйста, запустите тестирование'
                                     f'order-cancelling, чтобы проверить отмену ордеров.')
            await asyncio.sleep(0.5)
            if balances == last_balances:
                self.logger.critical(f'TEST FAILED. Баланс по символу {order.symbol} не обновился в '
                                     f'течение 0.5 секунды. Текущий баланс: {balances}\n'
                                     f'Баланс до отмены ордера: {last_balances}')
            last_balances = copy.deepcopy(balances)

        self.logger.info('SUCCESS. Тест успешно пройден.')
        return

    def get_order(self, order_type: str, orderbooks: OrderbookState, balances: BalancesState) -> Order:
        """
        Создаем ордер из случайного маркета
        :param order_type:
        :param orderbooks:
        :param balances:
        :return:
        """
        # перемешиваю маркеты, чтобы получить случайный и создать по нему ордер (если хватит баланса)
        shuffled_markets = list(self.markets.items())
        random.shuffle(shuffled_markets)
        for symbol, market in shuffled_markets:
            market_price = orderbooks[symbol].bids[0][0]

            # вычисляю минимальные корректный объем ордера
            amount = 0
            if market.limits.cost.min is not None:
                # умножаю на коэффициент, чтобы объем был немного больше минимального
                amount = market.limits.cost.min / market_price * 1.1
            if market.limits.cost.min is None or amount < market.limits.amount.min:
                # умножаю на коэффициен, чтобы объем был немного больше минимального
                amount = market.limits.amount.min * 1.1
            if balances[market.base_asset].free > amount:
                # умножаю ценлу ордера на коэффициент, чтобы лимитный ордер не исполнился сразу
                price = market_price * 1.3
                return self.trader.create_unplaced_order(
                    symbol=symbol,
                    order_type=order_type,
                    side='sell',
                    price=price,
                    amount=amount
                )
            elif balances[market.quote_asset].free > amount:
                # умножаю ценлу ордера на коэффициент, чтобы лимитный ордер не исполнился сразу
                price = market_price * 0.7
                return self.trader.create_unplaced_order(
                    symbol=symbol,
                    order_type=order_type,
                    side='buy',
                    price=price,
                    amount=amount
                )
        raise InsufficientBalance
