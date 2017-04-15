import argparse
import enum
import shlex


class ACTIONS(enum.Enum):
    """Actions that can be applied to tokens."""
    assign = 'assign'
    delete = 'delete'
    append = 'append'


lexer = argparse.ArgumentParser(add_help=False)
lexer.add_argument('-d', '--{}'.format(ACTIONS.delete.name), action='append')
lexer.add_argument('-a', '--{}'.format(ACTIONS.append.name), action='append')


def lex(argument_str):
    """Lex a string into a sequence of (action, token) pairs."""
    opts, args = lexer.parse_known_args(argument_str.split())
    tokens = vars(opts)
    tokens[ACTIONS.assign.name] = shlex.split(' '.join(args))
    return tuple(tokens.items())
