import random
import string
from functools import partial
from typing import Any, Callable, Optional

from restcli.utils import AttrMap, AttrSeq

ALPHANUMERIC_CHARS = string.ascii_letters + string.digits
ASCII_CHARS = ALPHANUMERIC_CHARS + string.punctuation
URLSAFE_CHARS = ALPHANUMERIC_CHARS + "_.-"


def _range_args(a, b=None):
    if b is None:
        return 0, a
    return a, b


def _random_len(a, b, min_len=1):
    a, b = _range_args(a, b)
    return max(min_len, random.randint(a, b))


def random_str(population, a=15, b=None, length=None):
    length = length or _random_len(a, b, min_len=3)
    k = min(length, len(population))
    return "".join(random.sample(population, k))


def random_alphanum(a=15, b=None, length=None):
    """Generate a random alphanumeric ASCII string."""
    return random_str(ALPHANUMERIC_CHARS, a, b, length)


def random_ascii(a=15, b=None, length=None):
    """Generate a random ASCII string."""
    return random_str(ASCII_CHARS, a, b, length)


def random_unicode(a=15, b=None, length=None):
    """Generate a random Unicode string."""
    include_ranges = [
        (0x0021, 0x0021),
        (0x0023, 0x0026),
        (0x0028, 0x007E),
        (0x00A1, 0x00AC),
        (0x00AE, 0x00FF),
        (0x0100, 0x017F),
        (0x0180, 0x024F),
        (0x2C60, 0x2C7F),
        (0x16A0, 0x16F0),
        (0x0370, 0x0377),
        (0x037A, 0x037E),
        (0x0384, 0x038A),
        (0x038C, 0x038C),
    ]
    alphabet = [
        chr(code_point)
        for start, end in include_ranges
        for code_point in range(start, end + 1)
    ]
    return random_str(alphabet, a, b, length)


def random_urlsafe(a=15, b=None, length=None):
    """Generate a random URL-safe string."""
    return random_str(URLSAFE_CHARS, a, b, length)


def random_number(a=99.999, b=None, int_chance=0.5):
    """Generate a random int or float."""
    a, b = _range_args(a, b)
    n = random.random() * (b - a) + a
    if random.random() < int_chance:
        return int(n)
    return n


def random_bool(p=0.5):
    """Generate a random bool."""
    return random.random() > p


def random_list(
    gen_func: Callable[[], Any] = None,
    min_len: int = 1,
    max_len: int = 5,
    depth: int = 0,
) -> list:
    r = []
    length = random.randint(min_len, max_len)

    for _ in range(length):
        if gen_func is None:
            if depth > 0:
                possible_types = GEN_TYPES_COMPOUND
                depth -= 1
            else:
                possible_types = GEN_TYPES_SIMPLE

            gen_type = random.sample(possible_types)
            gen_func = GEN_FUNCS[gen_type]

            if gen_type is GEN_TYPES.list:
                r.append(
                    gen_func(
                        gen_func=None,
                        min_len=min_len,
                        max_len=max_len,
                        depth=depth,
                    )
                )
            else:
                r.append(gen_func())
        else:
            r.append(gen_func)

    return r


def random_dict(
    key_gen: Callable[[], Any] = partial(random_ascii, 5, 10),
    value_gen: Optional[Callable[[], Any]] = None,
    min_len: int = 1,
    max_len: int = 5,
    depth: int = 0,
) -> dict:
    r = {}
    length = random.randint(min_len, max_len)

    for _ in range(length):
        key = key_gen()

        if value_gen is None:
            if depth > 0:
                possible_types = GEN_TYPES_COMPOUND
                depth -= 1
            else:
                possible_types = GEN_TYPES_SIMPLE

            gen_type = random.sample(possible_types)
            gen_func = GEN_FUNCS[gen_type]

            if gen_type is GEN_TYPES.dict:
                r[key] = gen_func(
                    key_gen=key_gen,
                    value_gen=value_gen,
                    min_len=min_len,
                    max_len=max_len,
                    depth=depth,
                )
            else:
                r[key] = gen_func()
        else:
            r[key] = value_gen()

    return r


GEN_TYPES_SIMPLE = AttrSeq("num", "str", "bool")
GEN_TYPES_COMPOUND = AttrSeq("list", "dict")
GEN_TYPES = AttrSeq(*GEN_TYPES_SIMPLE, *GEN_TYPES_COMPOUND,)
GEN_FUNCS = AttrMap(
    (GEN_TYPES.num, random_number),
    (GEN_TYPES.str, random_ascii),
    (GEN_TYPES.bool, random_bool),
    (GEN_TYPES.list, random_list),
    (GEN_TYPES.dict, random_dict),
)


def shuffled(seq):
    """Return a list with the contents of ``seq`` in random order."""
    return random.sample(seq, k=len(seq))
