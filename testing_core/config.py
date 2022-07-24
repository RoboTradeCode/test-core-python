import json
import logging
import asyncio
from pprint import pprint

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


class Configuration(BaseModel):

    # General gate settings
    exchange_id: str
    instance: str
    node: enums.Node = enums.Node.CORE
    algo: str
    symbols: list[str]
    assets: list[str]

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
        symbols=[market['common_symbol'] for market in follow_path(configuration, 'data/markets')],
        assets=[asset_label['common'] for asset_label in follow_path(configuration, 'data/assets_labels')],

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