import json
from string import Template

import six
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer
from pygments.lexers.python import Python3Lexer
from pygments.lexers.textfmts import HttpLexer

from restcli import utils
from restcli.exceptions import (
    GroupNotFoundError,
    ParameterNotFoundError,
    RequestNotFoundError,
)
from restcli.reqmod import lexer, parser
from restcli.requestor import Requestor

__all__ = ["App"]


class App(object):
    """High-level execution logic for restcli.

    Args:
        collection_file: Path to a Collection file.
        env_file: Path to an Environment file.
        autosave: Whether to automatically save Env changes.
        style: Pygments style to use for rendering.

    Attributes:
        r (:class:`Requestor`): The Requestor object. Handles almost all I/O.
        autosave (bool): Whether to automatically save Env changes.
    """

    HTTP_TPL = Template(
        "\n".join(
            (
                "HTTP/${http_version} ${status_code} ${reason}",
                "${headers}",
                "${body}",
            )
        )
    )

    def __init__(
        self,
        collection_file: str,
        env_file: str,
        autosave: bool = False,
        quiet: bool = False,
        raw_output: bool = False,
        style: str = "fruity",
    ):
        self.r = Requestor(collection_file, env_file)
        self.autosave = autosave
        self.quiet = quiet
        self.raw_output = raw_output

        self.http_lexer = HttpLexer()
        self.json_lexer = JsonLexer()
        self.python_lexer = Python3Lexer()
        self.formatter = Terminal256Formatter(style=style)

    def run(
        self,
        group_name: str,
        request_name: str,
        modifiers: list = None,
        env_args: list = None,
        save: bool = None,
        quiet: bool = None,
    ) -> str:
        """Run a Request.

        Args:
            group_name: A :class:`Group` name in the Collection.
            request_name: A :class:`Request` name in the Collection.
            modifiers (optional): List of :class:`Request` modifiers.
            env_args (optional): List of :class:`Environment` overrides.
            save (optional): Whether to save Env changes to disk.
            quiet (optional): Whether to suppress output.

        Returns:
            The command output.
        """
        # Make sure Request exists.
        group = self.get_group(group_name, action="run")
        self.get_request(group, group_name, request_name, action="run")

        # Parse modifiers.
        lexemes = lexer.lex(modifiers)
        updater = parser.parse(lexemes)

        response = self.r.request(group_name, request_name, updater, *env_args)

        if utils.select_first(save, self.autosave):
            self.r.env.save()

        output = self.show_response(response, quiet=quiet)
        return output

    def view(
        self,
        group_name: str,
        request_name: str = None,
        param_name: str = None,
        apply_env: bool = False,
    ) -> str:
        """Inspect a Group, Request, or Request Parameter.

        Args:
            group_name: The Group to inspect.
            request_name: The Request to inspect.
            param_name: The Request Parameter to inspect.
            apply_env: Whether to render with Environment variables inserted.

        Returns:
            The requested object in JSON, colorized.
        """
        output_obj = group = self.get_group(
            group_name, action="view", apply_env=apply_env
        )

        if request_name:
            output_obj = request = self.get_request(
                group, group_name, request_name, action="view"
            )

            if param_name:
                output_obj = param = self.get_request_param(
                    request,
                    group_name,
                    request_name,
                    param_name,
                    action="view",
                )

                if param_name == "script":
                    return self.highlight(param, self.python_lexer)

                if param_name == "headers":
                    headers = dict(
                        l.split(":") for l in param.strip().split("\n")
                    )
                    output = self.key_value_pairs(headers)
                    return self.highlight(output, self.http_lexer)

        output = self.fmt_json(output_obj)
        return self.highlight(output, self.json_lexer)

    def get_group(self, group_name, action, apply_env=False):
        """Retrieve a Group object."""
        try:
            group = self.r.collection[group_name]
        except KeyError:
            raise GroupNotFoundError(
                file=self.r.collection.source,
                action=action,
                path=[group_name],
            )

        if apply_env:
            # Apply Environment to all Requests
            group = {
                request_name: self.r.parse_request(request, self.r.env)
                for request_name, request in group.items()
            }

        return group

    def get_request(self, group, group_name, request_name, action):
        """Retrieve a Request object."""
        try:
            return group[request_name]
        except KeyError:
            raise RequestNotFoundError(
                file=self.r.collection.source,
                action=action,
                path=[group_name, request_name],
            )

    def get_request_param(
        self, request, group_name, request_name, param_name, action
    ):
        """Retrieve a Request Parameter."""
        try:
            return request[param_name]
        except KeyError:
            raise ParameterNotFoundError(
                file=self.r.collection.source,
                action=action,
                path=[group_name, request_name, param_name],
            )

    def load_collection(self, source=None):
        """Reload the current Collection, changing it to `source` if given."""
        if source:
            self.r.collection.source = source
        self.r.collection.load()
        return ""

    def load_env(self, source=None):
        """Reload the current Environment, changing it to `source` if given."""
        if source:
            self.r.env.source = source
        self.r.env.load()
        return ""

    def set_env(self, *env_args, save=False):
        """Set some new variables in the Environment."""
        self.r.mod_env(env_args, save=save or self.autosave)
        return ""

    def save_env(self):
        """Save the current Environment to disk."""
        self.r.env.save()
        return ""

    def show_env(self):
        """Return a formatted representation of the current Environment."""
        if self.r.env:
            output = self.fmt_json(self.r.env)
            return self.highlight(output, self.json_lexer)
        return "No Environment loaded."

    def show_response(self, response, quiet=None):
        """Format an HTTP Response."""
        if utils.select_first(quiet, self.quiet):
            return ""

        if response.headers.get("Content-Type", None) == "application/json":
            try:
                body = self.fmt_json(response.json())
            except json.JSONDecodeError:
                body = response.text
        else:
            body = response.text

        if self.raw_output:
            http_txt = body
        else:
            http_txt = self.HTTP_TPL.substitute(
                http_version=str(float(response.raw.version) / 10),
                status_code=response.status_code,
                reason=response.reason,
                headers=self.key_value_pairs(response.headers),
                body=body,
            )
        return self.highlight(http_txt, self.http_lexer)

    def highlight(self, code, pygments_lexer):
        """Highlight the given code.

        If ``self.raw_output`` is True, return ``code`` unaltered.
        """
        if self.raw_output:
            return code
        return highlight(code, pygments_lexer, self.formatter)

    def fmt_json(self, data):
        if self.raw_output:
            return json.dumps(data)
        return json.dumps(data, indent=2)

    @staticmethod
    def key_value_pairs(obj):
        """Format a dict-like object into lines of 'KEY: VALUE'."""
        return "\n".join(["%s: %s" % (k, v) for k, v in six.iteritems(obj)])
