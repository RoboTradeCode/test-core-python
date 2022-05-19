#!./venv/bin/python
# -*- coding: UTF-8 -*-

import asyncio
import logging

import click

from src.test_core import TestCore

gate_start_path = '../start.py'
gate_settings_path = '../settings.toml'

default_test_exchange = 'binance'


# logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    ...


@click.command()
@click.argument('exchange_name')
def run_fast_test(exchange_name):
    """Тип тестирования, при котором ядро прогоняет все команды и тестирует выставлени и отмену ордеров,
    получение баланса и ордербуков. То есть тестируется весь функционал, но макисмально быстро.
    Данный тест будет использоваться при незначительных изменениях гейта для проверки его работоспособности.

    :param exchange_name: Название биржи, для которой будет запущен тест.
    :return:
    """
    core = TestCore()
    core.exchange_name = exchange_name
    return asyncio.run(core.fast_test())


@click.command()
@click.argument('exchange_name')
def run_long_test(exchange_name):
    """При этом тестировании ядро запускается на продолжительное время (несколько дней) и реализует
    простую безубыточную торговую стратегию. Основная цель такого тестирования - проверить,
    как гейт конкретной биржи ведет себя при продолжительном запуске.
    Тест будет использоваться для проверки новых гейтов, гейтов со значительными изменениями или для гейтов,
    адаптированных под новые биржи.

    :param exchange_name: Название биржи, для которой будет запущен тест.
    :return:
    """
    core = TestCore()
    core.exchange_name = exchange_name
    return asyncio.run(core.long_test())


@click.command()
@click.argument('exchange_name')
def run_listener(exchange_name):
    """ Запуск тестового ядра, при котором оно будет слушать сообщения от гейта и логгировать их.
    Команды отправляться не будут.

    :param exchange_name:
    :return:
    """
    core = TestCore()
    core.exchange_name = exchange_name
    return asyncio.run(core.listen_gate_loop())


@click.command()
def hello():
    click.echo('Hello')


cli.add_command(hello)
cli.add_command(run_listener)
cli.add_command(run_fast_test)
cli.add_command(run_long_test)

#
if __name__ == '__main__':
    cli()
#     # run_listener(default_test_exchange)
