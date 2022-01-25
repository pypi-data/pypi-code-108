import click


from indico_install.utils import run_cmd


@click.command("update")
def update():
    """
    Generates image updates and scaling updates from a YAML file
    """
    # Read the cluster dump to grab the deployment names for updates
    # Read the update YAML to match the deployment names
    # Generate the script
    # Upload the script to google storage with proper permissions
    output = run_cmd(
        "kubectl get deploy -o wide  | grep indico | awk '{print $1\"=\"$7}'",
        silent=True,
    )

    images = {
        x[0]: x[1] for x in [y.split("=") for y in output.split("\n") if y.strip()]
    }

    for deploy, image in images.items():
        click.echo(f"kubectl set image deployment/{deploy} {deploy}={image}")

    output = run_cmd(
        "kubectl get statefulset -o wide  | grep indico | awk '{print $1\"=\"$5}'",
        silent=True,
    )

    images = {
        x[0]: x[1] for x in [y.split("=") for y in output.split("\n") if y.strip()]
    }

    for statefulset, image in images.items():
        click.echo(f"kubectl set image statefulset/{statefulset} {statefulset}={image}")

    click.echo(run_cmd("khash", silent=True))
