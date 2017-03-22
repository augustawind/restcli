import json
import re
from string import Template

from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer
from pygments.lexers.python import Python3Lexer
from pygments.lexers.textfmts import HttpLexer

from restcli.exceptions import InvalidInput, NotFound
from restcli.requestor import Requestor
from restcli import yaml_utils as yaml

ENV_RE = re.compile(r'([^:]+):(.*)')


class App:
    """Application interface for restcli."""

    HTTP_TPL = Template('\n'.join((
        'HTTP/${http_version} ${status_code} ${reason}',
        '${headers}',
        '${body}',
    )))

    def __init__(self, collection_file, env_file, autosave=False,
                 style='fruity'):
        self.r = Requestor(collection_file, env_file)
        self.autosave = autosave

        self.http_lexer = HttpLexer()
        self.json_lexer = JsonLexer()
        self.python_lexer = Python3Lexer()
        self.formatter = Terminal256Formatter(style=style)

    def run(self, group_name, request_name, *env_args):
        """Run a Request."""
        group = self.get_group(group_name, action='run')
        self.get_request(group, group_name, request_name, action='run')

        set_env, _ = self.parse_env(*env_args)
        response = self.r.request(group_name, request_name, **set_env)

        if self.autosave:
            self.r.save_env()

        output = self.show_response(response)
        return output

    def view(self, group_name, request_name=None, attr_name=None):
        """Inspect a Group, Request, or Request Attribute."""
        group = self.get_group(group_name, action='view')
        output_obj = group

        if request_name:
            request = self.get_request(group, group_name, request_name,
                                       action='view')
            output_obj = request

            if attr_name:
                attr = self.get_request_attr(request, group_name, request_name,
                                             attr_name, action='view')

                if attr_name == 'scripts':
                    output = ''
                    for name, script in attr.items():
                        output += '%s:\n%s\n' % (
                            name,
                            highlight(script, self.python_lexer,
                                      self.formatter),
                        )
                    return output

                if attr_name == 'headers':
                    headers = dict(l.split(':')
                                   for l in attr.strip().split('\n'))
                    output = self.key_value_pairs(headers)
                    return highlight(output, self.http_lexer, self.formatter)

                output_obj = attr

        output = json.dumps(output_obj, indent=2)
        return highlight(output, self.json_lexer, self.formatter)

    def load_collection(self, path=None):
        """Reload the current Collection, changing it to ``path`` if given."""
        self.r.collection.load(path)
        return ''

    def load_env(self, path=None):
        """Reload the current Env, changing it to ``path`` if given."""
        self.r.load_env(path)
        return ''

    def save_env(self):
        """Save the current Environment to disk."""
        self.r.save_env()
        return ''

    def parse_env(self, *args):
        """Parse some string args with Environment syntax."""
        del_env = []
        set_env = {}
        for arg in args:
            # Parse deletion syntax
            if arg.startswith('!'):
                var = arg[1:]
                del_env.append(var)
                if var in set_env:
                    del set_env[var]
                continue

            # Parse assignment syntax
            match = ENV_RE.match(arg)
            if not match:
                raise InvalidInput(
                    action='env',
                    message='Error: args must take the form `key:value`, where'
                            ' `key` is a string and `value` is a valid YAML'
                            ' value.',
                )
            key, val = match.groups()
            set_env[key] = yaml.dump(val)
        return set_env, del_env

    def set_env(self, *args):
        """Set some new variables in the Environment."""
        set_env, del_env = self.parse_env(*args)
        self.r.set_env(**set_env)
        self.r.del_env(*del_env)

        output = ''
        if self.autosave:
            output += self.save_env()
        return output

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

    def show_response(self, response):
        """Print an HTTP Response."""
        http_txt = self.HTTP_TPL.substitute(
            http_version=str(float(response.raw.version) / 10),
            status_code=response.status_code,
            reason=response.reason,
            headers=self.key_value_pairs(response.headers),
            body=json.dumps(response.json(), indent=2),
        )
        return highlight(http_txt, self.http_lexer, self.formatter)

    def show_env(self):
        """Print the current Environment."""
        env = self.r.env
        if env:
            return highlight(json.dumps(env, indent=2), self.json_lexer,
                             self.formatter)
        else:
            return 'No Environment loaded.'

    @staticmethod
    def key_value_pairs(obj):
        """Format a dict-like object into lines of 'KEY: VALUE'."""
        return '\n'.join(['%s: %s' % (k, v) for k, v in obj.items()])
