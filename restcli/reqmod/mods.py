import abc
import json
import re
import string

from restcli.exceptions import ReqModSyntaxError, ReqModValueError
from restcli.utils import AttrMap, AttrSeq, classproperty, is_ascii, quote_plus

PARAM_TYPES = AttrSeq("json_field", "str_field", "header", "url_param",)


def parse_mod(mod_str):
    """Attempt to parse a str into a Mod."""
    for mod_cls in MODS.values():
        try:
            mod = mod_cls.match(mod_str)
        except ReqModSyntaxError:
            continue
        return mod
    raise ReqModSyntaxError(value=mod_str)


class Mod(metaclass=abc.ABCMeta):

    param_type = NotImplemented
    param = NotImplemented
    delimiter = NotImplemented

    _types = None
    _pattern: re.Pattern = None

    split_re_tpl = string.Template(r"(?<=[^\\])${delimiter}")

    def __init__(self, key, value):
        self.key, self.value = self.clean_params(key, value)

    def __str__(self):
        attrs = ("key", "value")
        attr_kwargs = (
            f"{attr}{self.delimiter}{getattr(self, attr)!r}" for attr in attrs
        )
        return "{}({})".format(type(self).__name__, ", ".join(attr_kwargs))

    @classmethod
    @abc.abstractmethod
    def clean_params(cls, key, value):
        """Validate and format the Mod's key and/or value."""

    @classmethod
    def match(cls, mod_str):
        """Create a new Mod by matching syntax."""
        # pylint: disable=no-member
        parts = cls.pattern.split(mod_str, maxsplit=1)
        if len(parts) != 2:
            # TODO: add info about proper syntax in error msg
            raise ReqModSyntaxError(value=mod_str)
        key, value = parts
        return cls(key=key, value=value)

    @classproperty
    # pylint: disable=no-self-argument
    def pattern(cls) -> re.Pattern:
        if not cls._pattern:
            re_str = cls.split_re_tpl.substitute(
                delimiter=re.escape(cls.delimiter)
            )
            cls._pattern = re.compile(re_str)
        return cls._pattern


class JsonFieldMod(Mod):

    param_type = PARAM_TYPES.json_field
    param = "body"
    delimiter = ":="

    @classmethod
    def clean_params(cls, key, value):
        try:
            json_value = json.loads(value)
        except json.JSONDecodeError as err:
            # TODO: implement error handling
            raise ReqModValueError(value=value, msg=f"invalid JSON - {err}")
        return key, json_value


class StrFieldMod(Mod):

    param_type = PARAM_TYPES.str_field
    param = "body"
    delimiter = "="

    @classmethod
    def clean_params(cls, key, value):
        return key, value


class HeaderMod(Mod):

    param_type = PARAM_TYPES.header
    param = "headers"
    delimiter = ":"

    @classmethod
    def clean_params(cls, key, value):
        # TODO: legit error messages
        msg = "non-ASCII character(s) found in header"
        if not is_ascii(str(key)):
            raise ReqModValueError(value=key, msg=msg)
        if not is_ascii(str(value)):
            raise ReqModValueError(value=value, msg=msg)
        return key, value


class UrlParamMod(Mod):

    param_type = PARAM_TYPES.url_param
    param = "query"
    delimiter = "=="

    @classmethod
    def clean_params(cls, key, value):
        return quote_plus(key), quote_plus(value)


# Tuple of Mod classes, in order of specificity of delimiters
MODS = AttrMap(
    *(
        (mod_cls.delimiter, mod_cls)
        for mod_cls in (JsonFieldMod, UrlParamMod, HeaderMod, StrFieldMod,)
    )
)
