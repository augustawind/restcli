from collections import OrderedDict

from restcli import parser


class TestMiscUtilities:

    def test_recursive_update(self):
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
        parser.recursive_update(d0, updates)
        expected = OrderedDict((
            ('foo', 'quux'),
            ('bar', OrderedDict((
                ('age', 89),
                ('is_cool', True),
            ))),
            ('baz', [5]),
        ))
        assert d0 == expected
