from testing_core import enums
from testing_core.order.order import OrderUpdatable, OrderData
from tests.test_state_orders import empty_func

order_1 = OrderUpdatable(
    core_order_id='test_order_1',
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    price=10000,
    amount=100,
    placing_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_2 = OrderUpdatable(
    core_order_id='test_order_2',
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    placing_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_3 = OrderUpdatable(
    core_order_id='test_order_3',
    symbol='ETC/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1000,
    amount=0.1,
    placing_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_1_update = OrderData(
    core_order_id='test_order_1',
    state=enums.OrderState.CANCELED,
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    price=10000,
    amount=100,
    filled=0.1
)
order_2_update = OrderData(
    core_order_id='test_order_2',
    state=enums.OrderState.CLOSED,
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    filled=0.1
)
order_1_updated = OrderUpdatable(
    core_order_id='test_order_1',
    state=enums.OrderState.CANCELED,
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    price=10000,
    amount=100,
    filled=0.1,
    placing_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_2_updated = OrderUpdatable(
    core_order_id='test_order_2',
    state=enums.OrderState.CLOSED,
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    filled=0.1,
    placing_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
