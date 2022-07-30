from enum import Enum


class GateOrderStatus(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    CANCELED = 'canceled'
    EXPIRED = 'expired'
    REJECTED = 'rejected'

    def __repr__(self):
        return self.value


class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    FOK = 'fok'
    STOP_LIMIT = 'stop_limit'

    def __repr__(self):
        return self.value


class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'

    def __repr__(self):
        return self.value


class Event(Enum):
    COMMAND = 'command'
    DATA = 'data'
    ERROR = 'error'

    def __repr__(self):
        return self.value


class Node(Enum):
    CORE = 'core'
    GATE = 'gate'

    def __repr__(self):
        return self.value


class Action(Enum):
    ORDERBOOK_UPDATE = 'order_book_update'
    CREATE_ORDERS = 'create_orders'
    CANCEL_ORDERS = 'cancel_orders'
    CANCEL_ALL_ORDERS = 'cancel_all_orders'
    GET_ORDERS = 'get_orders'
    ORDERS_UPDATE = 'orders_update'
    GET_BALANCE = 'get_balance'
    PING = 'ping'
    BALANCE_UPDATE = 'balance_update'

    def __repr__(self):
        return self.value


class OrderState(Enum):
    UNPLACED = 'unplaced'
    PLACING = 'placing'
    OPEN = 'open'
    FILLED = 'filled'
    CLOSED = 'closed'
    CANCELED = 'canceled'
    ERROR = 'error'

    def __repr__(self):
        return self.value
