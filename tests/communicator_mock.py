from typing import Callable

from testing_core.communicator.aeron_communicator import Communicator
from testing_core.models.message import Message


class CommunicatorMock(Communicator):
    """
    Мок для имитации работы коммуникатора. Вместо отправления и получения сообщений, добавляет их в массивы
    """

    orderbook_handler: Callable[[Message], None]
    balance_handler: Callable[[Message], None]
    core_input_handler: Callable[[Message], None]

    def __init__(self):
        self.orderbooks_queue = []
        self.balances_queue = []
        self.core_input_queue = []
        self.published_messages = []

    def set_handlers(self,
                     orderbook_handler: Callable[[Message], None],
                     balance_handler: Callable[[Message], None],
                     core_input_handler: Callable[[Message], None]):

        self.orderbook_handler = orderbook_handler
        self.balance_handler = balance_handler
        self.core_input_handler = core_input_handler

    def handle_new_messages(self):
        """
        Проверить наличие новых сообщений. Если они есть, вызвать их обработчики.
        """
        if self.orderbooks_queue:
            self.orderbook_handler(self.orderbooks_queue.pop(len(self.orderbooks_queue) - 1))
        if self.balances_queue:
            self.balance_handler(self.balances_queue.pop(len(self.balances_queue) - 1))
        if self.core_input_queue:
            self.core_input_handler(self.core_input_queue.pop(len(self.core_input_queue) - 1))

    def publish(self, message: Message):
        """
        Опубликовать сообщение. Сообщение будет добавлено в массив в коммуникаторе.
        :param message: Message - сообщение
        """
        self.published_messages.append(message)
