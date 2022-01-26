from prettytable import PrettyTable

from . import context
from . import input_helpers

from .input_helpers import strip_none
from .output import table


def query(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs["org_id"] = input_helpers.get_org_from_input_or_ctx(ctx, **kwargs)
    dt_from = kwargs.pop("dt_from", "now-1day")
    kwargs = strip_none(kwargs)

    query_results = apiclient.audits_api.list_audits(dt_from=dt_from, **kwargs)

    if query_results:
        return query_results.audits

    return []


def format_audit_list_as_text(audits):
    table = PrettyTable(
        [
            "action",
            "user_id",
            "org_id",
            "source_ip",
            "target_resource_type",
            "target_id",
            "date",
            "trace_id",
            "session",
            "secondary_id",
            "tertiary_id",
            "parent_id",
            "grandparent_id",
        ]
    )
    for record in audits:
        date = "---"
        if record.time:
            date = record.time.strftime("%Y-%m-%d %H:%M:%S %z")

        table.add_row(
            [
                record.action,
                record.user_id,
                record.org_id,
                record.source_ip,
                record.target_resource_type,
                record.target_id,
                date,
                record.trace_id,
                record.session,
                record.secondary_id,
                record.tertiary_id,
                record.parent_id,
                record.grandparent_id,
            ]
        )
    table.align = "l"
    return table


def query_auth_audits(ctx, **kwargs):
    apiclient = context.get_apiclient(ctx)
    kwargs["org_id"] = input_helpers.get_org_from_input_or_ctx(ctx, **kwargs)
    dt_from = kwargs.pop("dt_from", "now-1day")
    kwargs = strip_none(kwargs)

    query_results = apiclient.audits_api.list_auth_records(dt_from=dt_from, **kwargs)

    if query_results:
        return query_results.auth_audits

    return []


def format_auth_audit_list_as_text(ctx, records):
    columns = [
        table.mapped_column("time", "date"),
        table.column("event"),
        table.column("user_id"),
        table.column("org_id"),
        table.column("source_ip"),
        table.column("token_id"),
        table.column("trace_id"),
        table.column("session"),
        table.column("issuer"),
        table.column("client_id"),
        table.column("application_name"),
        table.column("upstream_user_id"),
        table.column("login_org_id"),
        table.column("upstream_idp"),
        table.column("stage"),
        table.column("user_agent"),
    ]
    return table.format_table(ctx, records, columns)
