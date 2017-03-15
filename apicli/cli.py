import click

from apicli.app import App
from apicli.icli import Cmd


@click.group()
@click.option('-c', '--collection', envvar='APICLI_COLLECTION',
              type=click.Path(exists=True, dir_okay=False))
@click.option('-e', '--env', envvar='APICLI_ENV',
              type=click.Path(exists=True, dir_okay=False))
@click.option('-s', '--save/--no-save', default=False)
@click.pass_context
def cli(ctx, collection, env, save):
    ctx.obj = App(collection, env, autosave=save)


@cli.command()
@click.argument('group')
@click.argument('request')
@click.pass_obj
def run(app, group, request):
    output = app.run(group, request)
    click.echo(output)


@cli.command()
@click.argument('group')
@click.argument('request', required=False)
@click.argument('attr', required=False)
@click.pass_obj
def view(app, group, request, attr):
    output = app.view(group, request, attr)
    click.echo(output)


@cli.command()
@click.pass_obj
def repl(app):
    cmd = Cmd(app)  # , ctx.save)
    cmd.cmdloop()
