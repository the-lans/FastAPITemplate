import asyncio
import inspect
import threading
from collections import defaultdict
from functools import partial, update_wrapper

from backend.library.decorators.base import decorator_with_defaults
from backend.library.func import MultiFuncBase, args_to_dict
from backend.library.cache import TemporaryDict
from backend.library.coro import start_coro


def _args_to_dict(args, kwargs, func_args, key_args):
    cur_args = args_to_dict(args, kwargs, func_args)
    return {
        arg_name: cur_args[arg_name] for arg_name in key_args if arg_name in cur_args
    }


def _args_to_key(args, kwargs, func_args, key_args) -> frozenset:
    return frozenset(_args_to_dict(args, kwargs, func_args, key_args).items())


@decorator_with_defaults
class unified:
    def __init__(
        self,
        func,
        sem_value=1,
        depends_on=None,
        ignore_args=None,
        ttl=None,
        based_on=None,
        max_n=None,
        notifier: MultiFuncBase = None,
    ):
        """
        Decorator for providing cached results

        :param func: function that should be decorated (doesn't matter async or not)
        :param sem_value: number one time concurrent running functions for same input
        :param depends_on: list of args names that form key for result
        :param ignore_args: list of args names that don't form key for result
        :param ttl: time to live for each result
        :param based_on: if specified, then each instance of that field has its own list of answers
        :param max_n: maximum number of results
        :param notifier: MultiFunc that triggers deleting results by args
        :return:
        """
        self.func = func
        self.ttl = ttl
        self.max_n = max_n
        assert callable(self.func), 'Only callables are accepted'
        if not (inspect.isfunction(self.func) or inspect.ismethod(self.func)):
            # todo for callable custom objects (like class-decorated funcs)
            self.func = self.func.__call__

        self.func_args = inspect.getfullargspec(self.func).args
        key_args = set(depends_on or self.func_args) - set(ignore_args or ['cls'])
        is_async = asyncio.iscoroutinefunction(self.func)
        sem_class = asyncio.Semaphore if is_async else threading.Semaphore
        self.semaphores = defaultdict(lambda: sem_class(value=sem_value))
        self.answers = self.make_answers_dict()
        self.base_name = based_on if based_on in self.func_args else None
        key_args.discard(self.base_name)

        self.answers_attr_name = f'__answers_for_{self.func.__name__}'

        self.args_to_key = partial(
            _args_to_key, func_args=self.func_args, key_args=key_args
        )

        if notifier:
            notifier.add(self.delete_answers)

        if is_async:
            self.__call__ = self._async_call
            self._is_coroutine = asyncio.coroutines._is_coroutine
        else:
            self.__call__ = self._sync_call
        update_wrapper(self, self.func)

    def make_answers_dict(self):
        return TemporaryDict(ttl=self.ttl, max_n=self.max_n)

    def _get_answers(self, args, kwargs):
        if self.base_name:
            base = args_to_dict(args, kwargs, self.func_args)[self.base_name]

            if not hasattr(base, self.answers_attr_name):
                setattr(base, self.answers_attr_name, self.make_answers_dict())

            return getattr(base, self.answers_attr_name)
        return self.answers

    def delete_answers(self, *args, **kwargs):
        answers = self._get_answers(args, kwargs)
        args_to_key = self.args_to_key(args, kwargs)
        if not args_to_key:
            # without arguments clean all dict
            self.answers = self.make_answers_dict()
        else:
            key = str(args_to_key)
            if key in list(answers.keys()):
                del answers[key]

    def get_answer(self, args, kwargs):
        answers = self._get_answers(args, kwargs)
        key = str(self.args_to_key(args, kwargs))
        return answers.get(key)

    def set_answer(self, args, kwargs, answer):
        answers = self._get_answers(args, kwargs)
        key = str(self.args_to_key(args, kwargs))
        answers[key] = answer

    async def _release_semaphore(self, key: str):
        if key in self.semaphores:
            del self.semaphores[key]

    def _sync_call(self, *args, **kwargs):
        answers = self._get_answers(args, kwargs)
        key = str(self.args_to_key(args, kwargs))
        with self.semaphores[key]:
            if key not in answers:
                answers[key] = self.func(*args, **kwargs)
        start_coro(self._release_semaphore(key), 10)
        return answers[key]

    async def _async_call(self, *args, **kwargs):
        answers = self._get_answers(args, kwargs)
        key = str(self.args_to_key(args, kwargs))
        async with self.semaphores[key]:
            if key not in answers:
                answers[key] = await self.func(*args, **kwargs)
        start_coro(self._release_semaphore(key), 10)
        return answers[key]

    def __call__(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)

    def __get__(self, instance, owner):
        class BoundUnified:
            __call__ = partial(self.__call__, instance)
            _async_call = partial(self._async_call, instance)
            _sync_call = partial(self._sync_call, instance)

        return BoundUnified()
