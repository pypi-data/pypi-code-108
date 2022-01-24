import json
from operator import itemgetter
import click
from click import secho
from indico_install.utils import run_cmd

from tabulate import tabulate

unit_table = ["k", "m", "g"]


def convert_size(size):
    if size.isdigit():
        size = int(size)
    elif size[:-1].isdigit():
        unit = size[-1].lower()
        size = int(size[:-1]) * (1000 ** (1 + unit_table.index(unit)))
    else:
        raise ValueError()
    for x in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size


@click.group("inspect")
@click.pass_context
def inspect(ctx):
    """
    Inspect kubernetes resources
    """
    ctx.ensure_object(dict)


@inspect.command("hpa")
@click.pass_context
def hpa(ctx):
    """
    Outputs a formatted version of Horizontal Pod Autoscalers resource list
    that includes additional information that is usually hidden away in the metadata.
    """
    result = run_cmd(
        """kubectl get hpa -o custom-columns=NAME:.metadata.name,CURRENT:.status.currentReplicas,DESIRED:.status.desiredReplicas,LAST_SCALED:.status.lastScaleTime,MIN:.spec.minReplicas,MAX:spec.maxReplicas,ANNOTATION:.metadata.annotations."autoscaling\.alpha\.kubernetes\.io/current-metrics",TARGETMEM:.metadata.annotations."autoscaling\.alpha\.kubernetes\.io/metrics",CPUTARGET:.spec.targetCPUUtilizationPercentage""",
        silent=True,
    )

    lines = iter(result.split("\n"))
    headers = next(lines).split()
    output_values = []

    for line in lines:
        values = dict(zip(headers, line.split()))
        targets = {}

        # Parse Target Memory
        target_mem = {}
        try:
            target_mem = json.loads(values.pop("TARGETMEM"))
            for target_resource in target_mem:
                if target_resource["type"] != "Resource":
                    continue
                targets[target_resource["resource"]["name"]] = target_resource[
                    "resource"
                ]["targetAverageUtilization"]
        except Exception:
            target_mem["memory"] = target_mem.get("memory", "??")

        targets["cpu"] = values.pop("CPUTARGET")

        try:
            annotation = values.pop("ANNOTATION")
            annotation_json = json.loads(annotation)
            for resource_info in annotation_json:
                try:
                    if resource_info["type"] != "Resource":
                        continue
                    info = resource_info["resource"]
                    name, usage_percent, total_usage = itemgetter(
                        "name", "currentAverageUtilization", "currentAverageValue"
                    )(info)
                    values[
                        f"% {name.upper()} USED"
                    ] = f"{usage_percent}%/{targets[name]}%"
                    values[f"{name.upper()} USAGE"] = total_usage
                except Exception as e:
                    secho(f"Error occured while fetching data: {e.args[0]}")
        except Exception:
            pass

        if "MEMORY USAGE" in values:
            try:
                values["MEMORY USAGE"] = convert_size(values["MEMORY USAGE"])
            except Exception:
                pass
        output_values.append(values)

    headers = [
        "NAME",
        "CURRENT",
        "DESIRED",
        "MIN",
        "MAX",
        "% CPU USED",
        "CPU USAGE",
        "% MEMORY USED",
        "MEMORY USAGE",
    ]
    output_lines = []
    for values in output_values:
        output_line = []
        for item in headers:
            output_line.append(values.pop(item, "<N/A>"))
        output_lines.append(output_line)
    secho(tabulate(output_lines, headers=headers))
