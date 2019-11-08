from collections import Mapping, OrderedDict, Sequence

import six

if six.PY3:
    from urllib.parse import quote_plus
else:
    from urllib import quote_plus


class AttrSeq(Sequence):
    """An immutable sequence that supports dot notation.

    Args:
        *args: Items to create the sequence from.
    """

    def __init__(self, *args):
        self._seq = args

    def __getattr__(self, item):
        return item

    def __getitem__(self, item):
        return self._seq[item]

    def __iter__(self):
        return iter(self._seq)

    def __len__(self):
        return len(self._seq)

    def __copy__(self):
        return self.__class__(*self._seq)

    copy = __copy__


class AttrMap(Mapping):
    """An immutable, ordered mapping that supports dot notation.

    Args:
        *pairs: 2-tuples to create the mapping from.
    """

    def __init__(self, *pairs):
        self._dict = OrderedDict(pairs)

    def __getitem__(self, item):
        return self._dict[item]

    __getattr__ = __getitem__

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __copy__(self):
        return self.__class__(*six.iteritems(self._dict))

    copy = __copy__


class MultiAttrMap(AttrMap):
    """Like AttrMap, but supports multiple keys for each value.

    Each key must be a tuple. When accessing attrs, any key in the tuple works.
    """

    def __init__(self, *pairs):
        expanded_pairs = []
        for multi_key, value in six.iteritems(pairs):
            if not isinstance(multi_key, tuple):
                raise TypeError(
                    "'%s' object is not an instance of tuple" % type(multi_key)
                )
            expanded_pairs.extend((key, value) for key in multi_key)

        super(MultiAttrMap, self).__init__(*expanded_pairs)


class classproperty:
    """Like the @property decorator but for class methods."""

    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


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


def select_first(*args):
    """Return the first argument that's not None."""
    for arg in args:
        if arg is not None:
            return arg
