import random

import pytest

from restcli.exceptions import ReqModSyntaxError, ReqModValueError
from restcli.reqmod import mods
from restcli.reqmod.lexer import ACTIONS
from restcli.utils import quote_plus
from tests.helpers import (
    random_alphanum,
    random_unicode,
    random_urlsafe,
)

# Default value for function args where None doesn't make sense
DEFAULT = type("DEFAULT", (object,), {})


class ModTypesTestMixin(object):
    """Helper mixin for classes that test the Mod functions."""

    TEST_ITERATIONS = 9

    @classmethod
    def run_mod_test(
        cls,
        input_val,
        input_key=DEFAULT,
        expected_val=DEFAULT,
        expected_key=DEFAULT,
    ):
        if input_key is DEFAULT:
            input_key = random_alphanum(11)
        mod_str = cls.mod_cls.delimiter.join((input_key, input_val))
        mod = cls.mod_cls.match(mod_str)

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
            input_val="true", expected_val=True,
        )

    def test_number_int(self):
        self.run_mod_test(
            input_val="11", expected_val=11,
        )

    def test_number_float(self):
        self.run_mod_test(
            input_val="26.5", expected_val=26.5,
        )

    def test_null(self):
        self.run_mod_test(
            input_val="null", expected_val=None,
        )

    def test_array(self):
        self.run_mod_test(
            input_val="[1, 2, 3]", expected_val=[1, 2, 3],
        )

    def test_object(self):
        self.run_mod_test(
            input_val='{"foo": "bar", "baz": "biff"}',
            expected_val={"foo": "bar", "baz": "biff"},
        )

    def test_compound_1(self):
        self.run_mod_test(
            input_val=(
                '[5, 5.25, "hello", true, null, [1, 2], {"abc": "def"}]'
            ),
            expected_val=(
                [5, 5.25, "hello", True, None, [1, 2], {"abc": "def"}]
            ),
        )

    def test_compound_2(self):
        self.run_mod_test(
            input_val=(
                '{"who": null, "whom": true, "whomst": ["x", "y", "z"],'
                ' "whomst\'d\'ve": {"x": 11, "y": [2, 2], "z": [0, [], {}]}}'
            ),
            expected_val=(
                {
                    "who": None,
                    "whom": True,
                    "whomst": ["x", "y", "z"],
                    "whomst'd've": {"x": 11, "y": [2, 2], "z": [0, [], {}]},
                }
            ),
        )


class TestURLParamMod(ModTypesTestMixin):

    mod_cls = mods.UrlParamMod

    def test_urlsafe(self):
        for _ in range(self.TEST_ITERATIONS):
            self.run_mod_test(
                input_val=random_urlsafe(), input_key=random_urlsafe(),
            )

    def test_unicode_value(self):
        for _ in range(self.TEST_ITERATIONS):
            val = random_unicode()
            self.run_mod_test(
                input_val=val,
                input_key=random_urlsafe(),
                expected_val=quote_plus(val),
            )

    def test_unicode_key(self):
        for _ in range(self.TEST_ITERATIONS):
            key = random_unicode()
            self.run_mod_test(
                input_val=random_urlsafe(),
                input_key=key,
                expected_key=quote_plus(key),
            )

    def test_delimiter(self):
        inputs = (
            "\\=\\=%s" % random_urlsafe(),
            "%s\\=\\=" % random_urlsafe(),
            "%s\\=\\=%s" % (random_urlsafe(), random_urlsafe()),
            "%s\\=" % random_urlsafe(),
            "=%s" % random_urlsafe(),
            "%s=%s" % (random_urlsafe(), random_urlsafe()),
        )
        for item in inputs:
            self.run_mod_test(
                input_val=item,
                input_key=random_urlsafe(),
                expected_val=quote_plus(item),
            )
        for item in inputs:
            self.run_mod_test(
                input_val=random_urlsafe(),
                input_key=item,
                expected_key=quote_plus(item),
            )


class TestHeaderMod(ModTypesTestMixin):

    mod_cls = mods.HeaderMod

    def test_alphanum(self):
        for _ in range(self.TEST_ITERATIONS):
            self.run_mod_test(
                input_val=random_alphanum(), input_key=random_alphanum(),
            )

    def test_unicode_value(self):
        for _ in range(self.TEST_ITERATIONS):
            with pytest.raises(ReqModValueError):
                self.run_mod_test(
                    input_val=random_unicode(), input_key=random_alphanum(),
                )

    def test_unicode_key(self):
        for _ in range(self.TEST_ITERATIONS):
            with pytest.raises((ReqModValueError, ReqModSyntaxError)):
                self.run_mod_test(
                    input_val=random_alphanum(), input_key=random_unicode(),
                )


class TestStrFieldMod(ModTypesTestMixin):

    mod_cls = mods.StrFieldMod

    def test_alphanum(self):
        self.run_mod_test(
            input_val=random_alphanum(), input_key=random_alphanum(),
        )

    def test_unicode(self):
        self.run_mod_test(
            input_val=random_unicode(), input_key=random_unicode(),
        )
