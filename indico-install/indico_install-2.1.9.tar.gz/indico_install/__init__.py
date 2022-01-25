import click
from indico_install.sync import push, pull
from indico_install.helm import apply, install, render, upload
from indico_install.generate import generate
from indico_install.infra import infra
from indico_install.kube import pod, svc
from indico_install.package import package
from indico_install.encoder import encode, decode
from indico_install.updraft import updraft
from indico_install.inspect import inspect

command_groups = [
    pull,
    push,
    apply,
    render,
    generate,
    infra,
    inspect,
    install,
    package,
    pod,
    svc,
    encode,
    decode,
    updraft,
    upload,
]


@click.group("indico_cli")
@click.version_option()
@click.pass_context
def indico_cli(ctx):
    r"""
    Indico's CLI tool for cluster deployment and management.

    See `indico COMMAND [SUBCOMMAND, ] --help` for more information

    Scripts:

      These are utility scripts encapsulating the most common commands used in cluster management. They come installed with the indico CLI tool.

        kd [PODREGEX='']: describe all pods matching PODREGEX (wraps `kubectl describe pods`). Example: `kd custom-predict`

        kp [PODREGEX='']: list pods matching PODREGEX (wraps `kubectl get pods -o wide`). Example: `kp` or `kp custom`

        klogs [PODREGEX='']: tail logs for pods matching PODREGEX. Example: `klogs custom` or `klogs custom\|moonbow`

        kube exec PODREGEX [COMMAND='bash']: run COMMAND as a TTY in the first pod matching PODREGEX (wraps `kubectl exec -it <pod>`). Example: `kube exec fog`

        kube scale SERVICEREGEX AMOUNT: scale the number of pods for services matching SERVICEREGEX to AMOUNT.
        Will save settings in your input yaml. Alias of `indico svc scale`

        kube update SERVICEREGEX: roll the pods of all services matching SERVICEREGEX. Alias of `indico svc restart`

    """
    ctx.ensure_object(dict)


for command_group in command_groups:
    indico_cli.add_command(command_group)
