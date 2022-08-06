import decimal
import time
import uuid


def get_micro_timestamp() -> int:
    """ Функция для получения текущего timestamp в микросекундах
    :return: int - timestamp в микросекундах
    """
    return round(time.time() * 1_000_000)


def follow_path(dictionary: dict, path: str, separator: str = '/'):
    """ Функция для проследования пути внутри dict
    :param dictionary: словарь, в котором нужно проследовать пути.
    :param path: строка пути, по умолчанию части пути разделяются /, как в директориях *nix систем.
    :param separator: подстрока, с помощью которой разделяются части пути (по умолчанию /).
    :return: значение, полученное по заданному пути. None, если не удалось проследовать пути.
    """
    for item in path.split(separator):
        dictionary = dictionary.get(item, None)
        if dictionary is None:
            break
    return dictionary


def get_uuid(prefix: str = '', postfix: str = '') -> str:
    """
    Функция для генерации UUID.
    :param prefix: префикс UUID (не обязательный параметр)
    :param postfix: постфикс UUID (не обязательный параметр)
    :return: UUID в виде строки.
    """
    return f'{prefix}{uuid.uuid4().__str__()}{postfix}'


def truncate_to_increment(number: float, increment: float) -> float:
    """
    Округлить число вниз, чтобы оно соответствовало инкременту.
    Например:
        truncate(123.1234, 0.001) -> 123.123
        truncate(123.1234, 0.05) -> 123.1
        truncate(12345.1234, 10) -> 12340.0
    :param number: float
    :param increment: float
    :return: float - округленное число
    """
    number_decimal = decimal.Decimal(str(number))
    increment_decimal = decimal.Decimal(str(increment))
    result = number_decimal - number_decimal % increment_decimal
    return float(result)