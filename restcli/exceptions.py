from contextlib import contextmanager

import click

__all__ = [
    "expect",
    "Error",
    "InputError",
    "ReqModError",
    "ReqModSyntaxError",
    "ReqModValueError",
    "ReqModKeyError",
    "FileContentError",
    "NotFoundError",
    "GroupNotFoundError",
    "RequestNotFoundError",
    "ParameterNotFoundError",
    "CollectionError",
    "EnvError",
    "LibError",
]


@contextmanager
def expect(*exceptions):
    try:
        yield
    except exceptions as exc:
        raise click.ClickException(str(exc))


class Error(Exception):
    """Base library exception."""

    base_msg = ""

    def __init__(self, msg="", action=None):
        super().__init__(msg, action)
        # TODO: determine if `action` is still needed (I think no)
        self.action = action
        self.msg = msg

    def __str__(self):
        msg = self._fmt_label(self.base_msg, self.msg).format(**vars(self))
        if self.action:
            return self._fmt_label(self.action, msg)
        return msg

    @staticmethod
    def _fmt_label(first, second):
        return "{}{}".format(first, f": {second}" if second else "")

    @staticmethod
    def _is_custom_attr(attr):
        """Return whether an attr is a custom member of an Error instance."""
        return (
            not callable(attr)
            and attr != "args"
            and not (isinstance(attr, str) and attr.startswith("__"))
        )


class InputError(Error):
    """Exception for invalid user input."""

    base_msg = "Invalid input '{value}'"

    def __init__(self, value, msg="", action=None):
        super().__init__(msg, action)
        self.value = value


class ReqModError(InputError):
    """Invalid Mod input."""

    base_msg = "Invalid Request Modifier: '{value}'"


class ReqModSyntaxError(ReqModError):
    """Badly structured Mod input."""

    base_msg = "Syntax error in Request Modifier: '{value}'"


class ReqModValueError(ReqModError):
    """Badly formed Mod key or value."""


class ReqModKeyError(ReqModError):
    """Mod key does not exist."""

    base_msg = "Key does not exist: '{value}'"


class FileContentError(Error):
    """Exception for invalid file data."""

    base_msg = "Error in file"
    file_type = "content"

    def __init__(self, file="", msg="", path=None, action=None):
        super().__init__(msg, action)
        self.file = file
        self.path = path

    def __str__(self):
        s = f"{super().__str__()}\n{'':4}"
        if self.path:
            s += f"at {self._fmt_path()} "
        s += f"in {self.file_type.title()}"
        if self.file:
            s += f" <{self.file}>"
        return s

    @property
    def name(self):
        return self.path[-1]

    def _fmt_path(self):
        text = repr(self.path[0])
        for item in self.path[1:]:
            text += f".{repr(item)}"
        return text.replace("'", '"')


class NotFoundError(FileContentError):
    """Exception for invalid lookups."""

    base_msg = "Not found"


class CollectionError(FileContentError):
    """Exception for invalid Collection files."""

    file_type = "collection"
    base_msg = f"Error in {file_type.title()}"


class GroupNotFoundError(CollectionError):

    base_msg = "Group not found: '{name}'"


class RequestNotFoundError(CollectionError):

    base_msg = "Request not found: '{name}"


class ParameterNotFoundError(CollectionError):

    base_msg = "Parameter not found: '{name}'"


class EnvError(FileContentError):
    """Exception for invalid Env files."""

    file_type = "env"
    base_msg = f"Error in {file_type.title()}"


class LibError(FileContentError):
    """Exception for invalid Libs files."""

    file_type = "lib"
    base_msg = f"Invalid {file_type.title()}/s"
