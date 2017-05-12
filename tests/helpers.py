import random
import string


def get_random_unicode(length):
    """Helper to generate a random Unicode string."""
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
    return ''.join(random.sample(alphabet, length))


def get_random_ascii(length):
    """Helper to generate a random ASCII string."""
    return ''.join(random.sample(string.printable, length))


def contents_equal(*seqs):
    """Return True if the contents of each sequence are equal.

    Specifically, this function checks that each sequence has the same length,
    and that each item in each sequence is equal to (==) exactly one item in
    every other sequence, regardless of ordering.
    """
    if len(seqs) < 2:
        raise TypeError('contents_equal expected at least 2 arguments,'
                        ' got %s' % (len(seqs)))

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
        for k, v in (d.items() for d in dicts)
        if (not include or k in include)
        or (not exclude or k not in exclude)
    )
    return contents_equal(*items)


def pick(mapping, keys):
    """Return a new dict using only the given keys."""
    return {k: v for k, v in mapping.items() if k in keys}


def getitems(mapping, items):
    """Iterate values from `mapping` in order of the given `items`."""
    return (mapping[item] for item in items)


def getattrs(obj, attrs):
    """Iterate values from 'obj' in order of the given `attrs`."""
    return (getattr(obj, attr) for attr in attrs)
