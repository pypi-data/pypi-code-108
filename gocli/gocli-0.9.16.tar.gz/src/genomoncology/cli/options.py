# Shared state and options for all commands.
#
# Reference:
# https://github.com/pallets/click/issues/108#issuecomment-44691173

import uuid

import click
from gosdk import variables

from genomoncology import State
from . import const

pass_state = click.make_pass_decorator(State, ensure=True)


def debug_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.debug = value
        return value

    return click.option(
        "-d",
        "--debug",
        is_flag=True,
        expose_value=False,
        help="Run in debug mode. (debug level logging).",
        callback=callback,
    )(f)


def quiet_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.quiet = value
        return value

    return click.option(
        "-q",
        "--quiet",
        is_flag=True,
        expose_value=False,
        help="Run in quiet mode. (warning level logging).",
        callback=callback,
    )(f)


def pipeline_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.pipeline = value
        return value

    return click.option(
        "-p",
        "--pipeline",
        type=str,
        expose_value=False,
        help="Pipeline identifier.",
        callback=callback,
    )(f)


def build_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.build = value
        return value

    return click.option(
        "-b",
        "--build",
        type=click.Choice(const.BUILDS),
        expose_value=False,
        help="Reference assembly.",
        callback=callback,
        default=const.GRCh37,
    )(f)


def run_id_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.run_id = value or str(uuid.uuid4())
        return value

    return click.option(
        "-r",
        "--run_id",
        type=str,
        expose_value=False,
        help="Unique identifier of this run.",
        callback=callback,
    )(f)


def size_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.batch_size = value
        return value

    return click.option(
        "-s",
        "--size",
        type=int,
        default=50,
        expose_value=False,
        help="Size of batches when calling API.",
        callback=callback,
    )(f)


def glob_option(f, default=("*.vcf", "*.vcf.gz")):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.glob = value
        return value

    return click.option(
        "--glob",
        "-g",
        help="File pattern (e.g. *.vcf) of files to load",
        multiple=True,
        type=str,
        default=default,
        expose_value=False,
        callback=callback,
    )(f)


def include_tar_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.include_tar = value
        return value

    return click.option(
        "--include-tar",
        is_flag=True,
        expose_value=False,
        help="Search in tar (tgz, tar.gz, tar) files",
        callback=callback,
    )(f)


def hard_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.hard_failure = value
        return value

    return click.option(
        "-h",
        "--hard",
        is_flag=True,
        expose_value=False,
        help="Hard stop on failure.",
        callback=callback,
    )(f)


def token_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        value = value or variables.get_variable("token")
        state.token = value
        return value

    return click.option(
        "-t",
        "--token",
        help="API authorization token",
        type=str,
        expose_value=False,
        callback=callback,
    )(f)


def custom_header_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        value = value or variables.get_variable("custom_header_option")
        state.custom_header_option = value
        return value

    return click.option(
        "-ch",
        "--custom_header",
        help="pass one or multiple headers ex.-ch key1:val1",
        multiple=True,
        default=0,
        type=str,
        expose_value=False,
        callback=callback,
    )(f)


def host_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        value = value or variables.get_variable("host")
        state.host = value
        return value

    return click.option(
        "-H",
        "--host",
        help="Hostname of desired API",
        type=str,
        expose_value=False,
        callback=callback,
    )(f)


def schemes_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        value = value or variables.get_variable("schemes")
        value = value.split(",") if value is not None else None
        state.schemes = value
        return value

    return click.option(
        "-s",
        "--schemes",
        help="Desired API schemes",
        type=str,
        expose_value=False,
        callback=callback,
    )(f)


def timeout_option(f):
    def callback(ctx, _, value):
        state = ctx.ensure_object(State)
        value = value or variables.get_variable("timeout")
        state.timeout = value
        return value

    return click.option(
        "--timeout",
        help="Client enforced timeout for requests",
        type=int,
        default=300,
        callback=callback,
    )(f)


def common_options(f):
    f = quiet_option(f)
    f = debug_option(f)
    f = token_option(f)
    f = schemes_option(f)
    f = host_option(f)
    f = hard_option(f)
    f = custom_header_option(f)
    return f
