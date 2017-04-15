import random
from collections import OrderedDict

import pytest

from restcli.parser import lexer, parser

from ..helpers import get_random_unicode


class TestParseURLParam:

    def test_parse_url_param(self):
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

    def test_parse_url_param_invalid(self):
        action = get_random_action()
        key = get_random_unicode(10)
        value = get_random_unicode(10)
        with pytest.raises(AssertionError):
            parser.parse_url_param(action, key, value)


def test_parse_json_field():
    action = get_random_action()
    key = 'foo'
    value = 'true'
    result = parser.parse_json_field(action, key, value)


def get_random_action():
    return random.choice(tuple(lexer.ACTIONS))
