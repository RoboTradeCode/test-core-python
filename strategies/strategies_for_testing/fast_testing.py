import asyncio
import time

from testing_core.strategy.base_strategy import Strategy


class FastStrategy(Strategy):
    name = 'Fast Strategy'
    description = 'fast testing of gate. Using basic commands, ' \
                  'creating and cancelling market and limit orders'

    assets = ['BTC', 'USDT', 'ETH']

    async def execute(self):
        self.trader.cancel_all_orders()
        self.trader.request_update_balances(assets=self.assets)

        # дожидаюсь, пока будет получен баланс и ордербук от гейта
        while not self.trader.balances and self.trader.orderbooks.get('BTC/USDT'):
            await asyncio.sleep(0.1)

        print(f'Balances: {self.trader.balances}')
        print(f'Orderbooks: {self.trader.orderbooks}')

