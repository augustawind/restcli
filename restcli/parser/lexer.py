import argparse
import enum
import shlex
from collections import OrderedDict

from restcli import utils


class ACTIONS(enum.Enum):
    """Actions that can be applied to tokens."""
    assign = 'assign'
    delete = 'delete'
    append = 'append'


lexer = argparse.ArgumentParser(add_help=False)
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete.name), action='append')
lexer.add_argument('-a', '--{}'.format(ACTIONS.append.name), action='append')


def lex(argument_str):
    """Lex a string into a sequence of (action, tokens) pairs."""
    argv = utils.split_quoted(argument_str)
    opts, args = lexer.parse_known_args(argv)
    tokens = OrderedDict((ACTIONS[k], v) for k, v in vars(opts).items())
    tokens[ACTIONS.assign] = shlex.split(' '.join(args))
    return tuple(tokens.items())
