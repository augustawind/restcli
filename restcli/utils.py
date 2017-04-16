import re
import shlex
import string
from collections import Mapping
from typing import Iterable

QUOTES = '"\''
BACKSLASH = '\\'


def split_quoted(s, sep=string.whitespace):
    """Split a string on whitespace, respecting quotations (incl. escapes)."""
    words = []
    word = ''
    current_quote = None

    chars = iter(s)
    char = next(chars, '')

    while char:
        # Quotation marks begin or end a quoted section
        if char in QUOTES:
            if char == current_quote:
                current_quote = None
            elif not current_quote:
                current_quote = char

        # Backslash makes the following character literal
        elif char == BACKSLASH:
            word += char
            char = next(chars, '')

        # Unless in quotes, whitespace is skipped and signifies the word end.
        elif not current_quote and char in sep:
            while char in sep:
                char = next(chars, '')
            words.append(word)
            word = ''

            # Since we stopped at the first non-whitespace character, it
            # must be processed.
            continue

        word += char
        char = next(chars, '')

    words.append(word)
    return words


def recursive_update(mapping, *args, **kwargs):
    """Like dict.update, but recursively updates nested dicts as well."""
    mapping_cls = type(mapping)
    other_mapping = mapping_cls(*args, **kwargs)

    for key, val in other_mapping.items():
        if isinstance(val, Mapping):
            nested_mapping = mapping.setdefault(key, mapping_cls())
            recursive_update(nested_mapping, val.items())
        else:
            mapping[key] = val


def is_ascii(s):
    """Return True if the given string contains only ASCII characters."""
    return len(s) == len(s.encode())
