from collections import Mapping

import jinja2
import requests

from restcli import yaml_utils as yaml
from restcli.exceptions import InvalidConfig

REQUIRED_REQ_ATTRS = ('method', 'url')
REQ_ATTRS = REQUIRED_REQ_ATTRS + ('headers', 'body', 'script')


class Requestor:
    """Thing that reads config and makes requests."""

    def __init__(self, collection_file, env_file=None):
        self.collection_file = collection_file
        self.env_file = env_file
        self.collection = {}
        self.env = {}
        self.load_workspace()

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

    def load_workspace(self, collection_file=None, env_file=None):
        """Load all the config files."""
        self.load_collection(collection_file)
        self.load_env(env_file)

    def load_collection(self, path=None):
        """Reload the current Collection, changing it to ``path`` if given."""
        if path:
            self.collection_file = path
        if self.collection_file:
            with open(self.collection_file) as handle:
                data = yaml.load(handle, many=True)

            if len(data) == 1:
                meta, collection = {}, data[0]
            elif len(data) == 2:
                meta, collection = data
            else:
                raise InvalidConfig(
                    message='Collection can have at most two documents')

            self.apply_meta(collection, meta)
            self.collection = collection

    def load_env(self, path=None):
        """Reload the current Env, changing it to ``path`` if given."""
        if path:
            self.env_file = path
        if self.env_file:
            with open(self.env_file) as handle:
                self.env = yaml.load(handle)

    def apply_meta(self, collection, meta):
        """Apply Collection Meta to a Collection. Mutates ``collection``."""
        defaults = meta.get('defaults')
        if defaults:
            self.assert_mapping(defaults, 'Defaults', 'Meta.Defaults')
        else:
            defaults = {}

        for group_name, group in collection.items():
            path = 'Collection."%s"' % group_name
            self.assert_mapping(group, 'Group', path)
            for req_name, request in group.items():
                path += '."%s"' % req_name
                self.assert_mapping(request, 'Request', path)
                for key in REQ_ATTRS:
                    if key not in request and key in defaults:
                        request[key] = defaults[key]
                    self.validate_request(request, group_name, req_name)

    def set_env(self, **kwargs):
        """Update ``self.env`` with ``kwargs``."""
        self.env.update(kwargs)

    def del_env(self, *args):
        """Remove all ``args`` from ``self.env``."""
        for var in args:
            try:
                del self.env[var]
            except KeyError:
                pass

    def save_env(self):
        """Save ``self.env`` to ``self.env_path``."""
        with open(self.env_file, 'w') as handle:
            return yaml.dump(self.env, handle)

    def assert_type(self, obj, type, msg, path):
        if not isinstance(obj, type):
            raise InvalidConfig(
                message=msg, file=self.collection_file, path=path)

    def assert_mapping(self, obj, name, path):
        msg = '%s must be a mapping object' % name
        self.assert_type(obj, Mapping, msg, path)

    def validate_request(self, request, group_name, request_name):
        path = 'Collection."%s"."%s"' % (group_name, request_name)

        for attr in REQUIRED_REQ_ATTRS:
            if attr not in request:
                raise InvalidConfig(
                    file=self.collection_file,
                    path=path,
                    message='Required attribute "%s" not found' % attr,
                )

        headers = request.get('headers')
        if headers:
            self.assert_mapping(headers, 'Request headers', path)
