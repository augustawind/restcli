from invoke import task

PKG = "restcli"
TAG = "restcli"

# ----------------------------------------------------------------------
# Development


@task()
def clean(ctx):
    """Delete build files."""
    ctx.run("rm -rf `find . -name __pycache__`", pty=True)
    ctx.run("rm -f `find . -type f -name '*.py[co]' `", pty=True)
    ctx.run("rm -f `find . -type f -name '*~' `", pty=True)
    ctx.run("rm -f `find . -type f -name '.*~' `", pty=True)
    ctx.run("rm -rf .cache", pty=True)
    ctx.run("rm -rf htmlcov", pty=True)
    ctx.run("rm -rf *.egg-info", pty=True)
    ctx.run("rm -f .coverage", pty=True)
    ctx.run("rm -f .coverage.*", pty=True)


@task()
def fmt(ctx, check=False):
    """Run the formatters."""
    opts = check and " --check" or ""
    cmd = f"black{opts} --line-length=79 --exclude='docs' ."
    ctx.run(cmd, pty=True)

    opts = check and " --check-only" or ""
    cmd = (
        f"isort{opts} --trailing-comma --use-parentheses --line-width=79"
        " --force-grid-wrap=0 --multi-line=3 --skip=docs --skip=setup.py ."
    )
    ctx.run(cmd, pty=True)


@task()
def lint(ctx, verbose=False):
    """Run the linter(s)."""
    opts = " -v" if verbose else ""
    cmd = f"pylint{opts} {PKG}"
    ctx.run(cmd, pty=True)


@task()
def test(ctx, verbose=False):
    """Run unit tests."""
    opts = " -v" if verbose else ""
    cmd = f"pytest{opts}"
    ctx.run(cmd, pty=True)


@task(aliases=("cov",))
def coverage(ctx, html=False):
    """Run unit tests and generate a coverage report."""
    ctx.run(f"pytest --cov={PKG}", pty=True)
    if html:
        ctx.run("coverage html", pty=True)


# ----------------------------------------------------------------------
# Installation


@task()
def docs(ctx, target="html"):
    cmd = f"cd docs && make {target}"
    ctx.run(cmd, pty=True)


@task(aliases=("deps",))
def dependencies(ctx):
    ctx.run("pip install -r requirements.txt", pty=True)


@task(aliases=("i",))
def install(ctx, editable=False):
    """Install the app and its dependencies using pip.

    If the --editable option is given, install it with the -e flag.
    """
    opts = " -e" if editable else ""
    cmd = f"pip install{opts} ."
    ctx.run(cmd, pty=True)


# ----------------------------------------------------------------------
# Docker


@task(iterable=["arg"])
def docker(ctx, arg, clean=False):
    opts = clean and " --force-rm --no-cache" or ""
    build_args = "".join(f" --build-arg {a}" for a in arg)
    cmd = f"docker build{opts}{build_args} -t {TAG} ."
    ctx.run(cmd, pty=True)


@task(iterable=["env"])
def run(ctx, run_cmd, env):
    env_args = "".join(f" --env {e}" for e in env)
    cmd = f"docker run{env_args} -it {TAG} {run_cmd}"
    ctx.run(cmd, pty=True)


# ----------------------------------------------------------------------
# Composite tasks


# TODO: configure linter properly
# @task(aliases=("x",), pre=(clean, fmt, lint), post=(test,))
@task(aliases=("x",), pre=(clean, fmt), post=(test,))
def check(ctx):
    """Run unit tests and sanity checks."""
    ctx.run("python setup.py check -rms", pty=True)


@task(default=True, pre=(dependencies, check))
def build(ctx, editable=False):
    """Safely build the app, running checks and installing."""
    install(ctx, editable)
