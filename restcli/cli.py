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
    expect
)

pass_app = click.make_pass_decorator(App)


@click.group()
@click.version_option(
    restcli.__version__, '-v', '--version',
    prog_name='restcli',
    message=' '.join((
        '%(prog)s %(version)s',
        '(Python %s)' % '.'.join(map(str, sys.version_info[:3])),
    )),
)
@click.option('-c', '--collection', envvar='RESTCLI_COLLECTION',
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


@cli.command(help='Run a Request.', context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('group')
@click.argument('request')
@click.argument('modifiers', nargs=-1, type=click.UNPROCESSED)
@click.option('-o', '--override-env', multiple=True,
              help='Override Environment variables.')
@pass_app
def run(app, group, request, modifiers, override_env):
    with expect(InputError, NotFoundError):
        output = app.run(group, request, modifiers=modifiers,
                         env_overrides=override_env)
    click.echo(output)


@cli.command(help='View a Group, Request, or Request Parameter.')
@click.argument('group')
@click.argument('request', required=False)
@click.argument('param', required=False)
@pass_app
def view(app, group, request, param):
    with expect(NotFoundError):
        output = app.view(group, request, param)
    click.echo(output)


@cli.command(help='View or set Environment variables.'
                  ' If no args are given, print the current environment.'
                  ' Otherwise, change the Environment via the given args.')
@click.argument('args', nargs=-1)
@pass_app
def env(app, args):
    if args:
        with expect(InputError):
            output = app.set_env(*args)
    else:
        output = app.show_env()
    click.echo(output)


@cli.command(help='Start an interactive prompt.')
@click.pass_context
def repl(ctx):
    # Define REPL-only commands here.
    # --------------------------------------------

    @cli.command(help='Reload Collection and Environment from disk.')
    @pass_app
    def reload(app):
        output = ''
        output += app.load_collection()
        output += app.load_env()
        click.echo(output)

    @cli.command(help='Save the current Environment to disk.')
    @pass_app
    def save(app):
        output = app.save_env()
        click.echo(output)

    @cli.command(help='Change to and load a new Collection file.')
    @click.argument('path', type=click.Path(exists=True, dir_okay=False))
    @pass_app
    def change_collection(app, path):
        output = app.load_collection(path)
        click.echo(output)

    @cli.command(help='Change to and load a new Environment file.')
    @click.argument('path', type=click.Path(exists=True, dir_okay=False))
    @pass_app
    def change_env(app, path):
        output = app.load_env(path)
        click.echo(output)

    # Start REPL.
    # --------------------------------------------

    start_repl(ctx)
