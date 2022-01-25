import click
from indico_install.utils import run_cmd, find_names


@click.command("restart")
@click.pass_context
@click.argument("services", required=True, nargs=-1)
@click.option(
    "--wait",
    default="0",
    show_default=True,
    help="Amount of time to wait for the new pods to be ready. Ex: 3m, 4h",
)
@click.option(
    "--contains/--no-contains",
    default=True,
    show_default=True,
    help=(
        "Restart all services with names containing the <service> string. "
        "Only applicable if <service> is not 'all'"
    ),
)
@click.option(
    "--all",
    "all_services",
    is_flag=True,
    default=False,
    help=(
        "Update all services in the current namespace (--all). "
        "Requires <service> passed in to be 'all'"
    ),
)
def restart(ctx, services, all_services=False, contains=True, wait="0"):
    """
    Reroll a K8S cluster deployment or statefulset.

    ARGS:

        <SERVICES> grep string(s) of deployments and statefulsets to reroll

         - "all" reset all deployments and statefulsets with an
     inditype label of service or celerytask
    """
    for svc_type in ["deployment", "statefulset"]:
        wait_str = "--watch=false" if wait == "0" else f"--timeout={wait}"
        if services[0] == "all":
            label_match = (
                "" if all_services else "-l 'inditype in (service, celerytask)'"
            )
            _services = run_cmd(
                (
                    f"kubectl get {svc_type} {label_match} --no-headers "
                    "-o custom-columns=NAME:.metadata.name"
                ),
                silent=True,
            ).splitlines()
            for svc_to_update in _services:
                svc_to_update = f"{svc_type}/{svc_to_update}"
                click.secho(f"service {svc_to_update}")
                run_cmd(
                    f"kubectl rollout restart {svc_to_update} "
                    f"&& kubectl rollout status {svc_to_update} {wait_str}"
                )
        else:
            service_str = r"\|".join(services)
            _services = find_names(svc_type, service_str, contains)
            for svc_to_update in _services:
                svc_to_update = f"{svc_type}/{svc_to_update}"
                run_cmd(
                    f"kubectl rollout restart {svc_to_update} "
                    f"&& kubectl rollout status {svc_to_update} {wait_str}"
                )
