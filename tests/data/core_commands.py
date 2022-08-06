from testing_core import enums
from testing_core.models.message import Message

command_get_balance_1 = Message(
    event_id='7a7f3012-eaa9-11ec-8fea-0242ac120002',
    event=enums.Event.COMMAND,
    exchange='binance',
    instance='test',
    node=enums.Node.CORE,
    algo='test',
    action=enums.Action.GET_BALANCE,
    message=None,
    timestamp=1658584706807972,
    data=[
        'BTC',
        'ETH',
        'USDT'
    ]
)
command_cancel_all_orders_1 = Message(
    event_id='7a7f3012-eaa9-11ec-8fea-0242ac120002',
    event=enums.Event.COMMAND,
    exchange='binance',
    instance='test',
    node=enums.Node.CORE,
    algo='test',
    action=enums.Action.CANCEL_ALL_ORDERS,
    message=None,
    timestamp=1658584706807972,
    data=None
)