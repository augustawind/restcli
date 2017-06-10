import json
from collections import deque, namedtuple

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

FieldSpec = namedtuple('FieldSpec', ('field', 'delimiter', 'formatter'))


def parse(nodes):
    """Parse a sequence of ``Node``s with the override syntax.
    
    Args:
        nodes: An iterable of ``Node`` objects.
        
    Returns:
        A list of ``Updater`` objects.
    """
    results = []

    for node in nodes:
        for field_type, spec in FIELD_SPECS.items():
            key, operator, value = parse_node(node.value, spec.delimiter)
            if not (key and operator):
                continue

            # Instantiate Updater
            updater_cls = UPDATERS[node.action]

            # Parse parameters
            key, value = spec.formatter(key, value)
            updater = updater_cls(spec.field, key, value)
            results.append(updater)
            break
        else:
            # TODO: refine error handling here
            raise Exception('Unexpected argument: `{}`'.format(nodes))

    return results


def parse_node(node, delimiter):
    """Parse an individual ``Node`` value."""
    parser = NodeParser(node)
    key, operator = parser.consume_until(delimiter)
    value = parser.consume()
    return key, operator, value


class NodeParser:
    """Parser class for Nodes that provides generic tools for parsing.
    
    Args:
        value (str): The value being parsed.
    """

    def __init__(self, value):
        self._data = str(value)
        self._start_quotes = deque()
        self._escape_next = False

    def _startswith_any(self, *charsets):
        for chars in charsets:
            if self._data.startswith(chars):
                return chars
        return ''

    def consume(self, n=None):
        """Consume ``n`` characters.
        
        Args:
            n (int): The number of chars to consume. If n is None,
                consume all remaining characters.
                
        Returns:
            The chars that were consumed.
        """
        result = self._data[n:]
        self._data = ''
        return result

    def consume_chars(self, *charsets):
        """Consume a specific sequence of characters.
        
        Args:
            *charsets: Any number of character sequences (strings) to try, 
                in order. The first string that matches will be consumed.
                
        Returns:
            The chars that were consumed.
        """
        result = self._startswith_any(*charsets)
        if result is not None:
            index = len(result)
            self._data = self._data[index:]
        return result

    def consume_until(self, *charsets):
        """Consume characters until one of the given strings is found.
        
        Args:
            *charsets: Any number of character sequences (strings) to try, 
                in order. The first string that matches will be consumed.
                
        Returns:
            A 2-tuple of the chars consumed before the match, and the charset
            that did match. Note that this consumes the matching charset.
        """
        first = []
        second = ''
        for char in self._data:
            if char in ESCAPES:
                # If escape char, apply escaping rules
                if self._escape_next:
                    # If escaping, ignore escape char and continue
                    self._escape_next = False
                    continue
                else:
                    # Otherwise, escape next char
                    self._escape_next = True

            elif self._escape_next:
                # If not backslash and escaping, stop escaping
                self._escape_next = False

            elif self._start_quotes:
                # If inside quotes, process char literally
                pass

            elif char in QUOTES:
                if self._start_quotes and self._start_quotes[-1] == char:
                    self._start_quotes.pop()
                else:
                    self._start_quotes.append(char)

            else:
                # If condition met, stop parsing
                second = self._startswith_any(*charsets)
                if second:
                    break

            first.append(char)

        first = ''.join(first)
        index = len(first) + len(second)
        self._data = self._data[index:]
        return first, second


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
