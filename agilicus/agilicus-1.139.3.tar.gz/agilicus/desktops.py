import base64

from . import context
from agilicus.agilicus_api import (
    DesktopResource,
    DesktopResourceSpec,
    DesktopClientConfiguration,
)

from .input_helpers import build_updated_model
from .input_helpers import update_org_from_input_or_ctx
from .input_helpers import get_org_from_input_or_ctx
from .input_helpers import get_user_id_from_input_or_ctx
from .input_helpers import strip_none
from .output.table import (
    spec_column,
    format_table,
    metadata_column,
)


def list_desktop_resources(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    params = strip_none(kwargs)
    query_results = apiclient.app_services_api.list_desktop_resources(**params)
    return query_results.desktop_resources


def add_desktop_resource(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    spec = DesktopResourceSpec(**strip_none(kwargs))
    model = DesktopResource(spec=spec)
    return apiclient.app_services_api.create_desktop_resource(model).to_dict()


def _get_desktop_resource(ctx, apiclient, resource_id, **kwargs):
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.app_services_api.get_desktop_resource(resource_id, **kwargs)


def show_desktop_resource(ctx, resource_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return _get_desktop_resource(ctx, apiclient, resource_id, **kwargs).to_dict()


def delete_desktop_resource(ctx, resource_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.app_services_api.delete_desktop_resource(resource_id, **kwargs)


def update_desktop_resource(ctx, resource_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    get_args = {}
    update_org_from_input_or_ctx(get_args, ctx, **kwargs)
    mapping = _get_desktop_resource(ctx, apiclient, resource_id, **get_args)

    mapping.spec = build_updated_model(DesktopResourceSpec, mapping.spec, kwargs)
    return apiclient.app_services_api.replace_desktop_resource(
        resource_id, desktop_resource=mapping
    ).to_dict()


def create_desktop_client_config(ctx, desktop_resource_id, as_text, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    kwargs["org_id"] = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs["user_id"] = get_user_id_from_input_or_ctx(ctx, **kwargs)
    config = DesktopClientConfiguration(**strip_none(kwargs))
    result = apiclient.app_services_api.create_client_configuration(
        desktop_resource_id, desktop_client_configuration=config
    )

    cfg = result.generated_config.configuration_file
    if as_text:
        return base64.b64decode(cfg).decode()
    return cfg


def format_desktops_as_text(ctx, resources):
    columns = [
        metadata_column("id"),
        spec_column("org_id"),
        spec_column("name"),
        spec_column("address"),
        spec_column("desktop_type"),
        spec_column("session_type"),
        spec_column("connector_id"),
    ]

    return format_table(ctx, resources, columns)
