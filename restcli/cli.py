import cmd
import json
import readline
from string import Template

from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.lexers.python import Python3Lexer
from pygments.lexers.textfmts import HttpLexer
from pygments.formatters.terminal import TerminalFormatter

from restcli import Requestor

HTTP_TPL = Template('\n'.join([
    'HTTP ${status_code}',
    '${headers}',
]))

class Program(cmd.Cmd):

    def __init__(self, groups_file, env_file):
        super().__init__()
        self.r = Requestor(groups_file, env_file)

        self.http_lexer = HttpLexer()
        self.json_lexer = JsonLexer()
        self.python_lexer = Python3Lexer()
        self.formatter = TerminalFormatter()

        self.usage_info = {
            'run': 'Usage: run GROUP REQUEST',
            'inspect': 'Usage: inspect GROUP [REQUEST [ATTR]]'
        }

    def usage(self, command, msg):
        print(msg)
        print(self.usage_info[command])

    @staticmethod
    def key_value_pairs(obj):
        return '\n'.join(['{}: {}'.format(k, v) for k, v in obj.items()])

    def print_response(self, response):
        output = HTTP_TPL.substitute(
            status_code=response.status_code,
            headers=self.key_value_pairs(response.headers),
        )
        highlight(output, self.http_lexer, self.formatter, outfile=self.stdout)

        print()

        output = json.dumps(response.json(), indent=2)
        highlight(output, self.json_lexer, self.formatter, outfile=self.stdout)

    def get_group(self, command, group_name):
        group = self.r.groups.get(group_name)
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

    def do_run(self, arg):
        """Run an HTTP request."""
        args = arg.split()
        if len(args) != 2:
            return self.usage('run', 'Invalid input.')

        group_name, request_name = args

        group = self.get_group('run', group_name)
        if not group:
            return
        request = self.get_request('run', group, group_name, request_name)
        if not request:
            return

        response = self.r.request(group_name, request_name)
        self.print_response(response)

    def do_inspect(self, arg):
        """Inspect a Group, Request, or Attribute."""
        args = arg.split()
        if len(args) == 0:
            self.usage('inspect', 'Invalid input.')
        if len(args) > 3:
            self.usage('inspect', 'Invalid input.')

        output_obj = None
        if len(args) > 0:
            group_name = args[0]
            group = self.get_group('inspect', group_name)
            if not group:
                return
            output_obj = group
        if len(args) > 1:
            output_obj = None
            request_name = args[1]
            request = self.get_request('inspect', group, group_name,
                                       request_name)
            if not request:
                return
            output_obj = request
        if len(args) > 2:
            output_obj = None
            attr_name = args[2]
            attr = self.get_request_attr('inspect', request, group_name,
                                         request_name, attr_name)
            if not attr:
                return
            if attr_name == 'scripts':
                for name, script in attr.items():
                    print('{}:'.format(name))
                    highlight(script, self.python_lexer, self.formatter,
                              outfile=self.stdout)
                    print()
            elif attr_name == 'headers':
                headers = dict(l.split(':') for l in attr.strip().split('\n'))
                output = self.key_value_pairs(headers)
                highlight(output, self.http_lexer, self.formatter,
                          outfile=self.stdout)
            else:
                output_obj = attr

        if output_obj:
            output = json.dumps(output_obj, indent=2)
            highlight(output, self.json_lexer, self.formatter,
                      outfile=self.stdout)

    def do_reload(self, arg):
        """Reload the collection and environment from disk."""
        self.r.load_config()

    def do_env(self, arg):
        """Display the current environment."""
        env = self.r.env
        if env:
            print(self.key_value_pairs(env))
        else:
            print('No Environment loaded.')

    def do_save(self, arg):
        """Save the current environment to disk."""
        self.r.save_env()
