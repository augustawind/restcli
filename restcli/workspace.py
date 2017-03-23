import abc
import importlib
from collections import Mapping, OrderedDict, UserDict

from restcli.exceptions import InvalidConfig
from restcli import yaml_utils as yaml

__all__ = ['Collection', 'Environment']


class YamlDictReader(UserDict, metaclass=abc.ABCMeta):
    """Base class for dicts that read from YAML files."""

    def __init__(self, file_path):
        super().__init__()
        self._file = file_path
        self.load()

    @abc.abstractmethod
    def load(self, path=None):
        pass

    def assert_type(self, obj, type_, path, msg):
        if not isinstance(obj, type_):
            raise InvalidConfig(
                message=msg, file=self._file, path=path)

    def assert_mapping(self, obj, name, path):
        msg = '%s must be a mapping object' % name
        self.assert_type(obj, Mapping, path, msg)


class Collection(YamlDictReader):

    REQUIRED_REQ_ATTRS = (
        ('method', str),
        ('url', str)
    )
    REQ_ATTRS = REQUIRED_REQ_ATTRS + (
        ('headers', dict),
        ('body', str),
        ('script', str)
    )

    META_ATTRS = ('defaults', 'pre_run')

    def __init__(self, file_path):
        self.libs = []
        super().__init__(file_path)

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
                    message='Collection can have at most two documents',
                    file=self._file,
                    path='Collection',
                )

            self._parse_collection(collection, meta)

    def _parse_lib(self, libs):
        self.assert_type(libs, list, 'Collection::Meta(lib)',
                         msg='Meta "lib" must be an array')
        self.libs = []
        for path in libs:
            try:
                lib = importlib.import_module(path)
            except ImportError:
                raise InvalidConfig(
                    message='Failed to import lib "%s"' % path,
                    path='Collection::Meta(lib)',
                    file=self._file,
                )
            else:
                self.libs.append(lib)

    def _parse_collection(self, collection, meta):
        """Parse and validate a Collection and its Meta."""
        lib = meta.get('lib')
        if lib:
            self._parse_lib(lib)

        defaults = meta.get('defaults')
        if defaults:
            self.assert_mapping(
                defaults, 'Defaults', 'Collection::Meta(defaults)')
        else:
            defaults = {}

        new_collection = OrderedDict()
        for group_name, group in collection.items():
            path = 'Collection::Group(%s)' % group_name
            self.assert_mapping(group, 'Group', path)
            new_group = new_collection[group_name] = OrderedDict()

            for req_name, request in group.items():
                path += '.Request(%s)' % req_name
                self.assert_mapping(request, 'Request', path)
                new_req = new_group[req_name] = OrderedDict()

                for key, type_ in self.REQ_ATTRS:
                    if key in request:
                        new_req[key] = request[key]
                    elif key in defaults:
                        new_req[key] = defaults[key]
                    # Check required attributes
                    elif key in self.REQUIRED_REQ_ATTRS:
                        raise InvalidConfig(
                            file=self._file,
                            path=path,
                            message='Required attribute "%s" not found' % key,
                        )
                    else:
                        continue

                    # Check data type
                    path += '.Attribute(%s)' % key
                    self.assert_type(
                        obj=new_req[key],
                        type_=type_,
                        path=path,
                        msg='Request "%s" must be a %s'
                            % (key, type_.__name__),
                    )

        self.data = new_collection


class Environment(YamlDictReader):

    def load(self, path=None):
        """Reload the current Environment, changing it to ``path`` if given."""
        if path:
            self._file = path

        if self._file:
            with open(self._file) as handle:
                env = yaml.load(handle)
                self.clear()
                self.update(env)

    def remove(self, *args):
        """Remove each of the given vars from the Environment."""
        for var in args:
            try:
                del self.data[var]
            except KeyError:
                pass

    def save(self):
        """Save ``self.env`` to ``self.env_path``."""
        with open(self._file, 'w') as handle:
            return yaml.dump(self.data, handle)
