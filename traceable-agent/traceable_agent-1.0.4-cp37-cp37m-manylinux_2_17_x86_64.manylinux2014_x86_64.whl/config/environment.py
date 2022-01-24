import os

def _is_true(env_key):
    value = os.environ.get(env_key)
    return value.lower() == 'true'


def overwrite_with_environment(config):
    if "TA_BLOCKING_CONFIG_ENABLED" in os.environ:
        config.blocking_config.enabled.value = _is_true("TA_BLOCKING_CONFIG_ENABLED")

    if "TA_BLOCKING_CONFIG_DEBUG_LOG" in os.environ:
        config.blocking_config.debug_log.value = _is_true("TA_BLOCKING_CONFIG_DEBUG_LOG")

    if "TA_BLOCKING_CONFIG_EVALUATE_BODY" in os.environ:
        config.blocking_config.evaluate_body.value = _is_true("TA_BLOCKING_CONFIG_EVALUATE_BODY")

    if "TA_BLOCKING_CONFIG_MODSECURITY_ENABLED" in os.environ:
        config.blocking_config.modsecurity.enabled.value = _is_true("TA_BLOCKING_CONFIG_MODSECURITY_ENABLED")

    if "TA_BLOCKING_CONFIG_REGION_BLOCKING_ENABLED" in os.environ:
        config.blocking_config.region_blocking.enabled.value = _is_true("TA_BLOCKING_CONFIG_REGION_BLOCKING_ENABLED")

    if "TA_BLOCKING_CONFIG_REMOTE_CONFIG_ENABLED" in os.environ:
        config.blocking_config.remote_config.enabled.value = _is_true("TA_BLOCKING_CONFIG_REMOTE_CONFIG_ENABLED")

    if "TA_BLOCKING_CONFIG_REMOTE_CONFIG_ENDPOINT" in os.environ:
        config.blocking_config.remote_config.endpoint.value = os.environ["TA_BLOCKING_CONFIG_REMOTE_CONFIG_ENDPOINT"]

    if "TA_BLOCKING_CONFIG_REMOTE_CONFIG_POLL_PERIOD_SECONDS" in os.environ:
        config.blocking_config.remote_config.poll_period_seconds.value = \
            int(os.environ["TA_BLOCKING_CONFIG_REMOTE_CONFIG_POLL_PERIOD_SECONDS"])

    if "TA_BLOCKING_CONFIG_SKIP_INTERNAL_REQUEST" in os.environ:
        config.blocking_config.skip_internal_request.value = _is_true("TA_BLOCKING_CONFIG_SKIP_INTERNAL_REQUEST")

    if "TA_OPA_ENABLED" in os.environ:
        config.opa.enabled.value = _is_true("TA_OPA_ENABLED")

    if "TA_OPA_ENDPOINT" in os.environ:
        config.opa.endpoint.value = os.environ['TA_OPA_ENDPOINT']

    if "TA_OPA_POLL_PERIOD_SECONDS" in os.environ:
        config.opa.poll_period_seconds.value = int(os.environ['TA_OPA_POLL_PERIOD_SECONDS'])
