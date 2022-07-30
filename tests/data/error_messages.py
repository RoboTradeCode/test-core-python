from testing_core import enums
from testing_core.models.message import Message, GateOrderToCreate

error_message_1 = Message(
    event_id='7a7f3012-eaa9-11ec-8fea-0242ac120002',
    event=enums.Event.ERROR,
    exchange='binance',
    instance='test',
    node=enums.Node.CORE,
    algo='test',
    action=enums.Action.GET_BALANCE,
    message='An error',
    timestamp=1658584706807972,
    data=None
)

error_from_gate_1 = Message(
    event_id='90bb29fa-df8c-478a-b716-a170cda7c5ee',
    event=enums.Event.ERROR,
    exchange='binance',
    instance='test',
    node=enums.Node.GATE,
    algo='test',
    action=enums.Action.CREATE_ORDERS,
    message='Insufficient balance',
    timestamp=1658584706807972,
    data=GateOrderToCreate(
        client_order_id='test_prefix|b5fd78ba-a042-4e6e-8b73-8431ebcebba3|test_postfix',
        symbol='BTC/USDT',
        type=enums.OrderType.LIMIT,
        side=enums.OrderSide.BUY,
        amount=2_000_000,
        price=1000.132
    )
)
