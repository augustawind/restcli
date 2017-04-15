from restcli.parser import lexer

from ..helpers import contents_equal


def test_assign_headers():
    arg = "Authorization:'JWT abc123.foo'"
    tokens = lexer.lex(arg)
    expected = ((lexer.ACTIONS.assign.name, ["Authorization:JWT abc123.foo"]),
                (lexer.ACTIONS.append.name, None),
                (lexer.ACTIONS.delete.name, None))
    assert contents_equal(tokens, expected)
