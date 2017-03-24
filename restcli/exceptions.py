from contextlib import contextmanager
from functools import wraps

import click

USAGE_ARGS = {
    'change_collection': 'COLLECTION_FILE',
    'change_env': 'ENV_FILE',
    'env': '[key0:val0] [key1:val1] .. [keyN:valN]',
    'view': 'GROUP [REQUEST] [ATTR]',
    'reload': '[collection | env]',
    'run': 'GROUP REQUEST',
    'save': '',
}

#
# def expect(*exceptions):
#     """Wrap a function to gracefully handle the given exception(s)."""
#     exceptions = tuple(exceptions)
#
#     def wrapper(func):
#         @wraps(func)
#         def wrapped(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except exceptions as exc:
#                 if exc.message:
#                     click.echo('{}: {}'.format(exc.action, exc.message))
#                 if exc.action:
#                     usage(exc.action)
#         return wrapped
#     return wrapper


@contextmanager
def expect(*exceptions):
    try:
        yield
    except exceptions as exc:
        lines = []

        if exc.file:
            line = exc.file
            if exc.path:
                line += ' => {}'.format(exc.path)
            lines.append(line)

        if exc.message:
            lines.append('{}{}'.format(
                '{}: '.format(exc.action) if exc.action else '',
                exc.message,
            ))

        raise click.ClickException('\n'.join(lines))


def usage(action):
    """Print usage info for the given command."""
    return 'Usage: restcli {} {}'.format(action, USAGE_ARGS[action])


class Error(Exception):
    """Base library exception."""

    def __init__(self, action=None, msg=None, traceback=None):
        self.action = action
        self.message = msg
        self.traceback = traceback


class InvalidInput(Error):
    """Exception for invalid user input."""
    message = 'Invalid input'


class NotFound(Error):
    """Exception for invalid lookups."""
    message = 'Not found'


class InvalidConfig(Error):
    """Exception for invalid config files."""
    message = 'Invalid config entry'

    def __init__(self, action=None, msg=None, file=None, path=None):
        super().__init__(action, msg)
        self.file = file
        self.path = path
