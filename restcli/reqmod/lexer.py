import argparse
import string
from collections import namedtuple

import click
import six

from restcli.utils import AttrSeq

QUOTES = '"\''
ESCAPES = '\\'

ACTIONS = AttrSeq(
    'append',
    'assign',
    'delete',
)

Lexeme = namedtuple('Lexeme', ['action', 'value'])


class ClickArgumentParser(argparse.ArgumentParser):
    """Override `ArgumentParser#error()` to raise a `click.UsageError()`."""

    def error(self, message):
        raise click.UsageError(message)


lexer = ClickArgumentParser(prog='lexer', add_help=False)
lexer.add_argument('-a', '--{}'.format(ACTIONS.append), action='append')
lexer.add_argument('-n', '--{}'.format(ACTIONS.assign), action='append')
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete), action='append')
lexer.add_argument('args', nargs='*')


def lex(argv):
    """Lex an argv style sequence into a list of Lexemes.

    Args:
        argv: An iterable of strings.

    Returns:
        [ Lexeme(action, value) , ... ]

    Examples:
        >>> lex(('-a', 'foo:bar', '-d', 'baz==', 'a=b', 'x:=true'))
        [
            Lexeme(action='append', value='foo:bar'),
            Lexeme(action='delete', value='baz=='),
            Lexeme(action='assign', value='a=b'),
            Lexeme(action='assign', value='x:=true'),
        ]
    """
    opts = vars(lexer.parse_args(argv))
    args = opts.pop('args')
    # Lex flagged options
    lexemes = [
        Lexeme(action, val)
        for action, values in six.iteritems(opts)
        if values is not None
        for val in values
    ]
    # Lex short-form `ACTIONS.assign` args
    lexemes.extend(Lexeme(ACTIONS.assign, token) for token in args)
    return lexemes


def tokenize(s, sep=string.whitespace):
    """Split a string on whitespace.

    Whitespace can be present in a token if it is preceded by a backslash or
    contained within non-escaped quotations.

    Quotations can be present in a token if they are preceded by a backslash or
    contained within non-escaped quotations of a different kind.

    Args:
        s (str) - The string to tokenize.
        sep (str) - Character(s) to use as separators. Defaults to whitespace.

    Returns:
        A list of tokens.

    Examples:
        >>> tokenize('"Hello world!" I\ love \\\'Python programming!\\\'')
        ['Hello world!', 'I love', '\'Python', 'programming!\'']
    """
    tokens = []
    token = ''
    current_quote = None

    chars = iter(s)
    char = six.next(chars, '')

    while char:
        # Quotation marks begin or end a quoted section
        if char in QUOTES:
            if char == current_quote:
                current_quote = None
            elif not current_quote:
                current_quote = char

        # Backslash makes the following character literal
        elif char in ESCAPES:
            token += char
            char = six.next(chars, '')

        # Unless in quotes, whitespace is skipped and signifies the token end.
        elif not current_quote and char in sep:
            while char in sep:
                char = six.next(chars, '')
            tokens.append(token)
            token = ''

            # Since we stopped at the first non-whitespace character, it
            # must be processed.
            continue

        token += char
        char = six.next(chars, '')

    tokens.append(token)
    return tokens
