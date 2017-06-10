import argparse
import string
from collections import OrderedDict

import six

from restcli.utils import AttrSeq


QUOTES = '"\''
ESCAPES = '\\'

ACTIONS = AttrSeq(
    'append',
    'assign',
    'delete',
)

lexer = argparse.ArgumentParser(prog='lexer', add_help=False)
lexer.add_argument('-a', '--{}'.format(ACTIONS.append), action='append')
lexer.add_argument('-n', '--{}'.format(ACTIONS.assign), action='append')
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete), action='append')


def lex(argument_str):
    """Lex a string into a sequence of (action, tokens) pairs.
    
    Args:
        argument_str: The string to lex.
        
    Returns:
        A list of (action, token) pairs.
    """
    argv = tokenize(argument_str)
    opts, args = lexer.parse_known_args(argv)
    opts = ((k, v) for k, v in six.iteritems(vars(opts)) if v is not None)
    nodes = [
        (action, val) for action, values in opts
        for val in values
    ]
    if args:
        assign_tokens = tokenize(' '.join(args))
        nodes.extend((ACTIONS.assign, token) for token in assign_tokens)
    return nodes


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
    char = next(chars, '')

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
            char = next(chars, '')

        # Unless in quotes, whitespace is skipped and signifies the token end.
        elif not current_quote and char in sep:
            while char in sep:
                char = next(chars, '')
            tokens.append(token)
            token = ''

            # Since we stopped at the first non-whitespace character, it
            # must be processed.
            continue

        token += char
        char = next(chars, '')

    tokens.append(token)
    return tokens
