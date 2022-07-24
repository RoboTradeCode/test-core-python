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