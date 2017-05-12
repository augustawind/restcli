import argparse
import enum
from collections import OrderedDict, namedtuple

from restcli.utils import split_quoted


class ACTIONS(enum.Enum):
    append = 'append'
    assign = 'assign'
    delete = 'delete'


lexer = argparse.ArgumentParser(prog='lexer', add_help=False)
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete.value), action='append')
lexer.add_argument('-a', '--{}'.format(ACTIONS.append.value), action='append')

Node = namedtuple('Node', ['action', 'token'])


def lex(argument_str):
    """Lex a string into a sequence of (action, tokens) pairs."""
    argv = split_quoted(argument_str)
    opts, args = lexer.parse_known_args(argv)
    from pprint import pformat
    tokens = OrderedDict(
        Node(action=k, token=v)
        for k, v in vars(opts).items()
        if v is not None
    )
    if args:
        tokens[ACTIONS.assign.name] = split_quoted(' '.join(args))
    return tuple(tokens.items())
