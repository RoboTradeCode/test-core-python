import asyncio
import random

from testing_core import enums
from testing_core.exceptions import InsufficientBalance
from testing_core.order.order import Order
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class BreakingTesting(Strategy):
    """
    Стратегия неправильного поведения ядра. Тестирование стремится сломать гейт.

    1. Создаем лимитный ордер с нулевой ценой и должна быть ошибка от гейта.
    2. Создаем лимитный и рыночный ордер с нулевым объемом и ждем ошибку.
    3. Создаем ордер с `кривым` символом, ждем от гейта ошибку
    4. Отправляем ордер с пустым `client_order_id` - ждем ошибку гейта.
    5. Отправляем 10 ордеров в одной команде, из которых часть нормальных, часть кривых, ждем от гейта чтобы
    на кривые пришла ошибка.
    6. Создаем команду с 10 ордерами, 1 из них кривой, должно прийти 9 статусов open и одна ошибка.
    """
    name = 'Order Creating Testing'

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

        self.logger.info('1. Создаем лимитный ордер с нулевой ценой и должна быть ошибка от гейта.')
        zero_price_order = self.get_order(
            order_type='limit',
            price=0
        )
        zero_price_order.place()

        self.logger.info('2. Создаем лимитный и рыночный ордер с нулевым объемом и ждем ошибку.')
        zero_amount_limit_order = self.get_order(
            order_type='limit',
            amount=0
        )
        zero_amount_market_order = self.get_order(
            order_type='market',
            amount=0
        )
        zero_amount_limit_order.place()
        zero_amount_market_order.place()

        self.logger.info('3. Создаем ордер с `кривым` символом, ждем от гейта ошибку')
        zero_price_order = self.get_order(
            order_type='limit',
            price=0
        )
        zero_price_order.place()

        self.logger.info('4. Отправляем ордер с пустым `client_order_id` - ждем ошибку гейта.')
        empty_id_order = self.get_order(
            order_type='limit',
            price=0
        )
        empty_id_order.core_order_id = ''
        empty_id_order.place()

        self.logger.info('5. Отправляем 10 ордеров в одной команде, из которых часть нормальных, '
                         'часть кривых, ждем от гейта чтобы на кривые пришла ошибка.')
        for i in range(10):
            if i % 2 == 0:
                # create invalid order
                order = self.get_order(order_type='limit', amount=-10)
            else:
                order = self.get_order(order_type='limit')
            order.place()

        self.logger.info('6. Создаем команду с 10 ордерами, 1 из них кривой, должно прийти '
                         '9 статусов open и одна ошибка.')
        partially_invalid_orders = [self.get_order('limit') for _ in range(9)]
        # create invalid order
        partially_invalid_orders.append(self.get_order('limit', amount=-10))
        trader.place_orders(*partially_invalid_orders)

        self.logger.info('SUCCESS. Тест успешно пройден.')
        return

    def get_order(
            self,
            order_type: str,
            price: float = None,
            amount: float = None,
            symbol_in_order: str = None
    ) -> Order:
        """
        Создаем ордер из случайного маркета
        :param amount:
        :param price:
        :param order_type:
        :return:
        """
        orderbooks = self.trader.orderbooks
        balances = self.trader.balances
        shuffled_markets = list(self.markets.items())

        random.shuffle(shuffled_markets)
        for symbol, market in shuffled_markets:
            market_price = (orderbooks[symbol].bids[0][0] + orderbooks[symbol].asks[0][0]) / 2
            price = market_price if price is None else price
            if amount is None and market.limits.cost.min is not None:
                amount = market.limits.cost.min / market_price * 1.1
            elif amount is None:
                amount = market.limits.amount.min * market_price * 1.1
            if balances[market.base_asset].free > amount:
                return self.trader.create_unplaced_order(
                    symbol=symbol if symbol_in_order is None else symbol_in_order,
                    order_type=order_type,
                    side='sell',
                    price=price,
                    amount=amount,
                    enable_validating=False,
                )
            elif balances[market.quote_asset].free > amount:
                return self.trader.create_unplaced_order(
                    symbol=symbol if symbol_in_order is None else symbol_in_order,
                    order_type=order_type,
                    side='buy',
                    price=price,
                    amount=amount,
                    enable_validating=False
                )
        raise InsufficientBalance
