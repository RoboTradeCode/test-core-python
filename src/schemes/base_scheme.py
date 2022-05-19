from dataclasses import dataclass


@dataclass
class BaseScheme:
    event: str
    exchange: str
    node: str
    instance: str
    action: str
    message: str | None
    algo: str
    timestamp: int
    data = None
