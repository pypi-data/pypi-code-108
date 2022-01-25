import copy
import os
import re
import shutil
import tempfile
from collections import defaultdict
from contextlib import contextmanager

import click

from indico_install.cluster_manager import ClusterManager
from indico_install.config import (
    CLUSTER_NAME,
    D_PATH,
    REMOTE_TEMPLATES_PATH,
    SERVICES_YAML,
    ConfigsLoader,
    merge_dicts,
    yaml,
)
from indico_install.utils import run_cmd

var_regex = re.compile(r"<\!var:([^<>]*)>")
lookup_regex = re.compile(r"<\!lookup:([^<>]*)>")


@contextmanager
def _resolve_values(values):
    f = tempfile.NamedTemporaryFile(mode="w")
    yaml.dump(dict(values.items()), f, default_flow_style=False)
    yield f" -f {f.name}"
    f.close()


def _resolve_template(template_values, variables, conf):
    if isinstance(template_values, dict):
        new_values = {}
        for key, value in template_values.items():
            new_values[_resolve_template(key, variables, conf)] = _resolve_template(
                value, variables, conf
            )
        return new_values
    elif isinstance(template_values, list):
        return [_resolve_template(value, variables, conf) for value in template_values]
    elif isinstance(template_values, str):
        var_matches = var_regex.findall(template_values)
        lookup_matches = lookup_regex.findall(template_values)
        while var_matches or lookup_matches:
            for match in var_matches:
                parts = match.split("=", 1)
                if len(parts) > 1:
                    default = str(parts[1])
                else:
                    default = ""
                template_values = template_values.replace(
                    f"<!var:{match}>", str(variables.get(parts[0], default))
                )
            for match in lookup_matches:
                look_up_keys = match.split("|")
                target_value = dict(conf)
                parts = look_up_keys[-1].split("=", 1)
                if len(parts) > 1:
                    default = str(parts[1])
                    look_up_keys[-1] = parts[0]
                else:
                    default = ""
                for look_up_key in look_up_keys:
                    target_value = target_value.get(look_up_key, {})
                template_values = template_values.replace(
                    f"<!lookup:{match}>",
                    str(target_value) if target_value != {} else default,
                )
            var_matches = var_regex.findall(template_values)
            lookup_matches = lookup_regex.findall(template_values)

    return template_values

def helm_render(
    templates_dir,
    group,
    template,
    values,
    generated_dir,
    values_files="",
    enabled_resource_validation=True,
):
    click.echo(f"Generating {values['name']}.yaml")
    with _resolve_values(values) as resolved_str:
        results = run_cmd(
            f"helm template {values_files} {templates_dir / group} "
            f"--execute templates/{template}.yaml{resolved_str}",
            silent=True,
        )
        if enabled_resource_validation:
            validate_resource_constraints(results)

    with open(generated_dir / f"{values['name']}.yaml", "w") as f:
        f.write(results)


def validate_resource_constraints(generated_results):
    """
    validate that a generated template has the required resource section
    """
    results = yaml.safe_load_all(generated_results)
    deploys = [
        result
        for result in results
        if isinstance(result, dict)
        and result.get("kind") in ("Deployment", "StatefulSet", "DaemonSet")
    ]
    for deploy in deploys:
        for container in deploy["spec"]["template"]["spec"]["containers"]:
            if "resources" not in container:
                raise Exception(
                    "No resource specifications set for "
                    f"{deploy['kind']}: {deploy['metadata']['name']}"
                )


def resolve_templates(templates):
    unresolved_templates = lambda: {  # noqa
        template_name: template
        for template_name, template in templates.items()
        if "<!template>" in template
    }
    templates_to_resolve = unresolved_templates()
    while templates_to_resolve:
        for template_name, template in templates_to_resolve.items():
            template_to_merge = template.pop("<!template>")
            templates[template_name] = merge_dicts(
                copy.deepcopy(templates[template_to_merge]), templates[template_name]
            )
        templates_to_resolve = unresolved_templates()


def resolve_all(configs):
    resolve_templates(configs["_templates"])

    for resource, helm_info in configs["services"].items():
        if "<!template>" in helm_info:
            template_name = helm_info.pop("<!template>")
            configs["services"][resource] = merge_dicts(
                copy.deepcopy(configs["_templates"][template_name]), helm_info
            )
            # Attach additional values
        configs["services"][resource]["values"] = configs["services"][resource].get(
            "values", {}
        )
        configs["services"][resource] = _resolve_template(
            configs["services"][resource], configs["services"][resource], configs
        )

    configs.update(
        _resolve_template(
            {k: v for k, v in configs.items() if k not in ("_templates", "services")},
            {},
            configs,
        )
    )


def format_resources(helm_info, warn=True):
    """
    If resource contraints are specified within a 'resources' key, set that
    value in 'limits' and 'requests'. Else, use the value set in the limits
    key; otherwise, rely on the values.yaml default for a value
    """
    if (
        "requests" in helm_info["values"]["resources"]
        or "limits" in helm_info["values"]["resources"]
    ) and warn:
        click.secho(
            (
                "Usage of 'limits' and 'requests' in templates is deprecated; "
                "please specify resource constraints in a single 'resources' block"
            ),
            fg="yellow",
        )

    updated_resources = defaultdict(dict, helm_info["values"]["resources"])
    # Guaranteed Pods
    if "cpu" in updated_resources:
        cpu = updated_resources.pop("cpu")
        updated_resources["requests"]["cpu"] = cpu
        if updated_resources.pop("guaranteed", None):
            helm_info["values"]["hpaTargetCpuUtilization"] = 80
            updated_resources["limits"]["cpu"] = cpu

    # CPU Burstable / RAM Guaranteed
    for resource in ("memory", "nvidia.com/gpu"):
        if helm_info["values"]["resources"].get(resource):
            val = updated_resources.pop(resource)
            updated_resources["limits"].update({resource: val})
            updated_resources["requests"].update({resource: val})

        elif resource in updated_resources.get("limits", {}):
            updated_resources["requests"][resource] = updated_resources["limits"][
                resource
            ]
        elif resource in updated_resources.get("requests", {}):
            updated_resources["limits"][resource] = updated_resources["requests"][
                resource
            ]

    helm_info["values"]["resources"] = dict(updated_resources)
    return helm_info


def render_from_local(templates_dir, services_yaml, input_yaml, services=None):
    generated = D_PATH / "generated"
    click.secho(f"clearing {generated}", fg="yellow")
    os.makedirs(generated, exist_ok=True)
    run_cmd(f"rm -rf {generated/ '*.yaml'}", silent=True)

    # images will be "updated" by Indico and contains cluster defaults
    # input is customer overrides
    configs = ConfigsLoader(services_yaml, input_yaml)
    resolve_all(configs)

    with _resolve_values(configs) as resolved_str:
        for resource, helm_info in configs["services"].items():
            if services and not any(service in resource for service in services):
                continue

            helm_info["values"] = helm_info.get("values", {})
            helm_info["values"]["name"] = resource
            configs["services"][resource] = helm_info
            if helm_info.pop("<!disabled>", None):
                continue
            extra_keys = {
                k: v
                for k, v in helm_info.items()
                if k not in ("group", "template", "values")
            }
            if "disableResourceLimits" in helm_info:
                resource_limits = not helm_info.get("disableResourceLimits")
            else:
                resource_limits = not configs.get("disableResourceLimits", False)

            helm_info["values"] = merge_dicts(extra_keys, helm_info["values"])
            [helm_info.pop(k) for k in extra_keys.keys()]

            if "resources" in helm_info["values"]:
                helm_info = format_resources(helm_info, warn=resource_limits)

            try:
                helm_render(
                    templates_dir,
                    values_files=f"{resolved_str}",
                    enabled_resource_validation=resource_limits,
                    generated_dir=generated,
                    **helm_info,
                )
            except Exception as e:
                click.secho(f"Unable to render template for {resource}: {e}")
    configs.save(D_PATH / "configuration" / f"{CLUSTER_NAME}.yaml")


def _resolve_remote(remote_path):
    """
    Download remote templates and services yaml and unpack
    Unpack if necessary, and validate contents (error if validation fails)
    Return the location of the local, unpacked templates dir
    """
    remote_templates_path = REMOTE_TEMPLATES_PATH + remote_path + "/templates.tar.gz"
    remote_services_yaml = REMOTE_TEMPLATES_PATH + remote_path + "/services.yaml"
    local_directory = (
        D_PATH / "remote_configs" / "".join(c for c in str(remote_path) if c.isalnum)
    )
    if not local_directory.parent.exists():
        local_directory.parent.mkdir(exist_ok=True, parents=True)

    click.secho(f"Downloading remote configs to {local_directory}", fg="yellow")
    if local_directory.is_dir():
        run_cmd(f"rm -rf {local_directory}", silent=True)
    os.makedirs(local_directory / "templates", exist_ok=True)

    run_cmd(
        f"wget {remote_services_yaml} -O {local_directory / 'services.yaml'}",
        silent=True,
    )
    assert (
        local_directory / "services.yaml"
    ).is_file(), f"Unable to download version {remote_path}"
    run_cmd(
        f"wget {remote_templates_path} -O - | "
        f"tar -xz -C {local_directory / 'templates'}",
        silent=True,
    )
    return (local_directory / "services.yaml", local_directory / "templates")


@click.command("render")
@click.pass_context
@click.argument("services", required=False, nargs=-1)
@click.option("--local", is_flag=True, help="Use local services yaml and templates")
@click.option("--no-clean", is_flag=True, help="Keep the remote templates directory")
def render(
    ctx,
    services=None,
    local=None,
    no_clean=None,
    cluster_manager=None,
    allow_image_overrides=False,
):
    """
    Render remote Helm templates.

    Only render the template for services with names containing <SERVICE> if provided
    """
    templates_dir = D_PATH / "templates"
    remote = False

    cluster_manager = cluster_manager or ClusterManager()
    cluster_manager.set_default_namespace()
    # Determine and download the updraft version templates
    if cluster_manager.indico_version and not local:
        services_yaml, templates_dir = _resolve_remote(cluster_manager.indico_version)
        remote = True
    elif local:
        services_yaml = SERVICES_YAML
    else:
        click.secho(
            "No render version supplied! Please use `indico updraft -v`", fg="red"
        )
        return

    if not services_yaml.is_file():
        click.secho(f"Could not find {services_yaml}.", fg="red")
        return

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as input_yaml:

        # Keep track of which custom images were applied. We only use these to override
        # generated images in the templates if specified
        # Generally not used unless we're recovering to a previous state
        old_conf = {} if allow_image_overrides else cluster_manager.clean_services()
        input_yaml.write(
            yaml.dump(cluster_manager.cluster_config, default_flow_style=False).encode(
                "utf-8"
            )
        )
        input_yaml.flush()
        try:
            render_from_local(
                templates_dir, services_yaml, input_yaml.name, services=services
            )
            cluster_manager.edit_cluster_config(changes=old_conf)
            cluster_manager.save()
        finally:
            os.remove(input_yaml.name)

    click.secho("Templates generated!", fg="green", bold=True)
    if remote and not no_clean:
        shutil.rmtree(templates_dir.parent)
