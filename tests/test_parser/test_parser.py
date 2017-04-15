import random
from collections import OrderedDict

import pytest

from restcli.parser import lexer, parser

from ..helpers import get_random_ascii, get_random_unicode


class TestParseURLParam:

    def test_valid(self):
        action = get_random_action()
        key = ''.join(random.sample(parser.VALID_URL_CHARS, 10))
        value = ''.join(random.sample(parser.VALID_URL_CHARS, 10))
        result = parser.parse_url_param(action, key, value)
        expected = OrderedDict((
            (key, OrderedDict((
                (action, value),
            ))),
        ))
        assert result == expected

    def test_invalid(self):
        action = get_random_action()
        key = get_random_unicode(10)
        value = get_random_unicode(10)
        with pytest.raises(AssertionError):
            parser.parse_url_param(action, key, value)


class TestParseJSONField:

    @staticmethod
    def run_test(in_val, out_val, key=None, out_key=None):
        action = get_random_action()
        key = out_key or key or get_random_ascii(11)
        result = parser.parse_json_field(action, key, in_val)
        expected = OrderedDict((
            (key, OrderedDict((
                (action, out_val),
            ))),
        ))
        from pprint import pformat
        print('ACTUAL ==>', pformat(result))
        print('EXPECT ==>', pformat(expected))
        assert result == expected

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


def get_random_action():
    return random.choice(tuple(lexer.ACTIONS))
