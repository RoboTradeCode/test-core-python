from testing_core.models.balance import Balance

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
