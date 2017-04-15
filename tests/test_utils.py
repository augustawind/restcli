import random
import string
from collections import OrderedDict

import restcli.utils
from restcli import parser


def test_recursive_update():
    d0 = OrderedDict((
        ('foo', 'quux'),
        ('bar', OrderedDict((
            ('age', 25),
            ('is_cool', True),
        ))),
        ('baz', [1, 2, 4, 7, 11]),
    ))
    updates = {
        'baz': [5],
        'bar': {
            'age': 89
        }
    }
    utils.recursive_update(d0, updates)
    expected = OrderedDict((
        ('foo', 'quux'),
        ('bar', OrderedDict((
            ('age', 89),
            ('is_cool', True),
        ))),
        ('baz', [5]),
    ))
    assert d0 == expected


def test_is_ascii():
    assert utils.is_ascii(get_random_unicode(50)) is False
    assert utils.is_ascii(get_random_unicode(50)) is False
    assert utils.is_ascii(get_random_unicode(50)) is False

    assert utils.is_ascii(get_random_ascii(50)) is True
    assert utils.is_ascii(get_random_ascii(50)) is True
    assert utils.is_ascii(get_random_ascii(50)) is True


def get_random_unicode(length):
    """Helper to generate a random Unicode string."""
    include_ranges = [
        ( 0x0021, 0x0021 ),
        ( 0x0023, 0x0026 ),
        ( 0x0028, 0x007E ),
        ( 0x00A1, 0x00AC ),
        ( 0x00AE, 0x00FF ),
        ( 0x0100, 0x017F ),
        ( 0x0180, 0x024F ),
        ( 0x2C60, 0x2C7F ),
        ( 0x16A0, 0x16F0 ),
        ( 0x0370, 0x0377 ),
        ( 0x037A, 0x037E ),
        ( 0x0384, 0x038A ),
        ( 0x038C, 0x038C ),
    ]
    alphabet = [
        chr(code_point)
        for current_range in include_ranges
        for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.sample(alphabet, length))


def get_random_ascii(length):
    """Helper to generate a random ASCII string."""
    return ''.join(random.sample(string.printable, length))
