from string import (
    whitespace,
    ascii_lowercase,
    ascii_uppercase,
    ascii_letters,
    digits,
    hexdigits,
    octdigits,
    punctuation,
    printable,
)
from random import choice
from datetime import datetime

CHARS_DICT = {
    'whitespace': whitespace,
    'ascii_lowercase': ascii_lowercase,
    'ascii_uppercase': ascii_uppercase,
    'ascii_letters': ascii_letters,
    'digits': digits,
    'hexdigits': hexdigits,
    'octdigits': octdigits,
    'punctuation': punctuation,
    'printable': printable,
}


def random_string(size, chars: list[str] = None):
    if not chars:
        chars = ['ascii_letters', 'digits']
    chars_str = [CHARS_DICT[key] for key in chars]
    return ''.join(choice(''.join(chars_str)) for _ in range(size))


def date_to_dict(dt: datetime):
    return {
        key: getattr(dt, key)
        for key in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'tzinfo', 'fold']
    }
