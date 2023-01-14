import asyncio
import inspect
import threading
from functools import partial, wraps

from backend.library.coro import coro_func


class ClassProperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def executored(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await coro_func(func, *args, **kwargs)

    return wrapper


def decorator_with_defaults(decorator):
    """
    Makes decorator that can be applied both ways @decorator and @decorator()
    :param decorator: decorator itself
    :return: decorated decorator for decorating :)
    """

    sig = inspect.signature(decorator)
    args_n = len(
        list(
            filter(
                lambda item: item[0] != 'func' and item[1].default == item[1].empty,
                sig.parameters.items(),
            )
        )
    )

    def wrapper(*args, func=None, **kwargs):
        if args:
            if len(args) > args_n:
                return decorator(*args, **kwargs)
            elif len(args) == args_n:
                return partial(wrapper, *args, **kwargs)
            else:
                raise TypeError('Not enough arguments')
        elif func is not None:
            return decorator(func=func, **kwargs)
        else:
            return partial(wrapper, **kwargs)

    return wrapper


def semaphored(semaphore_class=None, value=1, semaphore=None, **kwargs):
    """
    Returns decorator which makes function semaphored, so that function can be executed simultaneously not more
    than number specified in value
    :param semaphore_class: semaphore class to use if semaphore is not specified
    :param value: number of simultaneous running functions
    :param semaphore: semaphore instance to use
    :param kwargs: kwargs for semaphore class if semaphore is not specified
    :return:
    """

    def decorator(func):
        is_async = asyncio.iscoroutinefunction(func)
        sem = semaphore or (semaphore_class or (asyncio.Semaphore if is_async else threading.Semaphore))(
            value, **kwargs
        )

        def wrapper(*fargs, **fkwargs):
            with sem:
                return func(*fargs, **fkwargs)

        async def awrapper(*fargs, **fkwargs):
            async with sem:
                return await func(*fargs, **fkwargs)

        if is_async:
            return awrapper
        else:
            return wrapper

    return decorator


def func_args(*args, **kwargs):
    """
    Returns decorator that passes args and kwargs to func when it called
    :param args:
    :param kwargs:
    :return:
    """

    def decorator(func):
        def wrapper(*fargs, **fkwargs):
            new_args = list(fargs) + list(args)[len(fargs) :]
            new_kwargs = dict(kwargs)
            new_kwargs.update(fkwargs)
            return func(*new_args, **new_kwargs)

        @wraps(func)
        async def async_wrapper(*fargs, **fkwargs):
            return await wrapper(*fargs, **fkwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def modifiable_func(func):
    """
    Makes decorated function modifiable. It means that calling that function with some args and kwargs will return
    callable function with args and kwargs as default ones
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return partial(func, *args, **kwargs)

    return wrapper


def aloop_passer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['loop'] = asyncio.get_event_loop()

        return func(*args, **kwargs)

    return wrapper
