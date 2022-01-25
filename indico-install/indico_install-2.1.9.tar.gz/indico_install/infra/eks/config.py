import os
from functools import wraps

import boto3
from cached_property import cached_property
from click import prompt

from indico_install.config import merge_dicts
from indico_install.infra.input_utils import postgres_input

access_key = os.getenv("AWS_ACCESS_KEY_ID")
access_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
aws_profile = os.getenv("AWS_PROFILE") or os.getenv("AWS_DEFAULT_PROFILE", "default")


def ask_for_infra_input(conf):
    """
    Conf is a full dictionary
    Root is the key path we've followed to get to conf
    ask_all is whether or not to re-ask for input for existing values
    """
    data_gw_details = conf["clusterVolumes"]["rwx"]["nfs"]
    api_gw_details = conf["clusterVolumes"]["rox"]["nfs"]
    gateway_ip = prompt(
        f"What is your gateway IP?", type=str, default=data_gw_details.get("server")
    )

    client_bucket_name = prompt(
        f"What is the name of your indico-data S3 bucket?",
        type=str,
        default=data_gw_details.get("path"),
    )
    if client_bucket_name and not client_bucket_name.startswith("/"):
        client_bucket_name = f"/{client_bucket_name}"

    model_bucket_name = prompt(
        f"What is the name of your indico-api-models S3 bucket?",
        type=str,
        default=api_gw_details.get("path"),
    )
    if model_bucket_name and not model_bucket_name.startswith("/"):
        model_bucket_name = f"/{model_bucket_name}"

    conf["clusterVolumes"]["rwx"]["nfs"] = {
        "server": gateway_ip,
        "path": client_bucket_name,
    }
    conf["clusterVolumes"]["rox"]["nfs"] = {
        "server": gateway_ip,
        "path": model_bucket_name,
    }

    postgres_input(conf)

    cluster_name = prompt(
        "What is the name of your EKS cluster?",
        type=str,
        default=conf.get("cluster", {}).get("name"),
    )
    gateway_name = prompt(
        "What is the name of your storage gateway?",
        type=str,
        default=conf.get("cluster", {}).get("gatewayName"),
    )
    internal_elb_annotation = "service.beta.kubernetes.io/aws-load-balancer-internal"
    cluster_private = prompt(
        "Will your ELB be on a private subnet?",
        type=bool,
        default=internal_elb_annotation
        in conf.get("services", {})
        .get("app-edge", {})
        .get("values", {})
        .get("annotations", {}),
    )
    if cluster_private:
        conf["services"] = merge_dicts(
            conf.get("services", {}),
            {
                "app-edge": {
                    "values": {
                        "annotations": {
                            "service.beta.kubernetes.io/aws-load-balancer-internal": "0.0.0.0/0"
                        }
                    }
                }
            },
        )
    else:
        conf.get("services", {}).get("app-edge", {}).get("values", {}).get(
            "annotations", {}
        ).pop(internal_elb_annotation, None)

    conf["cluster"] = {"name": cluster_name, "gatewayName": gateway_name}
    return conf


def session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs = kwargs or {}
        if not kwargs.get("session"):
            kwargs["session"] = Session()
        return f(*args, **kwargs)

    return wrapper


class Session(object):
    def __init__(self):
        if not ((access_key and access_secret) or aws_profile):
            self._boto_session = None
        else:
            self._boto_session = boto3.session.Session(
                region_name=aws_region,
                aws_access_key_id=access_key,
                aws_secret_access_key=access_secret,
                profile_name=aws_profile,
            )

    @cached_property
    def ASGClient(self):
        return self._boto_session.client("autoscaling")

    @cached_property
    def EC2Client(self):
        return self._boto_session.client("ec2")

    @cached_property
    def EC2Resource(self):
        return self._boto_session.resource("ec2")

    @cached_property
    def EKSClient(self):
        return self._boto_session.client("eks")

    @cached_property
    def IAMClient(self):
        return self._boto_session.client("iam")

    @cached_property
    def IAMResource(self):
        return self._boto_session.resource("iam")

    @cached_property
    def RDSClient(self):
        return self._boto_session.client("rds")

    @cached_property
    def S3Client(self):
        return self._boto_session.client("s3")

    @cached_property
    def SGWClient(self):
        return self._boto_session.client("storagegateway")
