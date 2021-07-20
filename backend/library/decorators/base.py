import asyncio
import inspect
import threading
from collections import defaultdict
from functools import partial, update_wrapper


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
