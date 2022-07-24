import json

from aeron import Subscriber
from time import sleep


def handler(message: str) -> None:
    message_json = json.loads(message)
    # if message_json['action'] != 'ping':
    print(f"{message}\n")


subscriber = Subscriber(
    handler=handler,  # Callable[[str], None]
    channel="aeron:ipc",  # str
    stream_id=1008,  # int
)

while True:
    sleep(0.1)
    fragments_read = subscriber.poll()

# subscriber.close()
