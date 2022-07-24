import dataclasses
from typing import Callable, Any

from pydantic import BaseModel

from testing_core import enums
from testing_core.enums import OrderType, OrderSide, OrderState
from testing_core.utils import get_micro_timestamp


@dataclasses.dataclass
class OrderData(object):
    core_order_id: str
    symbol: str
    type: OrderType
    side: OrderSide
    price: float
    amount: float
    state: OrderState = OrderState.UNPLACED
    filled: float = 0


class Order(OrderData):
    """
    Класс ордера. Содержит всю необходимую информацию об ордере. С помощью методов можно отправить ордер на биржу,
    отменить ордер, запросить обновление статуса ордера (синхронизация с биржей).
    """
    is_placed: bool = False
    is_open: bool = False
    place_timestamp: int = None
    last_update_timestamp: int = None
    _place_function: Callable[[OrderData], None] = None
    _request_update_function: Callable[[OrderData], None] = None
    _cancel_function: Callable[[OrderData], None] = None

    def __init__(self,
                 place_function: Callable[[OrderData], None],
                 request_update_function: Callable[[OrderData], None],
                 cancel_function: Callable[[OrderData], None],
                 **order_data: Any):
        """
        Класс ордера. Содержит всю необходимую информацию об ордере. С помощью методов можно отправить ордер на биржу,
        отменить ордер, запросить обновление статуса ордера (синхронизация с биржей).

        :param place_function: функция для размещения ордера на бирже;
        :param request_update_function: функция для синхронизации данных с ордером на бирже;
        :param cancel_function: функция для отмены ордера на бирже;
        :param order_data: Данные, относящиеся к классу OrderData.
        """
        super().__init__(**order_data)
        self._place_function = place_function
        self._request_update_function = request_update_function
        self._cancel_function = cancel_function

    def place(self) -> bool:
        """
        Разместить ордер на бирже (создать ордер на бирже). Гейту будет отправлена команда, гейт должен создать этот
        ордер на бирже. Если это market ордер, он будет завершен сразу (closed). Если это limit ордер,
        то он перейдет в состояние open.
        Функцию можно выполнить, если ордер находится в состояниях unplaced, error. Ордер перейдет в состояние posting,
        откуда может перейти в состояния open, closed, error.
        """
        # Проверка, находится ли ордер в состоянии, из которого может быть создан на бирже
        if self.state not in [enums.OrderState.UNPLACED, enums.OrderState.ERROR]:
            return False

        # Отправка ордера гейту
        self._place_function(self)

        # Изменение состояния ордера на placing
        self.state = enums.OrderState.PLACING

        return True

    def cancel(self):
        """
        Отменить ордер на бирже. Гейту будет отправлена команда на отмену этого ордера. Возможно только для
        ордера с типом limit.
        Функцию можно выполнить, если ордер находится в состояниях open, filled. Когда ядро получит результат
        операции, ордер перейдет в состояние cancelled или error.
        """
        # Проверка, находится ли ордер в состоянии, из которого может быть отменен на бирже
        if self.state not in [enums.OrderState.OPEN, enums.OrderState.FILLED]:
            return False

        # Отправка команды гейту
        self._cancel_function(self)

        return True

    def request_update(self):
        """
        Запросить обновление данные ордера (синхронизацию с биржей). Обновление придет не мгновенно.
        """
        # Проверка, находится ли ордер в состоянии, из которого может быть отменен на бирже
        if self.state in [enums.OrderState.UNPLACED, enums.OrderState.ERROR]:
            return False

        # отправка команды гейту
        self._request_update_function(self)


class OrderUpdatable(Order):
    def update(self, order_data: OrderData):
        """
        Обновить ордер новыми данными

        :param order_data: новые данные по ордеру;
        """
        self.state = order_data.state
        self.filled = order_data.filled
        self.amount = order_data.amount
        self.price = order_data.price

        self.last_update_timestamp = get_micro_timestamp()
