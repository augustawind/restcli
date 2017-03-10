import pytest

from restcli import Requestor

TEST_GROUPS_PATH = 'test_groups.yaml'
TEST_ENV_PATH = 'test_env.yaml'

@pytest.fixture
def requestor():
    return Requestor(TEST_GROUPS_PATH, TEST_ENV_PATH)


def test_interpolate():
    actual = Requestor.interpolate(
        data={
            'number': 3,
            'string': '{{ val0 }}',
            'boolean': True,
            'null': None,
            'object': {'foo': 5, '{{ key1 }}': ['{{ val1 }}', None]},
            'array': ['foo', True, 5, None, {'key': '{{ val2 }}'}],
        },
        env={
            'val0': 'xyz',
            'val1': 'abc',
            'key1': 'def',
            'val2': 'ghi',
        },
    )
    expected = {
        'number': 3,
        'string': 'xyz',
        'boolean': True,
        'null': None,
        'object': {'foo': 5, 'def': ['abc', None]},
        'array': ['foo', True, 5, None, {'key': 'ghi'}],
    }
    assert actual == expected
