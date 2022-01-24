import click

from indico_install.cluster_manager import (
    ClusterManager,
    get_services_yaml_from_tag,
    list_backups,
    get_default_namespace
)
from indico_install.config import merge_dicts, yaml, INPUT_YAML
from indico_install.helm.apply import apply
from indico_install.helm.render import render
from indico_install.setup import configure_gcr_key, setup
from indico_install.utils import options_wrapper, pretty_diff, string_to_tag


default_namespace = get_default_namespace(ClusterManager().cluster_config, "defaultNamespace")

def refresh_cluster_manager(
    ctx, cluster_manager, yes, allow_image_overrides=False
):
    """
    Given recent changes, apply them to the cluster
    """
    cluster_manager.lock()
    try:
        ctx.invoke(
            render,
            cluster_manager=cluster_manager,
            allow_image_overrides=allow_image_overrides,
        )
        ctx.invoke(
            apply,
            cluster_manager=cluster_manager,
            yes=yes,
        )
    finally:
        cluster_manager.save()
        cluster_manager.unlock()


@click.group("updraft")
def updraft():
    """Manage deployments and versioning"""
    pass


@updraft.command("ls")
@click.pass_context
@click.option("-n", "--number", type=int, help="Max number of results")
def list_versions(ctx, number=None):
    """
    Display available, released versions of updraft, ordered most to least recent
    """
    results = ClusterManager.get_updraft_versions(number)
    click.secho("\n".join(results))


@updraft.command("cat")
@click.pass_context
@click.argument("version", required=False)
def cat_version(ctx, version=None):
    """
    Show the service list for the provided VERSION (default: current cluster version)
    """
    version = string_to_tag(version) or ClusterManager().indico_version
    services = get_services_yaml_from_tag(version, apps_only=False)
    if services:
        click.echo(yaml.dump(services, default_flow_style=False))


@updraft.command("version")
@click.pass_context
def show_version(ctx):
    """
    Display version details about <TAG>. Defaults to current cluster rendered_tag
    """
    click.secho(f"Known version: {ClusterManager().indico_version}")


@updraft.command("current")
@click.pass_context
def show_current(ctx):
    """
    Display current configmap state (alias for viewing the configmap)
    """
    click.secho(ClusterManager().to_str())


@updraft.command("edit")
@click.pass_context
@click.option(
    "-I", "--interactive", is_flag=True, help="[Deprecated] Open configmap in an editor"
)
@click.option("-v", "--version", help="Update to new updraft version")
@click.option(
    "--force", is_flag=True, help="Render and apply even if there are no changes"
)
@click.option("--patch-file", type=click.File("r"), help="YAML-formatted patch file")
@options_wrapper()
def edit_configmap(ctx, *, force, patch_file, version, yes, **kwargs):
    """
    Edit configmap interactively or through a patch file.
    Only allows editing of the main cluster config portion
    """
    cluster_manager = ClusterManager()
    if not cluster_manager.cm_exists:
        click.secho(
            "Cannot edit cluster config. Please initialize with indico updraft init",
            fg="red",
        )
        return
    changes = None
    replace = False
    interactive = True

    if any([patch_file, version, force]):
        interactive = False

    if interactive or patch_file:
        cluster_manager.save(backup=True)

    service_state = cluster_manager.clean_services()
    if interactive:
        changes = click.edit(
            yaml.dump(cluster_manager.cluster_config, default_flow_style=False)
        )
        changes = yaml.safe_load(changes or "")
        replace = True
    elif patch_file:
        with open(patch_file, "r") as f:
            changes = yaml.safe_load(f)

    version = string_to_tag(version) if version else None
    if force or changes or (version and version != cluster_manager.indico_version):
        if force or version:
            click.secho("This will override custom images!", fg="yellow")
        cluster_manager.edit_cluster_config(
            changes=merge_dicts(changes or {}, service_state),
            version=version,
            replace=replace,
        )
        if cluster_manager.default_namespace_exists():
            cluster_manager.update_default_namespace()
    else:
        click.secho(
            "No changes or new version provided. Use --force if required", fg="yellow"
        )
        return

    cluster_manager.set_default_namespace()

    if yes or click.confirm("Render with changes?"):
        refresh_cluster_manager(
            ctx,
            cluster_manager,
            yes,
            allow_image_overrides=not version,
        )


@updraft.command("restore")
@click.pass_context
@click.option("--keep-images", is_flag=True, help="Keep the current deployed images")
@options_wrapper()
def restore_version(ctx, yes, keep_images=False):
    """
    (Alpha) If backups of the cluster_manager exist, choose and restore
    to a specific backup
    """
    backups = list_backups()
    if not backups:
        click.secho("No backup available!", fg="red")
        return
    backup = click.prompt(
        (
            "Backups available\n"
            + "\n".join(f" [{i}] {v}" for i, v in enumerate(backups))
            + "\nSelect backup id"
        ),
        type=click.Choice(list(str(i) for i in range(len(backups)))),
        default="0",
        show_choices=False,
    )
    backup = backups[int(backup)]

    cluster_manager = ClusterManager()
    curr_state = None
    if keep_images:
        cluster_manager.load_from_cluster()
        curr_state = cluster_manager.clean_services()

    cluster_manager.load_from_cluster(backup_conf=backup)
    if keep_images and curr_state:
        cluster_manager.clean_services()
        cluster_manager.edit_cluster_config(changes=curr_state)

    click.secho("Please review backup:", fg="green")
    click.secho(ClusterManager().to_str())

    if yes or click.confirm("Save and apply backup? "):
        refresh_cluster_manager(
            ctx, cluster_manager, yes, allow_image_overrides=True
        )


@updraft.command("init")
@click.pass_context
def init_tracking(ctx, yes=False, input_yaml=None):
    """
    Add or update version tracking to the cluster (idempotent)
    """
    if not input_yaml:
        input_yaml = INPUT_YAML if INPUT_YAML.is_file() else None
    if input_yaml:
        setup(input_yaml)
    cluster_manager = ClusterManager(reconcile=True, input_yaml=input_yaml)
    click.secho(cluster_manager.to_str())

    if yes or click.confirm("Save updated version cluster_manager?"):
        cluster_manager.save()
    cluster_manager.update_default_namespace()
    cluster_manager.set_default_namespace()
    configure_gcr_key(default_namespace)


@updraft.command("diff")
@click.pass_context
@click.argument("versions", required=False, nargs=-1)
@click.option(
    "--all/--no-all",
    "show_all",
    default=False,
    show_default=True,
    help="Include matches in diff",
)
def compare_versions(ctx, versions=None, show_all=False):
    """
    Compare versions
    If no versions are provided, diff rendered_release with current state
    If 1 version, diff current state with version
    If 2 versions, diff the versions
    """
    if len(versions) > 2:
        click.secho(
            "More that 2 versions provided for comparison. Ignoring extra versions"
        )
        versions = versions[:2]
    if versions:
        versions = [string_to_tag(v) for v in versions]

    cluster_manager = ClusterManager()
    if len(versions) == 2:
        diff = cluster_manager.diff(*versions)
    else:
        diff = cluster_manager.diff_version(tag=versions[0] if versions else None)

    pretty_diff(diff, show_all=show_all)


@updraft.command("clear-lock")
@click.pass_context
def clear_lock(ctx, versions=None, show_all=False):
    """Force clears and existing CM lock"""
    ClusterManager().unlock(force=True)
    click.secho("Cluster Manager unlocked", fg="green")
