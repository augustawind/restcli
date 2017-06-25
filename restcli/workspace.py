import abc
import importlib
import inspect
from collections import Mapping, OrderedDict

import six

from restcli import yaml_utils as yaml
from restcli.exceptions import (
    CollectionError,
    EnvError,
    LibError,
    FileContentError,
)
from restcli.params import REQUIRED_REQUEST_PARAMS, REQUEST_PARAMS, CONFIG_PARAMS

__all__ = ['Collection', 'Environment']


class YamlDictReader(six.with_metaclass(abc.ABCMeta, OrderedDict)):
    """Base class for dicts that read from YAML files."""

    error_class = FileContentError

    def __init__(self, source):
        super(YamlDictReader, self).__init__()
        self.source = source
        self.load()

    @abc.abstractmethod
    def load(self):
        pass

    def copy(self):
        """Override copy() so that ``source`` can be copied over."""
        return self.__class__(self.source)

    def raise_error(self, msg, path, error_class=None, source=None, **kwargs):
        """Helper for raising an error for a Reader instance."""
        if not error_class:
            error_class = self.error_class
        raise error_class(file=source or self.source, msg=msg, path=path,
                          **kwargs)

    def assert_type(self, obj, type_, path, msg, error_class=None,
                    **err_kwargs):
        if not isinstance(obj, type_):
            self.raise_error(msg, path, error_class or self.error_class,
                             **err_kwargs)

    def assert_mapping(self, obj, name, path, error_class=None, **err_kwargs):
        msg = '%s must be a mapping object' % name
        self.assert_type(obj, Mapping, path, msg, error_class, **err_kwargs)


class Collection(YamlDictReader):
    """A Collection reader and parser."""

    error_class = CollectionError

    def __init__(self, source):
        self.defaults = {}
        self.libs = []
        super(Collection, self).__init__(source)

    def load(self):
        """Reload the current Collection, changing it to ``path`` if given."""
        if self.source:
            with open(self.source) as handle:
                data = yaml.load(handle, many=True)

            if len(data) == 1:
                config, collection = {}, data[0]
            elif len(data) == 2:
                config, collection = data
            else:
                if len(data) == 0:
                    msg = 'Collection document not found'
                else:
                    msg = 'Too many documents; expected 1 or 2'
                self.raise_error(msg, [])

            self.load_config(config)
            self.load_collection(collection)

    def load_config(self, config):
        """Parse and validate Collection Config."""
        # Verify all fields are known
        for key in six.iterkeys(config):
            if key not in CONFIG_PARAMS:
                self.raise_error(
                    'Unexpected key in config: "{}"'.format(key), [])

        # Load libs
        lib = config.get('lib')
        if lib:
            self.libs = Libs(lib)

        # Load defaults
        defaults = config.get('defaults', OrderedDict())

        if defaults:
            path = ['defaults']
            self.assert_mapping(defaults, 'Defaults', path)

            for key in six.iterkeys(defaults):
                if key not in REQUEST_PARAMS:
                    self.raise_error(
                        'Unexpected key in defaults "{}"'.format(key), path)

            self.defaults.clear()
            self.defaults.update(defaults)

    def load_collection(self, collection):
        """Parse and validate a Collection."""
        new_collection = OrderedDict()
        for group_name, group in six.iteritems(collection):
            path = [group_name]
            self.assert_mapping(group, 'Group', path)
            new_group = OrderedDict()

            for req_name, request in six.iteritems(group):
                path.append('req_name')
                self.assert_mapping(request, 'Request', path)
                new_req = OrderedDict()

                for key, type_ in six.iteritems(REQUEST_PARAMS):
                    if key in request:
                        new_req[key] = request[key]
                    elif key in self.defaults:
                        new_req[key] = self.defaults[key]
                    # Check required parameters
                    elif key in REQUIRED_REQUEST_PARAMS:
                        self.raise_error(
                            'Required parameter "%s" not found' % key,
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

                new_group[req_name] = new_req
            new_collection[group_name] = new_group

        self.clear()
        self.update(new_collection)


class Environment(YamlDictReader):
    """An Env reader and parser."""

    error_class = EnvError

    def load(self):
        """Reload the current Environment, changing it to ``path`` if given."""
        if self.source:
            with open(self.source) as handle:
                env = yaml.load(handle)
                self.clear()
                self.update(env)

    def remove(self, *args):
        """Remove each of the given vars from the Environment."""
        for var in args:
            try:
                del self[var]
            except KeyError:
                pass

    def save(self):
        """Save ``self.env`` to ``self.env_path``."""
        with open(self.source, 'w') as handle:
            return yaml.dump(OrderedDict(self), handle)


class Libs(YamlDictReader):
    """A Libs reader and parser."""

    error_class = LibError

    def load(self):
        """Parse and validate a Libs list."""
        self.assert_type(self.source, list, ['lib'], '"lib" must be an array')
        for i, module in enumerate(self.source):
            path = ['lib', i]
            try:
                assert type(module) is str
                lib = importlib.import_module(module)
            except (AssertionError, ImportError):
                self.raise_error('Failed to import lib "%s"' % module, path,
                                 source=inspect.getsourcefile(module))
            try:
                assert hasattr(lib, 'define')
                assert inspect.isfunction(lib.define)
                sig = inspect.signature(lib.define)
                params = tuple(six.itervalues(sig.parameters))
                assert len(params) == 4
                assert params[0].name == 'response'
                assert params[1].name == 'env'
                assert params[2].kind == inspect.Parameter.VAR_POSITIONAL
                assert params[3].kind == inspect.Parameter.VAR_KEYWORD
            except AssertionError:
                self.raise_error(
                    'lib must contain a function with the signature'
                    ' `define(response, env, *args, **kwargs)`',
                    path,
                    error_class=LibError,
                    source=inspect.getsourcefile(lib),
                )

            self[module] = lib
