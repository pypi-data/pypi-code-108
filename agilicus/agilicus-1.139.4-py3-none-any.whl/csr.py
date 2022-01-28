from . import context
from .input_helpers import get_org_from_input_or_ctx
import agilicus
from .output.table import (
    spec_column,
    format_table,
    metadata_column,
    status_column,
    subtable,
)


def add_agent_csr(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    if kwargs["request"] is not None:
        csr_request = open(kwargs["request"], "r").read()
        kwargs["request"] = csr_request

    spec = agilicus.CertSigningReqSpec(org_id=org_id, **kwargs)
    req = agilicus.CertSigningReq(spec=spec)
    return apiclient.connectors_api.create_agent_csr(connector_id, req)


def list_agent_csr(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    query_results = apiclient.connectors_api.list_agent_csr(
        org_id=org_id, **kwargs
    ).certificate_signing_requests
    return query_results


def get_agent_csr(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    return apiclient.connectors_api.get_agent_csr(
        org_id=org_id,
        **kwargs,
    )


def list_csr(ctx, reason=None, not_valid_after=None, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    if reason is not None:
        kwargs["reason"] = reason

    if not_valid_after is not None:
        kwargs["not_valid_after"] = not_valid_after

    query_results = apiclient.certificates_api.list_csr(
        org_id=org_id, **kwargs
    ).certificate_signing_requests
    return query_results


def get_csr(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    return apiclient.certificates_api.get_csr(org_id=org_id, **kwargs)


def delete_csr(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    return apiclient.certificates_api.delete_csr(org_id=org_id, **kwargs)


def format_csr_as_text(ctx, csrs):
    certificate_columns = [
        spec_column("reason"),
        status_column("not_after"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("org_id"),
        spec_column("private_key_id", "key_id", max_size=8),
        status_column("dns_names"),
        subtable(ctx, "certificates", certificate_columns, subobject_name="status"),
    ]

    return format_table(ctx, csrs, columns)
