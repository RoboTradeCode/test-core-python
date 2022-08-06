from testing_core import enums
from testing_core.enums import OrderType, OrderSide
from testing_core.models.message import Message
from testing_core.order.order import OrderUpdatable
from testing_core.order.order_fabric import OrderFabric
from testing_core.trader.trader import Trader
from testing_core.utils import get_uuid


class UnsafeOrder(OrderUpdatable):
    core_order_id: str = None
    symbol: str = None
    type: str = None
    side: str = None
    price: float = None
    amount: float = None


class UnsafeOrderFabric(OrderFabric):
    def create_order(self,
                     core_order_id: str = None,
                     symbol: str = None,
                     order_type: OrderType | str = None,
                     side: OrderSide | str = None,
                     price: float = None,
                     amount: float = None,
                     enable_validating: bool = True
                     ) -> OrderUpdatable:
        """
        Создать ордер.

        :param core_order_id: произвольная строка для идентификации ордеров между частями торговой системы;
        :param symbol: символ валютной пары;
        :param order_type: тип ордера, например limit или market;
        :param side: сторона ордера, buy или sell;
        :param price: цена ордера, обязательно для всех типов ордеров (для market тоже);
        :param amount: объем ордера;
        :param enable_validating: bool - по умолчанию True. Если True, проверять ордер на лимиты;
        :return: созданный ордер
        """
        order = UnsafeOrder(
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
        return order


class UnsafeTrader(Trader):
    def create_unplaced_order(
            self,
            symbol: str = None,
            order_type: OrderType | str = None,
            side: OrderSide | str = None,
            price: float = None,
            amount: float = None,
            id_prefix: str = '',
            id_postfix: str = '',
            enable_validating: bool = True,
            generate_order_id: bool = True,
    ):
        # Создаю core order id
        core_order_id = get_uuid(prefix=id_prefix, postfix=id_postfix)

        # Тип и сторону ордера можно передавать в функцию в виде строки
        # Для внутреннего использования преобразую строку в enum
        if isinstance(order_type, str):
            order_type = enums.OrderType(order_type)
        if isinstance(side, str):
            side = enums.OrderSide(side)

        # создаю ордер
        order = self._order_fabric.create_order(
            core_order_id=core_order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            price=price,
            amount=amount,
            enable_validating=enable_validating
        )

        # добавляю ордер в хранилище ордеров
        self._orders_state.add_order(order)

        return order

