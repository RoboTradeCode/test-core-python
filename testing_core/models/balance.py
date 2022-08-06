from pydantic import BaseModel, NonNegativeFloat


class Balance(BaseModel):
    """
    Структура баланса одного ассета.
    """

    class Config:
        extra = 'forbid'

    free: NonNegativeFloat
    used: NonNegativeFloat
    total: NonNegativeFloat
