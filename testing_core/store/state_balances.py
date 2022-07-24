from testing_core.models.balance import Balance


class BalancesState(object):
    """
    Класс для хранения баланса аккаунта на бирже по различным ассетам.
    """
    balances: dict[str: Balance] = {}

    def update(self, balances: dict[str: Balance]):
        """
        Обновить баланс.

        :param balances: обновившиеся балансы от биржи.
        """
        for asset, balance in balances.items():
            self.balances[asset] = balance
