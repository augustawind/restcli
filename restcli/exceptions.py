import inspect
from contextlib import contextmanager

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

    def __init__(self, msg='', action=None):
        self.action = action
        self.msg = msg

    def show(self):
        msg = '%(base_msg)s%(msg)s' % {
            'base_msg': self._fmt_label(self.base_msg),
            'msg': self.msg,
        }
        return '%(action)s%(msg)s' % {
            'action': self._fmt_label(self.action),
            'msg': msg % self._attr_dict(),
        }

    @staticmethod
    def _fmt_label(text):
        return '%s: ' % (text,) if text else ''

    @staticmethod
    def _is_custom_attr(attr):
        """Return whether an attr is a custom member of an Error instance."""
        return (
            not callable(attr)
            and attr != 'args'
            and not (type(attr) is str and attr.startswith('__'))
        )

    def _attr_dict(self):
        return dict(inspect.getmembers(self, self._is_custom_attr))


class InputError(Error):
    """Exception for invalid user input."""

    base_msg = "Invalid input '%(input)s'"

    def __init__(self, line, item, msg='', action=None):
        super().__init__(msg, action)
        self.line = line
        self.item = item


class FileContentError(Error):
    """Exception for invalid file data."""

    base_msg = 'Invalid content'
    file_type = 'CONTENT'

    def __init__(self, file, msg='', path=None, action=None):
        super().__init__(msg, action)
        self.file = file
        self.path = path

    def show(self):
        line = self.file
        if self.path:
            line += ' => {}'.format(self._fmt_path(self.path))
        return '{}\n{}'.format(line, super().show())

    @property
    def name(self):
        return self.path[-1]

    def _fmt_path(self, path):
        text = ''
        for item in path:
            if type(item) is str:
                text += '.{}'.format(item)
            else:
                text += '[{}]'.format(item)
        return '{}{}'.format(self.file_type, text)


class NotFoundError(FileContentError):
    """Exception for invalid lookups."""

    base_msg = 'Not found'


class GroupNotFoundError(NotFoundError):

    base_msg = "Group '%(name)s' not found"


class RequestNotFoundError(NotFoundError):

    base_msg = "Request '%(name)s' not found"


class AttributeNotFoundError(NotFoundError):

    base_msg = "Attribute '%(name)s' not found"


class CollectionError(FileContentError):
    """Exception for invalid Collection files."""

    base_msg = 'Invalid collection'
    file_type = 'COLLECTION'


class EnvError(FileContentError):
    """Exception for invalid Env files."""

    base_msg = 'Invalid env'
    file_type = 'ENV'


class LibError(FileContentError):
    """Exception for invalid Libs files."""

    base_msg = 'Invalid lib(s)'
    file_type = 'LIB'
