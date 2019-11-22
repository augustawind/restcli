import operator
from functools import reduce

from restcli.reqmod import lexer
from tests.helpers import contents_equal


class LexerTestMixin:

    action = NotImplemented

    def transform_args(self, arg):
        raise NotImplementedError

    def run_test(self, args, result):
        argv = self.transform_args(args)
        tokens = lexer.lex(argv)
        assert contents_equal(
            tokens, [(self.action, token) for token in result]
        )

    def test_1_header_single_quotes(self):
        args = ["Authorization:'JWT abc123.foo'"]
        result = ["Authorization:'JWT abc123.foo'"]
        self.run_test(args, result)

    def test_2_json_str_double_quotes(self):
        args = ['description="foo bar baz"']
        result = ['description="foo bar baz"']
        self.run_test(args, result)

    def test_3_nested_json_number_unquoted(self):
        args = [".location.postal_code:=12345"]
        result = [".location.postal_code:=12345"]
        self.run_test(args, result)

    def test_4(self):
        args = ["foo:bar", 'conditions[0].var="haha ha"']
        result = ["foo:bar", 'conditions[0].var="haha ha"']
        self.run_test(args, result)


class TestAssignShortForm(LexerTestMixin):

    action = lexer.ACTIONS.assign

    def transform_args(self, args):
        return args


def intersperse_left(item, seq):
    """Insert `item` before every item in `seq`."""
    return reduce(operator.add, ((item, x) for x in seq))


class TestAssign(LexerTestMixin):

    action = lexer.ACTIONS.assign

    def transform_args(self, args):
        return intersperse_left("-n", args)


class TestAppend(LexerTestMixin):

    action = lexer.ACTIONS.append

    def transform_args(self, args):
        return intersperse_left("-a", args)


class TestDelete(LexerTestMixin):

    action = lexer.ACTIONS.delete

    def transform_args(self, args):
        return intersperse_left("-d", args)
