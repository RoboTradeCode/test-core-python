import datetime
import json
from pprint import pprint
from time import sleep
import time
import logging.config
from aeron import Subscriber, Publisher
import asyncio

from src.schemes.base_scheme import BaseScheme
from src.logging.logger import logging_config
from src.schemes.core_schemes import CancelAllOrdersCommand, CreateOrderCommand, GetBalanceCommand, CancelOrderCommand, \
    OrderStatusCommand
from src.schemes.gate_schemes import OrderBook, Balance, Order

# Загрузка настроек логгера и инициализация логгера
logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


def current_milli_time():
    return round(time.time() * 1_000_000)


def print_time_handler(message: str) -> None:
    try:
        print(datetime.datetime.now())
    except Exception as e:
        print(e)


def empty_handler(message: str) -> None:
    ...


class TestCore:

    def __init__(self):
        self.last_orderbook: dict = {}
        self.balances: dict = {}
        self.orders: list[dict] = []
        self.running = True

        self.algo: str = 'py_test'
        self.exchange: str = ''
        self.command_publisher: Publisher

    # обработчик сообщений от гейта (всех сообщений)
    def handler(self, message: str) -> None:
        try:
            message_data = json.loads(message)
            if message_data.get('event') == 'data':
                match message_data['action']:
                    case 'orderbook':
                        _orderbook = OrderBook(**message_data)
                        if message_data['data']['symbol'] == 'BTC/USDT':
                            self.last_orderbook = message_data['data']
                    case 'balances':
                        _balance = Balance(**message_data)
                        self.balances = message_data['data']
                        logger.info(f'Received balances: {message_data}')
                    case 'order_created':
                        _order = Order(**message_data)
                        logger.info(f'Received order data: {message_data}')
                        self.orders.append(_order.data)
                    case _:
                        logger.warning(f'Unexpected data: {message_data}')
            # elif message_data.get('event') == 'info':
            #     pprint(message_data)
            # print(f'=================================\n'
            #       f'orderbooks: {len(self.orderbooks)}\n'
            #       f'balances: {len(self.balances)}\n'
            #       f'orders: {len(self.orders)}\n'
            #       f'=================================')
        except Exception as e:
            print(e)

    def send_command(self, command: BaseScheme):
        if not self.command_publisher:
            raise Exception
        message = json.dumps(command, default=lambda o: o.__dict__)
        self.command_publisher.offer(message)

    def cancel_all_orders(self):
        self.send_command(CancelAllOrdersCommand(
            event="command",
            exchange=self.exchange,
            node="core",
            instance="py_test_core",
            action="cancel_all_orders",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=None
        ))

    def cancel_order(self, order_id: str, symbol: str):
        self.send_command(CancelOrderCommand(
            event="command",
            exchange=self.exchange,
            node="core",
            instance="py_test_core",
            action="cancel_order",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=[CancelOrderCommand.Order(
                id=order_id,
                symbol=symbol
            )]
        ))

    def order_status(self, order_id: str, symbol: str):
        self.send_command(OrderStatusCommand(
            event="command",
            exchange=self.exchange,
            node="core",
            instance="py_test_core",
            action="order_status",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=OrderStatusCommand.Order(
                id=order_id,
                symbol=symbol
            )
        ))

    def create_order(self, symbol: str, order_type: str, side: str, price: float, amount: float):
        self.send_command(CreateOrderCommand(
            event="command",
            exchange=self.exchange,
            node="core",
            instance="py_test_core",
            action="create_order",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=[CreateOrderCommand.Order(
                symbol=symbol,
                type=order_type,
                side=side,
                price=price,
                amount=amount
            )]
        ))

    def get_balances(self, assets: list[str] = None):
        self.send_command(GetBalanceCommand(
            event="command",
            exchange=self.exchange,
            node="core",
            instance="py_test_core",
            action="get_balances",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=GetBalanceCommand.Asset(
                assets=assets
            ) if assets is not None else None
        ))

    async def listen_gate_loop(self):
        subscribers = {i: Subscriber(self.handler, 'aeron:ipc', i) for i in range(1001, 1010)}
        subscribers[1001] = Subscriber(empty_handler, 'aeron:ipc', 1001)
        # subscribers[1006] = Subscriber(empty_handler, 'aeron:ipc', 1006)

        while self.running:
            for subscriber in subscribers.values():
                subscriber.poll()
            await asyncio.sleep(0.0001)

    async def logging_loop(self, sleep_delay: float):
        while self.running:
            print(f'=================================\n'
                  f'orderbooks: {len(self.last_orderbook)}\n'
                  f'balances: {len(self.balances)}\n'
                  f'orders: {len(self.orders)}\n'
                  f'=================================')
            await asyncio.sleep(sleep_delay)

    async def trade_strategy_loop(self):
        # command_publisher = Publisher('aeron:ipc', stream_id=1004)
        # while self.running:
        #     self.cancel_all_orders()
        #     self.get_balances(['BTC', 'USDT'])
        #
        #     while self.orderbooks is {} or self.balances is {}:
        #         await asyncio.sleep(1)
        ...

    async def _fast_test_strategy(self):
        logger.info('Start Fast testing.')
        self.command_publisher = Publisher('aeron:ipc', stream_id=1004)
        logger.info('Created command publisher.')

        logger.info('Sending command: cancel_all_orders.')
        self.cancel_all_orders()
        logger.info('Sending command: get_balances(["BTC", "USDT"]).')
        self.get_balances(['BTC', 'USDT'])

        while self.last_orderbook == {} or self.balances == {}:
            logger.info('Wait for orderbooks and balances...')
            await asyncio.sleep(5)

        logger.info('Successfully received and saved orderbook and balances.')
        logger.info(f'Balances: {self.balances}')
        logger.info(f'Last orderbook: {self.last_orderbook}')

        order: dict = {}
        if self.balances['USDT']['free'] > 50:
            order = {
                'symbol': 'BTC/USDT',
                'order_type': 'limit',
                'side': 'buy',
                'price': self.last_orderbook['bids'][len(self.last_orderbook['bids']) - 1][0] * 0.9,
                'amount': round(50 / self.last_orderbook['bids'][len(self.last_orderbook['bids']) - 1][0], 5)
            }
        elif self.balances['BTC']['free'] * self.last_orderbook['asks'][0][0] > 50:
            order = {
                'symbol': 'BTC/USDT',
                'order_type': 'limit',
                'side': 'sell',
                'price': self.last_orderbook['asks'][len(self.last_orderbook['asks']) - 1][0] * 1.1,
                'amount': round(50 / self.last_orderbook['asks'][len(self.last_orderbook['asks']) - 1][0], 5)
            }
        logger.info(f'Send command to create_order: {order}')
        self.create_order(**order)
        await asyncio.sleep(5)

        logger.info('Wait for order info...')
        while not self.orders:
            await asyncio.sleep(0.1)

        logger.info(f'Send command order_status: id = {self.orders[0]["id"]}, symbol = {self.orders[0]["symbol"]}')
        self.order_status(self.orders[0]['id'], self.orders[0]['symbol'])
        await asyncio.sleep(5)

        logger.info(f'Send command to cancel_order: id = {self.orders[0]["id"]}, symbol = {self.orders[0]["symbol"]}')
        self.cancel_order(self.orders[0]['id'], self.orders[0]['symbol'])

        logger.info(f'Send command to get_balances for full balance')
        self.get_balances()
        await asyncio.sleep(5)

        logger.info(f'Balances: {self.balances}')

    async def fast_test(self):
        # wait for gate loading
        await asyncio.sleep(1)
        await asyncio.gather(self.listen_gate_loop(), self._fast_test_strategy())

    async def long_test(self):
        ...
