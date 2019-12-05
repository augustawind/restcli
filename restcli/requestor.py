import re
from contextlib import contextmanager
from typing import Optional, Union

import jinja2
import requests

from restcli import yaml_utils as yaml
from restcli.exceptions import InputError
from restcli.reqmod.updater import Updater
from restcli.workspace import Collection, Environment

__all__ = ["Requestor"]

ENV_RE = re.compile(r"([^:]+):(.*)")


class Requestor:
    """Parser and executor of requests."""

    def __init__(
        self,
        collection: Union[Collection, str],
        env: Optional[Union[Environment, str]] = None,
    ):
        if isinstance(collection, Collection):
            self.collection = collection
        else:
            self.collection = Collection(collection)
        if isinstance(env, Environment):
            self.env = env
        else:
            self.env = Environment(env)

    def request(self, group, name, updater=None, *env_args):
        """Execute the Request found at ``self.collection[group][name]``."""
        request = self.collection[group][name]

        with self.override_env(env_args):
            request_kwargs = self.prepare_request(request, self.env, updater)

        response = requests.request(**request_kwargs)

        script = request.get("script")
        if script:
            script_locals = {"response": response, "env": self.env}
            if self.collection.libs:
                for lib in self.collection.libs.values():
                    script_locals.update(lib.define(response, self.env))
            self.run_script(script, script_locals)

        return response

    @classmethod
    def prepare_request(
        cls, request: dict, env: Environment, updater: Optional[Updater] = None
    ):
        """Prepare a Request to be executed."""
        request = {
            k: request.get(k)
            for k in ("method", "url", "query", "headers", "body")
        }
        kwargs = cls.parse_request(request, env, updater)

        kwargs["json"] = kwargs.pop("body")
        kwargs["params"] = kwargs.pop("query")

        return kwargs

    @classmethod
    def parse_request(
        cls, request: dict, env: Environment, updater: Optional[Updater] = None
    ):
        """Parse a Request object in the context of an Environment."""
        kwargs = {
            **request,
            "method": request["method"],
            "url": env.interpolate(request["url"]),
            "query": {},
            "headers": {},
            "body": {},
        }

        body = request.get("body")
        if body:
            kwargs["body"] = env.interpolate(body)
        headers = request.get("headers")
        if headers:
            kwargs["headers"] = {
                k: env.interpolate(v) for k, v in headers.items()
            }
        query = request.get("query")
        if query:
            kwargs["query"] = env.interpolate(query)

        if updater:
            updater.apply(kwargs)

        return kwargs

    @contextmanager
    def override_env(self, env_args):
        """Temporarily modify an Environment with the given overrides.

        On exit, the Env is returned to its previous state.
        """
        original = self.env.data
        self.mod_env(env_args)

        yield

        self.env.clear()
        self.env.update(original)

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
            if arg.startswith("!"):
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
                    msg="Error: args must take one of the forms `!KEY` or"
                    " `KEY:VAL`, where `KEY` is a string and `VAL` is a"
                    " valid YAML value.",
                    action="env",
                )
            key, val = match.groups()
            set_env[key.strip()] = yaml.load(val)
        return set_env, del_env

    @staticmethod
    def run_script(script, script_locals):
        """Run a Request script with a Response and Environment as context."""
        code = compile(script, "<<script>>", "exec")
        exec(code, script_locals)
