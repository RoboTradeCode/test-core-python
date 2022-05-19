from dataclasses import dataclass

from src.schemes.base_scheme import BaseScheme


@dataclass
class CreateOrderCommand(BaseScheme):
    @dataclass
    class Order:
        symbol: str
        type: str
        side: str
        price: float
        amount: float

    data: list[Order]


@dataclass
class CancelOrderCommand(BaseScheme):
    @dataclass
    class Order:
        id: str
        symbol: str

    data: list[Order]


@dataclass
class CancelAllOrdersCommand(BaseScheme):
    data: None


@dataclass
class OrderStatusCommand(BaseScheme):
    @dataclass
    class Order:
        id: str
        symbol: str

    data: Order


@dataclass
class GetBalanceCommand(BaseScheme):
    @dataclass
    class Asset:
        assets: list[str]

    data: Asset | None
