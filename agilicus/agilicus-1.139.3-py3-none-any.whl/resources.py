import click

from . import context
from .input_helpers import get_org_from_input_or_ctx, update_if_not_none
from .input_helpers import update_org_from_input_or_ctx, strip_none
from .output.table import (
    format_table,
    metadata_column,
    spec_column,
    status_column,
    subtable,
)
import agilicus

permissioned_resource_types = [
    "application",
    "fileshare",
    "application_service",
    "desktop",
    "group",
    "launcher",
]
resource_types = permissioned_resource_types + ["service_forwarder"]
permissioned_resource_type_enum = click.Choice(permissioned_resource_types)
resource_type_enum = click.Choice(resource_types)


def query_permissions(ctx, org_id=None, **kwargs):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    query_results = apiclient.permissions_api.list_resource_permissions(
        org_id=org_id, **strip_none(kwargs)
    )
    if query_results:
        return query_results.resource_permissions
    return []


def format_permissions(ctx, roles):
    columns = [
        metadata_column("id"),
        spec_column("resource_type", "type"),
        spec_column("user_id", "user id"),
        spec_column("org_id", "org id"),
        spec_column("resource_id", "resource id"),
        spec_column("resource_role_name", "role"),
    ]
    return format_table(ctx, roles, columns)


def add_permission(
    ctx, user_id, resource_id, resource_type, resource_role_name, org_id=None
):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    spec = agilicus.ResourcePermissionSpec(
        org_id=org_id,
        user_id=user_id,
        resource_type=resource_type,
        resource_role_name=resource_role_name,
        resource_id=resource_id,
    )
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    return apiclient.permissions_api.create_resource_permission(
        agilicus.ResourcePermission(spec=spec)
    ).to_dict()


def delete_permission(ctx, id, org_id=None):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    return apiclient.permissions_api.delete_resource_permission(id, org_id=org_id)


def bulk_delete_permission(ctx, **kwargs):
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    apiclient = context.get_apiclient_from_ctx(ctx)
    return apiclient.permissions_api.bulk_delete_resource_permission(
        **strip_none(kwargs)
    )


def query_resources(ctx, org_id=None, **kwargs):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs["org_id"] = org_id
    params = {}
    update_if_not_none(params, kwargs)
    query_results = apiclient.resources_api.list_resources(**params)
    if query_results:
        return query_results.resources
    return []


def format_resources(ctx, resources):
    member_columns = [
        metadata_column("id"),
        spec_column("name"),
        spec_column("resource_type"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("org_id", "org id"),
        spec_column("resource_type", "type"),
        spec_column("name", "name"),
        status_column("resource_stats.overall_status", "status", optional=True),
        status_column(
            "resource_stats.last_warning_message", "last_warning", optional=True
        ),
        status_column(
            "resource_stats.session_stats.total", "good_sessions", optional=True
        ),
        status_column(
            "resource_stats.session_stats.failed", "failed_sessions", optional=True
        ),
        subtable(ctx, "status.resource_members", member_columns),
    ]
    return format_table(ctx, resources, columns)


def query_roles(ctx, org_id=None, **kwargs):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    query_results = apiclient.permissions_api.list_resource_roles(
        org_id=org_id, **strip_none(kwargs)
    )
    return query_results.resource_roles


def format_roles(ctx, roles):
    columns = [
        spec_column("resource_type", "type"),
        spec_column("role_name", "name"),
    ]
    return format_table(ctx, roles, columns)


def create_resource_group(ctx, resource_members, name, org_id=None):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    member_objs = []
    for member in resource_members:
        member_objs.append(agilicus.ResourceMember(id=member))
    spec = agilicus.ResourceSpec(
        resource_members=member_objs, resource_type="group", name=name, org_id=org_id
    )
    resource = agilicus.Resource(spec=spec)

    return apiclient.resources_api.add_resource(resource).to_dict()


def delete_resource(ctx, id, org_id=None):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    return apiclient.resources_api.delete_resource(id, org_id=org_id)


def update_resource(
    ctx,
    id,
    resource_members=None,
    remove_resource_members=None,
    name=None,
    org_id=None,
    **kwargs,
):
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    resource = apiclient.resources_api.get_resource(id, org_id=org_id)
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
    if name is not None:
        resource.spec.name = name

    return apiclient.resources_api.replace_resource(id, resource=resource).to_dict()
