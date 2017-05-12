from invoke import task


@task
def dev(ctx):
    ctx.run('pip install -e .', pty=True)


@task
def lint(ctx):
    ctx.run('python setup.py check -rms')
    ctx.run('flake8 restcli/ tests/')


@task
def test(ctx):
    ctx.run('python setup.py test', pty=True)


