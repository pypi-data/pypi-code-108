import agilicus
from . import context
from .input_helpers import get_org_from_input_or_ctx
from .output.table import (
    spec_column,
    format_table,
    metadata_column,
)


def add(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    spec = agilicus.ServiceForwarderSpec(org_id=org_id, **kwargs)
    forwarder = agilicus.ServiceForwarder(spec=spec)
    return apiclient.app_services_api.create_service_forwarder(forwarder)


def query(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    kwargs["org_id"] = org_id
    query_results = apiclient.app_services_api.list_service_forwarders(**kwargs)
    return query_results.service_forwarders


def get(ctx, id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    return apiclient.app_services_api.get_service_forwarder(id, org_id=org_id, **kwargs)


def delete(ctx, id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    return apiclient.app_services_api.delete_service_forwarder(
        id, org_id=org_id, **kwargs
    )


def replace(
    ctx,
    id,
    name=None,
    port=None,
    connector_id=None,
    application_service_id=None,
    bind_address=None,
    protocol=None,
    **kwargs,
):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    forwarder = apiclient.app_services_api.get_service_forwarder(
        id, org_id=org_id, **kwargs
    )

    if name:
        forwarder.spec.name = name

    if port:
        forwarder.spec.port = port

    if connector_id:
        forwarder.spec.connector_id = connector_id

    if application_service_id:
        forwarder.spec.application_service_id = application_service_id

    if bind_address:
        forwarder.spec.bind_address = bind_address

    if protocol:
        forwarder.spec.protocol = protocol

    return apiclient.app_services_api.replace_service_forwarder(
        id, service_forwarder=forwarder
    )


def format_forwarders_as_text(ctx, forwarders):
    columns = [
        metadata_column("id"),
        spec_column("name"),
        spec_column("org_id"),
        spec_column("bind_address"),
        spec_column("port"),
        spec_column("protocol"),
        spec_column("connector_id"),
        spec_column("application_service_id", "app_service_id"),
    ]
    return format_table(ctx, forwarders, columns)
