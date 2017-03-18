class Error(Exception):
    """Base library exception."""

    def __init__(self, action=None, message=None):
        if action:
            self.action = action
        if message:
            self.message = message


class InvalidInput(Error):
    """Exception for invalid user input."""
    message = 'Invalid input'


class NotFound(Error):
    """Exception for invalid lookups."""
    message = 'Not found'


class InvalidConfig(Error):
    """Exception for invalid config files."""
    message = 'Invalid config entry'

    def __init__(self, action=None, message=None, file=None, path=None):
        super().__init__(action, message)
        self.file = file
        self.path = path
