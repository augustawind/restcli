import abc
import importlib
import inspect
from collections import Mapping, OrderedDict, UserDict

from restcli.exceptions import (
    CollectionError,
    EnvError,
    LibError,
    FileContentError,
)
from restcli import yaml_utils as yaml

__all__ = ['Collection', 'Environment']


class YamlDictReader(UserDict, metaclass=abc.ABCMeta):
    """Base class for dicts that read from YAML files."""

    error_class = FileContentError

    def __init__(self, file_path):
        super().__init__()
        self.file = file_path
        self.load()

    @abc.abstractmethod
    def load(self, path=None):
        pass

    def raise_error(self, msg, path, error_class=None, file=None,
                    **kwargs):
        """Helper for raising an error for a Reader instance."""
        if not error_class:
            error_class = self.error_class
        raise error_class(msg=msg, file=file or self.file, path=path, **kwargs)

    def assert_type(self, obj, type_, path, msg, error_class=error_class,
                    **err_kwargs):
        if not isinstance(obj, type_):
            self.raise_error(msg, path, error_class, **err_kwargs)

    def assert_mapping(self, obj, name, path, error_class=error_class,
                       **err_kwargs):
        msg = '%s must be a mapping object' % name
        self.assert_type(obj, Mapping, path, msg, error_class, **err_kwargs)


class Collection(YamlDictReader):

    error_class = CollectionError

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
            self.file = path

        if self.file:
            with open(self.file) as handle:
                data = yaml.load(handle, many=True)

            if len(data) == 1:
                meta, collection = {}, data[0]
            elif len(data) == 2:
                meta, collection = data
            else:
                if len(data) == 0:
                    msg = 'Collection document not found'
                else:
                    msg = 'Too many documents; expected 1 or 2'
                self.raise_error(msg, [])

            self._parse_collection(collection, meta)

    def _parse_lib(self, libs):
        self.assert_type(libs, list, ['lib'], '"lib" must be an array')
        self.libs = []
        for i, module in enumerate(libs):
            path = ['lib', i]
            try:
                assert type(module) is str
                lib = importlib.import_module(module)
            except (AssertionError, ImportError):
                self.raise_error('Failed to import lib "%s"' % module, path)
            try:
                assert hasattr(lib, 'define')
                assert inspect.isfunction(lib.define)
                sig = inspect.signature(lib.define)
                params = tuple(sig.parameters.values())
                assert len(params) == 4
                assert params[0].name == 'response'
                assert params[1].name == 'env'
                assert params[2].kind == inspect.Parameter.VAR_POSITIONAL
                assert params[3].kind == inspect.Parameter.VAR_KEYWORD
            except AssertionError:
                self.raise_error(
                    '"lib" modules must contain a function with the'
                    ' signature ``define(response, env, *args, **kwargs)``',
                    path,
                    file=inspect.getsourcefile(lib),
                )

            self.libs.append(lib)

    def _parse_collection(self, collection, meta):
        """Parse and validate a Collection and its Meta."""
        lib = meta.get('lib')
        if lib:
            self._parse_lib(lib)

        defaults = meta.get('defaults')
        if defaults:
            self.assert_mapping(
                defaults, 'Defaults', ['defaults'])
        else:
            defaults = {}

        new_collection = OrderedDict()
        for group_name, group in collection.items():
            path = [group_name]
            self.assert_mapping(group, 'Group', path)
            new_group = new_collection[group_name] = OrderedDict()

            for req_name, request in group.items():
                path.append('req_name')
                self.assert_mapping(request, 'Request', path)
                new_req = new_group[req_name] = OrderedDict()

                for key, type_ in self.REQ_ATTRS:
                    if key in request:
                        new_req[key] = request[key]
                    elif key in defaults:
                        new_req[key] = defaults[key]
                    # Check required attributes
                    elif key in self.REQUIRED_REQ_ATTRS:
                        self.raise_error(
                            'Required attribute "%s" not found' % key,
                            path,
                        )
                    else:
                        continue

                    # Check data type
                    path.append(key)
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
            self.file = path

        if self.file:
            with open(self.file) as handle:
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
        with open(self.file, 'w') as handle:
            return yaml.dump(self.data, handle)
