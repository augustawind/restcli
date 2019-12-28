from __future__ import annotations

import abc
import importlib
import inspect
from collections import OrderedDict
from collections.abc import Mapping
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from requests import Response

from restcli import yaml_utils as yaml
from restcli.exceptions import (
    CollectionError,
    EnvError,
    FileContentError,
    LibError,
)
from restcli.params import (
    CONFIG_PARAMS,
    REQUEST_PARAMS,
    REQUIRED_REQUEST_PARAMS,
)

__all__ = ["Document", "Collection", "Environment", "GroupType", "RequestType"]

# NOTE: these are OrderedDict, but Dict is necessary for type subscriptions
RequestType = Dict[str, Any]
GroupType = Dict[str, RequestType]


class Document(OrderedDict, metaclass=abc.ABCMeta):
    """Base class for dicts that read from YAML files."""

    error_class = FileContentError

    def __init__(
        self, source: Optional[str] = None, data: Optional[dict] = None
    ):
        super().__init__()

        if data:
            self.import_data(data)

        self.source = source
        self.load()

    @abc.abstractmethod
    def import_data(self, data: Dict[str, Any]):
        """Validate and process raw data to add to the Document."""

    @abc.abstractmethod
    def export_data(self) -> Any:
        """Return a primitive representation of the Document.

        The object returned should be suitable for serialization of the
        Document back into YAML.
        """

    @abc.abstractmethod
    def read(self) -> Optional[OrderedDict]:
        """Read document data from :attr:`source`.

        This should simply read the raw data and return it; use
        :method:`import_data` for data validation and processing.
        """

    def load(self):
        """Load and import latest data from :attr:`source`."""
        data = self.read()
        if data:
            self.import_data(data)

    def reload(self):
        """Like :method:`load`, but clears existing data first."""
        self.clear()
        self.load()

    def dump(self, **kwargs) -> str:
        """Return a YAML-encoded str representation of the Document."""
        return yaml.dump(OrderedDict(self), **kwargs)

    def copy(self) -> Document:
        """Override copy() so that ``source`` can be copied over."""
        return type(self)(self.source)

    def error(
        self, msg, path, error_class=None, source=None, **kwargs
    ) -> Exception:
        """Helper for raising an error for a Reader instance."""
        if not error_class:
            error_class = self.error_class
        return error_class(
            file=source or self.source, msg=msg, path=path, **kwargs
        )

    def assert_type(
        self, obj, type_, path, msg, error_class=None, **err_kwargs
    ):
        if not isinstance(obj, type_):
            raise self.error(
                msg, path, error_class or self.error_class, **err_kwargs
            )

    def assert_mapping(self, obj, name, path, error_class=None, **err_kwargs):
        msg = f"{name} must be a mapping object"
        self.assert_type(obj, Mapping, path, msg, error_class, **err_kwargs)


class Collection(Document):
    """A Collection reader and parser."""

    error_class = CollectionError

    def __init__(
        self, source: Optional[str] = None, data: Optional[dict] = None
    ):
        self.defaults = {}
        self.libs = []
        super().__init__(source, data=data)

    def import_data(self, data: Dict[str, Any]):
        """Import Collection data."""
        new_collection = OrderedDict()
        for group_name, group in data.items():
            path = [group_name]
            self.assert_mapping(group, "Group", path)
            new_group = OrderedDict()

            for req_name, request in group.items():
                path.append("req_name")
                self.assert_mapping(request, "Request", path)
                new_req = OrderedDict()

                for key, type_ in REQUEST_PARAMS.items():
                    if key in request:
                        new_req[key] = request[key]
                    elif key in self.defaults:
                        new_req[key] = self.defaults[key]
                    # Check required parameters
                    elif key in REQUIRED_REQUEST_PARAMS:
                        raise self.error(
                            f'Required parameter "{key}" not found', path
                        )
                    else:
                        new_req[key] = type_()
                        continue

                    # Check type
                    path.append(key)
                    self.assert_type(
                        obj=new_req[key],
                        type_=type_,
                        path=path,
                        msg=f'Request "{key}" must be a {type_.__name__}',
                    )

                new_group[req_name] = new_req
            new_collection[group_name] = new_group

        self.update(new_collection)

    def export_data(self) -> OrderedDict:
        data = OrderedDict()
        for group_name, group in self.items():
            data[group_name] = OrderedDict()
            for req_name, request in group.items():
                data[group_name][req_name] = OrderedDict(
                    (key, request[key]) for key in REQUEST_PARAMS
                )
        return data

    def read(self) -> Optional[OrderedDict]:
        """Read Collection data from :attr:`source`."""
        if self.source:
            with open(self.source) as handle:
                data = yaml.load(handle, many=True)

            if len(data) == 1:
                config, collection = {}, data[0]
            elif len(data) == 2:
                config, collection = data
            else:
                if len(data) == 0:
                    msg = "Collection document not found"
                else:
                    msg = "Too many documents; expected 1 or 2"
                raise self.error(msg, [])

            self.load_config(config)
            return collection

    def load_config(self, config):
        """Parse and validate Collection Config."""
        # Verify all fields are known
        for key in config.keys():
            if key not in CONFIG_PARAMS:
                raise self.error(f'Unexpected key in config: "{key}"', [])

        # Load libs
        lib = config.get("lib")
        if lib:
            self.libs = Libs(lib)

        # Load defaults
        defaults = config.get("defaults", OrderedDict())

        if defaults:
            path = ["defaults"]
            self.assert_mapping(defaults, "Defaults", path)

            for key in defaults.keys():
                if key not in REQUEST_PARAMS:
                    raise self.error(
                        f'Unexpected key in defaults "{key}"', path
                    )

            self.defaults.clear()
            self.defaults.update(defaults)

    def save(self):
        config = OrderedDict(
            [("defaults", self.defaults), ("lib", self.libs.export_data())]
        )
        collection = self.export_data()
        with open(self.source, "w") as handle:
            yaml.dump([config, collection], handle, many=True)


class Environment(Document):
    """An Env reader and parser."""

    error_class = EnvError

    def import_data(self, data: Dict[str, Any]):
        self.update(data)

    def export_data(self) -> OrderedDict:
        return deepcopy(OrderedDict(self))

    def read(self) -> Optional[OrderedDict]:
        """Read Environment data from :attr:`source`."""
        if self.source:
            with open(self.source) as handle:
                data = yaml.load(handle)

            return data

    def remove(self, *args):
        """Remove each of the given vars from the Environment."""
        for var in args:
            try:
                del self[var]
            except KeyError:
                pass

    def save(self):
        """Save ``self.env`` to ``self.env_path``."""
        with open(self.source, "w") as handle:
            return yaml.dump(self.export_data(), handle)


if TYPE_CHECKING:

    class LibType:
        define: Callable[[Response, Environment, ...], Dict[str, Any]]


class Libs(Document):
    """A Libs reader and parser."""

    error_class = LibError

    def import_data(self, data: Dict[str, LibType]):
        """Validate and import a mapping of names to lib objects.

        When called from :method:`load`, this will be a mapping of
        module names to modules. Otherwise, ``data`` can be any mapping
        of strings to objects that implement the Lib interface.
        """
        for module, lib in data.items():
            path = ["lib", module]
            sig = inspect.signature(lib.define)
            params = tuple(sig.parameters.values())
            if not all(
                (
                    hasattr(lib, "define"),
                    inspect.isfunction(lib.define),
                    len(params) == 4,
                    params[0].name == "response",
                    params[1].name == "env",
                    params[2].kind == inspect.Parameter.VAR_POSITIONAL,
                    params[3].kind == inspect.Parameter.VAR_KEYWORD,
                )
            ):
                raise self.error(
                    "lib must contain a function with the signature"
                    " `define(response, env, *args, **kwargs)`",
                    path,
                    source=inspect.getsourcefile(lib),
                )

            self[module] = lib

    def export_data(self) -> List[str]:
        return list(self.keys())

    def read(self) -> OrderedDict:
        """Read Libs data from :attr:`source`."""
        self.assert_type(self.source, list, ["lib"], '"lib" must be an array')

        data = OrderedDict()
        for i, module in enumerate(self.source):
            path = ["lib", i]
            try:
                if not isinstance(module, str):
                    raise TypeError
                data[module] = importlib.import_module(module)
            except (TypeError, ImportError):
                raise self.error(
                    f'Failed to import lib "{module}"',
                    path,
                    source=inspect.getsourcefile(module),
                )

        return data
