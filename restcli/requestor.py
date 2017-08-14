import jinja2
import requests
import six

from restcli import yaml_utils as yaml
from restcli.workspace import Collection, Environment

__all__ = ['Requestor']


class Requestor(object):
    """Parser and executor of requests."""

    def __init__(self, collection_file, env_file=None):
        self.collection = Collection(collection_file)
        self.env = Environment(env_file)

    def request(self, group, name, updater=None):
        """Execute the Request found at ``self.collection[group][name]``."""
        request = self.collection[group][name]
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

        kwargs['json'] = kwargs.pop('body', None)

        return kwargs

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
