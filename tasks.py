from invoke import task

# ----------------------------------------------------------------------
# Simple tasks


@task(aliases=('cl',))
def clean(ctx):
    """Delete build files."""
    ctx.run('rm -rf `find . -name __pycache__`', pty=True)
    ctx.run("rm -f `find . -type f -name '*.py[co]' `", pty=True)
    ctx.run("rm -f `find . -type f -name '*~' `", pty=True)
    ctx.run("rm -f `find . -type f -name '.*~' `", pty=True)
    ctx.run('rm -rf .cache', pty=True)
    ctx.run('rm -rf htmlcov', pty=True)
    ctx.run('rm -rf *.egg-info', pty=True)
    ctx.run('rm -f .coverage', pty=True)
    ctx.run('rm -f .coverage.*', pty=True)


@task(aliases=('l',))
def lint(ctx):
    """Run the linter(s)."""
    ctx.run('flake8 restcli/ tests/', pty=True)


@task(aliases=('t',))
def test(ctx):
    """Run unit tests."""
    ctx.run('pytest', pty=True)


@task(aliases=('cov',))
def coverage(ctx, html=False):
    """Run unit tests and generate a coverage report."""
    ctx.run('pytest --cov=restcli', pty=True)
    ctx.run('coverage combine', pty=True)
    if html:
        ctx.run('coverage html', pty=True)


@task(aliases=('deps',))
def dependencies(ctx):
    ctx.run('pip install -r requirements.txt', pty=True)


@task(aliases=('i',))
def install(ctx, editable=False):
    """Install the app and its dependencies using pip.

    If the --editable option is given, install it with the -e flag.
    """
    cmd = 'pip install{} .'.format(' -e' if editable else '')
    ctx.run(cmd, pty=True)


# ----------------------------------------------------------------------
# Composite tasks


@task(aliases=('ch',), pre=(clean, lint), post=(test,))
def check(ctx):
    """Run unit tests and sanity checks."""
    ctx.run('python setup.py check -rms', pty=True)


@task(default=True, aliases=('b',), pre=(dependencies, check, install))
def build(ctx, editable=False):
    """Safely build the app, running checks and installing."""
    pass
