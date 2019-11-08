from invoke import task

TAG = 'restcli'

# ----------------------------------------------------------------------
# Simple tasks


@task()
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


@task()
def lint(ctx, verbose=False):
    """Run the linter(s)."""
    opts = ' -v' if verbose else ''
    cmd = 'pylint%s restcli' % opts
    ctx.run(cmd, pty=True)


@task()
def test(ctx, verbose=False):
    """Run unit tests."""
    opts = '-v' if verbose else ''
    cmd = 'pytest %s' % opts
    ctx.run(cmd, pty=True)


@task(aliases=('cov',))
def coverage(ctx, html=False):
    """Run unit tests and generate a coverage report."""
    ctx.run('pytest --cov=restcli', pty=True)
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
    opts = '-e' if editable else ''
    cmd = 'pip install %s .' % opts
    ctx.run(cmd, pty=True)


@task()
def docker(ctx, clean=False, run=True):
    opts = '--force-rm --no-cache' if clean else ''
    cmd = 'docker build %s -t %s .' % (opts, TAG)
    ctx.run(cmd, pty=True)


@task()
def run(ctx, run_cmd):
    cmd = 'docker run -it %s %s' % (TAG, run_cmd)
    ctx.run(cmd, pty=True)


@task()
def docs(ctx, target='html'):
    cmd = 'cd docs && make %s' % target
    ctx.run(cmd, pty=True)


# ----------------------------------------------------------------------
# Composite tasks


@task(aliases=('x',), pre=(clean, lint), post=(test,))
def check(ctx):
    """Run unit tests and sanity checks."""
    ctx.run('python setup.py check -rms', pty=True)


@task(default=True, pre=(dependencies, check))
def build(ctx, editable=False):
    """Safely build the app, running checks and installing."""
    install(ctx, editable)
