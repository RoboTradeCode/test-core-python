import asyncio

from testing_core import enums
from testing_core.order.order import Order
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class FastTesting(Strategy):
    """
    Быстрая стратегия для проверки основных функций гейта.

    1. Отмена всех ордеров и запрос баланса - типичная операция на старте ядра
    2. Ожидание, пока не придут балансы и ордербуки
    3. Выставление лимитного ордера
    4. Запрос статуса лимитного ордера
    5. Отмена лимитного ордера
    6. Выставление рыночного ордера
    """
    name = 'Fast Testing'

    assets = ['BTC', 'USDT', 'ETH']

    async def strategy(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        """
        Стратегия для быстрого тестирования гейта.
        :param trader:
        :param orderbooks:
        :param balances:
        :return:
        """
        trader.cancel_all_orders()
        trader.request_update_balances(assets=self.assets)

        self.logger.info('Wait balances and orderbooks...')
        # дожидаюсь, пока будет получен баланс и ордербук от гейта
        while balances or orderbooks['BTC/USDT'] is None or orderbooks['ETH/USDT'] is None:
            await asyncio.sleep(0.1)

        self.logger.info(f'Balances: {balances.balances}')
        self.logger.info(f'Orderbooks: {orderbooks["BTC/USDT"]}')

        self.logger.info(f'Try to creating limit order')
        price_btcusdt = orderbooks['BTC/USDT'].bids[0][0]
        price_ethusdt = orderbooks['ETH/USDT'].bids[0][0]

        limit_order = self.get_order(order_type='limit', balances=balances, price_btcusdt=price_btcusdt,
                                     price_ethusdt=price_ethusdt)

        self.logger.info('Wait order info...')
        while limit_order.state == enums.OrderState.PLACING:
            await asyncio.sleep(0.1)

        self.logger.info(f'Limit order: {limit_order}')

        self.logger.info('Try to request order info')
        trader.request_update_orders(limit_order)
        await asyncio.sleep(1)

        self.logger.info('Try to cancel limit order')
        limit_order.cancel()

        self.logger.info('Wait order info...')
        while limit_order.state != enums.OrderState.CANCELED:
            await asyncio.sleep(0.1)

        self.logger.info(f'Cancelled limit order: {limit_order}')

        market_order = self.get_order(order_type='market', balances=balances, price_btcusdt=price_btcusdt,
                                      price_ethusdt=price_ethusdt)

        self.logger.info('Wait order info...')
        while market_order.state == enums.OrderState.PLACING:
            await asyncio.sleep(0.1)

        self.logger.info(f'Market order: {market_order}')

    def get_order(self, order_type: str, price_btcusdt: float, price_ethusdt: float, balances: BalancesState) -> Order:
        if balances['BTC'].free > 11 / price_btcusdt:
            amount = 10.5 / price_btcusdt
            price = price_btcusdt + 100
            return self.trader.create_order(
                symbol='BTC/USDT',
                order_type=order_type,
                side='sell',
                price=price,
                amount=amount
            )
        elif balances['USDT'].free > 11:
            amount = 10.5 / price_btcusdt
            price = price_btcusdt - 100
            return self.trader.create_order(
                symbol='BTC/USDT',
                order_type=order_type,
                side='buy',
                price=price,
                amount=amount
            )
        elif balances['ETH'].free > 11 / price_ethusdt:
            amount = 10.5 / price_ethusdt
            price = price_ethusdt + 100
            return self.trader.create_order(
                symbol='ETH/USDT',
                order_type=order_type,
                side='sell',
                price=price,
                amount=amount
            )
