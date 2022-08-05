import asyncio
import random

from testing_core import enums
from testing_core.exceptions import InsufficientBalance
from testing_core.order.order import Order
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class FastTesting(Strategy):
    """
    Быстрая стратегия для проверки основных функций гейта.

    1. Отмена всех ордеров и запрос баланса - типичная операция на старте ядра
    2. Ожидание, пока придут балансы и ордербуки
    3. Выставление лимитного ордера
    4. Запрос статуса лимитного ордера
    5. Отмена лимитного ордера
    6. Выставление рыночного ордера

    Причины, по которым тестирование может быть провалено:
    - некорректная работа гейта;
    - нехватка баланса на бирже;
    - проблемы с доступом к бирже со стороны гейта;
    - неправильно настроенная конфигурация (каналы aeron, ассеты и т.п.);
    """
    name = 'Fast Testing'

    async def execute(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        """
        Стратегия для быстрого тестирования гейта.
        """
        self.logger.info('1. Отмена всех ордеров и запрос баланса')
        trader.cancel_all_orders()
        trader.request_update_balances(assets=self.assets)

        self.logger.info('2. Ожидание, пока придут балансы и ордербуки')
        # проверяю наличие балансов, а также проверяю с помощью множеств, что для каждого маркета пришел ордербук
        while balances or \
                set(orderbooks.orderbooks.keys()).intersection(self.markets.keys()) != set(self.markets.keys()):
            await asyncio.sleep(0.1)

        self.logger.info(f'Балансы: {balances.balances}')
        self.logger.info(f'Ордербуки: {orderbooks.orderbooks}')

        self.logger.info(f'3. Выставление лимитного ордера')
        limit_order = self.get_order(order_type='limit', orderbooks=orderbooks, balances=balances)
        limit_order.place()

        self.logger.info('Ожидание информации по ордеру...')
        while limit_order.state == enums.OrderState.PLACING:
            await asyncio.sleep(0.1)

        self.logger.info(f'Лимитные ордер: {limit_order}')

        self.logger.info('4. Запрос статуса лимитного ордера')
        trader.request_update_orders(limit_order)
        await asyncio.sleep(1)

        self.logger.info('5. Отмена лимитного ордера')
        limit_order.cancel()

        self.logger.info('Ожидание информации по ордеру...')
        while limit_order.state != enums.OrderState.CANCELED:
            await asyncio.sleep(0.1)

        self.logger.info(f'Отмененный лимитный ордер: {limit_order}')

        self.logger.info('6. Выставление рыночного ордера')
        market_order = self.get_order(order_type='market', orderbooks=orderbooks, balances=balances)

        self.logger.info('Ожидание информации по ордеру...')
        while market_order.state == enums.OrderState.PLACING:
            await asyncio.sleep(0.1)

        self.logger.info(f'Рыночный ордер: {market_order}')

        self.logger.info('SUCCESS. Test completed.')

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
            # рыночная цена это середина спреда (лучшего бида и лучшего аска)
            # если выставить лимитный ордер по рыночной цене, то он исполнится быстро
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
                    price=price * 1.1,
                    amount=amount
                )
            elif balances[market.quote_asset].free > amount:
                price = market_price
                return self.trader.create_unplaced_order(
                    symbol=symbol,
                    order_type=order_type,
                    side='buy',
                    price=price * 0.9,
                    amount=amount
                )
        raise InsufficientBalance
