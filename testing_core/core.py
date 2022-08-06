import asyncio
import logging
import os
import subprocess
from typing import Type

import pydantic
import tomli as tomli

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
        strategy_executing = loop.create_task(strategy.execute(
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
