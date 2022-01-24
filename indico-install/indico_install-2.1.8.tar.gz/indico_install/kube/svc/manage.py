import click

from indico_install.helm.render import render


@click.command("put-resource")
@click.pass_context
@click.argument("service", required=True, type=str)
@click.option(
    "-l",
    "--limit",
    required=True,
    type=str,
    help="An int/float with '[E/P/T/G/M/K]i' mem or (optional) 'm' cpu suffix",
)
@click.option(
    "-r",
    "--resource",
    default="memory",
    type=click.Choice(["memory", "cpu"]),
    show_default=True,
    help="Resource to update limits for",
)
def put_resource(ctx, service, *, limit, resource="memory"):
    """
    Provide a new resource limit for limit for memory or cpu

    ARGS:

        <SERVICE> exact name of service to update
    """
    valid_limit = limit
    err = lambda e: click.secho(f"Invalid {resource} limit: {limit}. {e}", fg="red")
    if resource == "memory":
        if not limit[-2:] in ["Ei", "Pi", "Ti", "Gi", "Mi", "Ki"]:
            err("Mem limit must end in power-of-two suffix (Gi, Mi, etc)")
            return
        valid_limit = valid_limit[:-2]
    else:
        _suff = limit[-1:]
        if not (_suff.isdigit() or _suff == "m"):
            err("CPU limit must end in digit or 'm' suffix")
            return
        elif _suff == "m":
            valid_limit = valid_limit[:-1]

    try:
        float(valid_limit)
    except Exception:
        err("Limit must be a valid int or float")
        return

    ctx.obj["TRACKER"].edit_cluster_config(
        changes={"services": {service: {"values": {"resources": {resource: limit}}}}}
    )
    ctx.obj["TRACKER"].save()
    ctx.invoke(
        render,
        cluster_manager=ctx.obj["TRACKER"],
        services=[service],
        allow_image_overrides=True,
    )
    click.secho(
        f"Rendered template for {service}. Don't forget to apply!", fg="green",
    )
