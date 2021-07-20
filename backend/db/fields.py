from typing import Union, Iterable, Mapping, Any
import peewee

from backend.lib.decorators.cache import unified


class OptionsField(peewee.IntegerField):
    def __init__(
        self,
        options: Union[Iterable, Mapping[int, Any]] = None,
        *args,
        first_i=0,
        **kwargs,
    ):
        if options is not None:  # for migrations
            if not isinstance(options, Mapping):
                options = {i + first_i: item for i, item in enumerate(options)}
            else:
                for i in options.keys():
                    assert isinstance(
                        i, int
                    ), f'All keys for {self.__class__.__name__} should be int'

        self._options = options

        super().__init__(*args, **kwargs)

    @property
    def options(self):
        return self._options.values()

    def __contains__(self, item):
        return self.options.__contains__(item)

    def python_value(self, value):
        if value is not None:
            if isinstance(value, int):
                return self._options[value]
            elif isinstance(value, str) and value in self._options.values():
                return value

    @unified
    def db_value(self, value):
        if value is None:
            return
        for i, item in self._options.items():
            if value == item:
                return i
        if value in self._options:
            return value
        raise ValueError(f'There\'s no such option "{value}"')
