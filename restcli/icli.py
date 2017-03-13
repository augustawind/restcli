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

    @expect(InvalidInput, NotFound)
    def do_run(self, arg):
        """Run an HTTP request."""
        args = arg.split()
        if len(args) != 2:
            raise InvalidInput(action='run')

        self.app.run(*args)

    @expect(InvalidInput, NotFound)
    def do_inspect(self, arg):
        """Inspect a Group, Request, or Attribute."""
        args = arg.split()
        if len(args) == 0:
            raise InvalidInput(action='inspect')
        if len(args) > 3:
            raise InvalidInput(action='inspect')

        self.app.inspect(*args)

    def do_env(self, arg):
        """Display the current environment."""
        self.app.print_env()

    @expect(InvalidInput)
    def do_reload(self, arg):
        "Reload the Collection and/or Environment from disk."
        files = set(arg.split())
        if not all(f in ('env', 'collection') for f in files):
            raise InvalidInput(action='reload')

        if 'collection' in files:
            self.app.load_collection()
        if 'env' in files:
            self.app.load_env()

    def do_save(self, arg):
        """Save the current environment to disk."""
        self.app.save_env()

    @expect(InvalidInput)
    def do_set_collection(self, arg):
        args = arg.split()
        if len(args) != 1:
            raise InvalidInput(action='set_collection')

        path = args[0]
        self.app.load_collection(path)

    @expect(InvalidInput)
    def do_set_env(self, arg):
        """Set and load a new Environment file."""
        args = arg.split()
        if len(args) != 1:
            raise InvalidInput(action='set_env')

        path = args[0]
        self.app.load_env(path)
