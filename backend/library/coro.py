import asyncio
from datetime import timedelta
from typing import Union

from backend.library.func import call_func


def get_loop():
    """
    :return: current loop
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        return loop


loop = get_loop()


async def run_coro_after(coro, time: Union[float, timedelta]):
    """
    Sleeps before awaiting coro
    :param coro: coro to ba awaited after time
    :param time:
    :return:
    """
    if isinstance(time, timedelta):
        time = time.total_seconds()
    await asyncio.sleep(time)
    return await coro


def start_coro(coro, after: Union[timedelta, float] = None):
    """
    Starts coro
    :param coro: coro to be started
    :param after: if specified, then coro will be started after some time
    :return: started coro
    """
    if after:
        coro = run_coro_after(coro, after)
    return get_loop().create_task(coro)


async def coro_func(func, *args, **kwargs):
    """
    Makes coro from sync function
    :param func:
    :param args:
    :param kwargs:
    :return: running coro in executor
    """
    return await get_loop().run_in_executor(None, call_func, func, args, kwargs)
