import random
from collections import OrderedDict

import pytest

from restcli.parser import lexer, parser

from .. import utils


def test_parse_url_params():
    action = lexer.ACTIONS.assign.name
    key = ''.join(random.sample(parser.VALID_URL_CHARS, 10))
    value = ''.join(random.sample(parser.VALID_URL_CHARS, 10))
    result = parser.parse_url_param(action, key, value)
    expected = OrderedDict((
        (key, OrderedDict((
            (action, value),
        ))),
    ))
    assert result == expected


def test_parse_url_params_invalid():
    action = lexer.ACTIONS.assign.name
    key = utils.get_random_unicode(10)
    value = utils.get_random_unicode(10)
    with pytest.raises(AssertionError):
        parser.parse_url_param(action, key, value)
