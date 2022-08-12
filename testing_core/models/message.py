from typing import Union, Optional, Any

from pydantic import BaseModel, PositiveFloat, NonNegativeFloat

from testing_core import enums
from testing_core.models.balance import Balance
from testing_core.models.orderbook import Orderbook


class GateOrderId(BaseModel):
    """Информация для идентификации ордера, которую присылает ядро"""

    class Config:
        extra = 'forbid'

    client_order_id: str
    symbol: str
    id: Optional[str]


class OrderId(BaseModel):
    """Информация для идентификации ордера, которую присылает ядро"""

    class Config:
        extra = 'forbid'

    core_order_id: str
    symbol: str
    id: Optional[str]


class GateOrderToCreate(BaseModel):
    """Структура с информацией для создания ордера. Присылает ядро"""

    class Config:
        extra = 'forbid'

    client_order_id: str
    symbol: str
    type: enums.OrderType
    side: enums.OrderSide
    amount: float
    price: float


class GateOrderInfo(BaseModel):
    """Структура с информацией об ордере, которую отправляет гейт"""

    class Config:
        extra = 'forbid'

    id: str
    client_order_id: str
    symbol: str
    type: enums.OrderType
    side: enums.OrderSide
    amount: NonNegativeFloat
    price: NonNegativeFloat | None
    timestamp: int
    status: enums.GateOrderStatus | None
    filled: NonNegativeFloat | None
    # info is not formatted message of order from exchange
    info: Any | None


class Balances(BaseModel):
    timestamp: int | None
    assets: dict[str, Balance]


class Message(BaseModel):
    """Главная структура сообщения, которая используется для обмена информацией между частями торговой системы"""

    class Config:
        extra = 'forbid'

    event_id: str
    exchange: str
    instance: str
    event: enums.Event
    node: enums.Node
    action: enums.Action | None
    message: str | None
    algo: str
    timestamp: int
    data: Union[
        list[GateOrderToCreate], list[GateOrderInfo], list[OrderId],  list[GateOrderId], Orderbook,
        GateOrderToCreate, Balances, list[str], int, str, None
    ]
