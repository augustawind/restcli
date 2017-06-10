import json
import re
from collections import namedtuple

from restcli.utils import AttrMap, AttrSeq, is_ascii

from .lexer import ESCAPES, QUOTES
from .updater import UPDATERS

VALID_URL_CHARS = (
    r'''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'''
    r'''0123456789-._~:/?#[]@!$&'()*+,;=`'''
)

ACTIONS = AttrSeq(
    'append',
    'assign',
    'delete',
)

# Regex patterns for each type of token (syntax).
PATTERNS = AttrMap(
    ('header', re.compile(r'^(.+):(.*)$')),
    ('json_field', re.compile(r'^(.+):=(.+)$')),
    ('str_field', re.compile(r'^(.+)=(.+)$')),
    ('url_param', re.compile(r'^(.+)==(.*)$')),
)


class FieldParser:

    def __init__(self, seq):
        self._data = str(seq)
        self._in_quotes = []
        self._escaping = False

    def consume(self, n=None):
        """Consume ``n`` characters.
        
        If ``n`` is None, consume all remaining characters.
        """
        if n is None:
            n += 1
        result = self._data[:n]
        self._data = ''
        return result

    def _startswith_any(self, charsets):
        for chars in charsets:
            if self._data.startswith(chars):
                return chars
        return None

    def consume_until(self, *charsets):
        first = []
        second = None
        for char in self._data:
            if char in ESCAPES:
                # If escape char, apply escaping rules
                if self._escaping:
                    # If escaping, ignore escape char and continue
                    self._escaping = False
                    continue
                else:
                    # Otherwise, escape next char
                    self._escaping = True

            elif self._escaping:
                # If not backslash and escaping, stop escaping
                self._escaping = False

            elif self._in_quotes:
                # If inside quotes, process char literally
                pass

            elif char in QUOTES:
                if self._in_quotes[-1] == char:
                    self._in_quotes.pop()
                else:
                    self._in_quotes.append(char)

            else:
                # If condition met, stop parsing
                second = self._startswith_any(charsets)
                if second:
                    break

            first.append(char)

        first = ''.join(first)
        index = len(first) + len(second)
        self._data = self._data[index:]
        return first, second
        #
        # def consume_until(self, *charsets):
        #     """Consume the token until a char is in one of ``charsets``."""
        #     return self.consume_with_predicate(lambda char: char in sentinel)
        #
        # def consume_while(self, *charsets):
        #     """Consume the token while chars are in one of ``charsets``."""
        #     return self.consume_with_predicate(lambda char: char not in sentinel)


def parse(tokens):
    """Parse a sequence of tokens with the override syntax."""
    results = []

    for token in tokens:
        parser = FieldParser(token)
        for field_type, spec in FIELD_SPECS.items():
            has_bang, key, has_plus, operator, value = parse_token(
                token, spec.delimiter)
            if not (key and operator):
                continue

            # Determine Action
            action = determine_action(has_bang, has_plus)

            # Instantiate Updater
            updater_cls = UPDATERS[action]

            # Parse parameters
            params = spec.formatter(key, value)
            updater = updater_cls(spec.field, *params)
            results.append(updater)
            break
        else:
            # TODO: refine error handling here
            raise Exception('Unexpected argument: `{}`'.format(tokens))

    return results


def parse_token(token, delimiter):
    has_bang = token.consume_char('!')
    key, has_plus = token.consume_until('+')
    operator = token.consume_until(delimiter)
    value = token.consume()
    return bool(has_bang), key, bool(has_plus), operator, value


def determine_action(has_bang, has_plus):
    if has_bang:
        return ACTIONS.delete
    elif has_plus:
        return ACTIONS.append
    else:
        return ACTIONS.assign


def fmt_url_param(key, value):
    """Parse a URL parameter."""
    assert all(char in VALID_URL_CHARS for char in key + value), (
        'Invalid char(s) found in URL parameter. Accepted chars are: {}'
        '\nAll other chars must be percent-encoded.'.format(VALID_URL_CHARS)
    )
    return key, value


def fmt_json_field(key, value):
    """Parse a fully qualified JSON field."""
    try:
        json_value = json.loads(value)
    except json.JSONDecodeError:
        # TODO: implement error handling
        raise
    return key, json_value


def fmt_str_field(key, value):
    """Parse a JSON field as a string."""
    return key, value


def fmt_header(key, value):
    """Parse a header value."""
    msg = "Non-ASCII character(s) found in header %(section) '%(text)'."
    assert is_ascii(str(key)), (msg % {'section': 'name', 'text': key})
    assert is_ascii(str(value)), (msg % {'section': 'value', 'text': value})
    return key, value
#
#
# def mkregex(delimiter):
#     return re.compile(
#         r'''
#         ^
#         (?P<bang> !?)       # 1) Bang "!" (optional).
#         (?P<q1> ["']?)      # 2) Start quote (optional).
#         (?(q1)              # 3) IFDEF start quote [2]:
#           (?P<name>         #     3.1) Field name.
#             [^%(del)s]      #          Must have at least 1 non-delimiter,
#               |             #          OR
#             (?:\\%(del)s)   #          at least 1 backslash-escaped delimiter.
#           )+?               #
#           (?P=q1)           #     3.2) End quote.
#             |               # 4) ELSE:
#           ([^!+%(del)s]+)   #     4.1) Field name.
#         )                   #          Do not match `!`, `+`, or delimiter.
#         (?(bang) $          # 5) IFDEF leading bang [1], finish match.
#             |               # 6) ELSE:
#           (\+?)             #    6.1) Plus sign "+" (optional).
#           %(del)s           #    6.2) Delimiter.
#           (?P<q2> ["']?)    #    6.3) Start quote (optional).
#           (.*?)             #    6.4) Field value (optional).
#           (?(q2) (?P=q2))   #    6.5) IFDEF start quote [6.3], end quote.
#           $
#         )
#         '''
#         % locals(), re.VERBOSE,
#     )


FieldSpec = namedtuple('FieldSpec', ('field', 'delimiter', 'formatter'))
FIELD_SPECS = AttrMap(
    ('header', FieldSpec('headers', ':', fmt_header)),
    ('json_field', FieldSpec('body', ':=', fmt_json_field)),
    ('str_field', FieldSpec('body', '=', fmt_str_field)),
    ('url_param', FieldSpec('query', '==', fmt_url_param)),
)

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
