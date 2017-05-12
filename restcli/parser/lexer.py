import argparse
import enum
from collections import OrderedDict, namedtuple

from restcli.utils import split_quoted


class ACTIONS(enum.Enum):
    """Actions that can be applied to tokens."""
    assign = 'assign'
    delete = 'delete'
    append = 'append'


lexer = argparse.ArgumentParser(add_help=False)
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete.name), action='append')
lexer.add_argument('-a', '--{}'.format(ACTIONS.append.name), action='append')

Node = namedtuple('Node', ['action', 'token'])


def lex(argument_str):
    """Lex a string into a sequence of (action, tokens) pairs."""
    argv = split_quoted(argument_str)
    opts, args = lexer.parse_known_args(argv)
    tokens = OrderedDict(
        Node(action=ACTIONS[k], token=v)
        for k, v in vars(opts).items()
        if v is not None
    )
    tokens[ACTIONS.assign] = split_quoted(' '.join(args))
    return tuple(tokens.items())
