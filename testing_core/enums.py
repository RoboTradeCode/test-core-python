from enum import Enum


class OrderStatus(Enum):
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
    ORDER_BOOK_UPDATE = 'order_book_update'
    CREATE_ORDERS = 'create_orders'
    CANCEL_ORDERS = 'cancel_orders'
    CANCEL_ALL_ORDERS = 'cancel_all_orders'
    GET_ORDERS = 'get_orders'
    ORDERS_UPDATE = 'orders_update'
    GET_BALANCE = 'get_balance'
    PING = 'ping'
    BALANCES_UPDATE = 'balances_update'
