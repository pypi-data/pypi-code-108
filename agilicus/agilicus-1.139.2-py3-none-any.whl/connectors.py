import datetime
from datetime import timedelta
import agilicus

import agilicus_api.exceptions
import dateutil.tz
import operator

from . import context
from .input_helpers import get_org_from_input_or_ctx
from .input_helpers import strip_none
from agilicus import input_helpers
from .orgs import get_org_by_dictionary

from .output.table import (
    spec_column,
    format_table,
    column,
    metadata_column,
    subtable,
)


def query(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    params = {}
    params["org_id"] = org_id
    input_helpers.update_if_not_none(params, kwargs)
    query_results = apiclient.connectors_api.list_connector(**params)
    return query_results.connectors


def get(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    params = kwargs
    params["org_id"] = org_id
    input_helpers.update_if_not_none(params, kwargs)
    return apiclient.connectors_api.get_connector(connector_id, **params)


def query_agents(ctx, column_format=None, filter_not_has_version=None, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    if column_format == "newformat":
        kwargs["show_stats"] = True

    if org_id:
        kwargs["org_id"] = org_id
    query_results = apiclient.connectors_api.list_agent_connector(
        **strip_none(kwargs)
    ).agent_connectors
    return query_results


def format_connectors_as_text(ctx, connectors):
    app_service_columns = [
        column("id"),
        column("hostname"),
        column("port"),
        column("protocol"),
        column("service_type"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("name"),
        spec_column("org_id"),
        spec_column("connector_type", "type"),
        spec_column("service_account_id"),
        subtable(
            ctx, "application_services", app_service_columns, subobject_name="status"
        ),
    ]

    return format_table(ctx, connectors, columns)


def format_agents_with_version(  # noqa
    ctx, agents, column_format=None, filter_not_has_version=None, **kwargs
):
    org_by_id = dict()
    try:
        org_by_id, _ = get_org_by_dictionary(ctx, "")
    except agilicus_api.exceptions.ForbiddenException:
        # Fall back on getting just our own
        org_by_id, _ = get_org_by_dictionary(ctx, None)

    def _get_stats(record):
        status = record.get("status")
        if not status:
            return
        return status.to_dict()["stats"]

    def _get_version(record, key):
        return _get_stats(record)["system"]["agent_version"]

    def _get_os_version(record, key):
        return _get_stats(record)["system"]["os_version"]

    def _get_hostname(record, key):
        return _get_stats(record)["system"]["hostname"]

    def _get_agent_uptime(record, key):
        secs = _get_stats(record)["system"]["agent_uptime"]
        sec = timedelta(seconds=secs)
        d = datetime.datetime(1, 1, 1) + sec
        return f"{d.day-1}:{d.hour}:{d.minute}:{d.second}"

    def _get_collection_time(record, key):
        return _get_stats(record)["metadata"]["collection_time"]

    def _get_overall_status(record, key):
        return _get_stats(record)["overall_status"]

    def _get_org(record):
        spec = record.get("spec").to_dict()
        org_id = spec.get("org_id")
        return org_by_id.get(org_id, org_id)

    def _get_org_name(record, keys):
        return _get_org(record).get("organisation")

    def _get_org_contact(record, keys):
        return _get_org(record).get("contact_email")

    def _row_filter(record):
        if not filter_not_has_version:
            return True
        try:
            version = _get_version(record, None)
            if version != filter_not_has_version:
                return True
        except Exception:
            pass
        return False

    columns = [
        metadata_column("id"),
        spec_column("name"),
        column("stats", newname="version", getter=_get_version, optional=True),
        column("stats", newname="uptime", getter=_get_agent_uptime, optional=True),
        column("stats", newname="os_version", getter=_get_os_version, optional=True),
        column("stats", newname="last_seen", getter=_get_collection_time, optional=True),
        column("stats", newname="status", getter=_get_overall_status, optional=True),
        column("stats", newname="hostname", getter=_get_hostname, optional=True),
        column("spec", newname="org", getter=_get_org_name, optional=True),
        column("spec", newname="contact", getter=_get_org_contact, optional=True),
    ]

    return format_table(
        ctx, agents, columns, getter=operator.itemgetter, row_filter=_row_filter
    )


def format_agents_as_text(ctx, agents, column_format=None, **kwargs):
    if column_format == "newformat":
        return format_agents_with_version(ctx, agents, **kwargs)

    app_service_columns = [
        column("id"),
        column("hostname"),
        column("port"),
        column("protocol"),
        column("service_type"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("name"),
        spec_column("org_id"),
        spec_column("connection_uri"),
        spec_column("max_number_connections"),
        spec_column("local_authentication_enabled"),
        subtable(
            ctx, "application_services", app_service_columns, subobject_name="status"
        ),
    ]

    return format_table(ctx, agents, columns)


def add_agent(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    spec = agilicus.AgentConnectorSpec(org_id=org_id, **kwargs)
    connector = agilicus.AgentConnector(spec=spec)
    return apiclient.connectors_api.create_agent_connector(connector)


def get_agent(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    if org_id:
        kwargs["org_id"] = org_id
    return apiclient.connectors_api.get_agent_connector(connector_id, **kwargs)


def delete_agent(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    return apiclient.connectors_api.delete_agent_connector(
        connector_id, org_id=org_id, **kwargs
    )


def get_agent_info(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    return apiclient.connectors_api.get_agent_info(connector_id, org_id=org_id, **kwargs)


def replace_agent(
    ctx,
    connector_id,
    connection_uri=None,
    max_number_connections=None,
    name=None,
    service_account_required=None,
    local_authentication_enabled=None,
    name_slug=None,
    **kwargs,
):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    connector = apiclient.connectors_api.get_agent_connector(
        connector_id, org_id=org_id, **kwargs
    )

    if connection_uri:
        connector.spec.connection_uri = connection_uri

    if max_number_connections:
        connector.spec.max_number_connections = max_number_connections

    if name:
        connector.spec.name = name

    if service_account_required is not None:
        connector.spec.service_account_required = service_account_required

    if local_authentication_enabled is not None:
        connector.spec.local_authentication_enabled = local_authentication_enabled

    if name_slug is not None:
        connector.spec.name_slug = name_slug

    return apiclient.connectors_api.replace_agent_connector(
        connector_id, agent_connector=connector
    )


def replace_agent_auth_info(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    kwargs["org_id"] = get_org_from_input_or_ctx(ctx, **kwargs)

    info = agilicus.AgentLocalAuthInfo(**kwargs)
    return apiclient.connectors_api.replace_agent_connector_local_auth_info(
        connector_id, agent_local_auth_info=info
    )


def set_agent_connector_stats(ctx, connector_id, org_id, overall_status, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)

    system_objs = input_helpers.get_objects_by_location("system", kwargs)
    system = agilicus.AgentConnectorSystemStats(
        agent_connector_org_id=org_id, agent_connector_id=connector_id, **system_objs
    )
    transport_objs = input_helpers.get_objects_by_location("transport", kwargs)
    transport = agilicus.AgentConnectorTransportStats(**transport_objs)
    now = datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    metadata = agilicus.AgentConnectorStatsMetadata(collection_time=now)

    stats = agilicus.AgentConnectorStats(
        metadata=metadata,
        overall_status=overall_status,
        system=system,
        transport=transport,
    )

    return apiclient.connectors_api.create_agent_stats(connector_id, stats)


def get_agent_connector_stats(ctx, connector_id, org_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)

    return apiclient.connectors_api.get_agent_stats(
        connector_id, org_id=org_id, **kwargs
    )


def query_ipsec(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    kwargs["org_id"] = org_id
    kwargs = strip_none(kwargs)
    query_results = apiclient.connectors_api.list_ipsec_connector(**kwargs)
    return query_results


def add_ipsec(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    kwargs = strip_none(kwargs)

    spec = agilicus.IpsecConnectorSpec(org_id=org_id, **kwargs)
    connector = agilicus.IpsecConnector(spec=spec)
    return apiclient.connectors_api.create_ipsec_connector(connector)


def add_or_update_ipsec_connection(
    ctx,
    connector_id,
    name,
    org_id=None,
    inherit_from=None,
    remote_ipv4_block=None,
    ike_chain_of_trust_certificates_filename=None,
    update_connection=False,
    **kwargs,
):

    if ike_chain_of_trust_certificates_filename is not None:
        ike_chain_of_trust_certificates = open(
            ike_chain_of_trust_certificates_filename, "r"
        ).read()
        kwargs["ike_chain_of_trust_certificates"] = ike_chain_of_trust_certificates

    if remote_ipv4_block:
        remote_ipv4_ranges = []
        for block in remote_ipv4_block:
            remote_ipv4_ranges.append(agilicus.IpsecConnectionIpv4Block(block))
        kwargs["remote_ipv4_ranges"] = remote_ipv4_ranges

    connector = get_ipsec(ctx, connector_id, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    connection_spec = agilicus.IpsecConnectionSpec(**kwargs)
    if update_connection:
        new_connections = []
        for _connection in connector.spec.connections:
            if _connection.name == name:
                updates = {
                    key: item
                    for key, item in connection_spec.to_dict().items()
                    if item is not None
                }
                spec_dict = {**_connection.spec.to_dict(), **updates}
                # replay the kwargs into a new spec with the copy
                connectionSpec = agilicus.IpsecConnectionSpec(**spec_dict)
                _connection.spec = connectionSpec
                connection = _connection
                if inherit_from is not None:
                    connection.inherit_from = inherit_from

            new_connections.append(_connection)
        connector.spec.connections = new_connections
    else:
        connection = agilicus.IpsecConnection(
            name, inherit_from=inherit_from, spec=connection_spec
        )
        connector.spec.connections.append(connection)

    return apiclient.connectors_api.replace_ipsec_connector(
        connector_id, ipsec_connector=connector
    )


def delete_ipsec_connection(ctx, connector_id, name, org_id=None, **kwargs):
    connector = get_ipsec(ctx, connector_id, org_id=org_id)
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)

    kwargs = strip_none(kwargs)
    update_connections = []
    for connection in connector.spec.connections:
        if connection.name != name:
            update_connections.append(connection)
    connector.spec.connections = update_connections

    return apiclient.connectors_api.replace_ipsec_connector(
        connector_id, ipsec_connector=connector
    )


def get_ipsec(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    kwargs = strip_none(kwargs)
    return apiclient.connectors_api.get_ipsec_connector(
        connector_id, org_id=org_id, **kwargs
    )


def delete_ipsec(ctx, connector_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    kwargs = strip_none(kwargs)
    return apiclient.connectors_api.delete_ipsec_connector(
        connector_id, org_id=org_id, **kwargs
    )


def get_ipsec_info(ctx, connector_id, org_id=None, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    kwargs = strip_none(kwargs)
    return apiclient.connectors_api.get_ipsec_connector_info(
        connector_id, org_id=org_id, **kwargs
    )


def replace_ipsec(
    ctx,
    connector_id,
    name=None,
    name_slug=None,
    **kwargs,
):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs.pop("org_id", None)
    kwargs = strip_none(kwargs)

    connector = apiclient.connectors_api.get_ipsec_connector(
        connector_id, org_id=org_id, **kwargs
    )

    if name:
        connector.spec.name = name

    if name_slug:
        connector.spec.name_slug = name_slug

    return apiclient.connectors_api.replace_ipsec_connector(
        connector_id, ipsec_connector=connector
    )
