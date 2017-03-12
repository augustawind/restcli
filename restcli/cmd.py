import cmd

from restcli.app import App


class Cmd(cmd.Cmd):

    def __init__(self, groups_file=None, env_file=None):
        super().__init__()
        self.app = App(groups_file, env_file, self.stdout)

    def do_save(self, arg):
        """Save the current environment to disk."""
        self.app.save()

    def do_reload(self, arg):
        "Reload the Collection and/or Environment from disk."
        files = set(arg.split())
        if not all(f in ('env', 'collection') for f in files):
            self.app.usage('reload', 'Bad argument')
            return

        if 'collection' in files:
            self.app.r.load_collection()
        if 'env' in files:
            self.app.r.load_env()

    def do_set_env(self, arg):
        """Set and load a new Environment file."""
        args = arg.split()
        if len(args) != 1:
            self.app.usage('set_env', 'Missing argument')
            return

        path = args[0]
        self.app.r.load_env(path)

    def do_set_collection(self, arg):
        args = arg.split()
        if len(args) != 1:
            self.app.usage('set_collection', 'Missing argument')
            return

        path = args[0]
        self.app.r.load_collection(path)

    def do_inspect(self, arg):
        """Inspect a Group, Request, or Attribute."""
        args = arg.split()
        if len(args) == 0:
            self.app.usage('inspect', 'Invalid input.')
        if len(args) > 3:
            self.app.usage('inspect', 'Invalid input.')

        self.inspect(*args)

    def do_run(self, arg):
        """Run an HTTP request."""
        args = arg.split()
        if len(args) != 2:
            return self.app.usage('run', 'Invalid input.')

        self.app.run(*args)

    def do_env(self, arg):
        """Display the current environment."""
        self.app.print_env()
