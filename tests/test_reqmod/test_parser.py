import random
import string
from collections import OrderedDict
from unittest.mock import call

import pytest
import pytest_mock  # noqa: F401

from restcli import yaml_utils as yaml
from restcli.reqmod import parser
from restcli.reqmod.lexer import ACTIONS


@pytest.fixture
def request(pytestconfig):
    """Generate a semi-random request object."""
    req = OrderedDict()
    req['method'] = random.choice(('get', 'post', 'put', 'delete'))
    req['url'] = '%s.org' % ''.join(random.sample(string.ascii_lowercase, 10))
    req['headers'] = OrderedDict((
        ('Content-Type', 'application/json'),
        ('Accept', 'application/json')
    ))

    # Add body if method supports writes
    if req['method'] in ('post', 'put'):
        name = 'Fr%snken Fr%snkenfrank' % (
            'a' * random.randint(1, 6),
            'a' * random.randint(1, 6),
        )
        req['body'] = yaml.dump(OrderedDict((
            ('name', name),
            ('age', random.randint(10, 20)),
            ('color', random.choice(('red', 'yellow', 'blue'))),
            ('warranty', random.choice((True, False))),
            ('insurance', None),
        )))

    return req


class TestParse(object):

    formatter_name = 'fmt_header'
    field_type = 'header'
    attr = 'headers'
    action = ACTIONS.assign

    def test_assign_headers(self, request, mocker):
        # TODO: this test is useless
        mock_parser = mocker.patch('restcli.reqmod.parser.parse')

        lexemes = (
            (ACTIONS.assign, "Content-Type:application/json"),
            (ACTIONS.assign, "Accept:application/json"),
            (ACTIONS.assign, "Authorization:'JWT abc123.foo'"),
        )
        parser.parse(lexemes)

        calls = [call(lexemes)]
        assert mock_parser.call_count == 1
        assert mock_parser.call_args_list == calls
