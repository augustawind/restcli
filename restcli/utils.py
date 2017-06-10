from collections import Mapping, OrderedDict, Sequence

import six


class AttrSeq(Sequence):
    """An immutable sequence that supports dot and bracket notation."""

    def __init__(self, *args):
        self._dict = {x: x for x in args}

    def __copy__(self):
        return self.__class__(*self._dict.keys())

    def __getattr__(self, item):
        return self._dict[item]

    __getitem__ = __getattr__

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)


class AttrMap(Mapping):
    """An immutable, ordered mapping that supports dot and bracket notation.
    
    A ``name`` attr is also added to each value which returns the key of that
    value.
    """

    def __init__(self, *pairs):
        self._dict = OrderedDict(pairs)

    def __copy__(self):
        return self.__class__(*self._dict.items())

    def __getattr__(self, item):
        return self._dict[item]

    __getitem__ = __getattr__

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)


def recursive_update(mapping, data):
    """Like dict.update, but recursively updates nested dicts as well."""
    for key, val in six.iteritems(data):
        if isinstance(val, Mapping):
            if key in mapping:
                recursive_update(mapping[key], val)
            else:
                mapping[key] = val
        else:
            mapping[key] = val


def is_ascii(s):
    """Return True if the given string contains only ASCII characters."""
    return len(s) == len(s.encode())
