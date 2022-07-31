#!./venv/bin/python
# -*- coding: UTF-8 -*-

import asyncio
import logging
import os
import subprocess
from typing import Type

import click
import pydantic
import tomli as tomli

from strategies.strategies_for_testing.cancelling_testing import CancellingTesting
from strategies.strategies_for_testing.fast_testing import FastTesting
from strategies.strategies_for_testing.order_creating_testing import OrderCreatingTesting
from testing_core.config import receive_configuration
from testing_core.strategy.base_strategy import Strategy
from testing_core.trader.trader import Trader

# проверяю запущен ли aeron media driver
if subprocess.run('ps -A | grep aeron', shell=True, stdout=None).returncode != 0 and \
        subprocess.run('systemctl is-active --quiet aeron', shell=True, stdout=None).returncode != 0:
    print('Critical: Aeron service is not launched. Please launch Aeron before launching application.')
    exit(1)

# путь до начальной конфигурации (в ней указан способ получения полной конфигурации)
BASIC_SETTINGS_PATH = 'settings.toml'

logger = logging.getLogger(__name__)


async def run_core(strategy_type: Type[Strategy]):
    """Запуск гейта. Функция загружает конфигурацию и запускает гейт"""
    # Загрузка начальной конфигурации (в ней указан способ получения полной конфигурации)
    if not os.path.isfile(BASIC_SETTINGS_PATH):
        logger.critical(f'Could not find file with basic settings.'
                        f' Specified file path: "{BASIC_SETTINGS_PATH}".'
                        f' Please make sure the file exists.')
        exit(1)
    with open(BASIC_SETTINGS_PATH, "rb") as f:
        basic_settings = tomli.load(f)
    logger.info('Loaded basic settings for gate.')

    # получение полной конфигурации и создание объекта гейта
    try:
        config = await receive_configuration(basic_settings=basic_settings['configuration'])
        trader = Trader(config=config)
        strategy = strategy_type(trader=trader, markets=config.markets, assets=config.assets)
        loop = asyncio.get_event_loop()

        logger.info(f'Start strategy "{strategy.name}": {strategy.__doc__}')

        trader_executing = loop.create_task(trader.get_loop())
        strategy_executing = loop.create_task(strategy.strategy(
            trader=trader,
            orderbooks=trader.orderbooks,
            balances=trader.balances
        ))

        await strategy_executing

    except pydantic.error_wrappers.ValidationError as exception:
        logger.critical(f'Invalid of missed field in configuration: {exception}. '
                        f'Please, make sure that specified fields are in configuration '
                        f'and they are correct.')
        exit(1)


@click.group()
def cli():
    ...


@click.command()
def fast_testing():
    """Тип тестирования, при котором ядро прогоняет все команды и тестирует выставлени и отмену ордеров,
    получение баланса и ордербуков. То есть тестируется весь функционал, но макисмально быстро.
    Данный тест будет использоваться при незначительных изменениях гейта для проверки его работоспособности.
    """
    asyncio.run(run_core(strategy_type=FastTesting))


@click.command()
def cancelling_testing():
    asyncio.run(run_core(strategy_type=CancellingTesting))


@click.command()
def order_creating_testing():
    asyncio.run(run_core(strategy_type=OrderCreatingTesting))


# @click.command()
# def long_test():
#     """При этом тестировании ядро запускается на продолжительное время (несколько дней) и реализует
#     простую безубыточную торговую стратегию. Основная цель такого тестирования - проверить,
#     как гейт конкретной биржи ведет себя при продолжительном запуске.
#     Тест будет использоваться для проверки новых гейтов, гейтов со значительными изменениями или для гейтов,
#     адаптированных под новые биржи.
#
#     :param exchange_name: Название биржи, для которой будет запущен тест.
#     :return:
#     """
#     core = TestCore()
#     return asyncio.run(core.long_test())
#
#
# @click.command()
# @click.argument()
# def listener():
#     """ Запуск тестового ядра, при котором оно будет слушать сообщения от гейта и логгировать их.
#     Команды отправляться не будут.
#
#     :param exchange_name:
#     :return:
#     """
#     core = TestCore()
#     loop = asyncio.get_event_loop()
#     loop.create_task(core.listen_gate_loop())
#     loop.create_task(core.logging_loop(1))
#     loop.run_forever()


# cli.add_command(listener)
cli.add_command(fast_testing)
cli.add_command(cancelling_testing)
cli.add_command(order_creating_testing)

#
if __name__ == '__main__':
    cli()
