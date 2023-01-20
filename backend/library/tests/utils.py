from typing import Tuple, Optional, NoReturn
from types import TracebackType
from faker import Faker
import os

faker: Faker = Faker()


def raise_exc_info(
    exc_info,  # type: Tuple[Optional[type], Optional[BaseException], Optional[TracebackType]]
):
    # type: (...) -> NoReturn
    try:
        if exc_info[1] is not None:
            raise exc_info[1].with_traceback(exc_info[2])
        else:
            raise TypeError("raise_exc_info called with no exception")
    finally:
        # Clear the traceback reference from our stack frame to
        # minimize circular references that slow down GC.
        exc_info = (None, None, None)


def delete_random_items(data, chance_of_deleting=50):
    for key, value in dict(data).items():
        if faker.boolean(chance_of_getting_true=chance_of_deleting) or value is None:
            del data[key]


def get_async_test_timeout() -> float:
    """Get the global timeout setting for async tests.
    Returns a float, the timeout in seconds.
    """
    env = os.environ.get("ASYNC_TEST_TIMEOUT")
    if env is not None:
        try:
            return float(env)
        except ValueError:
            pass
    return 5
