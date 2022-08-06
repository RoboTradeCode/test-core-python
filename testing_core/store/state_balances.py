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

    def __getitem__(self, asset: str) -> Balance:
        """
        Получить баланс определенного ассета;
        :param asset: название ассета;
        :return: Balance - баланс ассета
        """
        return self.balances.get(asset)

    def __iter__(self):
        return self.balances.__iter__()

    def __repr__(self):
        return self.balances.__repr__()

    def __bool__(self):
        return self.balances == {}

    def items(self):
        return self.balances.items()
