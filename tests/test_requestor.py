import io
from types import SimpleNamespace

import pytest
import pytest_mock

from restcli import Requestor

TEST_GROUPS_PATH = 'tests/resources/test_collection.yaml'
TEST_ENV_PATH = 'tests/resources/test_env.yaml'


@pytest.fixture
def requestor():
    return Requestor(TEST_GROUPS_PATH, TEST_ENV_PATH)


def test_request(requestor, mocker):
    """Test Requestor()#request()."""
    mock = mocker.patch('requests.request')
    requestor.request('books', 'edit')
    assert mock.call_count == 1


def test_parse_request():
    """Test Requestor#parse_request()."""
    request = {
        'method': 'post',
        'url': '{{ server }}/authors',
        'headers': '''
            'Content-Type': 'application/json'
        ''',
        'body': '''
            id: 1
            name: Bartholomew McNozzleWafer
            date_of_birth: {{ birthday }}
        ''',
    }
    env = {
        'server': 'http://foobar.org',
        'birthday': '11/14/1991',
    }

    actual = Requestor.parse_request(request, env)
    expected = {
        'method': 'post',
        'headers': {
            'Content-Type': 'application/json',
        },
        'url': "http://foobar.org/authors",
        'json': {
            'id': 1,
            'name': 'Bartholomew McNozzleWafer',
            'date_of_birth': '11/14/1991',
        }
    }
    assert actual == expected


def test_interpolate():
    """Test Requestor#interpolate()."""
    actual = Requestor.interpolate(
        data="""
            number: 3
            string: '{{ val0 }}'
            boolean: True
            'null': null
            object: {'foo': 5, '{{ key1 }}': ['{{ val1 }}', null]}
            array: ['foo', True, 5, null, {'key': {{ val2 }}}]
        """,
        env={
            'val0': 'xyz',
            'val1': 'abc',
            'key1': 'def',
            'val2': 89,
        },
    )
    expected = {
        'number': 3,
        'string': 'xyz',
        'boolean': True,
        'null': None,
        'object': {'foo': 5, 'def': ['abc', None]},
        'array': ['foo', True, 5, None, {'key': 89}],
    }
    assert actual == expected


def test_run_script():
    """Test Requestor#run_script()."""
    response = SimpleNamespace(status_code=404)
    env = {'f': io.StringIO()}
    Requestor.run_script(
        r'''print('%s\n' % response.status_code, file=env['f'])''',
        response=response,
        env=env,
    )
    assert env['f'].getvalue().strip() == '404'
