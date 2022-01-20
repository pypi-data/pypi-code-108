from . import context
from .input_helpers import get_org_from_input_or_ctx
import agilicus
from .output.table import (
    spec_column,
    format_table,
    metadata_column,
    status_column,
)


def add_certificate(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs["org_id"] = org_id

    if kwargs["certificate"] is not None:
        certificate = open(kwargs["certificate"], "r").read()
        kwargs["certificate"] = certificate

    spec = agilicus.X509CertificateSpec(**kwargs)
    req = agilicus.X509Certificate(spec=spec)
    return apiclient.certificates_api.create_cert(req)


def get_certificate(ctx, certificate_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    return apiclient.certificates_api.get_cert(certificate_id, org_id=org_id, **kwargs)


def delete_certificate(ctx, certificate_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    return apiclient.certificates_api.delete_cert(
        certificate_id, org_id=org_id, **kwargs
    )


def list_certificates(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    query_results = apiclient.certificates_api.list_certs(
        org_id=org_id, **kwargs
    ).certificates
    return query_results


def format_certificates_as_text(ctx, certificates):
    columns = [
        metadata_column("id"),
        spec_column("csr_id"),
        spec_column("org_id"),
        spec_column("message"),
        spec_column("reason"),
        status_column("not_before"),
        status_column("not_after"),
    ]
    return format_table(ctx, certificates, columns)
