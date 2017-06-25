import abc
import json
import re
import string

import six

from restcli.exceptions import InputError
from restcli.params import VALID_URL_CHARS
from restcli.utils import AttrSeq, classproperty, is_ascii

ATTR_TYPES = AttrSeq(
    'json_field',
    'str_field',
    'header',
    'url_param',
)


class ModError(InputError):
    """Error class for badly formed mod strings."""


class Mod(six.with_metaclass(abc.ABCMeta, object)):

    attr_type = NotImplemented
    attr = NotImplemented
    delimiter = NotImplemented

    _types = None
    _pattern = None

    split_re_tpl = string.Template(r'[^\\]${delimiter}')

    def __init__(self, key, value, action):
        self.key, self.value = self.fmt_params(key, value)
        self.action = action

    @classmethod
    def match(cls, action, mod_str):
        parts = cls.pattern.split(mod_str)
        if len(parts) != 3:
            # TODO: custom error class
            raise ModError(value=mod_str, msg='Mod structure is ambiguous')
        key, delimiter, value = cls.fmt_params(*parts)
        return cls(key=key, value=value, action=action)

    @classproperty
    def pattern(cls):
        if not cls._pattern:
            re_str = cls.split_re_tpl.substitute(
                delimiter=re.escape(cls.delimiter))
            cls._pattern = re.compile(re_str)
        return cls._pattern

    @classproperty
    def types(cls):
        """Tuple of all available Mod types."""
        # The order here is important (still? we'll see)
        if not cls._types:
            cls._types = AttrSeq(*cls.__subclasses__())
        return cls._types

    @classmethod
    @abc.abstractmethod
    def fmt_params(self, key, value):
        """Validate and format the Mod's key and/or value."""


class JsonFieldMod(Mod):

    attr_type = ATTR_TYPES.json_field
    attr = 'body'
    delimiter = ':='

    @classmethod
    def fmt_params(cls, key, value):
        try:
            json_value = json.loads(value)
        except json.JSONDecodeError as err:
            # TODO: implement error handling
            raise ModError(value=value, msg='invalid JSON - %s' % err)
        return key, json_value


class StrFieldMod(Mod):

    attr_type = ATTR_TYPES.str_field
    attr = 'body'
    delimiter = '='

    @classmethod
    def fmt_params(cls, key, value):
        return key, value


class HeaderMod(Mod):

    attr_type = ATTR_TYPES.header
    attr = 'headers'
    delimiter = ':'

    @classmethod
    def fmt_params(cls, key, value):
        # TODO: legit error messages
        msg = "non-ASCII character(s) found in header"
        if not is_ascii(str(key)):
            raise ModError(value=key, msg=msg)
        if not is_ascii(str(value)):
            raise ModError(value=value, msg=msg)
        return key, value


class UrlParamMod(Mod):

    attr_type = ATTR_TYPES.url_param
    attr = 'query'
    delimiter = '=='

    @classmethod
    def fmt_params(cls, key, value):
        if not all(char in VALID_URL_CHARS for char in key + value):
            raise ModError(
                value=cls.delimiter.join((key, value)),
                msg='Invalid char(s) found in URL parameter.'
                    ' Accepted chars are: %s' % (VALID_URL_CHARS,)
        )
        return key, value

