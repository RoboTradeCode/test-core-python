from testing_core.config import Configuration, CoreAeronChannels, AeronChannel, Market

aeron_channels_1 = CoreAeronChannels(
    gate_input=AeronChannel(
        channel='aeron:ipc',
        stream_id=4200
    ),
    core_input=AeronChannel(
        channel='aeron:ipc',
        stream_id=4201
    ),
    orderbooks=AeronChannel(
        channel='aeron:ipc',
        stream_id=4202
    ),
    balances=AeronChannel(
        channel='aeron:ipc',
        stream_id=4203
    ),
    logs=AeronChannel(
        channel='aeron:ipc',
        stream_id=4204
    ),
)
aeron_channels_2 = CoreAeronChannels(
    gate_input=AeronChannel(
        channel='aeron:ipc',
        stream_id=4300
    ),
    core_input=AeronChannel(
        channel='aeron:ipc',
        stream_id=4301
    ),
    orderbooks=AeronChannel(
        channel='aeron:ipc',
        stream_id=4302
    ),
    balances=AeronChannel(
        channel='aeron:ipc',
        stream_id=4303
    ),
    logs=AeronChannel(
        channel='aeron:ipc',
        stream_id=4304
    ),
)

markets_1 = {
    'ETH/USDT': Market(
        exchange_symbol='ETH-USDT',
        common_symbol='ETH/USDT',
        price_increment=0.01,
        amount_increment=1e-07,
        limits=Market.Limits(
            amount=Market.Limits.MinMax(
                min=0.0001,
                max=10000000000.0
            ),
            price=Market.Limits.MinMax(
                min=None,
                max=None
            ),
            cost=Market.Limits.MinMax(
                min=0.01,
                max=999999999.0
            ),
            leverage=Market.Limits.MinMax(
                min=None,
                max=None
            )
        ),
        base_asset='ETH',
        quote_asset='USDT'
    ),
    'BTC/USDT': Market(
        exchange_symbol='BTC-USDT',
        common_symbol='BTC/USDT',
        price_increment=0.001,
        amount_increment=1e-08,
        limits=Market.Limits(
            amount=Market.Limits.MinMax(
                min=1e-05,
                max=10000000000.0
            ),
            price=Market.Limits.MinMax(
                min=None,
                max=None
            ),
            cost=Market.Limits.MinMax(
                min=0.01,
                max=99999999.0
            ),
            leverage=Market.Limits.MinMax(
                min=None,
                max=None
            )
        ),
        base_asset='BTC',
        quote_asset='USDT'
    ),
    'ETH/BTC': Market(
        exchange_symbol='ETH-BTC',
        common_symbol='ETH/BTC',
        price_increment=1e-06,
        amount_increment=1e-07,
        limits=Market.Limits(
            amount=Market.Limits.MinMax(
                min=0.0001,
                max=10000000000.0
            ),
            price=Market.Limits.MinMax(
                min=None,
                max=None
            ),
            cost=Market.Limits.MinMax(
                min=1e-05,
                max=999999999.0
            ),
            leverage=Market.Limits.MinMax(
                min=None,
                max=None
            )
        ),
        base_asset='ETH',
        quote_asset='BTC'
    )
}

config_1 = Configuration(
    exchange_id='binance',
    instance='test',
    algo='test_algo',
    symbols=['BTC/USDT', 'ETH/BTC', 'ETH/USDT'],
    assets=['BTC', 'ETH', 'USDT'],
    aeron_channels=aeron_channels_1,
    no_subscriber_log_delay=10,
    orderbook_depth=10,
    markets=markets_1
)

config_2 = Configuration(
    exchange_id='binance',
    instance='test',
    algo='test_algo',
    symbols=['BTC/USDT', 'ETH/BTC', 'ETH/USDT'],
    assets=['BTC', 'ETH', 'USDT'],
    aeron_channels=aeron_channels_2,
    no_subscriber_log_delay=10,
    orderbook_depth=10,
    markets=markets_1
)
