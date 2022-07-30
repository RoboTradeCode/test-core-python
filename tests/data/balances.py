from testing_core import enums
from testing_core.models.balance import Balance
from testing_core.models.message import Message

balances_1 = {
    'assets': {
        'BTC': Balance(
            free=321.00,
            used=234.00,
            total=555.00
        ),
        'ETH': Balance(
            free=167.00,
            used=290.00,
            total=457.00
        ),
        'USDT': Balance(
            free=123.00,
            used=456.00,
            total=579.00
        ),
        'EVER': Balance(
            free=0,
            used=0,
            total=0
        )
    },
    'timestamp': 1658584052032997,
}

balances_2 = {
    'assets': {
        'BTC': Balance(
            free=285.81935,
            used=814.22578,
            total=1100.04513
        ),
        'ETH': Balance(
            free=620.62,
            used=813.02,
            total=1433.64
        ),
        'USDT': Balance(
            free=394.11,
            used=269.71,
            total=663.82
        )
    },
    'timestamp': 1658584706807972,
}

balances_3_total = {
    'assets': {
        'BTC': Balance(
            free=285.81935,
            used=814.22578,
            total=1100.04513
        ),
        'ETH': Balance(
            free=620.62,
            used=813.02,
            total=1433.64
        ),
        'USDT': Balance(
            free=394.11,
            used=269.71,
            total=663.82
        ),
        'EVER': Balance(
            free=0,
            used=0,
            total=0
        )
    },
    'timestamp': 1658584706807972,
}
balances_missing_usdt_1 = {
    'assets': {
        'BTC': Balance(
            free=285.81935,
            used=814.22578,
            total=1100.04513
        ),
        'ETH': Balance(
            free=620.62,
            used=813.02,
            total=1433.64
        )
    },
    'timestamp': 1658584706807972,
}

balances_1_message = Message(
    event_id='5f4b7bb5-2bb0-495c-9a98-9a0b3b5cf413',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.BALANCE_UPDATE,
    message=None,
    timestamp=1659033627752151,
    data=balances_1
)

balances_2_message = Message(
    event_id='679b726b-1283-4274-8c6f-80c7bc29a422',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.BALANCE_UPDATE,
    message=None,
    timestamp=1659033648149830,
    data=balances_2
)

balances_missing_1_message = Message(
    event_id='679b726b-1283-4274-8c6f-80c7bc29a422',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.BALANCE_UPDATE,
    message=None,
    timestamp=1659033648149830,
    data=balances_missing_usdt_1
)