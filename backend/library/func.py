from enum import auto, IntFlag
from typing import Mapping, Callable


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


class MultiFunc(MultiFuncBase):
    def __call__(self, *args, **kwargs):
        return {func: func(*args, **kwargs) for func in self._funcs}


class MultiFuncAsync(MultiFuncBase):
    async def __call__(self, *args, **kwargs):
        return {func: await func(*args, **kwargs) for func in self._funcs}


def args_to_dict(args, kwargs, func_args):
    cur_args = dict(zip(func_args, args))
    cur_args.update(kwargs)
    return cur_args


def call_func(func, args, kwargs):
    return func(*args, **kwargs)


def auto_func(func_variants: Mapping[Callable, Callable], else_func=None):
    def func(*args, **kwargs):
        nonlocal func
        is_set = False
        for cond_func, _func in func_variants.items():
            if cond_func(*args, **kwargs):
                func = _func
                is_set = True
                break
        if not is_set:
            func = else_func

        return func(*args, **kwargs)

    return func


def str_to_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    elif val.isnumeric():
        return bool(int(val))
    elif val and val[0].lower() in ('t', 'f'):
        return val[0].lower() == 't'
    else:
        return bool(val)


def dict_to_str(data: dict, sep: str = ', ', sformat: str = '{:}: {:}') -> str:
    return sep.join([sformat.format(str(key), str(val)) for key, val in data.items()])


def new_file(file_path: str):
    open(file_path, 'w').close()
