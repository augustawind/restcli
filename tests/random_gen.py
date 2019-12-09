import random
import string
from functools import partial
from typing import Any, Callable, Mapping, Optional, Sequence

from restcli.utils import AttrMap, AttrSeq

ALPHANUMERIC_CHARS = string.ascii_letters + string.digits
ASCII_CHARS = ALPHANUMERIC_CHARS + string.punctuation
URLSAFE_CHARS = ALPHANUMERIC_CHARS + "_.-"


def _range_args(a, b=None):
    if b is None:
        return 0, a
    return a, b


def _len(a, b, min_len=1):
    a, b = _range_args(a, b)
    return max(min_len, random.randint(a, b))


def string(population, a=15, b=None, length=None):
    length = length or _len(a, b, min_len=3)
    k = min(length, len(population))
    return "".join(random.sample(population, k))


def alphanum(a=15, b=None, length=None):
    """Generate a random alphanumeric ASCII string."""
    return string(ALPHANUMERIC_CHARS, a, b, length)


def ascii(a=15, b=None, length=None):
    """Generate a random ASCII string."""
    return string(ASCII_CHARS, a, b, length)


def unicode(a=15, b=None, length=None):
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
    return string(alphabet, a, b, length)


def urlsafe(a=15, b=None, length=None):
    """Generate a random URL-safe string."""
    return string(URLSAFE_CHARS, a, b, length)


def number(a=99.999, b=None, int_chance=0.5):
    """Generate a random int or float."""
    a, b = _range_args(a, b)
    n = random.random() * (b - a) + a
    if random.random() < int_chance:
        return int(n)
    return n


def boolean(p=0.5):
    """Generate a random bool."""
    return random.random() > p


def sequence(
    gen_item: Callable[[], Any] = None,
    min_len: int = 1,
    max_len: int = 5,
    depth: int = 0,
    cls: Callable[[list], Sequence] = list,
) -> Sequence:
    r = []
    length = random.randint(min_len, max_len)

    for _ in range(length):
        if gen_item is None:
            if depth > 0:
                possible_types = GEN_TYPES_COMPOUND
                depth -= 1
            else:
                possible_types = GEN_TYPES_SIMPLE

            gen_type = random.sample(possible_types)
            gen_item = GEN_FUNCS[gen_type]

            if gen_type is GEN_TYPES.list:
                r.append(
                    gen_item(
                        gen_item=None,
                        min_len=min_len,
                        max_len=max_len,
                        depth=depth,
                    )
                )
            else:
                r.append(gen_item())
        else:
            r.append(gen_item())

    return cls(r)


def mapping(
    gen_key: Callable[[], Any] = partial(ascii, 5, 10),
    gen_value: Optional[Callable[[], Any]] = None,
    min_len: int = 1,
    max_len: int = 5,
    depth: int = 0,
    cls: Callable[[dict], Mapping] = dict,
) -> Mapping:
    r = {}
    length = random.randint(min_len, max_len)

    for _ in range(length):
        key = gen_key()

        if gen_value is None:
            if depth > 0:
                possible_types = GEN_TYPES_COMPOUND
                depth -= 1
            else:
                possible_types = GEN_TYPES_SIMPLE

            gen_type = random.sample(possible_types)
            gen_value = GEN_FUNCS[gen_type]

            if gen_type is GEN_TYPES.dict:
                r[key] = gen_value(
                    gen_key=gen_key,
                    gen_value=None,
                    min_len=min_len,
                    max_len=max_len,
                    depth=depth,
                )
            else:
                r[key] = gen_value(depth=depth)
        else:
            r[key] = gen_value()

    return cls(r)


GEN_TYPES_SIMPLE = AttrSeq("num", "str", "bool")
GEN_TYPES_COMPOUND = AttrSeq("list", "dict")
GEN_TYPES = AttrSeq(*GEN_TYPES_SIMPLE, *GEN_TYPES_COMPOUND,)
GEN_FUNCS = AttrMap(
    (GEN_TYPES.num, number),
    (GEN_TYPES.str, ascii),
    (GEN_TYPES.bool, boolean),
    (GEN_TYPES.list, sequence),
    (GEN_TYPES.dict, mapping),
)


def shuffled(seq):
    """Return a list with the contents of ``seq`` in random order."""
    return random.sample(seq, k=len(seq))
