import logging

from tecton_spark import conf


def get_snowflake_feature_view_name(feature_view_name):
    """ Get the pre-defined view name in snowflake for a given feature view."""
    # TODO(TEC-6895): Put the registered feature view name in the data proto and get it from there instead.
    cluster_name = conf.get_or_none("TECTON_CLUSTER_NAME") or "TECTON_DEV_SNOWFLAKE"
    cluster_name = cluster_name.replace("-", "_")
    workspace_name = conf.get_or_none("TECTON_WORKSPACE").replace("-", "_")
    fv_name = feature_view_name.replace("-", "_")
    source = f"{cluster_name}.{workspace_name}.{fv_name}".upper()
    return source


def supress_snowflake_logs():
    """ Suppress snowflake logs. This is usually needed after an import."""
    logger = logging.getLogger("snowflake")
    logger.setLevel(logging.CRITICAL)
