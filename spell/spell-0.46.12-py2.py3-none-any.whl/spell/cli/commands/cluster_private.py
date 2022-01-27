import click

from spell.cli.exceptions import (
    api_client_exception_handler,
)

from spell.cli.utils import (
    cluster_utils,
)

cluster_version = 1


@click.command(name="private", short_help="Sets up a Private instance cluster as a Spell cluster", hidden=True)
@click.pass_context
@click.option("-n", "--name", "name", help="This will be used by Spell for you to identify the cluster")
@click.option("-s", "--storage_path", "storage_path", help="Location of networked storage on every instance")
def create_private(ctx, name, storage_path):
    """ """

    # Verify the owner is the admin of an org and cluster name is valid
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    if not name:
        name = click.prompt("Enter a display name for this Private cluster within Spell")
    if not storage_path:
        storage_path = click.prompt(
            "Enter the path to the networked storage mount on every instance", default="default"
        )

    with api_client_exception_handler():
        spell_client.validate_cluster_name(name)

    with api_client_exception_handler():
        cluster = spell_client.create_private_cluster(
            name,
            storage_path,
        )
        cluster_utils.echo_delimiter()
        url = f"{ctx.obj['web_url']}/{ctx.obj['owner']}/clusters/{cluster['name']}"
        click.echo(
            f"Your cluster {name} is initialized! Head over to the web console to create machine types "
            f"to execute your runs on - {url}"
        )

    spell_client.update_cluster_version(cluster["name"], cluster_version)


def delete_private_cluster(ctx, cluster):
    """
    Deletes a Private cluster.
    """

    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    if not click.confirm(f"Are you SURE you want to delete the spell cluster {cluster['name']}?"):
        return

    # Delete Machine Types and Model Servers on cluster first
    cluster_utils.echo_delimiter()
    with api_client_exception_handler():
        click.echo(f"Sending message to Spell to remove all machine types from the cluster {cluster['name']}...")
        spell_client.delete_cluster_contents(cluster["name"])

    # Last step is to mark the cluster as deleted
    cluster_utils.echo_delimiter()
    click.echo("Deleting cluster on Spell...")
    with api_client_exception_handler():
        spell_client.delete_cluster(cluster["name"])
        click.echo("Successfully deleted cluster on Spell")
