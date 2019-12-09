import abc
from dataclasses import dataclass
from typing import Dict, List, Union

from restcli.exceptions import ReqModKeyError, ReqModValueError
from restcli.utils import AttrMap

JsonValue = Union[
    str, bool, int, float, List["JsonValue"], Dict[str, "JsonValue"]
]


class Updates(list):
    """Simple list wrapper that provides update utilities."""

    def apply(self, request):
        """Apply all updates to a Request object.

        Args:
            request (object): The Request object to update.
        """
        for updater in self:
            updater(request)


@dataclass
class Updater(metaclass=abc.ABCMeta):
    """Base class for callable objects that update Request Parameters.

    Args:
        request_param (str): The name of the Request Parameter to update.
        key (str): The key that will be updated within the Request Parameter.
        value: The new value.

    Notes:
        Child classes must implement the ``update_request`` method.
    """

    request_param: str
    key: str
    value: JsonValue

    def __call__(self, request):
        """Update a Request.

        This method dispatches to ``update_request`` to execute the update.

        Args:
            request (dict): The Request object.

        Returns:
            The updated value.
        """
        current_request_param = request[self.request_param]
        try:
            self.update_request(current_request_param)
        except KeyError:
            raise ReqModKeyError(value=self.key)
        except (TypeError, ValueError):
            raise ReqModValueError(value=self.value)

    @abc.abstractmethod
    def update_request(self, param_value):
        """Update a Request Parameter.

        Args:
            param_value: The value of the Request Parameter to update.

        Notes:
            Child classes must implement this method.
        """


class AppendUpdater(Updater):
    """Appends a value to a Request Parameter field."""

    def update_request(self, param_value):
        param_value[self.key] += self.value


class AssignUpdater(Updater):
    """Sets a new value in a Request Parameter field."""

    def update_request(self, param_value):
        param_value[self.key] = self.value


class DeleteUpdater(Updater):
    """Deletes a field in a Request Parameter."""

    def update_request(self, param_value):
        del param_value[self.key]


UPDATERS = AttrMap(
    ("append", AppendUpdater),
    ("assign", AssignUpdater),
    ("delete", DeleteUpdater),
)
