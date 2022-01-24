import click

from indico_install.helm.render import render
from indico_install.utils import find_names, run_cmd


@click.command("enable")
@click.pass_context
@click.argument("service", required=True, type=str)
def enable(ctx, service):
    """
    Enable a K8S deployment/statefulset/service.
    Will also render the templates - you must apply on your own

    ARGS:
        <SERVICE> exact name of service to enable
    """
    click.secho(
        f"Setting {service}.disabled=False in cluster config", fg="blue",
    )
    ctx.obj["TRACKER"].edit_cluster_config(
        changes={"services": {service: {"<!disabled>": False}}}
    )
    ctx.obj["TRACKER"].save()
    ctx.invoke(
        render,
        cluster_manager=ctx.obj["TRACKER"],
        services=[service],
    )
    click.secho(
        f"Rendered template for {service}. Don't forget to apply!", fg="green",
    )


@click.command("delete")
@click.pass_context
@click.argument("service", required=True, type=str)
def delete(ctx, service):
    """
    Delete a K8S deployment/statefulset/service and any associated pdbs/hpas

    ARGS:
        <SERVICE> grep string of deployments, statefulsets, services to delete
    """
    updated_svcs = []
    for svc_type in ["deployment", "statefulset", "service", "pdb", "hpa"]:
        out = find_names(svc_type, service)
        if not out:
            continue
        for _svc in out:
            if click.confirm(f"Ok to delete {svc_type} {_svc}"):
                click.secho(run_cmd(f"kubectl delete {svc_type} {_svc}"), fg="green")
                if svc_type not in ("hpa", "pdb"):
                    updated_svcs.append(_svc)

    if updated_svcs:
        ctx.obj["TRACKER"].edit_cluster_config(
            changes={"services": {_svc: {"<!disabled>": True} for _svc in updated_svcs}}
        )
        ctx.obj["TRACKER"].save()


@click.command("scale")
@click.pass_context
@click.argument("service", required=True, type=str)
@click.argument("amount", required=True, type=int)
@click.option(
    "--contains/--no-contains",
    default=True,
    show_default=True,
    help=("Scale all services with names containing the <service> string."),
)
def scale(ctx, service, amount, contains=True):
    """
    Scale a K8S cluster deployment or statefulset

    ARGS:
        <SERVICE> grep string of deployments and statefulsets to scale

        <AMOUNT> number of pods to create
    """
    updated_svcs = []
    for svc_type in ["deployment", "statefulset"]:
        out = find_names(svc_type, service, contains)
        if not out:
            continue
        for _svc in out:
            click.secho(
                run_cmd(f"kubectl scale --replicas={amount} {svc_type} {_svc}"),
                fg="green",
            )
            hpa_exists = run_cmd(
                f"kubectl get hpa {_svc} -o json 2>/dev/null", silent=True
            )
            if hpa_exists:
                click.secho(
                    run_cmd(
                        "kubectl patch hpa %s --patch "
                        """'{"spec":{"minReplicas": %s, "maxReplicas": %s}}'"""
                        % (_svc, amount, amount + 2)
                    ),
                    fg="green",
                )
            updated_svcs.append(_svc)

    if updated_svcs:
        ctx.obj["TRACKER"].edit_cluster_config(
            changes={
                "services": {
                    _svc: {"values": {"replicas": amount}} for _svc in updated_svcs
                }
            }
        )
        ctx.obj["TRACKER"].save()
