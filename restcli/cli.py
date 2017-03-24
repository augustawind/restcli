import click

from restcli.app import App
from restcli.cmdprompt import Cmd
from restcli.exceptions import FileContentError, expect

pass_app = click.make_pass_decorator(App)


@click.group()
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
    with expect(FileContentError):
        ctx.obj = App(collection, env, autosave=save)


@cli.command(help='Run a Request.')
@click.argument('group')
@click.argument('request')
@click.option('-o', '--override', multiple=True)
@pass_app
def run(app, group, request, override):
    output = app.run(group, request, *override)
    click.echo(output)


@cli.command(help='View a Group, Request, or Request Attribute.')
@click.argument('group')
@click.argument('request', required=False)
@click.argument('attr', required=False)
@pass_app
def view(app, group, request, attr):
    output = app.view(group, request, attr)
    click.echo(output)


@cli.command(help='Start an interactive command prompt.')
@pass_app
def repl(app):
    cmd = Cmd(app, stdout=click.get_text_stream('stdout'))
    cmd.cmdloop()
