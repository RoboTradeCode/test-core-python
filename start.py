#!./venv/bin/python
# -*- coding: UTF-8 -*-

import asyncio

import click

from strategies.strategies_for_testing.cancelling_testing import CancellingTesting
from strategies.strategies_for_testing.fast_testing import FastTesting
from strategies.strategies_for_testing.order_creating_testing import OrderCreatingTesting
from strategies.strategies_for_testing.orderbook_testing import OrderbookTesting
from testing_core.core import run_core


@click.group()
def cli():
    ...


@cli.command()
def fast_testing():
    """Тип тестирования, при котором ядро прогоняет все команды и тестирует выставлени и отмену ордеров,
    получение баланса и ордербуков. То есть тестируется весь функционал, но макисмально быстро.
    Данный тест будет использоваться при незначительных изменениях гейта для проверки его работоспособности.
    """
    asyncio.run(run_core(strategy_type=FastTesting))


@cli.command()
def cancelling_testing():
    asyncio.run(run_core(strategy_type=CancellingTesting))


@cli.command()
def order_creating_testing():
    asyncio.run(run_core(strategy_type=OrderCreatingTesting))


@cli.command()
def orderbook_testing():
    asyncio.run(run_core(strategy_type=OrderbookTesting))


if __name__ == '__main__':
    cli()
