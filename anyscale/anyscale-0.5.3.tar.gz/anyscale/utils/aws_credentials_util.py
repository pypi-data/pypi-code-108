from typing import Any, cast, Dict


def get_credentials_from_cluster_config(
    cluster_config: Dict[str, Any]
) -> Dict[str, Any]:
    provider_config = cluster_config.get("provider")

    try:
        if provider_config:
            if provider_config["type"] == "external" and provider_config["module"] in [
                "anyscale.autoscaler.node_provider.AnyscalePoolingNodeProvider",
                "anyscale.autoscaler.node_provider.AnyscaleInstanceManagerNodeProvider",
            ]:
                # Grab the Inner provider
                provider_config = provider_config["inner_provider"]

            if (
                provider_config["type"] == "external"
                and provider_config["module"]
                == "anyscale.autoscaler.aws.node_provider.AnyscaleAWSNodeProvider"
            ):
                # Anyscale AWS provider
                return cast(Dict[str, Any], provider_config["aws_credentials"])
            elif provider_config["type"] == "aws":
                return cast(Dict[str, Any], provider_config["aws_credentials"])

        return {}
    except KeyError:
        return {}


def get_credentials_as_env_vars_from_cluster_config(
    cluster_config: Dict[str, Any]
) -> Dict[str, Any]:
    aws_credentials = get_credentials_from_cluster_config(cluster_config)

    key_id = aws_credentials.get("aws_access_key_id")
    access_key = aws_credentials.get("aws_secret_access_key")
    session_token = aws_credentials.get("aws_session_token")

    result = {}

    if key_id:
        result["AWS_ACCESS_KEY_ID"] = key_id
    if access_key:
        result["AWS_SECRET_ACCESS_KEY"] = access_key
    if session_token:
        result["AWS_SESSION_TOKEN"] = session_token

    return result
