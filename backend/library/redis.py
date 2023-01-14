import asyncio
import aioredis
from functools import wraps
from typing import Iterable, Union

from backend.library.decorators.cache import unified
from backend.library.decorators.other import decorator_with_defaults
from backend.library.coro import start_coro
from backend.library.func import MultiFunc

reset_redis_client = MultiFunc()


@unified(notifier=reset_redis_client)
async def get_aclient(db: int = 0):
    return await get_new_aclient(db)


async def get_new_aclient(db: int = 0):
    return await aioredis.from_url('redis://127.0.0.1', db=db)


async def redis_call(op_name, *args, **kwargs):
    return await getattr(await get_aclient(), op_name)(*args, **kwargs)


async def get_channel(name):
    return (await (await get_new_aclient()).subscribe(name))[0]


async def incrby(key, n=1):
    if key:
        return await (await get_aclient()).incrby(key, n)


async def publish(message, channel):
    await (await get_aclient()).publish(channel, message)


def runs_counter(**kwargs):
    kwargs.update(func=lambda *args, **kws: None)
    return count_runs(**kwargs)


def default_key_func(args, kwargs, func, key):
    return key or f'n_{func.__name__}_runs'


@decorator_with_defaults
def count_runs(
    func,
    key=None,
    by_args=True,
    key_func: Union[callable, Iterable[callable]] = default_key_func,
    n: int = 1,
):
    is_async = asyncio.iscoroutinefunction(func)

    key_funcs = [key_func] if callable(key_func) else key_func

    def get_key_by_args(args, kwargs):
        cur_key = key
        for item_func in key_funcs:
            cur_key = item_func(args, kwargs, func, cur_key)
        return cur_key

    def get_key_by_result(result, args, kwargs):
        cur_key = key
        for item_func in key_funcs:
            cur_key = item_func(result, args, kwargs, func, cur_key)
        return cur_key

    @wraps(func)
    def wrapper(*args, **kwargs):
        if by_args:
            key_to_use = get_key_by_args(args, kwargs)
            start_coro(incrby(key_to_use, n))
            return func(*args, **kwargs)
        else:
            res = func(*args, **kwargs)
            key_to_use = get_key_by_result(res, args, kwargs)
            start_coro(incrby(key_to_use, n))
            return res

    @wraps(func)
    async def awrapper(*args, **kwargs):
        if by_args:
            key_to_use = get_key_by_args(args, kwargs)
            return (await asyncio.gather(func(*args, **kwargs), incrby(key_to_use, n)))[0]
        else:
            res = await func(*args, **kwargs)
            key_to_use = get_key_by_result(res, args, kwargs)
            start_coro(incrby(key_to_use, n))
            return res

    return awrapper if is_async else wrapper
