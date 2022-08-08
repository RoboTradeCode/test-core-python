#!./venv/bin/python
# -*- coding: UTF-8 -*-

import asyncio

import click

from strategies.strategies_for_testing.breaking import BreakingTesting
from strategies.strategies_for_testing.fast_test import FastTesting
from strategies.strategies_for_testing.order_creating import OrderCreatingTesting
from strategies.strategies_for_testing.orderbooks import OrderbookTesting
from strategies.strategies_for_testing.orders_cancelling import CancellingTesting
from testing_core.core import run_core


class CustomMultiCommand(click.Group):

    def command(self, *args, **kwargs):
        """
        Behaves the same as `click.Group.command()` except if passed
        a list of names, all after the first will be aliases for the first.
        """

        def decorator(f):
            if isinstance(args[0], list):
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    cmd = super(CustomMultiCommand, self).command(
                        alias, *args[1:], **kwargs)(f)
                    cmd.short_help = "Alias for '{}'".format(_args[0])
            else:
                _args = args
            cmd = super(CustomMultiCommand, self).command(
                *_args, **kwargs)(f)
            return cmd

        return decorator


@click.group(cls=CustomMultiCommand)
def cli():
    ...


@cli.command(['fast-testing'])
def fast_testing():
    """
    Быстрая стратегия тестирования гейта.

    1. Отмена всех ордеров и запрос баланса - типичная операция на старте ядра;

    2. Ожидание, пока не придут балансы и ордербуки;

    3. Выставление лимитного ордера;

    4. Запрос статуса лимитного ордера;

    5. Отмена лимитного ордера;

    6. Выставление рыночного ордера;
    """
    asyncio.run(run_core(strategy_type=FastTesting))


@cli.command(['cancelling-testing'])
def cancelling_testing():
    """
    Стратегия тестирования отмены ордеров.

    1. Посылаем команду гейту на отмену всех ордеров, принимаем ответ на команду
    отмены (пока что ответ на отмену еще не реализован);

    2. Проверяем баланс, поле `used` у всех ассетов должно быть нулевым, если где-то не нулевое, ждем 1 секунду,
    повторяем пункт 1;

    2.1. Если поле `used` у какого-то ассета не нулевое - тест провален;

    3. Выбираем случайным образом рынок (BTC/USDT) из настроек, и ставим по нему 1 ордер;

    4. Баланс после установки должен измениться, а именно, поле `used`;

    5. Отменяем ранее выставленный ордер по id;

    6. Проверяем баланс, поле `used` у ассетов должно быть нулевым, если не нулевое - тест провален;

    7. Выбираем случайным образом от 3 до 5 рынков из настроек и выполняем с п.3 - 7. Только ордера создаем одной
    командой, и отменяем командой `cancel_all_orders`;
    """
    asyncio.run(run_core(strategy_type=CancellingTesting))


@cli.command(['order-creating-testing'])
def order_creating_testing():
    """
    Стратегия тестирования создания ордеров.

    1. Отменяем все ордера и запрашиваем баланс;

    2. Создаем лимитный ордер на случайном маркете. Цена подбирается таким образом, чтобы ордер быстро исполнился;

    3. Жду от гейта статусы об открытии, затем о закрытии;

    4. Шаги 2 и 3 повторяются 10 раз;

    5. Создаю рычночный ордер на случайном маркете;

    6. Жду от гейта статусы об открытии, затем о закрытии;

    7. Шаги 5 и 6 повторяются 10 раз;

    8. Отправляю команду гейту, в которой есть лимитные и рыночные ордера одновременно;

    """
    asyncio.run(run_core(strategy_type=OrderCreatingTesting))


@cli.command(['orderbook-testing'])
def orderbook_testing():
    """
    Стратегия для тестирования корректного получения ордербуков.
    В данной стратегии надо проверить работу гейта в следующем:

    1. Проверяю, что ордербуки приходят и меняются. Ордербук должен измениться за 5 секунд.

    2. Проверяю на задержки в передаче данных. Должно прийти не менее 5 ордербуков за 2.5 секунды

    3. Проверяю, что гейт присылает ордербуки с последовательным timestamp.

    Если биржа не присылает timestamp, этот шаг будет пропущен.
    """
    asyncio.run(run_core(strategy_type=OrderbookTesting))


@cli.command(['breaking-testing'])
def breaking_testing():
    """
    Стратегия неправильного поведения ядра.
    Тестирование стремится сломать гейт.

    1. Создаем лимитный ордер с нулевой ценой и должна быть ошибка от гейта;

    2. Создаем лимитный и рыночный ордер с нулевым объемом и ждем ошибку;

    3. Создаем ордер с `кривым` символом, ждем от гейта ошибку;

    4. Отправляем ордер с пустым `client_order_id` - ждем ошибку гейта;

    5. Отправляем 10 ордеров в одной команде, из которых часть нормальных, часть кривых, ждем от гейта чтобы
    на кривые пришла ошибка;

    6. Создаем команду с 10 ордерами, 1 из них кривой, должно прийти 9 статусов open и одна ошибка;
    """
    asyncio.run(run_core(strategy_type=BreakingTesting))


async def run_all():
    """
    Асинхронная функция для запуска стратегий.
    """
    await run_core(strategy_type=FastTesting)
    await run_core(strategy_type=OrderbookTesting)
    await run_core(strategy_type=OrderCreatingTesting)
    await run_core(strategy_type=CancellingTesting)
    await run_core(strategy_type=BreakingTesting)


@cli.command(['full-testing', 'all'])
def full_testing():
    """
    По очереди запустить все тестирующие стратегии. Порядок следующий:

    fast-testing
    orderbook-testing
    order-creating-testing
    cancelling-testing
    breaking-testing
    """
    asyncio.run(run_all())


if __name__ == '__main__':
    cli()
