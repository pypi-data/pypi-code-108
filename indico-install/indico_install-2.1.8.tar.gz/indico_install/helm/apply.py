import click

from indico_install.cluster_manager import ClusterManager
from indico_install.config import D_PATH
from indico_install.kube.svc.restart import restart
from indico_install.utils import options_wrapper, run_cmd


def find_dependent_services(updated_services: list) -> set:
    """
    From a list of services, determine if any configs or secrets have been updated
    and return a list of deployment and statefulset names that need to be restarted
    to pick up changes. Determined if the services use any of the <updated_confs>
    in their envFrom or volumes.
    """
    updated_confs = [
        ups.split("/", 1)[1]
        for ups in updated_services
        if ups.startswith("secret/") or ups.startswith("configmap/")
    ]
    # We bank on the fact that names of deployments,
    # statefulsets, configs, secrets are all unique

    dependency_info = []
    dependent_services = set([])
    # 1. Get all the conf dependencies for our resources
    for svc_type in ("deployment", "statefulset"):
        dependency_info.extend(
            run_cmd(
                f"kubectl get {svc_type} "
                "--no-headers -o custom-columns=NAME:.metadata.name,"
                "ENVFROM:{.spec.template.spec.containers[0].envFrom[*]},"
                "CONFIGMAPVOL:{.spec.template.spec.volumes[*]}",
                silent=True,
            ).splitlines()
        )

    # 2. For each conf, find the list of dependent resources
    for conf in updated_confs:
        conf_deps = set([ds.split("  ", 1)[0] for ds in dependency_info if conf in ds])
        dependent_services.update(conf_deps)

    return dependent_services


@click.command("apply")
@click.pass_context
@click.argument("services", required=False, nargs=-1)
@click.option(
    "--restart-deps/--no-restart-deps",
    default=True,
    show_default=True,
    help="Restart services affected by updated configmap or secrets",
)
@options_wrapper()
def apply(
    ctx,
    restart_deps=True,
    services=None,
    yes=False,
    cluster_manager=None,
):
    """
    Apply templates in the "generated/" directory.
    Apply only the template files matching <SERVICE> if provided.
    Creates the image pull secret if missing.
    Performs a dry-run for confirmation before applying. Skip dry-run with --yes
    """
    generated_dir = D_PATH / "generated"
    if not generated_dir.is_dir():
        click.secho(f"'generated/' directory not found in {D_PATH}")
        return

    # These are services that were actually modified
    updated_services = []
    if services:
        for service in services:
            templates = run_cmd(
                f"ls {generated_dir} | grep '{service}'", silent=True
            ).splitlines()
            for t in templates:
                results = run_cmd(
                    f"kubectl apply -f {generated_dir / t} --dry-run 2>&1 | "
                    "grep -v 'support dry-run'"
                )

            if yes or click.confirm("Ready to apply these changes?"):
                outs = [
                    run_cmd(f"kubectl apply -f {generated_dir / t}") for t in templates
                ]
                updated_services.extend(
                    [
                        line.split(" ", 1)[0]
                        for out in outs
                        for line in out.splitlines()
                        if any(status in line for status in ("created", "configured"))
                    ]
                )
    else:
        results = run_cmd(
            f"kubectl apply -R -f {generated_dir} --dry-run 2>&1 "
            "| grep -v 'support dry-run'",
            silent=True,
        )
        click.echo("\n".join(results.split(",")) + "\n")

        if yes or click.confirm("Ready to apply these changes?"):
            out = run_cmd(f"kubectl apply -R -f {generated_dir}", silent=True)
            for line in out.splitlines():
                color = "red"
                if "unchanged" in line:
                    color = "yellow"
                elif "configured" in line or "created" in line:
                    color = "green"
                    updated_services.append(line.split(" ", 1)[0])
                click.secho(line, fg=color)

    # Now we reroll any dependent services as necessary
    # And save information with the version cluster_manager
    if updated_services:
        cluster_manager = cluster_manager or ClusterManager()
        cluster_manager.set_default_namespace()
        cluster_manager.update_from_current(
            [s.split("/", 1)[-1] for s in updated_services]
        )
        updated_confs = [
            ups
            for ups in updated_services
            if ups.startswith("secret/") or ups.startswith("configmap/")
        ]
        if not updated_confs:
            return
        if restart_deps:
            dependent_services = find_dependent_services(updated_services)
            if not dependent_services:
                click.secho(
                    "No dependent services found that need to be restarted", fg="yellow"
                )
                return
            ctx.invoke(
                restart, services=list(dependent_services), contains=False, wait="2m"
            )
        else:
            click.secho(
                f"{', '.join(updated_confs)} were updated. "
                "Make sure to restart dependent services"
            )
