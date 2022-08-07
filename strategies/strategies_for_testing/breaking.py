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

    0. Отменяю все ордера и запрашиваю баланс.
    1. Создаю лимитный ордер с нулевой ценой и жду ошибку в течение 5 секунд.
    2. Создаю лимитный и рыночный ордер с нулевым объемом и жду ошибку в течение 5 секунд.
    3. Создаю ордер с `кривым` символом, жду от гейта ошибку в течение 5 секунд
    4. Отправляю ордер с пустым `client_order_id` - жду ошибку гейта в течение 5 секунд.
    5. Отправляю 10 ордеров в одной команде, из которых часть нормальных, часть кривых, жду от гейта
    чтобы на кривые пришла ошибка в течение 5 секунд.
    6. Создаю команду с 10 ордерами, один из них кривой, должно прийти 9 статусов open и 1 ошибка в течение 5 секунд.
    7. Отменяю ордера, созданные на предыдущем шаге, кроме одного ордера.
    8. Отменяю ордер, оставленный на предыдущем шаге, и посылаю в команде отмены один "лишний" ордер с несуществующим
    client_order_id, в ответ ожидаю получить сообщение об ошибке по лишнему ордеру, и сообщение об успешной отмене
    первого ордера.

    Причины, по которым тестирование может быть провалено:
    - некорректная работа гейта;
    - гейт не присылает сообщения об ошибках, или присылает их некорректно;
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
        self.logger.info('0. Отменяю все ордера и запрашиваю баланс.')
        trader.cancel_all_orders()
        trader.request_update_balances(assets=self.assets)

        self.logger.info('Жду баланс и ордербуки...')
        # проверяю наличие балансов, а также проверяю с помощью множеств, что для каждого маркета пришел ордербук
        while balances or \
                set(orderbooks.orderbooks.keys()).intersection(self.markets.keys()) != set(self.markets.keys()):
            await asyncio.sleep(0.1)

        self.logger.info('1. Создаю лимитный ордер с нулевой ценой и жду ошибку в течение 5 секунд.')
        zero_price_order = self.get_order(
            order_type='limit',
            price=0
        )
        zero_price_order.place()
        if not await self.wait_for_order_state(zero_price_order, enums.OrderState.ERROR, 5):
            self.logger.critical(
                f'TEST FAILED. Ордер не вернулся с ошибкой {zero_price_order} в течение 5 секунд')
            return

        self.logger.info('2. Создаю лимитный и рыночный ордер с нулевым объемом и жду ошибку в течение 5 секунд.')
        zero_amount_limit_order = self.get_order(
            order_type='limit',
            amount=0
        )
        zero_amount_market_order = self.get_order(
            order_type='market',
            amount=0
        )
        zero_amount_limit_order.place()
        if not await self.wait_for_order_state(zero_amount_limit_order, enums.OrderState.ERROR, 5):
            self.logger.critical(
                f'TEST FAILED. Ордер не вернулся с ошибкой {zero_amount_limit_order} в течение 5 секунд')
            return
        zero_amount_market_order.place()
        if not await self.wait_for_order_state(zero_amount_market_order, enums.OrderState.ERROR, 5):
            self.logger.critical(
                f'TEST FAILED. Ордер не вернулся с ошибкой {zero_amount_market_order}')
            return

        self.logger.info('3. Создаю ордер с `кривым` символом, жду от гейта ошибку в течение 5 секунд')
        invalid_symbol_order = self.get_order(
            order_type='limit',
            price=0
        )
        invalid_symbol_order.place()
        if not await self.wait_for_order_state(invalid_symbol_order, enums.OrderState.ERROR, 5):
            self.logger.critical(
                f'TEST FAILED. Ордер не вернулся с ошибкой {invalid_symbol_order}')
            return

        self.logger.info('4. Отправляю ордер с пустым `client_order_id` - жду ошибку гейта в течение 5 секунд.')
        empty_id_order = self.get_order(
            order_type='limit',
            price=0
        )
        empty_id_order.core_order_id = ''
        empty_id_order.place()
        if not await self.wait_for_order_state(empty_id_order, enums.OrderState.ERROR, 5):
            self.logger.critical(
                f'TEST FAILED. Ордер не вернулся с ошибкой {empty_id_order} в течение 5 секунд')
            return

        self.logger.info('5. Отправляю 10 ордеров в одной команде, из которых часть нормальных, '
                         'часть кривых, жду от гейта чтобы на кривые пришла ошибка в течение 5 секунд.')
        # чётные ордера - кривые, нечетные - нормальные. Жду 5 секунд после того, как отправляю ордер гейту
        for i in range(10):
            self.logger.info(f'Order {i}')
            if i % 2 == 0:
                # создаю ордер с очень большим amount
                order = self.get_order(order_type='limit', amount=10 ** 7)
                order.place()
                if not await self.wait_for_order_state(order, enums.OrderState.ERROR, 5):
                    self.logger.critical(
                        f'TEST FAILED. Ордер не вернулся с ошибкой {order} в течение 5 секунд')
                    return
            else:
                order = self.get_order(order_type='limit')
                order.place()
                if not await self.wait_for_order_state(order, enums.OrderState.OPEN, 5):
                    self.logger.critical(
                        f'TEST FAILED. Ордер не был открыт на бирже {order} в течение 5 секунд')
                    return
                order.cancel()
                # жду, пока ордер закроется
                await asyncio.sleep(0.3)

        self.logger.info('6. Создаю команду с 10 ордерами, один из них кривой, должно прийти 9 статусов open '
                         'и 1 ошибка в течение 5 секунд.')
        partially_invalid_orders = [self.get_order('limit') for _ in range(9)]
        # создаю ордер с очень большим amount
        partially_invalid_orders.append(self.get_order('limit', amount=10 ** 7))
        trader.place_orders(*partially_invalid_orders)
        await asyncio.sleep(5)

        # проверка, что не был выставлен только неправильный ордер
        for order in partially_invalid_orders[:9]:
            if order.state in [enums.OrderState.PLACING, enums.OrderState.ERROR]:
                self.logger.critical(
                    f'TEST FAILED. Ордер не был открыт на бирже {empty_id_order} в течение 5 секунд')
        if partially_invalid_orders[9].state != enums.OrderState.ERROR:
            self.logger.critical(
                f'TEST FAILED. Ордер не вернулся с ошибкой {empty_id_order} в течение 5 секунд')

        self.logger('7. Отменяю ордера, созданные на предыдущем шаге, кроме одного ордера.')
        trader.cancel_orders(*partially_invalid_orders[:8])
        await asyncio.sleep(1)
        self.logger.info('8. Отменяю ордер, оставленный на предыдущем шаге, и посылаю в команде отмены один "лишний" '
                         'ордер с несуществующим client_order_id, в ответ в течение 3 секунд ожидаю получить сообщение '
                         'об ошибке по лишнему ордеру, и сообщение об успешной отмене первого ордера.')
        # создаю ордер, который не размещен на бирже
        unplaced_order = self.get_order('limit')
        trader.cancel_orders(partially_invalid_orders[8], unplaced_order)
        await asyncio.sleep(3)
        if trader.last_error is None or \
                trader.last_error.action != enums.Action.CANCEL_ORDERS or \
                trader.last_error.data[0].client_order_id != unplaced_order.core_order_id:
            self.logger.info(f'TEST FAILED. Последнее полученное сообщение об ошибке не содержит информацию о '
                             f'несуществующем ордере {unplaced_order}, который ядро пыталось отменить. Также тест мог '
                             f'быть провален, если ядро получило другое сообщение об ошибке сразу после ошибки '
                             f'cancel_orders. Последнее сообщение об ошибке: {trader.last_error}')
            return

        if partially_invalid_orders[8].state != enums.OrderState.CANCELED:
            self.logger.info(f'TEST FAILED. Ордер {partially_invalid_orders[8]} не был отменен.')
            return

        self.logger.info('9. Пробую получить информацию по несуществующему ордеру, ожидаю получить в ответ в течение '
                         '3 секунд сообщение об ошибке.')
        trader.request_update_orders(unplaced_order)
        await asyncio.sleep(3)
        if trader.last_error is None or \
                trader.last_error.action != enums.Action.GET_ORDERS or \
                trader.last_error.data[0].client_order_id != unplaced_order.core_order_id:
            self.logger.info(f'TEST FAILED. Последнее полученное сообщение об ошибке не содержит информацию о '
                             f'несуществующем ордере {unplaced_order}, по которому ядро пыталось получить информацию. '
                             f'Также тест мог быть провален, если ядро получило другое сообщение об ошибке сразу после '
                             f'ошибки cancel_orders. Последнее сообщение об ошибке: {trader.last_error}')

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

        # перемешиваю маркеты, чтобы получить случайный и создать по нему ордер (если хватит баланса)
        random.shuffle(shuffled_markets)
        for symbol, market in shuffled_markets:
            # рыночная цена это середина спреда (лучшего бида и лучшего аска)
            market_price = (orderbooks[symbol].bids[0][0] + orderbooks[symbol].asks[0][0]) / 2
            price = market_price if price is None else price
            if amount is None:
                amount = 0
                if market.limits.cost.min is not None:
                    # умножаю на коэффициент, чтобы объем был немного больше минимального
                    amount = market.limits.cost.min / market_price * 1.1
                if market.limits.cost.min is None or amount < market.limits.amount.min:
                    # умножаю на коэффициен, чтобы объем был немного больше минимального
                    amount = market.limits.amount.min * 1.1
            if balances[market.base_asset].free > balances[market.quote_asset].free:
                return self.trader.create_unplaced_order(
                    symbol=symbol if symbol_in_order is None else symbol_in_order,
                    order_type=order_type,
                    side='sell',
                    # умножаю цену на коэффициент, чтобы лимитные ордера не исполнялись сразу же
                    price=price * 1.1,
                    amount=amount,
                    enable_validating=False,
                )
            else:
                return self.trader.create_unplaced_order(
                    symbol=symbol if symbol_in_order is None else symbol_in_order,
                    order_type=order_type,
                    side='buy',
                    # умножаю цену на коэффициент, чтобы лимитные ордера не исполнялись сразу же
                    price=price * 0.9,
                    amount=amount,
                    enable_validating=False
                )
        raise InsufficientBalance

    async def wait_for_order_state(self, order: Order, state: enums.OrderState, max_waiting_time: int):
        """
        Дождаться пока ордер примет правильное состояние. Есть ограничение максимального времени ожидания
        """
        sleeping_time = 0
        while order.state != state:
            await asyncio.sleep(0.1)
            sleeping_time += 0.1
            if sleeping_time >= max_waiting_time:
                return False
        return True
