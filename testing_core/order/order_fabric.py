import logging
from typing import Callable

from testing_core.config import Market
from testing_core.enums import OrderType, OrderSide
from testing_core.exceptions import LimitViolation
from testing_core.order.order import OrderData, OrderUpdatable, Order
from testing_core.utils import truncate_to_increment

logger = logging.getLogger(__name__)

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
                 markets: dict[str, Market],
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
        self._markets = markets
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
            type=order_type,
            side=side,
            price=price,
            amount=amount,
            place_function=self._place_function,
            request_update_function=self._request_update_function,
            cancel_function=self._cancel_function
        )
        order = self.truncate_values_to_increment(order)
        if not self.check_order_to_limits(order):
            logger.error(f'Limit violation on order: {order}')
            raise LimitViolation
        return order

    def truncate_values_to_increment(self, order: OrderUpdatable) -> OrderUpdatable:
        """
        Округляет значения price и amount до значений, подходящих под инкремент маркета (минимальный шаг).
        :param order: Order
        :return: Order с округленными значениями price и amount
        """
        market = self._markets.get(order.symbol)
        if market is None:
            raise KeyError('Unknown symbol. Check configuration.')
        order.amount = truncate_to_increment(order.amount, market.amount_increment)
        order.price = truncate_to_increment(order.price, market.price_increment)
        return order

    def check_order_to_limits(self, order: Order) -> bool:
        """
        Проверяет ордер на соответствие лимитам маркета;
        :param order: Order который нужно проверить;
        :return: True если валидный, т.е. соответствует лимитам. False, если невалидный
        """
        market = self._markets.get(order.symbol)
        if market is None:
            raise KeyError('Unknown symbol. Check configuration.')
        limits = market.limits

        is_valid = True
        # amount
        if limits.amount.min is not None and not limits.amount.min < order.amount or \
                limits.amount.max is not None and not order.amount < limits.amount.max:
            is_valid = False
        # price
        elif limits.price.min is not None and not limits.price.min < order.price or \
                limits.price.max is not None and not order.price < limits.price.max:
            is_valid = False
        # cost
        if limits.cost.min is not None and not limits.cost.min < order.price * order.amount or \
                limits.cost.max is not None and not order.price * order.amount < limits.cost.max:
            is_valid = False

        return is_valid
