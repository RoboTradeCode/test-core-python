from testing_core.config import Configuration, CoreAeronChannels, AeronChannel

aeron_channels = CoreAeronChannels(
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

config_1 = Configuration(
    exchange_id='binance_test',
    instance='test',
    algo='test_algo',
    symbols=['BTC/USDT', 'ETH/BTC', 'ETH/USDT'],
    assets=['BTC', 'ETH', 'USDT'],
    aeron_channels=aeron_channels,
    no_subscriber_log_delay=10
)