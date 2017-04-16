from restcli.parser import lexer

from ..helpers import contents_equal


def test_assign_headers():
    arg = "Authorization:'JWT abc123.foo'"
    tokens = lexer.lex(arg)
    expected = [(lexer.ACTIONS.assign, ["Authorization:'JWT abc123.foo'"])]
    assert contents_equal(tokens, expected)
