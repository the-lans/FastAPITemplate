import asyncio
from asyncio import (
    FIRST_COMPLETED,
    Task,
    iscoroutinefunction,
    iscoroutine,
    wait,
)
from datetime import timedelta
from typing import Union
import logging
import traceback
import aiostream

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


def run_and_get(coro):
    task = asyncio.create_task(coro)
    asyncio.get_running_loop().run_until_complete(task)
    return task.result()


async def maybe_coro(func, *args, __to_executor=False, **kwargs):
    """
    Await either coro or func
    :param func: either async or sync callable to be awaited
    :param args: args that should be passed to func
    :param __to_executor: if True and func is not async then func will be passed to executor
    :param kwargs: kwargs that should be passed to func
    :return:
    """
    if iscoroutinefunction(func) or (hasattr(func, 'func') and iscoroutinefunction(func.func)):
        return await func(*args, **kwargs)
    elif iscoroutine(func):
        return await func
    elif callable(func):
        if __to_executor:
            return await coro_func(func, *args, **kwargs)
        return func(*args, **kwargs)
    else:
        assert not (args or kwargs)
        return func


async def coro_func(func, *args, **kwargs):
    """
    Makes coro from sync function
    :param func:
    :param args:
    :param kwargs:
    :return: running coro in executor
    """
    return await get_loop().run_in_executor(None, call_func, func, args, kwargs)


async def run_on_interval(corofunc, *args, wait_time=25, **kwargs):
    """
    Runs coro_func on interval
    :param corofunc:
    :param args:
    :param wait_time:
    :param kwargs:
    """
    while True:
        try:
            await corofunc(*args, **kwargs)
        except Exception:
            traceback.print_exc()
        await asyncio.sleep(wait_time)


async def remove_done_coros_from_list(coros_list, results=None):
    """
    Searches for done coros and removes them from list
    :param coros_list:
    :param results:
    """
    if results is None:
        results = []
    done_coros = []
    for coro in list(coros_list):
        if coro.done():
            try:
                results.append(await coro)
                done_coros.append(coro)
            except Exception as e:
                logging.warning(f'Coroutine not finished: {e}')
            finally:
                coros_list.remove(coro)
    return done_coros


async def add_coro_to_list(coro, coros_list, max_num=None, results=None):
    """
    Waits while there will be space for coro in list and starts and adds it to list
    :param coro:
    :param coros_list:
    :param max_num:
    :param results:
    """
    if results is None:
        results = []
    done_coros = []
    await remove_done_coros_from_list(coros_list, results=results)
    while max_num and len(coros_list) >= max_num:
        await asyncio.wait(coros_list, return_when=FIRST_COMPLETED)
        done_coros.extend(await remove_done_coros_from_list(coros_list, results=results))
    if not isinstance(coro, Task):
        coro = start_coro(coro)
    coros_list.append(coro)
    return done_coros


async def gen_finish_coro_list(coros_list, results=None):
    if results is None:
        results = []
    while coros_list:
        await asyncio.wait(coros_list, return_when=FIRST_COMPLETED)
        for coro in await remove_done_coros_from_list(coros_list, results=results):
            yield coro


async def finish_coro_list(coros_list, results=None):
    return await aiostream.stream.list(gen_finish_coro_list(coros_list, results))


def sync_coro(coro):
    return get_loop().run_until_complete(coro)


async def coro_gen(gen):
    queue = asyncio.Queue()

    def exhaust_gen():
        for item in gen:
            queue.put_nowait(item)

    main_coro = start_coro(coro_func(exhaust_gen))
    coro = None
    while not main_coro.done():
        coro = coro or start_coro(queue.get())
        await wait([main_coro, coro], return_when=asyncio.FIRST_COMPLETED)
        if coro.done():
            yield coro.result()
            coro = None
    if coro:
        if queue.qsize():
            yield await coro
        else:
            coro.cancel()
    while queue.qsize():
        yield await queue.get()
