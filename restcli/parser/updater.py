import abc

import six


def update(request, updaters):
    """Update the given request, given an iterable of BaseUpdater instances."""
    for updater in updaters:
        updater(request)


class BaseUpdater(six.with_metaclass(abc.ABCMeta, object)):
    """Base class for callable objects that update Request Attributes."""

    action = None

    def __init__(self, attr, key, value=None):
        self.request_field = attr
        self.key = key
        self.value = value

    def __call__(self, request):
        request_attr = request[self.request_field]
        self.update(request_attr)
        return request_attr[self.key]

    @abc.abstractmethod
    def update(self, request_attr):
        pass


class AppendUpdater(BaseUpdater):
    """Appends to a field in a Request Attribute."""

    def update(self, request_attr):
        request_attr[self.key] += self.value


class AssignUpdater(BaseUpdater):
    """Sets a field in a Request Attribute."""

    def update(self, request_attr):
        request_attr[self.key] = self.value


class DeleteUpdater(BaseUpdater):
    """Deletes a field in a Request Attribute."""

    def update(self, request_attr):
        del request_attr[self.key]


UPDATERS = {
    'append': AppendUpdater,
    'assign': AssignUpdater,
    'delete': DeleteUpdater,
}
