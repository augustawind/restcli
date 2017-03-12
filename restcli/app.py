import json
import sys
from string import Template

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer
from pygments.lexers.python import Python3Lexer
from pygments.lexers.textfmts import HttpLexer

from restcli import Requestor

HTTP_TPL = Template('\n'.join([
    'HTTP ${status_code}',
    '${headers}',
]))


class App:
    """Application interface for restcli."""

    def __init__(self, groups_file, env_file, outfile=sys.stdout):
        self.r = Requestor(groups_file, env_file)
        self.outfile = outfile

        self.http_lexer = HttpLexer()
        self.json_lexer = JsonLexer()
        self.python_lexer = Python3Lexer()
        self.formatter = TerminalFormatter()

        self.usage_info = {
            'run': 'Usage: run GROUP REQUEST',
            'inspect': 'Usage: inspect GROUP [REQUEST [ATTR]]',
            'set_env': 'Usage: set_env ENV_FILE',
            'set_collection': 'Usage: set_collection COLLECTION_FILE',
            'reload': 'Usage: reload [collection, env]',
        }

    def run(self, group_name, request_name):
        """Run a Request."""
        group = self.get_group('run', group_name)
        if not group:
            return
        request = self.get_request('run', group, group_name, request_name)
        if not request:
            return

        response = self.r.request(group_name, request_name)
        self.print_response(response)

    def inspect(self, group_name, request_name=None, attr_name=None):
        """Inspect a Group, Request, or Request Attribute."""
        group = self.get_group('inspect', group_name)
        if not group:
            return
        output_obj = group

        if request_name:
            request = self.get_request('inspect', group, group_name,
                                       request_name)
            if not request:
                return
            output_obj = request

        if attr_name:
            attr = self.get_request_attr('inspect', request, group_name,
                                         request_name, attr_name)
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

    def save(self):
        self.r.save_env()

    def get_group(self, command, group_name):
        group = self.r.collection.get(group_name)
        if not group:
            self.usage(command, "Group '{}' not found.".format(group_name))
        return group

    def get_request(self, command, group, group_name, request_name):
        request = group.get(request_name)
        if not request:
            self.usage(command, "Request '{}' not found in Group '{}'."
                       .format(request_name, group_name))
        return request

    def get_request_attr(self, command, request, group_name, request_name,
                         attr_name):
        attr = request.get(attr_name)
        if not attr:
            self.usage(command,
                       "Attribute '{}' not found in Request '{}'"
                       " of Group '{}'.".format(attr_name, request_name,
                                                group_name))
        return attr

    def print_response(self, response):
        output = HTTP_TPL.substitute(
            status_code=response.status_code,
            headers=self.key_value_pairs(response.headers),
        )
        highlight(output, self.http_lexer, self.formatter, self.outfile)

        print()

        output = json.dumps(response.json(), indent=2)
        highlight(output, self.json_lexer, self.formatter, self.outfile)

    def print_env(self):
        env = self.r.env
        if env:
            print(self.key_value_pairs(env))
        else:
            print('No Environment loaded.')

    def usage(self, command, msg):
        print(msg)
        print(self.usage_info[command])

    @staticmethod
    def key_value_pairs(obj):
        return '\n'.join(['{}: {}'.format(k, v) for k, v in obj.items()])
