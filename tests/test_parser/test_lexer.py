from restcli.parser import lexer

from .. import utils


def test_assign_headers():
    arg = "Authorization:'JWT abc123.foo'"
    tokens = lexer.lex(arg)
    expected = ((lexer.ACTIONS.assign.name, ["Authorization:JWT abc123.foo"]),
                (lexer.ACTIONS.append.name, None),
                (lexer.ACTIONS.delete.name, None))
    assert utils.contents_equal(tokens, expected)
