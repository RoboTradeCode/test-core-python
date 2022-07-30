from typing import Any

from pydantic import BaseModel


class Orderbook(BaseModel):
    """
    Структура с информацией об ордербуке
    """
    symbol: str
    timestamp: int = None
    bids: list[list[float]]
    asks: list[list[float]]
