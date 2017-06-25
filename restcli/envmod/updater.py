import abc

import six

from restcli.utils import AttrMap


class Updates(list):
    """Simple list wrapper that provides update utilities."""

    def apply(self, request):
        """Apply all updates to a Request object.

        Args:
            request (object): The Request object to update.
        """
        for updater in self:
            updater(request)


class BaseUpdater(six.with_metaclass(abc.ABCMeta, object)):
    """Base class for callable objects that update Request Attributes.

    Args:
        request_attr (str): The name of the Request Attribute to update.
        key (str): The key that will be updated within the Request Attribute.
        value: The new value.

    Notes:
        Child classes must implement the ``update_request`` method.
    """

    def __init__(self, request_attr, key, value):
        self.request_attr = request_attr
        self.key = key
        self.value = value

    def __call__(self, request):
        """Update a Request.

        This method dispatches to ``update_request`` to execute the update.

        Args:
            request (dict): The Request object.

        Returns:
            The updated value.
        """
        current_request_attr = request[self.request_attr]
        self.update_request(current_request_attr)
        return current_request_attr[self.key]

    @abc.abstractmethod
    def update_request(self, request_attr):
        """Update a Request Attribute.

        Args:
            request_attr: The current value of the Request Attribute to update.

        Notes:
            Child classes must implement this method.
        """


class AppendUpdater(BaseUpdater):
    """Appends a value to a Request Attribute field."""

    def update_request(self, request_attr):
        request_attr[self.key] += self.value


class AssignUpdater(BaseUpdater):
    """Sets a new value in a Request Attribute field."""

    def update_request(self, request_attr):
        request_attr[self.key] = self.value


class DeleteUpdater(BaseUpdater):
    """Deletes a field in a Request Attribute."""

    def update_request(self, request_attr):
        del request_attr[self.key]


UPDATERS = AttrMap(
    ('append', AppendUpdater),
    ('assign', AssignUpdater),
    ('delete', DeleteUpdater),
)
