import jinja2
import requests

from restcli.utils import dump_ordered, load_ordered


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
        body = request.get('body')
        headers = request.get('headers')
        return {
            'method': request['method'],
            'url': cls.interpolate(request['url'], env),
            'headers': cls.interpolate(headers, env) if headers else None,
            'json': cls.interpolate(body, env) if body else None,
        }

    @staticmethod
    def interpolate(data, env):
        """Given some ``data``, render it with the given ``env``."""
        tpl = jinja2.Template(data)
        rendered = tpl.render(env)
        return load_ordered(rendered)

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
            collections = self.load_file(self.collection_file)
            self.validate_collections(collections)
            self.collection = collections

    def load_env(self, path=None):
        """Reload the current Env, changing it to ``path`` if given."""
        if path:
            self.env_file = path
        if self.env_file:
            self.env = self.load_file(self.env_file)

    @staticmethod
    def load_file(path):
        """Load a  YAML config file with the given ``path``."""
        with open(path) as handle:
            return load_ordered(handle)

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
            return dump_ordered(self.env, handle)

    @staticmethod
    def validate_collections(collections):
        """Validate that the given collections are valid."""
        # TODO: Add more validation
        for group_name, group in collections.items():
            for req_name, request in group.items():
                assert 'method' in request, (
                    'Missing required field: "method"\n'
                    'Group "{}", Request "{}"'.format(group_name, req_name)
                )
                assert 'url' in request, (
                    'Missing required field: "url"\n'
                    'Group "{}", Request "{}"'.format(group_name, req_name)
                )
