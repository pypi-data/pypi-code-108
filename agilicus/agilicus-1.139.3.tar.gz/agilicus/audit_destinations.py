from typing import Union

from agilicus.agilicus_api import (
    AuditDestination,
    AuditDestinationSpec,
    AuditDestinationFilter,
    AuditDestinationAuthentication,
    HTTPBasicAuth,
    HTTPBearerAuth,
)

from . import context
from .input_helpers import build_updated_model
from .input_helpers import update_org_from_input_or_ctx
from .input_helpers import strip_none
from .output.table import (
    column,
    spec_column,
    format_table,
    metadata_column,
    subtable,
)

DESTINATION_TYPES = ["file", "webhook"]
FILTER_TYPES = ["subsystem", "audit_agent_type", "audit_agent_id", "hostname"]
AUTH_TYPES = ["none", "http_basic", "http_bearer", "agilicus_bearer"]


def _get_properties(property_names, properties) -> dict:
    result = {}
    no_entry = object()
    for key in property_names:
        val = properties.get(key, no_entry)
        if val != no_entry:
            result[key] = val
    return result


def _get_audit_destination_properties(properties) -> dict:
    return _get_properties(
        ["name", "org_id", "comment", "destination_type", "location", "enabled"],
        properties,
    )


def _get_basic_auth(properties):
    existing = properties.get("http_basic", {})
    props = _get_properties(["username", "password"], properties)
    existing.update(props)

    if not existing:
        return None

    return HTTPBasicAuth(
        username=existing.get("username", ""), password=existing.get("password", "")
    )


def _get_bearer_auth(properties):
    existing = properties.get("http_bearer", {})
    props = _get_properties(["token"], properties)
    existing.update(props)

    if not existing:
        return None

    return HTTPBearerAuth(**existing)


def _build_authentication(properties):
    auth_type = properties.get("authentication_type", None)
    if not auth_type:
        return None

    auth = AuditDestinationAuthentication(authentication_type=auth_type)

    basic_auth = _get_basic_auth(properties)
    bearer_auth = _get_bearer_auth(properties)

    if basic_auth is not None:
        auth.http_basic = basic_auth

    if bearer_auth is not None:
        auth.http_bearer = bearer_auth

    return auth


def _update_authentication(
    auth: Union[AuditDestinationAuthentication, None], properties: dict
):
    if auth is None:
        return None

    as_dict = auth.to_dict()

    as_dict.update(properties)

    return _build_authentication(as_dict)


def list_audit_destinations(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    params = strip_none(kwargs)
    query_results = apiclient.audits_api.list_audit_destinations(**params)
    return query_results.audit_destinations


def add_audit_destination(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    audit_properties = _get_audit_destination_properties(kwargs)
    spec = AuditDestinationSpec(filters=[], **audit_properties)
    spec.authentication = _build_authentication(kwargs)

    model = AuditDestination(spec=spec)
    return apiclient.audits_api.create_audit_destination(model).to_dict()


def _get_audit_destination(ctx, apiclient, destination_id, **kwargs):
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.audits_api.get_audit_destination(destination_id, **kwargs)


def show_audit_destination(ctx, destination_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return _get_audit_destination(ctx, apiclient, destination_id, **kwargs).to_dict()


def delete_audit_destination(ctx, destination_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.audits_api.delete_audit_destination(destination_id, **kwargs)


def update_audit_destination(ctx, destination_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    get_args = {}
    update_org_from_input_or_ctx(get_args, ctx, **kwargs)
    mapping = _get_audit_destination(ctx, apiclient, destination_id, **get_args)

    kwargs = strip_none(kwargs)
    audit_properties = _get_audit_destination_properties(kwargs)
    auth = mapping.spec.authentication

    # Clear out the old auth which failds with build_updated_model
    del mapping.spec["authentication"]
    mapping.spec = build_updated_model(
        AuditDestinationSpec, mapping.spec, audit_properties
    )
    auth = _update_authentication(auth, kwargs)
    if auth is not None:
        mapping.spec.authentication = auth
    return apiclient.audits_api.replace_audit_destination(
        destination_id, audit_destination=mapping
    ).to_dict()


def add_audit_destination_filter(ctx, destination_id, filter_type, value, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    get_args = {}
    update_org_from_input_or_ctx(get_args, ctx, **kwargs)
    mapping = _get_audit_destination(ctx, apiclient, destination_id, **get_args)
    filter = AuditDestinationFilter(filter_type, value)

    mapping.spec.filters.append(filter)
    return apiclient.audits_api.replace_audit_destination(
        destination_id, audit_destination=mapping
    ).to_dict()


def delete_audit_destination_filter(ctx, destination_id, filter_type, value, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    get_args = {}
    update_org_from_input_or_ctx(get_args, ctx, **kwargs)
    mapping = _get_audit_destination(ctx, apiclient, destination_id, **get_args)
    remaining = []
    total = 0
    for filter in mapping.spec.filters:
        if filter.filter_type != filter_type:
            remaining.append(filter)
            continue
        if value is not None and filter.value != value:
            remaining.append(filter)
            continue
        total += 1
    mapping.spec.filters = remaining

    return apiclient.audits_api.replace_audit_destination(
        destination_id, audit_destination=mapping
    ).to_dict()


def format_audit_destinations_as_text(ctx, resources):
    filter_columns = [
        column("filter_type"),
        column("value"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("org_id"),
        spec_column("name"),
        spec_column("destination_type"),
        spec_column("location"),
        spec_column("comment"),
        spec_column("enabled"),
        spec_column("authentication.authentication_type", "authentication_type"),
        subtable(ctx, "filters", filter_columns, subobject_name="spec"),
    ]

    return format_table(ctx, resources, columns)
