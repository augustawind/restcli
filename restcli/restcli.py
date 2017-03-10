import json
import os

import jinja2
import requests
import yaml

class Requestor:
    """Thing that reads config and makes requests."""

    def __init__(self, groups_file, env_file):
        # TODO: validate input
        # TODO: split this out into one or two "load" functions
        self.groups = self.load_config(groups_file)
        self.env = self.load_config(env_file)

    @staticmethod
    def load_config(path):
        """Load a JSON or YAML config file with the given ``path``."""
        _, ext = os.path.splitext(path)
        if ext == '.json':
            loader = json.load
        elif ext == '.yaml':
            loader = yaml.safe_load
        else:
            raise ValueError("Invalid file extension '{}'. Supported"
                             " extensions are .yaml and .json.".format(ext))

        with open(path) as handle:
            return loader(handle)

    @staticmethod
    def interpolate(data, env):
        """Given some ``data``, render it with the given ``env``."""
        raw = json.dumps(data)
        tpl = jinja2.Template(raw)
        rendered = tpl.render(env)
        return json.loads(rendered)

    def request(self, group, name):
        """Execute the request with the given ``name`` in the given ``group``."""
        request = self.groups[group][name]

        method = request['method']
        headers = request['headers']
        url = self.interpolate(request['url'], self.env)
        body = self.interpolate(request['body'], self.env)

        response = requests.request(method, url, headers=headers, json=body)

        # TODO: Run scripts here

        return response
