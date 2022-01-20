from copy import deepcopy
from . import context
from .input_helpers import get_org_from_input_or_ctx
from .output.table import (
    format_table,
    metadata_column,
    spec_column,
    column,
    subtable,
)
import agilicus


def get(ctx, id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    return apiclient.launchers_api.get_launcher(id, org_id=org_id, **kwargs)


def delete(ctx, id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    return apiclient.launchers_api.delete_launcher(id, org_id=org_id, **kwargs)


def add(ctx, org_id=None, resource_members=[], **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    kwargs.pop("org_id", None)

    spec = agilicus.LauncherSpec(org_id=org_id)
    for k, v in deepcopy(kwargs).items():
        if v is None:
            kwargs.pop(k)

    spec.config = agilicus.LauncherConfig(**kwargs)
    member_objs = []
    for member in resource_members:
        member_objs.append(agilicus.ResourceMember(id=member))
    spec.resource_members = member_objs
    launcher = agilicus.Launcher(spec=spec)
    return apiclient.launchers_api.create_launcher(launcher)


def query(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    kwargs["org_id"] = org_id
    query_results = apiclient.launchers_api.list_launchers(**kwargs)
    return query_results.launchers


def replace(  # noqa
    ctx,
    id,
    resource_members=None,
    remove_resource_members=None,
    name=None,
    org_id=None,
    command_path=None,
    command_arguments=None,
    start_in=None,
    do_intercept=None,
    hide_console=None,
    disable_http_proxy=None,
    application_ids=None,
    remove_application_ids=None,
    **kwargs,
):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    resource = apiclient.launchers_api.get_launcher(id, org_id=org_id)
    if remove_resource_members is not None:
        old_members = resource.spec.resource_members
        resource.spec.resource_members = []
        for member in old_members:
            if member.id in remove_resource_members:
                # needs to be removed.
                continue
            resource.spec.resource_members.append(member)
    if resource_members is not None:
        for member in resource_members:
            resource.spec.resource_members.append(agilicus.ResourceMember(id=member))

    if remove_application_ids is not None:
        old_ids = resource.spec.applications
        resource.spec.applications = []
        for app_id in old_ids:
            if app_id in remove_application_ids:
                # needs to be removed.
                continue
            resource.spec.applications.append(app_id)
    if application_ids is not None:
        for app_id in application_ids:
            resource.spec.applications.append(app_id)

    if name is not None:
        resource.spec.name = name
    if resource.spec.config is None:
        resource.spec.config = agilicus.LauncherConfig()
    if command_path is not None:
        resource.spec.config.command_path = command_path
    if command_arguments is not None:
        resource.spec.config.command_arguments = command_arguments
    if start_in is not None:
        resource.spec.config.start_in = start_in
    if do_intercept is not None:
        resource.spec.config.do_intercept = do_intercept
    if hide_console is not None:
        resource.spec.config.hide_console = hide_console
    if disable_http_proxy is not None:
        resource.spec.config.disable_http_proxy = disable_http_proxy
    print(resource)
    return apiclient.launchers_api.replace_launcher(id, launcher=resource).to_dict()


def add_interceptor_rule(
    ctx,
    id,
    org_id=None,
    allow_name_exact_list=[],
    allow_value_regex_list=[],
    disallow_name_exact_list=[],
    disallow_value_regex_list=[],
    **kwargs,
):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    allow_commands = []
    for name in allow_name_exact_list:
        allow_commands.append(agilicus.InterceptorCommand(name_exact=name))

    for regex in allow_value_regex_list:
        allow_commands.append(agilicus.InterceptorCommand(value_regex=regex))

    disallow_commands = []
    for name in disallow_name_exact_list:
        disallow_commands.append(agilicus.InterceptorCommand(name_exact=name))

    for regex in disallow_value_regex_list:
        disallow_commands.append(agilicus.InterceptorCommand(value_regex=regex))

    resource = apiclient.launchers_api.get_launcher(id, org_id=org_id)

    _initialize_interceptor_config(resource)

    resource.spec.config.interceptor_config.allow_list.extend(allow_commands)
    resource.spec.config.interceptor_config.disallow_list.extend(disallow_commands)

    return apiclient.launchers_api.replace_launcher(id, launcher=resource).to_dict()


def _initialize_interceptor_config(launcher):
    if not launcher.spec.config.interceptor_config:
        launcher.spec.config.interceptor_config = agilicus.InterceptorConfig()

    if not launcher.spec.config.interceptor_config.allow_list:
        launcher.spec.config.interceptor_config.allow_list = []

    if not launcher.spec.config.interceptor_config.disallow_list:
        launcher.spec.config.interceptor_config.disallow_list = []


def remove_name(interceptor_command_list, name):
    new_list = []
    for command in interceptor_command_list:
        if command.get("name_exact") != name:
            new_list.append(command)
    return new_list


def remove_regex(interceptor_command_list, regex):
    new_list = []
    for command in interceptor_command_list:
        if command.get("value_regex") != regex:
            new_list.append(command)
    return new_list


def remove_interceptor_rule(
    ctx,
    id,
    org_id=None,
    allow_name_exact_list=[],
    allow_value_regex_list=[],
    disallow_name_exact_list=[],
    disallow_value_regex_list=[],
    **kwargs,
):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    resource = apiclient.launchers_api.get_launcher(id, org_id=org_id)

    _initialize_interceptor_config(resource)

    for name in allow_name_exact_list:
        resource.spec.config.interceptor_config.allow_list = remove_name(
            resource.spec.config.interceptor_config.allow_list, name
        )

    for regex in allow_value_regex_list:
        resource.spec.config.interceptor_config.allow_list = remove_regex(
            resource.spec.config.interceptor_config.allow_list, regex
        )

    for name in disallow_name_exact_list:
        resource.spec.config.interceptor_config.disallow_list = remove_name(
            resource.spec.config.interceptor_config.disallow_list, name
        )

    for regex in disallow_value_regex_list:
        resource.spec.config.interceptor_config.disallow_list = remove_regex(
            resource.spec.config.interceptor_config.disallow_list, regex
        )

    return apiclient.launchers_api.replace_launcher(id, launcher=resource).to_dict()


def format_launchers(ctx, launchers):
    app_service_columns = [
        column("id"),
        column("name"),
    ]
    fs_columns = [
        metadata_column("id"),
        spec_column("name"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("org_id", "org id"),
        spec_column("name", "name"),
        spec_column("config", "config"),
        spec_column("applications"),
        subtable(ctx, "status.file_shares", fs_columns, optional=True),
        subtable(ctx, "status.application_services", app_service_columns, optional=True),
    ]
    return format_table(ctx, launchers, columns)
