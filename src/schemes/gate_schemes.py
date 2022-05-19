from dataclasses import dataclass

from src.schemes.base_scheme import BaseScheme


@dataclass
class SimpleMessage(BaseScheme):

    data: dict


@dataclass
class Order(BaseScheme):
    @dataclass
    class OrderInfo:
        id: str
        timestamp: int
        status: str
        symbol: str
        type: str
        side: str
        price: float
        amount: float
        filled: float

    data: OrderInfo


@dataclass
class Balance(BaseScheme):
    @dataclass
    class AssetBalance:
        free: float
        used: float
        total: float

    data: list[AssetBalance]


@dataclass
class OrderBook(BaseScheme):
    @dataclass
    class OrderBook:
        bids: list[tuple[float, float]]
        asks: list[tuple[float, float]]
        symbol: str
        timestamp: str

    data: OrderBook


@dataclass
class Error(BaseScheme):
    data: Order | None
