import os
import shlex
import sys

from invoke import task, util


in_ci = os.environ.get("CI", "false") == "true"
if in_ci:
    pty = False
else:
    pty = util.isatty(sys.stdout) and util.isatty(sys.stderr)


@task
def reformat(c):
    c.run("isort freiner tests setup.py tasks.py", pty=pty)
    c.run("black freiner tests setup.py tasks.py docs/source/conf.py", pty=pty)


@task
def lint(c):
    c.run("flake8 --show-source --statistics freiner tests", pty=pty)
    # TODO: start using pydocstyle
    # Gotta use pydocstyle directly rather than through the flake8 config, because the flake8
    # plugin doesn't support configuring pydocstyle sensibly.

    c.run("check-manifest", pty=pty)

    bandit_args = ["bandit", "--configfile", "bandit.yaml", "-r"]
    if pty:
        bandit_args.extend(("-f", "screen"))
    if not in_ci:
        bandit_args.append("--quiet")
    bandit_args.extend(("freiner", "tests"))
    c.run(" ".join(bandit_args), pty=pty)


@task
def test(c, onefile=""):
    pytest_args = ["pytest", "--strict-config", "--cov=freiner", "--cov-report=term-missing"]
    if in_ci:
        pytest_args.extend(("--cov-report=xml", "--strict-markers"))
    else:
        pytest_args.append("--cov-report=html")

    if onefile:
        pytest_args.append(shlex.quote(onefile))

    c.run("docker-compose down --remove-orphans --volumes", pty=pty)
    c.run("docker-compose up -d", pty=pty)
    try:
        c.run(" ".join(pytest_args), pty=pty)
    finally:
        c.run("docker-compose down --remove-orphans --volumes", pty=pty)

        c.run("rm .docker/memcached/freiner.memcached.sock", pty=pty, warn=True)
        c.run("rm .docker/redis/freiner.redis.sock", pty=pty, warn=True)


@task
def type_check(c):
    c.run("mypy freiner tests", pty=pty)


@task
def docs(c):
    with c.cd("docs"):
        c.run("sphinx-build -M html source build -a -W", pty=pty)
