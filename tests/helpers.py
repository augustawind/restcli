import random
import string

import six

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


def _random_str(population, a=15, b=None, length=None):
    length = length or _random_len(a, b, min_len=3)
    k = min(length, len(population))
    return "".join(random.sample(population, k))


def random_alphanum(a=15, b=None, length=None):
    """Generate a random alphanumeric ASCII string."""
    return _random_str(ALPHANUMERIC_CHARS, a, b, length)


def random_ascii(a=15, b=None, length=None):
    """Generate a random ASCII string."""
    return _random_str(ASCII_CHARS, a, b, length)


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
        for current_range in include_ranges
        for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return _random_str(alphabet, a, b, length)


def random_urlsafe(a=15, b=None, length=None):
    """Generate a random URL-safe string."""
    return _random_str(URLSAFE_CHARS, a, b, length)


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


def _random_iter(
    a=5, b=None, length=None, dict_kwargs=None, list_kwargs=None, max_depth=2
):
    length = length or _random_len(a, b)

    dict_kwargs = dict_kwargs or {}
    list_kwargs = list_kwargs or {}

    # Iterate evenly through types but in random order
    for i in random.sample(range(length), length):
        # Get generate func and any args to pass through
        if max_depth > 0:
            types = GEN_TYPES_COMPOUND
        else:
            types = GEN_TYPES_SIMPLE
        gen_type = types[i % len(types)]
        gen_func = GEN_FUNCS[gen_type]

        # If generating a child list, use same params
        if gen_type == GEN_TYPES.list:
            max_depth -= 1
            gen_kwargs = dict(
                **list_kwargs, dict_kwargs=dict_kwargs, max_depth=max_depth
            )
        # If generating other compound type, give params for its child lists
        elif gen_type == GEN_TYPES.dict:
            max_depth -= 1
            gen_kwargs = dict(
                **dict_kwargs, list_kwargs=list_kwargs, max_depth=max_depth
            )
        # TODO: implement passing args for other types
        else:
            gen_kwargs = {}

        yield gen_func(**gen_kwargs)


def random_list(a=5, b=None, length=None, dict_kwargs=None, max_depth=2):
    """Generate a random list."""
    list_kwargs = dict(a=a, b=b, length=length)
    return list(
        _random_iter(a, b, length, dict_kwargs, list_kwargs, max_depth)
    )


def random_dict(
    a=5,
    b=None,
    length=None,
    key_min=1,
    key_max=5,
    list_kwargs=None,
    max_depth=2,
):
    """Generate a random dict."""
    length = length or _random_len(a, b)

    dict_kwargs = dict(
        a=a, b=b, length=length, key_min=key_min, key_max=key_max
    )

    gen_str = GEN_FUNCS.str
    return {
        gen_str(key_min, key_max): value
        for value in _random_iter(
            a, b, length, dict_kwargs, list_kwargs, max_depth
        )
    }


GEN_TYPES_SIMPLE = AttrSeq("num", "str", "bool",)
GEN_TYPES_COMPOUND = AttrSeq("list", "dict",)
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


def contents_equal(*seqs):
    """Return True if the contents of each sequence are equal.

    Specifically, this function checks that each sequence has the same length,
    and that each item in each sequence is equal to (==) exactly one item in
    every other sequence, regardless of ordering.
    """
    if len(seqs) < 2:
        raise TypeError(
            "contents_equal expected at least 2 arguments,"
            " got %s" % (len(seqs))
        )

    head = seqs[0]
    tail = seqs[1:]
    prev_len = len(head)

    for seq in tail:
        # Check that each sequence has the same length
        next_len = len(seq)
        if next_len != prev_len:
            return False
        prev_len = next_len

        # Check that each sequence has the same contents
        for x in seq:
            for y in head:
                if x == y:
                    break
            else:
                return False

    return True


def dicts_equal(*dicts, include=None, exclude=None):
    """Like `contents_equal`, but compares both keys and values of each dict.

    Args:
        dicts: Two or more dicts to compare.
        include: A subset of keys to use, ignoring others.
        exclude: A subset of keys to ignore.

    `include` and `exclude` are mutually exclusive and cannot both be given.

    Returns:
        True or False depending on the outcome of the comparison.
    """
    assert not (include and exclude)
    # if include:
    #     dicts = [{k: v for k, v in dict_ if k in include}
    #              for dict_ in dicts]
    # elif exclude:
    #     dicts = [{k: v for k, v in dict_ if k not in exclude}
    #              for dict_ in dicts]
    items = (
        (k, v)
        for k, v in (six.iteritems(d) for d in dicts)
        if (not include or k in include) or (not exclude or k not in exclude)
    )
    return contents_equal(*items)


def pick(mapping, keys):
    """Return a new dict using only the given keys."""
    return {k: v for k, v in six.iteritems(mapping) if k in keys}


def items_list(mapping, items):
    """Return a list of values from `mapping` in order of the given `items`."""
    return [mapping[item] for item in items]


def attrs_list(obj, attrs):
    """Return a list of values from 'obj' in order of the given `attrs`."""
    return [getattr(obj, attr) for attr in attrs]
