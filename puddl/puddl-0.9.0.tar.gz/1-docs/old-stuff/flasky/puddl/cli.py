import logging
import socket

import click
import pendulum

import puddl
import puddl.config

log = logging.getLogger(__name__)
LOG_LEVELS = ["CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG"]


@click.group()
@click.option("--debug/--no-debug")
@click.option(
    "--log-level", type=click.Choice(LOG_LEVELS, case_sensitive=False), default="INFO"
)
def root(debug, log_level):
    if debug:
        logging.basicConfig(level="DEBUG")
        log.debug(f'debug mode enabled (run "PUDDL_DEBUG=false" to disable)')
    else:
        logging.basicConfig(level=log_level)
    puddl.config.read()


@root.command()
def date():
    dt = pendulum.now()
    print(dt.format("YYYY-MM-DD__HH-mm-ss__ZZ"))


_default_source = socket.gethostname()


@root.command()
@click.option("--db/--no-db", default=True)
def setup(db):
    puddl.config.from_env()
    puddl.config.write()
    if db:
        puddl.get_db().migrate()


@root.command()
@click.option("-s", "--source")
@click.option("--dump", default=False)
@click.argument("file", type=click.Path(exists=True), nargs=-1)
def index(source, dump, file):
    for path in file:
        if dump:
            print(puddl.dump(source, path))
        else:
            # an "infer t0" would be nice here...
            puddl.index(source, path)
    print(f"indexed {len(file)} files")


@root.command()
@click.argument("stream")
@click.argument("comment")
def comment(stream, comment):
    print(stream, comment)


@root.group()
def ingress():
    pass


@ingress.command(deprecated=True)
@click.option("--binary")
def stdin(binary):
    if binary:
        raise NotImplementedError
    db = puddl.get_db()
    source = _default_source
    db.stream(source=source, ingress="stdin", in_stream=click.get_text_stream("stdin"))


@root.group(name="db")
def database():
    pass


@database.command()
def status():
    if not puddl.get_db().is_ok():
        click.get_current_context().exit(code=1)


@database.command()
def env():
    for k, v in puddl.config.to_env().items():
        if k.startswith("PG"):
            print(f"export {k}={v}")


@root.group()
def dev():
    pass


@dev.command()
def drop_all_tables():
    puddl.get_db().drop_all_tables()


def main():
    # Note that this function is referenced in `setup.py`.
    root(auto_envvar_prefix="PUDDL")


if __name__ == "__main__":
    # https://click.palletsprojects.com/en/7.x/options/#values-from-environment-variables
    main()
