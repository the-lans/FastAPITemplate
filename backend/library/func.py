from enum import auto, IntFlag


class FieldHidden(IntFlag):
    NOT = 0
    READ = auto()
    EDIT = auto()
    INIT = auto()
    FULL = READ | EDIT | INIT
    WRITE = EDIT | INIT


class MultiFuncBase:
    """Lets you call many functions with same arguments"""

    def __init__(self, funcs=None):
        self._funcs = funcs or []

    def add(self, func):
        self._funcs.append(func)


def args_to_dict(args, kwargs, func_args):
    cur_args = dict(zip(func_args, args))
    cur_args.update(kwargs)
    return cur_args


def call_func(func, args, kwargs):
    return func(*args, **kwargs)
