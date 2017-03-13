import cmd
from functools import wraps

from restcli.app import App
from restcli.exceptions import InvalidInput, NotFound

USAGE_INFO = {
    'run': 'Usage: run GROUP REQUEST',
    'inspect': 'Usage: inspect GROUP [REQUEST [ATTR]]',
    'set_env': 'Usage: set_env ENV_FILE',
    'set_collection': 'Usage: set_collection COLLECTION_FILE',
    'reload': 'Usage: reload [collection, env]',
}


def usage(action):
    """Print usage info for the given command."""
    print(USAGE_INFO[action])


def expect(*exceptions):
    """Wrap a function to gracefully handle the given exception(s)."""
    exceptions = tuple(exceptions)
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as exc:
                if exc.message:
                    print('restcli: {}: {}'.format(exc.action, exc.message))
                if exc.action:
                    usage(exc.action)
        return wrapped
    return wrapper


def nargs(min, max=None):
    """Wrap a function to accept a certain number of arguments."""
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            count = len(args) + len(kwargs)
            if count < min or (max and count > max):
                raise InvalidInput(action=func.__name__)
            return func(*args, **kwargs)
        return wrapped
    return wrapper


class Cmd(cmd.Cmd):
    """Interactive command prompt for restcli."""

    def __init__(self, groups_file, env_file=None):
        super().__init__()
        self.app = App(groups_file, env_file, self.stdout)

    @staticmethod
    def parse_args(action, line, min_args, max_args=None):
        """Utility to parse input and validate the number of args given."""
        args = line.split()
        n = len(args)
        if n < min_args or (max_args and n > max_args):
            raise InvalidInput(action=action)
        return args

    @expect(InvalidInput, NotFound)
    def do_run(self, line):
        """Run an HTTP request."""
        args = self.parse_args('run', line, 2, 2)
        self.app.run(*args)

    @expect(InvalidInput, NotFound)
    def do_inspect(self, line):
        """Inspect a Group, Request, or Attribute."""
        args = self.parse_args('inspect', line, 1, 3)
        self.app.inspect(*args)

    def do_env(self, line):
        """Display the current environment."""
        self.app.print_env()

    @expect(InvalidInput)
    def do_reload(self, line):
        "Reload the Collection and/or Environment from disk."
        args = line.split()
        options = ('collection', 'env')
        if not args:
            args = options
        elif not all(o in options for o in args):
            raise InvalidInput(action='reload')

        if 'collection' in args:
            self.app.load_collection()
        if 'env' in args:
            self.app.load_env()

    def do_save(self, line):
        """Save the current environment to disk."""
        self.app.save_env()

    @expect(InvalidInput)
    def do_set_collection(self, line):
        """Set and load a new Collection file."""
        args = self.parse_args('set_collection', line, 1, 1)
        path = args[0]
        self.app.load_collection(path)

    @expect(InvalidInput)
    def do_set_env(self, line):
        """Set and load a new Environment file."""
        args = self.parse_args('set_env', line, 1, 1)
        path = args[0]
        self.app.load_env(path)

    def do_quit(self, line):
        """Quit the program."""
        return True
