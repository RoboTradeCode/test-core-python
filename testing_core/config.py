import json
import logging
import asyncio
from pprint import pprint
from typing import Optional

import requests
from pydantic import BaseModel

from testing_core import enums
from testing_core.exceptions import InvalidConfigurationSource
from testing_core.utils import follow_path

PING_DELAY = 1


class AeronChannel(BaseModel):
    channel: str
    stream_id: int


class CoreAeronChannels(BaseModel):
    gate_input: AeronChannel
    core_input: AeronChannel
    orderbooks: AeronChannel
    balances: AeronChannel
    logs: AeronChannel


class Market(BaseModel):
    """
    Класс для хранения данных о торговой паре на бирже
    exchange_symbol: str - как торговая пара называется на бирже (примеры: BTC/USDT, ETH-USDT, fBTCUST)
    common_symbol: str - универсальное название торговой пары (примеры: BTC/USDT, ETH/USDT, SHIB/BTC)
    price_increment: float - шаг цены (примеры: 0.00001, 0.5, 0.025)
    amount_increment: float - шаг объема (примеры: 0.00001, 0.5, 0.025)
    min_amount: float - минимальный объем ордера
    max_amount: float - максимальный объем ордера
    base_asset: str - базовый актив
    quote_asset: str - котируемый актив
    """
    class Limits(BaseModel):
        class MinMax(BaseModel):
            min: Optional[float]
            max: Optional[float]
        amount: MinMax
        price: MinMax
        cost: MinMax
        leverage: MinMax

    exchange_symbol: str
    common_symbol: str
    price_increment: Optional[float]
    amount_increment: Optional[float]
    limits: Limits
    base_asset: str
    quote_asset: str

class Configuration(BaseModel):

    # General settings
    exchange_id: str
    instance: str
    node: enums.Node = enums.Node.CORE
    algo: str
    assets: list[str]
    markets: dict[str, Market]
    orderbook_depth: int = 3

    # Aeron communicator settings
    aeron_channels: CoreAeronChannels
    no_subscriber_log_delay: int


def parse_configuration(configuration: dict) -> Configuration:
    """
    convert dictionary to configuration with fields validation
    """
    result = Configuration(
        # General gate settings
        exchange_id=follow_path(configuration, 'exchange'),
        instance=follow_path(configuration, 'instance'),
        algo=follow_path(configuration, 'algo'),
        assets=[asset_label['common'] for asset_label in follow_path(configuration, 'data/assets_labels')],
        markets={market['common_symbol']: Market(**market) for market in follow_path(configuration, 'data/markets')},

        # Aeron communicator settings
        aeron_channels=CoreAeronChannels(
            gate_input=follow_path(configuration, 'data/configs/core_config/aeron/publishers/gate_input'),
            core_input=follow_path(configuration, 'data/configs/core_config/aeron/subscribers/core_input'),
            orderbooks=follow_path(configuration, 'data/configs/core_config/aeron/subscribers/orderbooks'),
            balances=follow_path(configuration, 'data/configs/core_config/aeron/subscribers/balances'),
            logs=follow_path(configuration, 'data/configs/core_config/aeron/publishers/logs'),
        ),
        no_subscriber_log_delay=follow_path(configuration, 'data/configs/core_config/aeron/no_subscriber_log_delay')
    )
    return result


def get_configuration_from_api(api_url: str, params: dict = None) -> Configuration:
    """Receive json from api and parse it to Configuration object"""
    response = requests.request(url=api_url, method='GET')
    json_data = response.json()
    configuration = parse_configuration(json_data)
    return configuration


def get_configuration_from_file(file_path: str) -> Configuration:
    """Read json file with configuration and parse it to Configuration object"""
    with open(file_path) as file:
        json_data = json.load(file)
    configuration = parse_configuration(json_data)
    return configuration


async def receive_configuration(basic_settings: dict) -> Configuration:
    """Receive full gate configuration from basic settings"""
    match basic_settings.get('type'):
        case 'api':
            if basic_settings.get('path') is None:
                raise InvalidConfigurationSource
            config = get_configuration_from_api(api_url=basic_settings['path'])
        case 'file':
            if basic_settings.get('path') is None:
                raise InvalidConfigurationSource
            config = get_configuration_from_file(file_path=basic_settings['path'])
        case _:
            raise InvalidConfigurationSource
    return config

if __name__ == '__main__':
    basic_settings = {
        'type': 'api',
        'path': 'https://configurator.robotrade.io/binance/sandbox?only_new=false'
    }
    config = asyncio.run(receive_configuration(basic_settings=basic_settings))
    pprint(config.dict())