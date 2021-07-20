from collections import OrderedDict
from datetime import timedelta, datetime

from backend.lib.coro import start_coro, coro_func


class TemporaryDict(OrderedDict):
    """dict for temporary storing. Usually used as cache"""

    def __init__(self, ttl: timedelta = None, max_n=None, auto_clean=True, **kwargs):
        super().__init__(**kwargs)
        self._ttl = ttl
        self.max_n = max(max_n, 1) if max_n else None
        self.auto_clean = auto_clean

    def __contains__(self, key):
        key = str(key)
        if super().__contains__(key):
            if self._ttl:
                item = super().__getitem__(key)
                if datetime.now() - item[1] >= self._ttl:
                    del self[key]
                    return False
                else:
                    return True
            else:
                return True
        else:
            return False

    def __getitem__(self, key):
        key = str(key)
        self.__contains__(key)
        return super().__getitem__(key)[0]

    def get(self, key, default=None):
        key = str(key)
        self.__contains__(key)
        return super().get(key, (default, None))[0]

    def clean(self):
        # todo add Limit class
        while self.max_n and len(self) > self.max_n:
            try:
                self.popitem(False)  # todo add buffer before deletion
            except KeyError:
                pass

    def __setitem__(self, key, value):
        key = str(key)
        if self.auto_clean:
            self.clean()
        args = key, (value, datetime.now())
        super().__setitem__(*args)

        # to prevent memory leak
        if self._ttl:
            start_coro(coro_func(self.__contains__, key), self._ttl)

    def __delitem__(self, key):
        key = str(key)
        super().__delitem__(key)
