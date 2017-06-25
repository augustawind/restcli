import random

import pytest

from restcli.envmod import mods
from restcli.envmod.lexer import ACTIONS
from tests.helpers import (
    get_random_ascii,
    get_random_unicode,
    get_random_url_chars,
)

# Default value for function args where None doesn't make sense
DEFAULT = type('DEFAULT', (object,), {})


class ModTypesTestMixin(object):
    """Helper mixin for classes that test the Mod functions."""

    @classmethod
    def run_mod_test(cls, input_val, input_key=DEFAULT,
                     expected_val=DEFAULT, expected_key=DEFAULT):
        if input_key is DEFAULT:
            input_key = get_random_ascii(11)
        mod_str = cls.mod_cls.delimiter.join((input_key, input_val))
        mod = cls.mod_cls.match(mod_str)
        mod.clean()
        assert mod.raw_key == input_key
        assert mod.raw_value == input_val

        if expected_key is DEFAULT:
            expected_key = input_key
        assert mod.key == expected_key
        if expected_val is DEFAULT:
            expected_val = input_val
        assert mod.value == expected_val

    @staticmethod
    def get_random_action():
        return random.choice(tuple(ACTIONS))


class TestJsonFieldMod(ModTypesTestMixin):
    # TODO: add tests for invalid input, once error handling is implemented

    mod_cls = mods.JsonFieldMod

    def test_bool(self):
        self.run_mod_test(
            input_val='true',
            expected_val=True,
        )

    def test_number_int(self):
        self.run_mod_test(
            input_val='11',
            expected_val=11,
        )

    def test_number_float(self):
        self.run_mod_test(
            input_val='26.5',
            expected_val=26.5,
        )

    def test_null(self):
        self.run_mod_test(
            input_val='null',
            expected_val=None,
        )

    def test_array(self):
        self.run_mod_test(
            input_val='[1, 2, 3]',
            expected_val=[1, 2, 3],
        )

    def test_object(self):
        self.run_mod_test(
            input_val='{"foo": "bar", "baz": "biff"}',
            expected_val={'foo': 'bar', 'baz': 'biff'},
        )

    def test_compound_1(self):
        self.run_mod_test(
            input_val=(
                '[5, 5.25, "hello", true, null, [1, 2], {"abc": "def"}]'
            ),
            expected_val=(
                [5, 5.25, 'hello', True, None, [1, 2], {'abc': 'def'}]
            ),
        )

    def test_compound_2(self):
        self.run_mod_test(
            input_val=(
                '{"who": null, "whom": true, "whomst": ["x", "y", "z"],'
                ' "whomst\'d\'ve": {"x": 11, "y": [2, 2], "z": [0, [], {}]}}'
            ),
            expected_val=(
                {'who': None, 'whom': True, 'whomst': ['x', 'y', 'z'],
                 "whomst'd've": {'x': 11, 'y': [2, 2], 'z': [0, [], {}]}}
            ),
        )


class TestURLParamMod(ModTypesTestMixin):

    mod_cls = mods.UrlParamMod

    def test_valid(self):
        self.run_mod_test(
            input_val=get_random_url_chars(),
            input_key=get_random_url_chars(),
        )

    def test_invalid_value(self):
        val = get_random_unicode()
        key = get_random_url_chars()
        with pytest.raises(mods.ModValueError):
            self.run_mod_test(
                input_val=val,
                input_key=key,
            )

    def test_invalid_key(self):
        val = get_random_url_chars()
        key = get_random_unicode()
        with pytest.raises(mods.ModValueError):
            self.run_mod_test(
                input_val=val,
                input_key=key,
            )


class TestHeaderMod(ModTypesTestMixin):

    mod_cls = mods.HeaderMod

    def test_valid(self):
        self.run_mod_test(
            input_val=get_random_ascii(),
            input_key=get_random_ascii(),
        )

    def test_invalid_value(self):
        val = get_random_unicode()
        key = get_random_ascii()
        with pytest.raises(mods.ModValueError):
            self.run_mod_test(
                input_val=val,
                input_key=key,
            )

    def test_invalid_key(self):
        val = get_random_ascii()
        key = get_random_unicode()
        with pytest.raises(mods.ModValueError):
            self.run_mod_test(
                input_val=val,
                input_key=key,
            )


class TestStrFieldMod(ModTypesTestMixin):

    mod_cls = mods.StrFieldMod

    def test_valid(self):
        self.run_mod_test(
            input_val=get_random_ascii(),
            input_key=get_random_ascii(),
        )
