from testing_core import enums
from testing_core.models.message import Message, GateOrderInfo
from testing_core.order.order import OrderUpdatable, OrderData


def empty_func(_: OrderData):
    return None


order_1 = OrderUpdatable(
    core_order_id='test_prefix|ae4d1f7a-97e5-4a05-88eb-98fe9e2f321c|test_postfix',
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    price=1000.132,
    amount=20.1,
    place_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_2 = OrderUpdatable(
    core_order_id='test_prefix|56202bc7-0584-4a85-9118-391af8c34a49|test_postfix',
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    place_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_3 = OrderUpdatable(
    core_order_id='test_prefix|ac6e0011-bc13-4590-8a96-c458a3c63754|test_postfix',
    symbol='ETC/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1000,
    amount=0.1,
    place_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_4 = OrderUpdatable(
    core_order_id='test_prefix|b5fd78ba-a042-4e6e-8b73-8431ebcebba3|test_postfix',
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    amount=2_000_000,
    price=1000.132,
    place_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_1_update = OrderData(
    core_order_id='test_prefix|ae4d1f7a-97e5-4a05-88eb-98fe9e2f321c|test_postfix',
    state=enums.OrderState.CANCELED,
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    price=10000,
    amount=100,
    filled=0.1
)
order_2_update = OrderData(
    core_order_id='test_prefix|56202bc7-0584-4a85-9118-391af8c34a49|test_postfix',
    state=enums.OrderState.CLOSED,
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    filled=0.1,
)
order_2_update_gate_order_info = GateOrderInfo(
    id='123443211234',
    client_order_id='test_prefix|56202bc7-0584-4a85-9118-391af8c34a49|test_postfix',
    status=enums.GateOrderStatus.CLOSED,
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    filled=0.1,
    timestamp=1659041333365984,
    info=None
)
order_2_update_message = Message(
    event_id='ca54b757-b739-46b6-89f3-27b07f0477cd',
    event=enums.Event.DATA,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.ORDERS_UPDATE,
    message=None,
    timestamp=1659041333365984,
    data=[order_2_update_gate_order_info]
)
order_1_updated = OrderUpdatable(
    core_order_id='test_prefix|ae4d1f7a-97e5-4a05-88eb-98fe9e2f321c|test_postfix',
    state=enums.OrderState.CANCELED,
    symbol='BTC/USDT',
    type=enums.OrderType.LIMIT,
    side=enums.OrderSide.BUY,
    price=10000,
    amount=100,
    filled=0.1,
    place_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)
order_2_updated = OrderUpdatable(
    core_order_id='test_prefix|56202bc7-0584-4a85-9118-391af8c34a49|test_postfix',
    state=enums.OrderState.CLOSED,
    symbol='ETH/BTC',
    type=enums.OrderType.MARKET,
    side=enums.OrderSide.SELL,
    price=1_000_00,
    amount=0.1,
    filled=0.1,
    place_function=empty_func,
    request_update_function=empty_func,
    cancel_function=empty_func
)

order_message_str_1 = '''{
    "event_id":"9978009a-eb10-11ec-8fea-0242ac120002",
    "event":"data",
    "exchange":"binance",
    "node":"gate",
    "instance":"1",
    "algo":"cross_3t_php",
    "action":"create_orders",
    "message":null,
    "timestamp":1502962946216000,
    "data":[
        {
            "id":"12345-67890:09876/54321",
            "client_order_id":"7b0b6fda-e9ed-11ec-8fea-0242ac120002",
            "timestamp":1502962946216000,
            "status":"open",
            "symbol":"ETH/BTC",
            "type":"limit",
            "side":"buy",
            "price":0.06917684,
            "amount":1.5,
            "filled":1.1,
            "info":null
        }
    ]
}'''