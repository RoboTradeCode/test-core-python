import asyncio

from test.test_core.core import TestCore


async def get_task_fast_test():
    core = TestCore()
    core.exchange = 'ascendex'
    return asyncio.create_task(await core.fast_test())


if __name__ == '__main__':
    asyncio.run(get_task_fast_test())
