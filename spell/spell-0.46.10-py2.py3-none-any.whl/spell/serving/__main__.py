import click

from spell.serving.main import main


@click.command()
@click.option(
    "--num-server-workers",
    type=int,
    help=(
        "Number of worker processes to run the model server with. "
        "This defaults to (2 * num_CPUS) + 1, but should be set to the GPU Limit "
        "on GPU-enabled machines"
    ),
)
@click.option(
    "--gunicorn-server-settings",
    help=(
        "Additional configuration to use for the Gunicorn model server, "
        "as a single-quoted string, e.g. '--bind 0.0.0.0:8000 -w 8'"
    ),
)
@click.option(
    "--gunicorn-proxy-settings",
    help=(
        "Additional configuration to use for the Gunicorn proxy, "
        "as a single-quoted string, e.g. '--bind 0.0.0.0:8000 -w 8'"
    ),
)
def run_server(
    num_server_workers,
    gunicorn_server_settings,
    gunicorn_proxy_settings,
    **kwargs,  # This is to make changes to parameters more backwards compatible
):
    if num_server_workers is not None and num_server_workers < 1:
        raise click.UsageError("--num-server-workers must be greater than 0")
    main(
        num_server_workers=num_server_workers,
        additional_server_settings=gunicorn_server_settings or "",
        additional_proxy_settings=gunicorn_proxy_settings or "",
    )


run_server()
