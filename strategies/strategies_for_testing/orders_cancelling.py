import asyncio
import random

from testing_core import enums
from testing_core.exceptions import InsufficientBalance
from testing_core.order.order import Order
from testing_core.store.state_balances import BalancesState
from testing_core.store.state_orderbook import OrderbookState
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader


class CancellingTesting(Strategy):
    """
    Стратегия тестирования отмены ордеров

    1. Посылаем команду гейту на отмену всех ордеров, принимаем ответ на команду
    отмены (пока что ответ на отмену еще не реализован)
    2. Проверяем баланс, поле `used` у всех ассетов должно быть нулевым, если где-то не нулевое, ждем 1 секунду,
    повторяем пункт 1.
    2.1. Если поле `used` у какого-то ассета не нулевое - тест провален
    3. Выбираем случайным образом рынок (BTC/USDT) из настроек, и ставим по нему 1 ордер.
    4. Баланс после установки должен измениться, а именно, поле `used`
    5. Отменяем ранее выставленный ордер по id
    6. Проверяем баланс, поле `used` у ассетов должно быть нулевым, если не нулевое - тест провален
    7. Ордер должен бы получить статус cancelled.
    8. Выбираем случайным образом от 3 до 5 рынков из настроек и выполняем с п.3 - 7., Только ордера
    создаем одной командой, и отменяем командой`cancel_all_orders
    8.1. Выбираем 5 случайных рынков и создаем по ним лимитные ордера.
    8.2. Баланс после установки должен измениться, а именно, поле used
    8.3 Отменяем ранее выставленный ордер
    8.4. Проверяем баланс, поле used у ассетов должно быть нулевым, если не нулевое - тест провален
    8.5 Ордера должны были получить статус cancelled, после получения сообщения об успешной отмене ордеров.
    """
    name = 'Cancelling Testing'

    async def execute(self, trader: Trader, orderbooks: OrderbookState, balances: BalancesState):
        """
        Стратегия для быстрого тестирования гейта.
        :param trader:
        :param orderbooks:
        :param balances:
        :return:
        """
        self.logger.info('1. Посылаем команду гейту на отмену всех ордеров, принимаем ответ на команду отмены '
                         '(пока что ответ на отмену еще не реализован)')
        trader.cancel_all_orders()
        trader.request_update_balances(assets=self.assets)
        # небольшая задержка, чтобы успела исполниться команда cancel_all_orders
        await asyncio.sleep(0.5)

        self.logger.info('Жду баланс и ордербуки...')
        # проверяю наличие балансов, а также проверяю с помощью множеств, что для каждого маркета пришел ордербук
        while balances or \
                set(orderbooks.orderbooks.keys()).intersection(self.markets.keys()) != set(self.markets.keys()):
            await asyncio.sleep(0.1)

        self.logger.info(' 2. Проверяем баланс, поле `used` у всех ассетов должно быть нулевым, '
                         'если где-то не нулевое, ждем 1 секунду, повторяем пункт 1.')
        if not self.check_balances_to_free(balances):
            trader.cancel_all_orders()
            await asyncio.sleep(2)
            if not self.check_balances_to_free(balances):
                self.logger.info('2.1. Если поле `used` у какого-то ассета не нулевое - тест провален')
                self.logger.critical('TEST FAILED. Не удалось отменить все ордера, есть используемый баланс.')
                return

        self.logger.info(' 3. Выбираем случайным образом рынок (BTC/USDT) из настроек, и ставим по нему 1 ордер.')
        order = self.get_order(order_type='limit', orderbooks=orderbooks, balances=balances)
        trader.place_orders(order)

        self.logger.info('Жду информации об ордере...')
        while order.state == enums.OrderState.PLACING:
            await asyncio.sleep(0.1)

        self.logger.info('4. Баланс после установки должен измениться, а именно, поле `used`')
        if self.check_balances_to_free(balances=balances):
            self.logger.critical(
                f'TEST FAILED. После создания ордера должен был появиться используемый баланс: {balances}')
            return

        self.logger.info('5. Отменяем ранее выставленный ордер по id')
        order.cancel()

        self.logger.info('6. Проверяем баланс, поле `used` у ассетов должно быть нулевым, если не нулевое -'
                         ' тест провален')
        await asyncio.sleep(2)
        if not self.check_balances_to_free(balances):
            self.logger.critical(f'TEST FAILED. Не удалось отменить ордер, есть используемый баланс: {balances}')
            return

        self.logger.info('7. Ордер должен бы получить статус cancelled.')
        if order.state != enums.OrderState.CANCELED:
            self.logger.critical(f'TEST FAILED. Не удалось отменить ордер, либо не был получен ответ '
                                 f'на команду отмены ордеров: {order}')
            return

        self.logger.info('8. Выбираем случайным образом от 3 до 5 рынков из настроек и выполняем с п.3 - 7. '
                         'Только ордера создаем Только ордера создаем одной командой, и отменяем '
                         'командой `cancel_all_orders')

        self.logger.info('8.1. Выбираем 5 случайных рынков и создаем по ним лимитные ордера.')

        orders = [self.get_order(order_type='limit', orderbooks=orderbooks, balances=balances) for _ in range(5)]
        trader.place_orders(*orders)

        self.logger.info('Жду информации об ордерах...')
        while True:
            await asyncio.sleep(0.5)
            for order in orders:
                if order.state == enums.OrderState.PLACING:
                    continue
            break

        self.logger.info('8.2. Баланс после установки должен измениться, а именно, поле `used`')
        if self.check_balances_to_free(balances=balances):
            self.logger.critical(
                f'TEST FAILED. После создания ордера должен был появиться используемый баланс: {balances}')
            return

        self.logger.info('8.3 Отменяем ранее выставленный ордер')
        trader.cancel_all_orders()

        self.logger.info('8.4. Проверяем баланс, поле `used` у ассетов должно быть нулевым, если не нулевое -'
                         ' тест провален')
        trader.request_update_balances(self.assets)
        await asyncio.sleep(5)
        if not self.check_balances_to_free(balances):
            self.logger.critical(f'TEST FAILED. Не удалось отменить ордера, есть используемый баланс: {balances}')
            return

        self.logger.info('8.5 Ордера должны были получить статус cancelled.')
        for order in orders:
            if order.state != enums.OrderState.CANCELED:
                self.logger.critical(f'TEST FAILED. Не удалось отменить ордер, либо не был получен ответ '
                                     f'на команду отмены ордеров: {order}')
                return

        self.logger.info('SUCCESS. Тест успешно пройден.')
        return

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
