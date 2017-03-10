import pytest

from restcli import Requestor

TEST_GROUPS_PATH = 'test_groups.yaml'
TEST_ENV_PATH = 'test_env.yaml'

@pytest.fixture
def requestor():
    return Requestor(TEST_GROUPS_PATH, TEST_ENV_PATH)


def test_interpolate():
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


def test_parse_request():
    request = {
        'method': 'post',
        'url': '{{ server }}/authors',
        'headers': {
            'Content-Type': 'application/json',
        },
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
