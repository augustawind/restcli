import json
from collections import namedtuple, deque

from restcli.envmod.mods import Mod
from restcli.envmod.lexer import ESCAPES, QUOTES

from restcli.envmod.mods import MOD_TYPES
from restcli.envmod.updater import UPDATERS, Updates

VALID_URL_CHARS = (
    r'''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'''
    r'''0123456789-._~:/?#[]@!$&'()*+,;=`'''
)


def parse(lexemes):
    """Parse a sequence of Lexemes.

    Args:
        lexemes: An iterable of Lexeme objects.

    Returns:
        An Updates object that can be used to update Requests.
    """
    updates = Updates()

    for lexeme in lexemes:
        for mod_cls in MOD_TYPES:
            mod = mod_cls(action=lexeme.action, mod_str=lexeme.value)
            if not (key and operator):
                continue

            # Format Mod params
            key, value = mod_type.formatter(key, value)

            # Create Updaters
            updater_cls = UPDATERS[lexeme.action]
            updater = updater_cls(mod_type.field, key, value)
            updates.append(updater)
            break
        else:
            # TODO: refine error handling here
            raise Exception('Unexpected argument: `{}`'.format(lexemes))

    return updates


def parse_mod(lexeme, delimiter):
    """Parse a Modifier.

    Args:
        lexeme (str): The Mod string to parse.
        delimiter (str): The operator to split on.

    Returns:
        Mod(key, operator, value)
    """
    parser = ModParser(lexeme)
    key, operator = parser.consume_until(delimiter)
    value = parser.consume()
    return Mod(key=key, operator=operator, value=value)


class ModParser:
    """Wrapper for Modifiers that provides generic tools for parsing.

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

    # TODO: combine this with lexer.tokenize
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
