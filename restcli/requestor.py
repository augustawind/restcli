from collections import Mapping

import jinja2
import requests

from restcli import yaml_utils as yaml
from restcli.workspace import Collection, Environment

REQUIRED_REQ_ATTRS = ('method', 'url')
REQ_ATTRS = REQUIRED_REQ_ATTRS + ('headers', 'body', 'script')


class Requestor:
    """Parser and executor of requests."""

    def __init__(self, collection_file, env_file=None):
        self.collection = Collection(collection_file)
        self.env = Environment(env_file)

    def request(self, group, name, **env_override):
        """Execute the Request found at ``self.collection[group][name]``."""
        request = self.collection[group][name]
        request_kwargs = self.parse_request(request, self.env, **env_override)
        response = requests.request(**request_kwargs)

        script = request.get('script')
        if script:
            self.run_script(script, response, self.env)

        return response

    @classmethod
    def parse_request(cls, request, env, **env_override):
        """Parse a Request object in the context of an Environment."""
        env = {**env, **env_override}
        obj = {
            'method': request['method'],
            'url': cls.interpolate(request['url'], env),
        }

        body = request.get('body')
        if body:
            obj['json'] = cls.interpolate(body, env)

        headers = request.get('headers')
        if headers:
            obj['headers'] = {k: cls.interpolate(v, env)
                              for k, v in headers.items()}

        return obj

    @staticmethod
    def interpolate(data, env):
        """Given some ``data``, render it with the given ``env``."""
        tpl = jinja2.Template(data)
        rendered = tpl.render(env)
        return yaml.load(rendered)

    @staticmethod
    def run_script(script, response, env):
        """Run a Request script with a Response and Environment as context."""
        exec(script, {'response': response, 'env': env})

    def save_env(self):
        """Save ``self.env`` to ``self.env_path``."""
        with open(self.env_file, 'w') as handle:
            return yaml.dump(self.env, handle)
