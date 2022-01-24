import re
from collections import defaultdict

import click

from indico_install.utils import run_cmd

status_order = defaultdict(lambda: len(status_order))
status_order.update(
    {
        "STATUS": 0,
        "Running": 1,
        "Terminating": 2,
        "ContainerCreating": 2,
        "CrashLoopBackOff": 3,
        "Unknown": 10,
    }
)


@click.group("pod")
@click.pass_context
def pod(ctx):
    """Utility commands to interact with pods"""


@pod.command("exec")
@click.pass_context
@click.argument("podname", required=True)
@click.option(
    "-c", "--command", default="bash", help="Command to run", show_default=True
)
def exc(ctx, podname, command="bash"):
    """
    Execute a command in a pod interactively through a TTY.

    Args:
        <PODNAME> pod name substring to exec into
    """
    pod = run_cmd(
        f"kubectl get pods --no-headers | grep {podname} | head -n 1 | awk '{{print $1}}'",
        silent=True,
    )
    run_cmd(["kubectl", "exec", "-it", pod, command], tty=True)


@pod.command("activate-user")
@click.pass_context
@click.argument("user_email", required=True)
def activate_user(ctx, user_email):
    """
    Activate a user and grant them administrator privileges

    Args:
        <USER_EMAIL> email of user to activate
    """
    noct_pod = run_cmd(
        "kubectl get pods | grep noct | head -n 1 | awk '{print $1}'", silent=True
    )
    run_cmd(
        f"kubectl exec -it {noct_pod} -- python3 /noct/alembic/migrations/setup_user_access.py {user_email}"
    )


@pod.command("ls")
@click.pass_context
@click.argument("podname", required=False)
def list_pods(ctx, podname):
    """
    List pods with optional <PODNAME> filter.
    """
    output = run_cmd("kubectl get pods -o wide", silent=True)
    if not output or "No resources" in output:
        click.secho(output, fg="yellow")
        return
    podname = podname or ""

    lines = output.split("\n")
    header = lines[0]
    output_lines = [line for line in lines[1:] if line.strip() and podname in line]
    sort_lines = sorted(
        enumerate([re.split(r"\s{2,}", line) for line in output_lines]),
        key=lambda parts: (
            status_order[parts[1][2]],
            -int(parts[1][1].split("/")[0]),
            parts[1][0],
        ),
    )

    click.echo(header)
    click.echo("\n".join(output_lines[idx] for idx, _ in sort_lines))
