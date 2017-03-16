import click

from restcli.app import App
from restcli.cmdprompt import Cmd


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
    ctx.obj = App(collection, env, autosave=save)


@cli.command(help='Run a Request.')
@click.argument('group')
@click.argument('request')
@click.argument('env', nargs=-1)
@click.pass_obj
def run(app, group, request, env):
    output = app.run(group, request, *env)
    click.echo(output)


@cli.command(help='View a Group, Request, or Request Attribute.')
@click.argument('group')
@click.argument('request', required=False)
@click.argument('attr', required=False)
@click.pass_obj
def view(app, group, request, attr):
    output = app.view(group, request, attr)
    click.echo(output)


@cli.command(help='Start an interactive command prompt.')
@click.pass_obj
def repl(app):
    cmd = Cmd(app, stdout=click.get_text_stream('stdout'))
    cmd.cmdloop()
