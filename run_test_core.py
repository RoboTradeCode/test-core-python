#!./venv/bin/python
# -*- coding: UTF-8 -*-

import asyncio

import click

from src.test_core import TestCore

gate_start_path = '../start.py'
gate_settings_path = '../settings.toml'

default_test_exchange = 'binance'


@click.group()
def cli():
    ...


@click.command()
@click.argument('exchange_name')
def fast_test(exchange_name):
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
def long_test(exchange_name):
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


async def listen_gather(exchange_name: str):
    core = TestCore()
    core.exchange_name = exchange_name
    listen_coroutine = core.listen_gate_loop()
    logging_coroutine = core.logging_loop(1)
    await asyncio.gather(core.listen_gate_loop(), core.logging_loop(1))


@click.command()
@click.argument('exchange_name')
def listener(exchange_name: str):
    """ Запуск тестового ядра, при котором оно будет слушать сообщения от гейта и логгировать их.
    Команды отправляться не будут.

    :param exchange_name:
    :return:
    """
    return asyncio.run(listen_gather(exchange_name))


@click.command()
def hello():
    click.echo('Hello')


cli.add_command(hello)
cli.add_command(listener)
cli.add_command(fast_test)
cli.add_command(long_test)

#
if __name__ == '__main__':
    cli()
