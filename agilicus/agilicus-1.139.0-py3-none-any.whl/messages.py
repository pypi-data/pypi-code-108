from . import context
from .output.table import (
    format_table,
    metadata_column,
    spec_column,
)


def list_message_endpoints(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    results = apiclient.messages_api.list_message_endpoints(**kwargs)
    return results.messages


def format_message_endpoints(ctx, details):
    columns = [
        metadata_column("id"),
        metadata_column("user_id", "User ID"),
        spec_column("endpoint_type", "Type"),
        spec_column("nickname", "Nickname"),
        spec_column("address", "Address"),
    ]

    return format_table(ctx, details, columns)


def delete_message_endpoint(ctx, message_endpoint_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    resp = apiclient.messages_api.delete_message_endpoint(message_endpoint_id)
    return resp


def get_message_endpoint(ctx, message_endpoint_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    result = apiclient.messages_api.get_message_endpoint(message_endpoint_id, **kwargs)
    return result
