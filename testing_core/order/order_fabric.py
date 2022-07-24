from typing import Callable

from testing_core.enums import OrderType, OrderSide
from testing_core.order.order import OrderData, OrderUpdatable


class OrderFabric(object):
    """
    Отвечает за создание объектов ордеров. Не размещает ордера на бирже.
    Содержит функции для создания, отмены, запроса обновления ордеров, которые передает
     создаваемым ордерам.
    """
    _place_function: Callable[[OrderData], None]
    _request_update_function: Callable[[OrderData], None]
    _cancel_function: Callable[[OrderData], None]

    def __init__(self,
                 place_function: Callable[[OrderData], None],
                 request_update_function: Callable[[OrderData], None],
                 cancel_function: Callable[[OrderData], None]
                 ):
        """
        Создать фабрику ордеров.

        :param place_function: функция для размещения ордера на бирже (передается создаваемым ордерам)
        :param request_update_function: функция для запроса обновления ордера (передается создаваемым ордерам)
        :param cancel_function: функция для отмены ордера на бирже (передается создаваемым ордерам)
        """
        self._place_function = place_function
        self._request_update_function = request_update_function
        self._cancel_function = cancel_function

    def create_order(self,
                     core_order_id: str,
                     symbol: str,
                     order_type: OrderType,
                     side: OrderSide,
                     price: float,
                     amount: float
                     ) -> OrderUpdatable:
        """
        Создать ордер.

        :param core_order_id: произвольная строка для идентификации ордеров между частями торговой системы;
        :param symbol: символ валютной пары;
        :param order_type: тип ордера, например limit или market;
        :param side: сторона ордера, buy или sell;
        :param price: цена ордера, обязательно для всех типов ордеров (для market тоже);
        :param amount: объем ордера;
        :return: созданный ордер
        """
        order = OrderUpdatable(
            core_order_id=core_order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            price=price,
            amount=amount,
            place_function=self._place_function,
            request_update_function=self._request_update_function,
            cancel_function=self._cancel_function
        )
        return order
