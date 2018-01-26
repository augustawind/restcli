from collections import OrderedDict

from restcli.reqmod import lexer
from restcli import utils
from .helpers import random_alphanum, random_unicode


def test_tokenize():
    s = r"""When I said "hi, foo", foo said 'hi, "hi, foo"' \a\1\3 \4."""
    words = lexer.tokenize(s)
    expected = ['When', 'I', 'said', '"hi, foo",', 'foo', 'said',
                '\'hi, "hi, foo"\'', '\\a\\1\\3', '\\4.']
    assert words == expected


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
            'age': 89,
        },
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
    assert utils.is_ascii(random_unicode(50)) is False
    assert utils.is_ascii(random_unicode(50)) is False
    assert utils.is_ascii(random_unicode(50)) is False

    assert utils.is_ascii(random_alphanum(50)) is True
    assert utils.is_ascii(random_alphanum(50)) is True
    assert utils.is_ascii(random_alphanum(50)) is True
