from typing import Union

from pydantic import BaseModel, PositiveFloat, NonNegativeFloat, Field
from dragon_gate import enums


class Balance(BaseModel):
    """The balance structure that gate returns"""

    class Config:
        extra = 'forbid'

    free: NonNegativeFloat
    used: NonNegativeFloat
    total: NonNegativeFloat


class OrderId(BaseModel):
    """Order client id and symbol that the Core sends"""

    class Config:
        extra = 'forbid'

    client_order_id: str
    symbol: str
    # order_id field will only be set at Gate
    id: str = None


class OrderToCreate(BaseModel):
    """The basic order structure. It sends the Core for creating order"""

    class Config:
        extra = 'forbid'

    client_order_id: str
    symbol: str
    type: enums.OrderType
    side: enums.OrderSide
    amount: PositiveFloat
    price: PositiveFloat


class OrderInfo(BaseModel):
    """Order info structure that Gate returns"""

    class Config:
        extra = 'forbid'

    id: str
    client_order_id: str
    symbol: str
    order_type: enums.OrderType = Field(enums.OrderType, alias='type')
    side: enums.OrderSide
    amount: PositiveFloat
    price: PositiveFloat
    timestamp: int
    status: enums.OrderStatus
    filled: NonNegativeFloat
    # info is not formatted message of order from exchange
    info: dict


class OrderBook(BaseModel):
    """Order book message"""
    symbol: str
    timestamp: int = None
    bids: list[list[float]]
    asks: list[list[float]]


class Message(BaseModel):
    """Base message scheme"""

    class Config:
        extra = 'forbid'

    event_id: str
    exchange: str
    instance: str
    event: enums.Event
    node: enums.Node
    action: enums.Action
    message: str | None
    algo: str
    timestamp: int
    data: Union[
        list[OrderInfo], list[OrderToCreate], list[OrderId], OrderBook,
        dict[str, dict[str, Balance] | int | None], list[str], int, None
    ]
