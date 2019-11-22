import shlex
import sys

import click
from click_repl import repl as start_repl

import restcli
from restcli.app import App
from restcli.exceptions import (
    CollectionError,
    EnvError,
    InputError,
    LibError,
    NotFoundError,
    expect,
)

pass_app = click.make_pass_decorator(App)


@click.group()
@click.version_option(
    restcli.__version__,
    "-v",
    "--version",
    prog_name="restcli",
    message=(
        "%(prog)s %(version)s"
        f" (Python {'.'.join(map(str, sys.version_info[:3]))})"
    ),
)
@click.option(
    "-c",
    "--collection",
    envvar="RESTCLI_COLLECTION",
    type=click.Path(exists=True, dir_okay=False),
    help="Collection file.",
)
@click.option(
    "-e",
    "--env",
    envvar="RESTCLI_ENV",
    type=click.Path(exists=True, dir_okay=False),
    help="Environment file.",
)
@click.option(
    "-s/-S",
    "--save/--no-save",
    envvar="RESTCLI_AUTOSAVE",
    default=False,
    help="Save Environment to disk after changes.",
)
@click.option(
    "-q/-Q",
    "--quiet/--no-quiet",
    envvar="RESTCLI_QUIET",
    default=False,
    help="Suppress HTTP output.",
)
@click.option(
    "-r/-R",
    "--raw-output/--no-raw-output",
    envvar="RESTCLI_RAW_OUTPUT",
    default=False,
    help="Don't color or format output.",
)
@click.pass_context
def cli(ctx, collection, env, save, quiet, raw_output):
    if not ctx.obj:
        with expect(CollectionError, EnvError, LibError):
            ctx.obj = App(
                collection,
                env,
                autosave=save,
                quiet=quiet,
                raw_output=raw_output,
            )


@cli.command(
    help="Run a Request.", context_settings=dict(ignore_unknown_options=True,)
)
@click.argument("group")
@click.argument("request")
@click.argument("modifiers", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "-o",
    "--override-env",
    multiple=True,
    help="Override Environment variables.",
)
@pass_app
def run(app, group, request, modifiers, override_env):
    with expect(InputError, NotFoundError):
        output = app.run(
            group, request, modifiers=modifiers, env_args=override_env
        )
    click.echo(output)


@cli.command(
    help="""Run multiple Requests from a file.

If '-' is given, stdin will be used. Lines beginning with '#' are ignored. Each
line in the file should specify args for a single "run" invocation:

    [OPTIONS] GROUP REQUEST [MODIFIERS]...
"""
)
@click.argument("file", type=click.File())
@click.pass_context
def exec(ctx, file):
    for line in file:
        line = line.strip()
        if line.startswith("#"):
            continue
        click.echo(">>> run %s" % line)
        args = shlex.split(line)
        try:
            run(args, prog_name="restcli", parent=ctx)
        except SystemExit:
            continue


@cli.command(help="View a Group, Request, or Request Parameter.")
@click.argument("group")
@click.argument("request", required=False)
@click.argument("param", required=False)
@click.option(
    "-r/-R",
    "--render/--no-render",
    default=False,
    help="Render with Environment variables.",
)
@pass_app
def view(app, group, request, param, render):
    with expect(NotFoundError):
        output = app.view(group, request, param, render)
    click.echo(output)


@cli.command(
    help="View or set Environment variables."
    " If no args are given, print the current environment."
    " Otherwise, change the Environment via the given args."
)
@click.argument("args", nargs=-1)
@pass_app
def env(app, args):
    if args:
        with expect(InputError):
            output = app.set_env(*args)
    else:
        output = app.show_env()
    click.echo(output)


@cli.command(help="Start an interactive prompt.")
@click.pass_context
def repl(ctx):
    # Define REPL-only commands here.
    # --------------------------------------------

    @cli.command(help="Reload Collection and Environment from disk.")
    @pass_app
    def reload(app):
        output = ""
        output += app.load_collection()
        output += app.load_env()
        click.echo(output)

    @cli.command(help="Save the current Environment to disk.")
    @pass_app
    def save(app):
        output = app.save_env()
        click.echo(output)

    @cli.command(help="Change to and load a new Collection file.")
    @click.argument("path", type=click.Path(exists=True, dir_okay=False))
    @pass_app
    def change_collection(app, path):
        output = app.load_collection(path)
        click.echo(output)

    @cli.command(help="Change to and load a new Environment file.")
    @click.argument("path", type=click.Path(exists=True, dir_okay=False))
    @pass_app
    def change_env(app, path):
        output = app.load_env(path)
        click.echo(output)

    # Start REPL.
    # --------------------------------------------

    start_repl(ctx)
