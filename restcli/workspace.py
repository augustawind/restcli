from collections import Mapping, UserDict

from restcli.exceptions import InvalidConfig
from restcli import yaml_utils as yaml


class YamlFileMixin:

    def assert_type(self, obj, type_, msg, path):
        if not isinstance(obj, type_):
            raise InvalidConfig(
                message=msg, file=self._file, path=path)

    def assert_mapping(self, obj, name, path):
        msg = '%s must be a mapping object' % name
        self.assert_type(obj, Mapping, msg, path)


class Collection(YamlFileMixin, UserDict):

    REQUIRED_REQ_ATTRS = ('method', 'url')
    REQ_ATTRS = REQUIRED_REQ_ATTRS + ('headers', 'body', 'script')

    def __init__(self, collection_file):
        super().__init__()
        self._file = collection_file
        self.load()

    def load(self, path=None):
        """Reload the current Collection, changing it to ``path`` if given."""
        if path:
            self._file = path

        if self._file:
            with open(self._file) as handle:
                data = yaml.load(handle, many=True)

            if len(data) == 1:
                meta, collection = {}, data[0]
            elif len(data) == 2:
                meta, collection = data
            else:
                raise InvalidConfig(
                    message='Collection can have at most two documents')

            self._parse_collection(collection, meta)
            self.data = collection

    def _parse_collection(self, collection, meta):
        """Apply Collection Meta to a Collection. Mutates ``collection``."""
        defaults = meta.get('defaults')
        if defaults:
            self.assert_mapping(defaults, 'Defaults', 'Meta.Defaults')
        else:
            defaults = {}

        for group_name, group in collection.items():
            path = 'Collection."%s"' % group_name
            self.assert_mapping(group, 'Group', path)
            for req_name, request in group.items():
                path += '."%s"' % req_name
                self.assert_mapping(request, 'Request', path)
                for key in self.REQ_ATTRS:
                    if key not in request and key in defaults:
                        request[key] = defaults[key]
                    self._validate_request(request, group_name, req_name)

    def _validate_request(self, request, group_name, request_name):
        path = 'Collection."%s"."%s"' % (group_name, request_name)

        for attr in self.REQUIRED_REQ_ATTRS:
            if attr not in request:
                raise InvalidConfig(
                    file=self._file,
                    path=path,
                    message='Required attribute "%s" not found' % attr,
                )

        headers = request.get('headers')
        if headers:
            self.assert_mapping(headers, 'Request headers', path)
