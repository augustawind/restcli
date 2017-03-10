import os
import http

import jinja2
import requests
import yaml

class Requestor:
    """Thing that reads config and makes requests."""

    def __init__(self, groups_file, env_file):
        self.groups_file = groups_file
        self.env_file = env_file
        self.load_config()

    def load_config(self):
        """Load all the config files."""
        groups = self.load_file(self.groups_file)
        self.validate_groups(groups)

        self.groups = groups
        self.env = self.load_file(self.env_file)

    @staticmethod
    def validate_groups(groups):
        """Validate that the given groups are valid."""
        # TODO: Add more validation
        for group_name, group in groups.items():
            for req_name, request in group.items():
                assert 'method' in request, (
                    'Missing required field: "method"\n'
                    'Group "{}", Request "{}"'.format(group_name, req_name)
                )
                assert 'url' in request, (
                    'Missing required field: "url"\n'
                    'Group "{}", Request "{}"'.format(group_name, req_name)
                )

    @staticmethod
    def load_file(path):
        """Load a JSON or YAML config file with the given ``path``."""
        _, ext = os.path.splitext(path)
        if ext == '.yaml':
            loader = yaml.safe_load
        else:
            raise ValueError("Invalid file extension '{}'. Supported"
                             " extensions are .yaml.".format(ext))

        with open(path) as handle:
            return loader(handle)

    @staticmethod
    def interpolate(data, env):
        """Given some ``data``, render it with the given ``env``."""
        tpl = jinja2.Template(data)
        rendered = tpl.render(env)
        return yaml.load(rendered)

    @classmethod
    def parse_request(cls, request, env):
        body = request.get('body')
        headers = request.get('headers')
        return {
            'method': request['method'],
            'url': cls.interpolate(request['url'], env),
            'headers': cls.interpolate(headers, env) if headers else None,
            'json': cls.interpolate(body, env) if body else None,
        }

    @staticmethod
    def run_script(script, response, env):
        exec(script, {'response': response, 'env': env})

    def request(self, group, name):
        """Execute the request with the given ``name`` in the given ``group``."""
        request = self.groups[group][name]
        scripts = request.get('scripts', {})
        request_kwargs = self.parse_request(request, self.env)
        response = requests.request(**request_kwargs)

        post_request = scripts.get('post_request')
        if post_request:
            self.run_script(post_request, response, self.env)

        return response

    def save_env(self):
        """Save ``self.env`` to ``self.env_path``."""
        _, ext = os.path.splitext(self.env_file)
        if ext == '.yaml':
            dumper = yaml.safe_dump
        else:
            raise ValueError("Invalid file extension '{}'. Supported"
                             " extensions are .yaml.".format(ext))

        with open(self.env_file, 'w') as handle:
            return dumper(self.env, handle)

