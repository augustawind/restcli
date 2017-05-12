import random
import string
from collections import OrderedDict
from unittest.mock import call

import pytest
import pytest_mock  # noqa: F401

from restcli import yaml_utils as yaml
from restcli.parser import parser
from restcli.parser.lexer import ACTIONS
from restcli.parser.parser import PATTERNS

odict = OrderedDict


@pytest.fixture
def request():
    """Generate a semi-random request object."""
    req = odict()
    req['method'] = random.choice(('get', 'post', 'put', 'delete'))
    req['url'] = '%s.org' % ''.join(random.sample(string.ascii_lowercase, 10))
    req['headers'] = odict((
        ('Content-Type', 'application/json'),
        ('Accept', 'application/json')
    ))

    # Add body if method supports writes
    if req['method'] in ('post', 'put'):
        name = 'Fr%snken Fr%snkenfrank' % (
            'a' * random.randint(1, 6),
            'a' * random.randint(1, 6),
        )
        req['body'] = yaml.dump(odict((
            ('name', name),
            ('age', random.randint(10, 20)),
            ('color', random.choice(('red', 'yellow', 'blue'))),
            ('warranty', random.choice((True, False))),
            ('insurance', None),
        )))

    return req


class TestParse:

    attr = 'headers'
    action = ACTIONS.assign
    pattern_key = PATTERNS.header
    parser_name = 'parse_header'

    @staticmethod
    def mock_subparser(mocker, key, attr):
        in_dict = 'restcli.parser.parser.PATTERN_MAP'
        mock_parser = mocker.MagicMock()
        values = {key: (mock_parser, attr)}
        mocker.patch.dict(in_dict, values)
        return mock_parser

    def test_assign_headers(self, request, mocker):
        mock_parser = self.mock_subparser(mocker, self.pattern_key, self.attr)

        # Call parser.parse
        lexemes = (
            (ACTIONS.assign, [
                "Content-Type:application/json",
                "Accept:application/json",
                "Authorization:'JWT abc123.foo'",
            ]),
        )
        parser.parse(lexemes, request)

        # Check call args
        calls = [
            call(self.attr, self.action, 'Content-Type', 'application/json'),
            call(self.attr, self.action, 'Accept', 'application/json'),
            call(self.attr, self.action, 'Authorization', "'JWT abc123.foo'"),
        ]
        assert mock_parser.call_count == 3
        assert mock_parser.call_args_list == calls
