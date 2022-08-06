invalid_order_message_1 = '''{
    "event_id":"9978009a-eb10-11ec-8fea-0242ac120002",
    "event":"data",
    "exchange":"binance",
    "node":"gate",
    "instance":"1",
    "algo":"cross_3t_php",
    "action":"create_order",
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
invalid_order_message_2 = '''{
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
invalid_order_message_3 = '''{
    "event_id":"9978009a-eb10-11ec-8fea-0242ac120002",
    "event":"data",
    "exchange":"binance",
    "node":"gate",
    "instance":"1",
    "algo":"cross_3t_php",
    "action":"create_orders",
    "message":null,
    "timestamp":1502962946216000,
    "data":
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
    
}'''
invalid_order_message_4 = '''{
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
            "status":"closed",
            "symbol":"ETH/BTC",
            "type":"limit",
            "side":"buy",
            "price":0.06917684,
            "amount":1.5,
            "filled":0.0,
            "info":null
        }
    ]
}'''
invalid_order_message_5 = '''{
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
            "info":None
        }
    ]
}'''
invalid_balance_message_1 = '''
{
    "event_id": "7a7f3012-eaa9-11ec-8fea-0242ac120002",
    "event": "data",
    "exchange": "binance",
    "node": "gate",
    "instance": "1",
    "action": "get_balance",
    "message": null,
    "timestamp": 1502962946216000,
    "data": {
        "assets": {
            "BTC": {
                "free": 321.12,
                "used": 234.32,
                "total": 555.44
            },
            "ETH": {
                "free": 167.643,
                "used": 290.312,
                "total": 457.955
            },
            "USDT": {
                "free": 123.53,
                "used": 456.2153,
                "total": 579.7453
            }
        },
        "timestamp": 1499280391811
    }
}
'''
invalid_orderbook_message_1 = '''
{
    "event_id":"01a14e44-f13b-11ec-8ea0-0242ac120002",
    "event":"data",
    "exchange":"binance",
    "node":"gate",
    "instance":"1",
    "algo":"cross_3t_php",
    "action":"order_book_update",
    "message":null,
    "timestamp":1652962946216000,
    "data":{
        "bids":[
            [
                8724.77,
                0.149594
            ],
            [
                8724.11,
                2.537818
            ],
            [
                8724.08,
                0.030605
            ]
        ],
        "symbol":"ETH/BTC",
        "timestamp":1499280391811000
    }
}
'''
invalid_orderbook_message_2 = '''
{
    "event_id":"01a14e44-f13b-11ec-8ea0-0242ac120002",
    "event":"data",
    "exchange":"binance",
    "node":"gate",
    "instance":"1",
    "algo":"cross_3t_php",
    "action":"order_book_update",
    "message":null,
    "timestamp":1652962946216000,
    "data":{
        "bids":[
            [
                8724.77,
                0.149594
            ],
            [
                8724.11,
                2.537818
            ],
            [
                8724.08,
                0.030605
            ]
        ],
        "asks":[
            [
                8725.61,
                0.055265
            ],
            [
                8725.7,
                0.028131
            ],
            [
                8725.81,
                0.116984
            ]
        ],
        "timestamp":1499280391811000
    }
}
'''
invalid_orderbook_message_depth_1 = '''
{
    "event_id":"01a14e44-f13b-11ec-8ea0-0242ac120002",
    "event":"data",
    "exchange":"binance",
    "node":"gate",
    "instance":"1",
    "algo":"cross_3t_php",
    "action":"order_book_update",
    "message":null,
    "timestamp":1652962946216000,
    "data":{
        "bids":[
            [
                8724.77,
                0.149594
            ],
            [
                8724.11,
                2.537818
            ]
        ],
        "asks":[
            [
                8725.61,
                0.055265
            ],
            [
                8725.7,
                0.028131
            ]
        ],
        "timestamp":1499280391811000
    }
}
'''