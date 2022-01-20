import time
import click
import subprocess

from cnvrgv2.cli.utils import messages
from cnvrgv2.config import error_messages
from cnvrgv2.cli.utils.decorators import prepare_command


@click.group(name='ssh')
def ssh_group():
    pass


@ssh_group.command()
@click.argument('job_id')
@click.option("-p", "--port", help=messages.SSH_HELP_PORT, default=2222)
@click.option("-u", "--username", help=messages.SSH_HELP_USERNAME, default=None)
@click.option("-pw", "--password", help=messages.SSH_HELP_PASSWORD, default=None)
@click.option("-kc", "--kubeconfig", help=messages.SSH_HELP_KUBECTL, default=None)
@prepare_command()
def start(cnvrg, logger, job_id, port, username, password, kubeconfig):
    """
    Creates an ssh session to the pod of the given JOB_ID
    """
    logger.log_and_echo(messages.SSH_STARTING_SESSION)
    ssh = cnvrg.ssh.create_ssh(job_id)
    ssh.start(username, password)

    while True:
        ssh.reload()
        if ssh.ssh_status == "in_progress":
            click.echo(messages.SSH_WAITING_FOR_READY)
            time.sleep(3)
            continue
        elif ssh.ssh_status == "finished":
            break
        else:
            message = error_messages.SSH_FAILED_TO_START.format(ssh.ssh_status)
            logger.log_and_echo(message, error=True)

    if ssh.pod_name is None or ssh.password is None or ssh.username is None:
        message = error_messages.SSH_FAILED_GET_REQUIRED_PARAMS.format(ssh.ssh_status)
        logger.log_and_echo(message, error=True)

    connection_message = messages.SSH_READY.format(port, username, password)
    logger.log_and_echo(connection_message)

    run_portforward_command(ssh.pod_name, port, kubeconfig, ssh.namespace)


def run_portforward_command(pod_name, port, kubeconfig, namespace):
    command = "kubectl"
    if kubeconfig is not None:
        command = "kubectl --kubeconfig={}".format(kubeconfig)

    bashCommand = "{} -n {} port-forward {} {}:22".format(command, namespace, pod_name, port)
    click.echo("\nrunning command {}".format(bashCommand))
    subprocess.check_output(['bash', '-c', bashCommand])
