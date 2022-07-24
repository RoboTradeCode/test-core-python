from enum import Enum


class GateOrderStatus(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    CANCELED = 'canceled'
    EXPIRED = 'expired'
    REJECTED = 'rejected'


class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    FOK = 'fok'
    STOP_LIMIT = 'stop_limit'


class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'


class Event(Enum):
    COMMAND = 'command'
    DATA = 'data'
    ERROR = 'error'


class Node(Enum):
    CORE = 'core'
    GATE = 'gate'


class Action(Enum):
    ORDERBOOK_UPDATE = 'orderbook_update'
    CREATE_ORDERS = 'create_orders'
    CANCEL_ORDERS = 'cancel_orders'
    CANCEL_ALL_ORDERS = 'cancel_all_orders'
    GET_ORDERS = 'get_orders'
    ORDERS_UPDATE = 'orders_update'
    GET_BALANCE = 'get_balance'
    PING = 'ping'
    BALANCES_UPDATE = 'balances_update'


class OrderState(Enum):
    UNPLACED = 'unplaced'
    PLACING = 'placing'
    OPEN = 'open'
    FILLED = 'filled'
    CLOSED = 'closed'
    CANCELED = 'canceled'
    ERROR = 'error'
