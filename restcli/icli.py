import cmd
import re
from functools import wraps

import yaml

from restcli.app import App
from restcli.exceptions import InvalidInput, NotFound

ENV_RE = re.compile(r'([^:]+):(.*)')

USAGE_ARGS = {
    'change_collection': 'COLLECTION_FILE',
    'change_env': 'ENV_FILE',
    'env': '[ENV0 [ENV1 ... [ENVn]]]',
    'inspect': 'GROUP [REQUEST [ATTR]]',
    'reload': '[collection, env]',
    'run': 'GROUP REQUEST',
}


def usage(action):
    """Print usage info for the given command."""
    print('Usage: {} {}'.format(action, USAGE_ARGS[action]))


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


class Cmd(cmd.Cmd):
    """Interactive command prompt for restcli."""

    def __init__(self, groups_file, env_file=None):
        super().__init__()
        self.app = App(groups_file, env_file, self.stdout)

    @staticmethod
    def parse_args(action, line, min_args=None, max_args=None):
        """Utility to parse input and validate the number of args given."""
        args = line.split()
        n = len(args)
        if (min_args and n < min_args) or (max_args and n > max_args):
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
        """Display the current Environment, or set env vars."""
        args = self.parse_args('env', line)
        if not args:
            self.app.print_env()
            return

        env = {}
        for arg in args:
            match = ENV_RE.match(arg)
            if not match:
                raise InvalidInput(
                    action='env',
                    message='Error: args must take the form `key:value`, where'
                            ' `key` is a string and `value` is a valid YAML'
                            ' value.',
                )
            key, val = match.groups()
            env[key] = yaml.safe_load(val)

        self.app.save_env(**env)

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
    def do_change_collection(self, line):
        """Set and load a new Collection file."""
        args = self.parse_args('set_collection', line, 1, 1)
        path = args[0]
        self.app.load_collection(path)

    @expect(InvalidInput)
    def do_change_env(self, line):
        """Set and load a new Environment file."""
        args = self.parse_args('set_env', line, 1, 1)
        path = args[0]
        self.app.load_env(path)

    def do_quit(self, line):
        """Quit the program."""
        return True
