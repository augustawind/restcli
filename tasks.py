from invoke import task


@task
def lint(ctx):
    """Run the linter(s)."""
    ctx.run('flake8 restcli/ tests/')


@task
def test(ctx):
    """Run the unit tests."""
    ctx.run('python setup.py test', pty=True)


@task
def dev(ctx):
    """Install the app in editable mode."""
    ctx.run('pip install -e .', pty=True)


@task
def install(ctx):
    """Install the app."""
    ctx.run('pip install -U pip setuptools')
    ctx.run('pip install .')
    ctx.run('pip install -r requirements.txt')


@task
def clean(ctx):
    """Delete build files."""
    ctx.run('rm -rf `find . -name __pycache__`')
    ctx.run("rm -f `find . -type f -name '*.py[co]' `")
    ctx.run("rm -f `find . -type f -name '*~' `")
    ctx.run("rm -f `find . -type f -name '.*~' `")
    ctx.run('rm -rf .cache')
    ctx.run('rm -rf htmlcov')
    ctx.run('rm -rf *.egg-info')
    ctx.run('rm -f .coverage')
    ctx.run('rm -f .coverage.*')
    ctx.run('rm -rf build')
    ctx.run('python setup.py check -rms')
