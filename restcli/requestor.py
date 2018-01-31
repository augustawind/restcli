import re
from contextlib import contextmanager

import jinja2
import requests
import six

from restcli import yaml_utils as yaml
from restcli.exceptions import InputError
from restcli.workspace import Collection, Environment

__all__ = ['Requestor']

ENV_RE = re.compile(r'([^:]+):(.*)')


class Requestor(object):
    """Parser and executor of requests."""

    def __init__(self, collection_file, env_file=None):
        self.collection = Collection(collection_file)
        self.env = Environment(env_file)

    def request(self, group, name, updater=None, *env_args):
        """Execute the Request found at ``self.collection[group][name]``."""
        request = self.collection[group][name]

        with self.override_env(env_args):
            request_kwargs = self.parse_request(request, self.env, updater)

        response = requests.request(**request_kwargs)

        script = request.get('script')
        if script:
            script_locals = {'response': response, 'env': self.env}
            if self.collection.libs:
                for lib in six.itervalues(self.collection.libs):
                    script_locals.update(lib.define(response, self.env))
            self.run_script(script, script_locals)

        return response

    @classmethod
    def parse_request(cls, request, env, updater=None):
        """Parse a Request object in the context of an Environment."""
        env = env.copy()
        kwargs = {
            'method': request['method'],
            'url': cls.interpolate(request['url'], env),
            'query': {},
            'headers': {},
            'body': {},
        }

        body = request.get('body')
        if body:
            kwargs['body'] = cls.interpolate(body, env)
        headers = request.get('headers')
        if headers:
            kwargs['headers'] = {k: cls.interpolate(v, env)
                                 for k, v in six.iteritems(headers)}

        if updater:
            updater.apply(kwargs)

        kwargs['json'] = kwargs.pop('body')
        kwargs['params'] = kwargs.pop('query')

        return kwargs

    @contextmanager
    def override_env(self, env_args):
        """Temporarily modify an Environment with the given overrides.

        On exit, the Env is returned to its previous state.
        """
        original = self.env.data
        self.mod_env(env_args)

        yield

        self.env.replace(original)

    def mod_env(self, env_args, save=False):
        """Modify an Environment with the given overrides."""
        set_env, del_env = self.parse_env_args(*env_args)
        self.env.update(**set_env)
        self.env.remove(*del_env)

        if save:
            self.env.save()

    @staticmethod
    def parse_env_args(*env_args):
        """Parse some string args with Environment syntax."""
        del_env = []
        set_env = {}
        for arg in env_args:
            # Parse deletion syntax
            if arg.startswith('!'):
                var = arg[1:].strip()
                del_env.append(var)
                if var in set_env:
                    del set_env[var]
                continue

            # Parse assignment syntax
            match = ENV_RE.match(arg)
            if not match:
                raise InputError(
                    value=arg,
                    msg='Error: args must take one of the forms `!KEY` or'
                        ' `KEY:VAL`, where `KEY` is a string and `VAL` is a'
                        ' valid YAML value.',
                    action='env',
                )
            key, val = match.groups()
            set_env[key.strip()] = yaml.load(val)
        return set_env, del_env

    @staticmethod
    def interpolate(data, env):
        """Given some ``data``, render it with the given ``env``."""
        tpl = jinja2.Template(data)
        rendered = tpl.render(env)
        return yaml.load(rendered)

    @staticmethod
    def run_script(script, script_locals):
        """Run a Request script with a Response and Environment as context."""
        code = compile(script, '<<script>>', 'exec')
        exec(code, script_locals)
