import random

import pytest

from restcli.envmod import parser
from restcli.envmod.lexer import ACTIONS
from tests.helpers import attrs_list, get_random_ascii, get_random_unicode


class FormatterTestMixin(object):
    """Helper mixin for classes that test the formatter functions."""

    @classmethod
    def run_test(cls, in_val, out_val, key=None, out_key=None):
        key = out_key or key or get_random_ascii(11)
        values = cls.fmt(key, in_val)
        expected = (key, out_val)
        assert values == expected

    @staticmethod
    def get_random_action():
        return random.choice(tuple(ACTIONS))


class TestFormatURLParam(FormatterTestMixin):
    # TODO: maybe add more tests? may not be necessary

    attr = 'query'
    fmt = parser.fmt_url_param

    def test_valid(self):
        value = ''.join(random.sample(parser.VALID_URL_CHARS, 10))
        self.run_test(
            in_val=value,
            out_val=value,
            key=''.join(random.sample(parser.VALID_URL_CHARS, 10)),
        )

    def test_invalid(self):
        key = get_random_unicode(10)
        value = get_random_unicode(10)
        with pytest.raises(AssertionError):
            parser.fmt_url_param(key, value)


class TestFormatStrField(FormatterTestMixin):

    attr = 'body'
    fmt = parser.fmt_str_field

    def test_simple(self):
        self.run_test(
            in_val='foobarbaz',
            out_val='foobarbaz',
        )


class TestFormatJSONField(FormatterTestMixin):
    # TODO: add tests for invalid input, once error handling is implemented

    attr = 'body'
    fmt = parser.fmt_json_field

    def test_bool(self):
        self.run_test(
            in_val='true',
            out_val=True,
        )

    def test_number_int(self):
        self.run_test(
            in_val='11',
            out_val=11,
        )

    def test_number_float(self):
        self.run_test(
            in_val='26.5',
            out_val=26.5,
        )

    def test_null(self):
        self.run_test(
            in_val='null',
            out_val=None,
        )

    def test_array(self):
        self.run_test(
            in_val='[1, 2, 3]',
            out_val=[1, 2, 3],
        )

    def test_object(self):
        self.run_test(
            in_val='{"foo": "bar", "baz": "biff"}',
            out_val={'foo': 'bar', 'baz': 'biff'},
        )

    def test_compound_1(self):
        self.run_test(
            in_val='[5, 5.25, "hello", true, null, [1, 2], {"abc": "def"}]',
            out_val=[5, 5.25, 'hello', True, None, [1, 2], {'abc': 'def'}],
        )

    def test_compound_2(self):
        self.run_test(
            in_val=(
                '{"who": null, "whom": true, "whomst": ["x", "y", "z"],'
                ' "whomst\'d\'ve": {"x": 11, "y": [2, 2], "z": [0, [], {}]}}'
            ),
            out_val=(
                {'who': None, 'whom': True, 'whomst': ['x', 'y', 'z'],
                 "whomst'd've": {'x': 11, 'y': [2, 2], 'z': [0, [], {}]}}
            ),
        )
