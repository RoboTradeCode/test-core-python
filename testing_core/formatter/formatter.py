from typing import Any

from testing_core import enums
from testing_core.models.message import Message, GateOrderToCreate, GateOrderId, GateOrderInfo
from testing_core.order.order import OrderData
from testing_core.utils import get_uuid, get_micro_timestamp


class Formatter(object):
    """
    Класс для форматирования сообщений под формат сообщений торговой системы.
    """
    _exchange: str
    _instance: str
    _algo: str
    _node: str

    def __init__(self,
                 exchange: str,
                 instance: str,
                 algo: str,
                 node: str = 'core'
                 ):
        """
        Создать форматтер, инициализация основных полей;
        :param exchange: название биржи, на которое будет вестись торговля;
        :param instance: название инстанса торгового сервера;
        :param algo: название алгоритма торгового сервера;
        :param node: название узла торговой системы (по умолчанию 'core')
        """
        self._exchange = exchange
        self._instance = instance
        self._algo = algo
        self._node = node

    def format_command(self, action: enums.Action, data: Any, message: str = None) -> Message:
        """
        Форматировать команду под формат сообщений
        """
        command = Message(
            event_id=get_uuid(),
            exchange=self._exchange,
            instance=self._instance,
            event=enums.Event.COMMAND,
            node=self._node,
            action=action,
            message=message,
            algo=self._algo,
            timestamp=get_micro_timestamp(),
            data=data
        )
        return command

    def format_error(self,
                     message: str,
                     action: enums.Action | None,
                     event_id: str | None,
                     data: dict | str | None = None) -> Message:
        """
        Форматировать сообщение об ошибке под формат сообщений
        """
        message = Message(
            event_id=event_id if event_id is not None else get_uuid(),
            exchange=self._exchange,
            instance=self._instance,
            event=enums.Event.COMMAND,
            node=self._node,
            action=action,
            message=message,
            algo=self._algo,
            timestamp=get_micro_timestamp(),
            data=data
        )
        return message

    def format_create_orders(self, orders: list[OrderData]) -> Message:
        """
        Форматировать команду для создания ордеров;
        :param orders: список ордеров;
        :return: Message готовое сообщение, которое можно отправить гейту;
        """
        formatted_orders: list[GateOrderToCreate] = []
        for order in orders:
            formatted_orders.append(GateOrderToCreate(
                client_order_id=order.core_order_id,
                symbol=order.symbol,
                type=order.type,
                side=order.side,
                amount=order.amount,
                price=order.price
            ))
        command = self.format_command(action=enums.Action.CREATE_ORDERS, data=formatted_orders)
        return command

    @staticmethod
    def format_order_ids(orders: list[OrderData]) -> list[GateOrderId]:
        """
        Форматировать список ордеров в список идентификаторов ордеров (symbol и client_order_id)
        :param orders: список ордеров;
        :return: list[OrderRequestId] список идентификаторов
        """
        order_ids: list[GateOrderId] = []
        for order in orders:
            order_ids.append(GateOrderId(
                client_order_id=order.core_order_id,
                symbol=order.symbol
            ))
        return order_ids

    def format_cancel_orders(self, orders: list[OrderData]):
        """
        Форматировать команду для отмены ордеров;
        :param orders: список ордеров;
        :return: Message готовое сообщение, которое можно отправить гейту;
        """
        order_ids = self.format_order_ids(orders=orders)
        command = self.format_command(action=enums.Action.CANCEL_ORDERS, data=order_ids)
        return command

    def format_cancel_all_orders(self):
        """
        Форматировать команду для отмены всех открытых ордеров;
        :return: Message готовое сообщение, которое можно отправить гейту;
        """
        command = self.format_command(
            action=enums.Action.CANCEL_ALL_ORDERS,
            data=None
        )
        return command

    def format_get_orders(self, orders: list[OrderData]):
        """
        Форматировать команду для запроса статусов ордеров;
        :param orders: список ордеров;
        :return: Message готовое сообщение, которое можно отправить гейту;
        """
        order_ids = self.format_order_ids(orders=orders)
        command = self.format_command(action=enums.Action.GET_ORDERS, data=order_ids)
        return command

    def format_get_balance(self, assets: list[str]):
        """
        Форматировать команду для запроса баланса;
        :param assets: список ассетов;
        :return: Message готовое сообщение, которое можно отправить гейту;
        """
        command = self.format_command(action=enums.Action.GET_BALANCE, data=assets)
        return command

    @staticmethod
    def format_order_state(gate_order: GateOrderInfo) -> enums.OrderState:
        """
        Форматировать статус ордера от гейта в состояние ордера, которое используется в ядре;
        :param gate_order: ордер в общем формате;
        :return: enums.OrderState состояние ордера;
        """
        match gate_order.status:
            case enums.GateOrderStatus.OPEN:
                if gate_order.filled == 0:
                    return enums.OrderState.OPEN
                return enums.OrderState.FILLED
            case enums.GateOrderStatus.CANCELED:
                return enums.OrderState.CANCELED
            case enums.GateOrderStatus.CLOSED:
                return enums.OrderState.CLOSED
            case _:
                return enums.OrderState.ERROR

    def format_order_data(self, orders: list[GateOrderInfo]) -> list[OrderData]:
        """
        Форматировать список из данных по ордерам во внутренний формат данных;
        :param orders: список ордеров в общем формате;
        :return: список ордеров во внутреннем формате;
        """
        formatted_orders: list[OrderData] = []
        for order in orders:
            formatted_orders.append(OrderData(
                core_order_id=order.client_order_id,
                symbol=order.symbol,
                type=order.type,
                side=order.side,
                amount=order.amount,
                price=order.price,
                filled=order.filled,
                state=self.format_order_state(order)
            ))

