import enum
import json
import re
from collections import OrderedDict

from restcli.utils import recursive_update, is_ascii

__all__ = ['parse']

odict = OrderedDict

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


def parse(lexemes, request):
    """Parse a sequence of lexemes with the override syntax."""
    result = odict()

    for action, tokens in lexemes:
        for token in tokens:
            for pattern in PATTERNS:
                match = pattern.value.match(token)

                if match:
                    # Obtain parameter key/value
                    key, value = match.groups()

                    # Obtain parser function
                    parser, request_attr = PATTERN_MAP[pattern]

                    # Parse parameter and update result
                    result = parser(action, key, value)
                    recursive_update(result, {request_attr: result})
                    break
            else:
                # TODO: refine error handling here
                raise Exception('Unexpected argument: `{}`'.format(tokens))

    return result


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


def fmt_arg(action, key, value):
    """Form token data into a common structure.."""
    return odict((
        (key, odict((
            (action, value),
        ))),
    ))


PATTERN_MAP = {
    PATTERNS.url_param: (parse_url_param, 'query'),
    PATTERNS.json_field: (parse_json_field, 'body'),
    PATTERNS.str_field: (parse_str_field, 'body'),
    PATTERNS.header: (parse_header, 'headers'),
}

examples = [
    # Set a header (:)
    '''Authorization:'JWT abc123\'''',
    # Delete a header (-d)
    '''-d Authorization:''',
    # Set a JSON param (string only) (=)
    '''description="A test Device."''',
    # Append (-a) to a url parameter (==)
    '''-a _annotate==,counts''',
    # Set a nested (.) JSON field (non-string) (:=)
    '''.location.postal_code:=33705''',
    # Set a nested (. / []) JSON field (string) (=)
    '''.conditions[0].variable=ambient_light''',
    # Delete (-d) a nested (.) JSON field
    '''-d .location.addr2''',
]
