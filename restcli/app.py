import json
import sys
from string import Template

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer
from pygments.lexers.python import Python3Lexer
from pygments.lexers.textfmts import HttpLexer

from restcli.exceptions import NotFound
from restcli.requestor import Requestor


class App:
    """Application interface for restcli."""

    HTTP_TPL = Template('\n'.join([
        'HTTP ${status_code}',
        '${headers}',
    ]))

    def __init__(self, collection_file, env_file, outfile=sys.stdout):
        self.r = Requestor(collection_file, env_file)
        self.outfile = outfile

        self.http_lexer = HttpLexer()
        self.json_lexer = JsonLexer()
        self.python_lexer = Python3Lexer()
        self.formatter = TerminalFormatter()

    def run(self, group_name, request_name):
        """Run a Request."""
        group = self.get_group(group_name, action='run')
        if not group:
            return
        request = self.get_request(group, group_name, request_name,
                                   action='run')
        if not request:
            return

        response = self.r.request(group_name, request_name)
        self.print_response(response)

    def inspect(self, group_name, request_name=None, attr_name=None):
        """Inspect a Group, Request, or Request Attribute."""
        group = self.get_group(group_name, action='inspect')
        if not group:
            return
        output_obj = group

        if request_name:
            request = self.get_request(group, group_name, request_name,
                                       action='inspect')
            if not request:
                return
            output_obj = request

        if attr_name:
            attr = self.get_request_attr(request, group_name, request_name,
                                         attr_name, action='inspect')
            if not attr:
                return

            if attr_name == 'scripts':
                for name, script in attr.items():
                    print('{}:'.format(name))
                    highlight(script, self.python_lexer, self.formatter,
                              self.outfile)
                    print()
                    return

            if attr_name == 'headers':
                headers = dict(l.split(':') for l in attr.strip().split('\n'))
                output = self.key_value_pairs(headers)
                highlight(output, self.http_lexer, self.formatter,
                          self.outfile)
                return

            output_obj = attr

        output = json.dumps(output_obj, indent=2)
        highlight(output, self.json_lexer, self.formatter, self.outfile)

    def load_collection(self, path=None):
        """Reload the current Collection, changing it to ``path`` if given."""
        self.r.load_collection(path)

    def load_env(self, path=None):
        """Reload the current Env, changing it to ``path`` if given."""
        self.r.load_env(path)

    def save_env(self, **kwargs):
        """Save the current Environment to disk."""
        self.r.save_env(**kwargs)

    def get_group(self, group_name, action):
        """Retrieve a Group object."""
        try:
            return self.r.collection[group_name]
        except KeyError:
            raise NotFound(
                action,
                "Group '{}' not found.".format(group_name)
            )

    def get_request(self, group, group_name, request_name, action):
        """Retrieve a Request object."""
        try:
            return group[request_name]
        except KeyError:
            raise NotFound(
                action,
                "Request '{}' not found in Group '{}'."
                    .format(request_name, group_name),
            )

    def get_request_attr(self, request, group_name, request_name, attr_name,
                         action):
        """Retrieve a Request Attribute."""
        try:
            return request[attr_name]
        except KeyError:
            raise NotFound(
                action,
                "Attribute '{}' not found in Request '{}.{}'."
                    .format(attr_name, request_name, group_name)
            )

    def print_response(self, response):
        """Print an HTTP Response."""
        output = self.HTTP_TPL.substitute(
            status_code=response.status_code,
            headers=self.key_value_pairs(response.headers),
        )
        highlight(output, self.http_lexer, self.formatter, self.outfile)

        print()

        output = json.dumps(response.json(), indent=2)
        highlight(output, self.json_lexer, self.formatter, self.outfile)

    def print_env(self):
        """Print the current Environment."""
        env = self.r.env
        if env:
            print(self.key_value_pairs(env))
        else:
            print('No Environment loaded.')

    @staticmethod
    def key_value_pairs(obj):
        """Format a dict-like object into lines of 'KEY: VALUE'."""
        return '\n'.join(['{}: {}'.format(k, v) for k, v in obj.items()])
