import cmd
from functools import wraps

from restcli.exceptions import InvalidInput, NotFound

USAGE_ARGS = {
    'change_collection': 'COLLECTION_FILE',
    'change_env': 'ENV_FILE',
    'env': '[key0:val0] [key1:val1] .. [keyN:valN]',
    'view': 'GROUP [REQUEST] [ATTR]',
    'reload': '[collection | env]',
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

    prompt = '> '
    intro = (
        'restcli 0.1\n'
        'Type "help" for more information.\n'
    )

    def __init__(self, app):
        super().__init__()
        self.app = app

    def output(self, msg):
        if msg:
            print(msg, file=self.stdout)

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
        args = self.parse_args('run', line, 2)
        output = self.app.run(*args)
        self.output(output)

    @expect(InvalidInput, NotFound)
    def do_view(self, line):
        """Inspect a Group, Request, or Attribute."""
        args = self.parse_args('view', line, 1, 3)
        output = self.app.view(*args)
        self.output(output)

    @expect(InvalidInput)
    def do_env(self, line):
        """Display the current Environment, or set env vars."""
        args = self.parse_args('env', line)
        if not args:
            self.output(self.app.show_env())
            return

        output = self.app.set_env(*args)
        self.output(output)

    @expect(InvalidInput)
    def do_reload(self, line):
        "Reload the Collection and/or Environment from disk."
        args = line.split()
        options = ('collection', 'env')
        if not args:
            args = options
        elif not all(o in options for o in args):
            raise InvalidInput(action='reload')

        output = ''
        if 'collection' in args:
            output += self.app.load_collection()
        if 'env' in args:
            output += self.app.load_env()
        self.output(output)

    def do_save(self, line):
        """Save the current environment to disk."""
        output = self.app.save_env()
        self.output(output)

    @expect(InvalidInput)
    def do_change_collection(self, line):
        """Set and load a new Collection file."""
        args = self.parse_args('set_collection', line, 1, 1)
        path = args[0]
        output = self.app.load_collection(path)
        self.output(output)

    @expect(InvalidInput)
    def do_change_env(self, line):
        """Set and load a new Environment file."""
        args = self.parse_args('set_env', line, 1, 1)
        path = args[0]
        output = self.app.load_env(path)
        self.output(output)

    def do_quit(self, line):
        """Quit the program."""
        return True
