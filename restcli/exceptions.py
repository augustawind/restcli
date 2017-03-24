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
        raise click.ClickException(exc.show())


def usage(action):
    """Print usage info for the given command."""
    return 'Usage: restcli {} {}'.format(action, USAGE_ARGS[action])


class Error(Exception):
    """Base library exception."""

    base_msg = ''

    def __init__(self, msg, action=None, traceback=None):
        self.action = action
        self.msg = msg
        self.traceback = traceback

    def show(self):
        return '{action}{base_msg}{msg}'.format(
            action=self._fmt_label(self.action),
            base_msg=self._fmt_label(self.base_msg),
            msg=self.msg,
        )

    @staticmethod
    def _fmt_label(text):
        return '{}: '.format(text) if text else ''


class InputError(Error):
    """Exception for invalid user input."""

    base_msg = 'Invalid input'


class NotFoundError(Error):
    """Exception for invalid lookups."""

    base_msg = 'Not found'


class FileContentError(Error):
    """Exception for invalid file data."""

    base_msg = 'Invalid content'

    def __init__(self, msg, file, path=None, action=None, traceback=None):
        super().__init__(msg, action)
        self.file = file
        self.path = path

    def show(self):
        line = self.file
        if self.path:
            line += ' => {}'.format(self._fmt_path(self.path))
        return '{}\n{}'.format(line, super().show())

    @staticmethod
    def _fmt_path(path):
        text = ''
        for item in path:
            if type(item) is str:
                text += '.{}'.format(item)
            else:
                text += '[{}]'.format(item)
        return text.lstrip('.')
