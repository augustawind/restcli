import re
import shlex
import string
from collections import deque, Mapping, OrderedDict


def shlex_token(s, **kwargs):
    """Do a `shlex.split` but return a single string instead of a list.
    
    This is basically abusing `shlex.split` for its quoting and escaping logic.
    """
    words = re.split(r'(\s+)', s)
    for i, word in enumerate(words):
        if any(char not in string.whitespace for char in word):
            words[i] = ''.join(shlex.split(word))
    return ''.join(words)


def split_quoted(s, sep=string.whitespace):
    """Split a string on whitespace, respecting quotations (incl. escapes)."""
    words = []
    open_quotes = deque()

    chars = iter(s)
    char = next(chars, None)

    while char:
        word = ''

        # Skip past whitespace (if not quoted), then finish the word
        if char in sep and not open_quotes:
            while char in sep:
                char = next(chars, None)
            words.append(word)
            word = ''
            continue

        # Unconditionally add anything after a backslash
        if char == '\\':
            word += char
            word += next(chars, '')

        if char in ('"', "'"):
            if open_quotes and char == open_quotes[0]:
                open_quotes.popleft()
            else:
                open_quotes.appendleft(char)
            word += char

        char = next(chars)


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


def fmt_arg(action, key, value):
    """Form token data into a common structure.."""
    return OrderedDict((
        (key, OrderedDict((
            (action, value),
        ))),
    ))
