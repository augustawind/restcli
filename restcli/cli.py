import sys

import click
from click_repl import repl as start_repl

from version import VERSION
from restcli.app import App
from restcli.exceptions import (
    CollectionError,
    EnvError,
    InputError,
    LibError,
    NotFoundError,
    expect
)

pass_app = click.make_pass_decorator(App)


@click.group(invoke_without_command=True)
@click.version_option(
    VERSION, '-v', '--version',
    prog_name='restcli',
    message=' '.join((
        '%(prog)s %(version)s',
        '(Python %s)' % '.'.join(map(str, sys.version_info[:3])),
    )),
)
@click.option('-c', '--collection', envvar='RESTCLI_COLLECTION', required=True,
              type=click.Path(exists=True, dir_okay=False),
              help='Collection file.')
@click.option('-e', '--env', envvar='RESTCLI_ENV',
              type=click.Path(exists=True, dir_okay=False),
              help='Environment file.')
@click.option('-s/-S', '--save/--no-save', envvar='RESTCLI_AUTOSAVE',
              default=False,
              help='Save Environment to disk after changes.')
@click.pass_context
def cli(ctx, collection, env, save):
    if not ctx.obj:
        with expect(CollectionError, EnvError, LibError):
            ctx.obj = App(collection, env, autosave=save)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command(help='Run a Request.', context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('group')
@click.argument('request')
@click.argument('env_modifiers', nargs=-1, type=click.UNPROCESSED)
@pass_app
def run(app, group, request, env_modifiers):
    with expect(InputError, NotFoundError):
        output = app.run(group, request, *env_modifiers)
    click.echo(output)


@cli.command(help='View a Group, Request, or Request Parameter.')
@click.argument('group')
@click.argument('request', required=False)
@click.argument('attr', required=False)
@pass_app
def view(app, group, request, attr):
    with expect(NotFoundError):
        output = app.view(group, request, attr)
    click.echo(output)


@cli.command(help='View or set Environment variables.'
                  ' If no args are given, print the current environment.'
                  ' Otherwise, change the Environment via the given args.')
@click.argument('args', nargs=-1)
@pass_app
def env(app, args):
    if args:
        output = app.set_env(*args)
    else:
        output = app.show_env()
    click.echo(output)


@cli.command(help='Start an interactive prompt.')
@click.pass_context
def repl(ctx):
    # Define REPL-only commands here.
    # --------------------------------------------

    @cli.command(help='Reload Collection or Environment from disk.'
                      ' If no options are given, reload both.')
    @click.option('-c/-C', '--collection/--no-collection', default=False,
                  help='Reload the Collection.')
    @click.option('-e/-E', '--env/--no-env', default=False,
                  help='Reload the Environment.')
    @pass_app
    def reload(app, collection, env):
        output = ''
        if not (collection or env):
            collection = True
            env = True
        if collection:
            output += app.load_collection()
        if env:
            output += app.load_env()
        click.echo(output)

    @cli.command(help='Save the current Environment to disk.')
    @pass_app
    def save(app):
        output = app.save_env()
        click.echo(output)

    @cli.command(help='Change to and load a new Collection file.')
    @click.argument('path')
    @pass_app
    def change_collection(app, path):
        output = app.load_collection(path)
        click.echo(output)

    @cli.command(help='Change to and load a new Environment file.')
    @click.argument('path')
    @pass_app
    def change_env(app, path):
        output = app.load_env(path)
        click.echo(output)

    # Start REPL.
    # --------------------------------------------

    start_repl(ctx)
