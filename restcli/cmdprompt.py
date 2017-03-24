import cmd

import click

from restcli.exceptions import InvalidInput, NotFound, expect
from restcli.version import VERSION


class Cmd(cmd.Cmd):
    """Interactive command prompt for restcli."""

    identchars = cmd.Cmd.identchars + '-'
    prompt = '> '
    intro = (
        'restcli %s\n'
        'Type "help" for more information.\n' % VERSION
    )

    def __init__(self, app, stdout=None):
        super().__init__(stdout=stdout)
        self.app = app

    @staticmethod
    def output(msg):
        if msg:
            _, height = click.get_terminal_size()
            if len(msg.splitlines()) > height - 3:
                click.echo_via_pager(msg)
            else:
                click.echo(msg)

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
