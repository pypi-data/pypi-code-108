from dataclasses import dataclass
from . import (
    apps,
    orgs,
    context,
    issuers as _issuers,
    users as _users,
    resources as _resources,
)


@dataclass
class PrimaryKeyMapping:
    primary_key_field: str
    collection: str = None


def get_key_from_dict(obj, pk_mapping):
    if pk_mapping.collection:
        return obj[pk_mapping.collection][pk_mapping.primary_key_field]
    return obj[pk_mapping.primary_key_field]


def get_key_from_obj(obj, pk_mapping):
    if pk_mapping.collection:
        base = getattr(obj, pk_mapping.collection)
        return getattr(base, pk_mapping.primary_key_field)
    return getattr(obj, pk_mapping.primary_key_field)


def _get_primary_keys(obj, primary_key_mapping):
    res = []
    for mapping in primary_key_mapping:
        if isinstance(obj, dict):
            res.append(get_key_from_dict(obj, mapping))
        else:
            res.append(get_key_from_obj(obj, mapping))
    if len(res) == 1:
        return res[0]
    return tuple(res)


def get_orphaned_resources(working_resource_set, obj_list, primary_key_mapping):
    result = []
    for obj in obj_list:
        key = _get_primary_keys(obj, primary_key_mapping)
        if key not in working_resource_set:
            result.append(obj)
    return result


def get_org_id_list(ctx, **kwargs):
    return {org["id"] for org in orgs.query(ctx, **kwargs)}


# This function takes a working resource set, query function, and a mapping object
# that indicates how to get the primary key values out of the objects returned from
# the query function. These keys are compared to the working resource set. Keys not
# found in the working resource set are determined to be orphaned.
def get_api_orphaned_resources(
    ctx, working_resource_set, query_func, primary_key_mapping, **kwargs
):
    obj_list = query_func(ctx, **kwargs)
    return get_orphaned_resources(working_resource_set, obj_list, primary_key_mapping)


def output_orphan_info(ctx, collection_name, orphans, format_func):
    num_orphans = len(orphans)

    if context.output_console(ctx):
        print(f"There are {num_orphans} orphanded {collection_name}")
    print(format_func(ctx, orphans))


RESOURCE_TO_FORMATTER_MAP = {
    "applications": apps.format_apps_for_garbage_collection,
    "issuers": _issuers.format_issuers_for_garbage_collection,
    "resources": _resources.format_permissions,
    "users": _users.format_users_for_garbage_collection,
    "roles": _users.format_org_user_roles,
}


def output_orphaned_resources(ctx, result_table):
    for k, v in result_table.items():
        output_orphan_info(ctx, k, v, RESOURCE_TO_FORMATTER_MAP[k])


def get_all_orphaned_resources(
    ctx,
    applications=None,
    issuers=None,
    users=None,
    resources=None,
    roles=None,
    **kwargs,
):

    result = {}
    if any([applications, issuers, users, resources]):
        result.update(
            get_org_orphaned_resources(
                ctx,
                applications=applications,
                issuers=issuers,
                users=users,
                resources=resources,
                **kwargs,
            )
        )

    if roles:
        result.update(get_app_orphaned_resources(ctx, roles=roles, **kwargs))
    return result


def get_org_orphaned_resources(
    ctx, applications=None, issuers=None, users=None, resources=None, **kwargs
):
    org_id_list = get_org_id_list(ctx, **kwargs)
    result = {}

    if applications:
        result["applications"] = get_api_orphaned_resources(
            ctx, org_id_list, apps.query, [PrimaryKeyMapping("org_id")], **kwargs
        )

    if issuers:
        result["issuers"] = get_api_orphaned_resources(
            ctx, org_id_list, _issuers.query, [PrimaryKeyMapping("org_id")], **kwargs
        )

    if resources:
        result["resources"] = get_api_orphaned_resources(
            ctx,
            org_id_list,
            _resources.query_permissions,
            [PrimaryKeyMapping("org_id", collection="spec")],
            **kwargs,
        )

    if users:
        result["users"] = _users.query(ctx, orgless_users=True, **kwargs)["users"]

    return result


def get_app_orphaned_resources(ctx, roles=None, **kwargs):
    result = {}
    list_of_apps = apps.query(ctx, **kwargs)
    app_org_id_list = {(app.name, app.org_id) for app in list_of_apps}
    orphans = get_api_orphaned_resources(
        ctx,
        app_org_id_list,
        _users.list_org_user_roles,
        [PrimaryKeyMapping("application"), PrimaryKeyMapping("org_id")],
        **kwargs,
    )

    orphans = [
        orphan
        for orphan in orphans
        if not orphan.application.startswith("urn:api:agilicus")
    ]

    result["roles"] = orphans
    return result
