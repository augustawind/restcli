class Error(Exception):
    """Base library exception."""

    def __init__(self, action=None, message=None):
        self.action = action
        self.message = message


class InvalidInput(Error):
    """Exception for invalid user input."""
    message = 'Invalid input'


class NotFound(Error):
    """Exception for invalid lookups."""
    message = 'Not found'
