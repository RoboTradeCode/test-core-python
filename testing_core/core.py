import json
import time
import logging.config
import uuid

from aeron import Subscriber, Publisher
import asyncio

from testing_core.message_format import *
from testing_core.logging.logger import logging_config

# Загрузка настроек логгера и инициализация логгера
logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


def current_milli_time():
    return round(time.time() * 1_000_000)


def empty_handler(message: str) -> None:
    ...


class TestCore:

    def __init__(self):
        self.last_orderbook: dict = {}
        self.balances: dict = {}
        self.orders: list[dict] = []
        self.running = True

        self.algo: str = 'py_test'
        self.exchange_name: str = ''
        self.command_publisher: Publisher

    # обработчик сообщений от гейта (всех сообщений)
    def handler(self, message: str) -> None:
        try:
            message_data = json.loads(message)
            match message_data['action']:
                case 'order_book_update':
                    if message_data['data']['symbol'] == 'ETH/USDT':
                        self.last_orderbook = message_data['data']

                        # self.last_orderbooks[message_data['data']['symbol']] = message_data['data']
                case 'get_balance' | 'balances_update':
                    self.balances = message_data['data']['assets']
                    logger.info(f'Received balances: {message_data}')
                case 'orders_update' | 'get_orders':
                    logger.info(f'Received order data: {message_data}')
                    self.orders.append(message_data['data']['client_order_id'])
                case _:
                    logger.warning(f'Unexpected data: {message_data}')
            # print(f'=================================\n'
            #       f'orderbooks: {len(self.orderbooks)}\n'
            #       f'balances: {len(self.balances)}\n'
            #       f'orders: {len(self.orders)}\n'
            #       f'=================================')
        except Exception as e:
            print(e)

    def send_command(self, command: Message):
        if not self.command_publisher:
            raise Exception
        self.command_publisher.offer(command.json())
        logger.info(f'Send command {command.action.value}: {command.json()}')

    def cancel_all_orders(self):
        self.send_command(Message(
            event="command",
            event_id=uuid.uuid4().__str__(),
            exchange=self.exchange_name,
            node="core",
            instance="py_test_core",
            action="cancel_all_orders",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=None
        ))

    def cancel_order(self, order_id: str, symbol: str):
        self.send_command(Message(
            event="command",
            event_id=uuid.uuid4().__str__(),
            exchange=self.exchange_name,
            node="core",
            instance="py_test_core",
            action="cancel_orders",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=[OrderId(
                client_order_id=order_id,
                symbol=symbol
            )]
        ))

    def order_status(self, order_id: str, symbol: str):
        self.send_command(Message(
            event="command",
            event_id=uuid.uuid4().__str__(),
            exchange=self.exchange_name,
            node="core",
            instance="py_test_core",
            action="get_orders",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=[OrderId(
                id=order_id,
                symbol=symbol
            )]
        ))

    def create_order(self, symbol: str, order_type: str, side: str, price: float, amount: float):
        client_order_id = uuid.uuid4().__str__()
        self.send_command(Message(
            event="command",
            event_id=client_order_id,
            exchange=self.exchange_name,
            node="core",
            instance="py_test_core",
            action="create_orders",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=[OrderToCreate(
                client_order_id=client_order_id,
                symbol=symbol,
                type=order_type,
                side=side,
                price=price,
                amount=amount
            )]
        ))

    def get_balances(self, assets: list[str] = []):
        self.send_command(Message(
            event="command",
            event_id=uuid.uuid4().__str__(),
            exchange=self.exchange_name,
            node="core",
            instance="py_test_core",
            action="get_balance",
            message=None,
            algo=self.algo,
            timestamp=current_milli_time(),
            data=assets
        ))

    async def listen_gate_loop(self):
        subscribers = {i: Subscriber(self.handler, 'aeron:ipc', i) for i in range(1001, 1010)}
        subscribers[1004] = Subscriber(empty_handler, 'aeron:ipc', 1004)
        subscribers[1008] = Subscriber(empty_handler, 'aeron:ipc', 1008)

        while self.running:
            for subscriber in subscribers.values():
                subscriber.poll()
            await asyncio.sleep(0.0001)

    async def logging_loop(self, sleep_delay: float = 1):
        while self.running:
            print(f'=================================\n'
                  f'order books: {len(self.last_orderbook)}\n'
                  f'balances: {len(self.balances)}\n'
                  f'orders: {len(self.orders)}\n'
                  f'order books symbols: {", ".join(self.last_orderbook.keys())}\n'
                  f'=================================')
            await asyncio.sleep(sleep_delay)

    async def _base_strategy_iteration(self):
        logger.info('Sending command: cancel_all_orders.')
        self.cancel_all_orders()
        logger.info('Sending command: get_balances(["BTC", "USDT"]).')
        # self.get_balances(['BTC', 'USDT', 'ETH'])
        self.get_balances()

        while self.last_orderbook == {} or self.balances == {}:
            logger.info('Wait for orderbooks and balances...')
            await asyncio.sleep(5)

        logger.info('Successfully received and saved orderbook and balances.')
        logger.info(f'Balances: {self.balances}')
        logger.info(f'Last orderbook: {self.last_orderbook}')

        order: dict = {}
        if 11 < self.balances['USDT']['free'] > self.balances['ETH']['free'] * self.last_orderbook['asks'][0][0]:
            order = {
                'symbol': 'ETH/USDT',
                'order_type': 'limit',
                'side': 'buy',
                'price': round(self.last_orderbook['bids'][len(self.last_orderbook['bids']) - 1][0] * 0.95, 5),
                'amount': round(11 / self.last_orderbook['bids'][len(self.last_orderbook['bids']) - 1][0], 5)
            }
        elif self.balances['ETH']['free'] * self.last_orderbook['asks'][0][0] > 11:
            order = {
                'symbol': 'ETH/USDT',
                'order_type': 'limit',
                'side': 'sell',
                'price': round(self.last_orderbook['asks'][len(self.last_orderbook['asks']) - 1][0] * 1.05, 5),
                'amount': round(11 / self.last_orderbook['asks'][len(self.last_orderbook['asks']) - 1][0], 5)
            }

        if order:
            self.create_order(**order)
        else:
            logger.error('Insufficient funds on BTC and USDT.')

        self.cancel_all_orders()

    async def _long_test_strategy(self):
        logger.info('Start Long testing.')
        self.command_publisher = Publisher('aeron:ipc', stream_id=1004)
        logger.info('Created command publisher.')

        while self.running:
            await self._base_strategy_iteration()
            await asyncio.sleep(180)

    async def _fast_test_strategy(self):
        logger.info('Start Fast testing.')
        self.command_publisher = Publisher('aeron:ipc', stream_id=1004)
        logger.info('Created command publisher.')

        await self._base_strategy_iteration()
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
        await asyncio.sleep(1)
        await asyncio.gather(self.listen_gate_loop(), self._long_test_strategy())
