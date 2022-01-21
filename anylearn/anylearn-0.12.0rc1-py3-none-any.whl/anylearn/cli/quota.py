from io import StringIO
from pathlib import Path

import click
from ruamel.yaml import YAML

from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    cmd_confirm_or_abort,
    check_config,
    check_connection,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    get_cmd_command,
)
from anylearn.interfaces import QuotaGroup


@click.group("quota")
def commands():
    """
    Operate quotas configured in Anylearn remote.
    """
    pass


@commands.command()
@check_config()
@check_connection()
@get_cmd_command()
def ls():
    """
    List all available quotas.
    """
    quotas = QuotaGroup.get_list()
    s = []
    for q in quotas:
        available = q.available()
        s.append({
            'name': q.name,
            'id': q.id,
            'available': {
                k: f"{available[k]}/{q.capacity[k]}"
                for k in q.capacity.keys()
            }
        })
    yaml = YAML()
    with StringIO() as stream:
        yaml.dump(s, stream)
        s = stream.getvalue()
    cmd_info(msg=str(s))


@commands.command()
@click.argument('quota_name')
@check_config()
@check_connection()
@get_cmd_command()
def template(quota_name: str):
    quotas = QuotaGroup.get_list()
    try:
        q = next(q for q in quotas if q.name == quota_name)
    except StopIteration:
        cmd_error(msg=f"Failed to get QuotaGroup {quota_name}")
        raise click.Abort
    req = [{q.id: q.default}]
    path = Path(f"resource_request_{q.name}.template.yaml")
    path.touch(exist_ok=True)
    yaml = YAML()
    yaml.dump(req, path)
    cmd_success(msg=(
        f"Resource request in QuotaGroup {q.name} "
        f"is templated in file `./{path}`. "
        "Feel free to customize its filename and content "
        "in order to use it in `anyctl run train` as `--resource-yaml`."
    ))
