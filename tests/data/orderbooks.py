from testing_core import enums
from testing_core.models.message import Message
from testing_core.models.orderbook import Orderbook

orderbook_1 = Orderbook(
    symbol='BTC/USDT',
    timestamp=1658583969732365,
    bids=[
            [8724.77, 0.149594],
            [8724.11, 2.537818],
            [8724.08, 0.030605]
        ],
    asks=[
            [8725.61, 0.055265],
            [8725.7, 0.028131],
            [8725.81, 0.116984]
        ]
)
orderbook_2 = Orderbook(
    symbol='BTC/USDT',
    timestamp=1658584052033997,
    bids=[
            [8724.77, 0.149594],
            [8724.11, 3.537818],
            [8724.08, 0.030605]
        ],
    asks=[
            [8725.61, 0.055265],
            [8725.7, 1.028131],
            [8725.81, 0.016984]
        ]
)
orderbook_3 = Orderbook(
    symbol='ETH/USDT',
    timestamp=1658584052032997,
    bids=[
            [1023.77, 12.2432],
            [1023.11, 124.323],
            [1023.08, 657.2342]
        ],
    asks=[
            [1024.61, 123.432],
            [1024.7, 645.454],
            [1024.81, 345.34]
        ]
)
orderbook_4 = Orderbook(
    symbol='XRP/USDT',
    timestamp=1658584052032997,
    bids=[
            [103.77, 12.2432],
            [103.11, 124.323],
            [103.08, 657.2342]
        ],
    asks=[
            [104.61, 123.432],
            [104.7, 645.454],
            [104.81, 345.34]
        ]
)

orderbook_1_message = Message(
    event_id='59819994-2e04-4e26-a025-ef7238709ff5',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.ORDERBOOK_UPDATE,
    message=None,
    timestamp=1658583969732365,
    data=orderbook_1
)

orderbook_2_message = Message(
    event_id='9c0a032e-08eb-4494-a20a-d2cf7c2dbf24',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.ORDERBOOK_UPDATE,
    message=None,
    timestamp=1658584052033997,
    data=orderbook_2
)

orderbook_3_message = Message(
    event_id='9ebc7f3e-e272-4549-958a-d98d8a57f49c',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.ORDERBOOK_UPDATE,
    message=None,
    timestamp=1658584052032997,
    data=orderbook_3
)
orderbook_4_message = Message(
    event_id='9ebc7f3e-e272-4549-958a-d98d8a57f49c',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.ORDERBOOK_UPDATE,
    message=None,
    timestamp=1658584052032997,
    data=orderbook_4
)