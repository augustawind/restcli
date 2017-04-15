import argparse
import enum
import json
import re
import shlex
from collections import Mapping, OrderedDict

VALID_URL_CHARS = (
    r'''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'''
    r'''0123456789-._~:/?#[]@!$&'()*+,;=`'''
)


class PATTERNS(enum.Enum):
    """Regex patterns for each type of token (syntax)."""
    url_param = re.compile(r'^(.+)==(.*)$')
    json_field = re.compile(r'^(.+):=(.+)$')
    str_field = re.compile(r'^(.+)=(.+)$')
    header = re.compile(r'^(.+):(.*)$')


class ACTIONS(enum.Enum):
    """Actions that can be applied to tokens."""
    assign = 'assign'
    delete = 'delete'
    append = 'append'


lexer = argparse.ArgumentParser(add_help=False)
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete), action='append')
lexer.add_argument('-a', '--{}'.format(ACTIONS.append), action='append')


def lex(argument_str):
    """Lex a string into a sequence of (action, token) pairs."""
    opts, args = lexer.parse_known_args(argument_str.split())
    tokens = vars(opts)
    tokens[ACTIONS.assign] = args
    return tuple(tokens.items())


def parse_overrides(tokens, request):
    """Parse a sequence of tokens with the override syntax."""
    overrides = OrderedDict()

    for action, token in tokens:
        for pattern in PATTERNS:
            match = pattern.value.match(token)

            if match:
                # Obtain parameter key/value using shell-like syntax
                # TODO: verify that `shlex.split` returns a single-item list
                key, value = (shlex.split(g, posix=True)[0]
                              for g in match.groups())

                # Obtain parser function
                parser, request_attr = PATTERN_MAP[pattern.name]

                # Parse parameter and update result
                result = parser(action, key, value)
                recursive_update(overrides, (request_attr, result))

                break
        else:
            raise Exception('Unexpected argument: `{}`'.format(token))


def parse_url_param(action, key, value):
    """Parse a URL parameter."""
    assert all(char in VALID_URL_CHARS for char in key + value), (
        'Invalid char(s) found in URL parameter. Accepted chars are: {}'
        '\nAll other chars must be percent-encoded.'.format(VALID_URL_CHARS)
    )
    return fmt_arg(action, key, value)


def parse_json_field(action, key, value):
    """Parse a fully qualified JSON field."""
    try:
        json_value = json.loads(value)
    except json.JSONDecodeError:
        # TODO: implement error handling
        raise

    return fmt_arg(action, key, json_value)


def parse_str_field(action, key, value):
    """Parse a JSON field as a string."""
    return fmt_arg(action, key, value)


def parse_header(action, key, value):
    """Parse a header value."""
    assert is_ascii(key + value), (
        'Invalid char(s) found in header. Only ASCII chars are supported.'
    )
    return fmt_arg(action, key, value)


PATTERN_MAP = {
    PATTERNS.url_param.name: (parse_url_param, 'query'),
    PATTERNS.json_field.name: (parse_json_field, 'body'),
    PATTERNS.str_field.name: (parse_str_field, 'body'),
    PATTERNS.header.name: (parse_header, 'headers'),
}


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


examples = [
    '''Authorization:'JWT abc123''',         # Set a header (:)
    '''-d Authorization:''',                 # Delete a header (-d)
    '''description="A test Device."''',      # Set a JSON param (string only) (=)
    '''-a _annotate==,counts''',             # Append (-a) to a url parameter (==)
    '''.location.postal_code:=33705''',      # Set a nested (.) JSON field (non-string) (:=)
    '''.conditions[0].variable=ambient_light''',  # Set a nested (. / []) JSON field (string) (=)
    '''-d .location.addr2''',                # Delete (-d) a nested (.) JSON field
]
