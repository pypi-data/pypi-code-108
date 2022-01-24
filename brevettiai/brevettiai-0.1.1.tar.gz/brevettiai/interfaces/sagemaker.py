import json
import logging
import os
import sys

from brevettiai.io.credentials import Credentials, LoginError

log = logging.getLogger(__name__)

SAGEMAKER_HYPERPARAMETER_PATH = "/opt/ml/input/config/hyperparameters.json"


def load_hyperparameters_cmd_args(hyperparameter_path=SAGEMAKER_HYPERPARAMETER_PATH):
    try:
        with open(hyperparameter_path, "r") as hyper:
            hyper_parameters = json.load(hyper)
        log.info("Loaded hyper parameters " + json.dumps(hyper_parameters))
        sys.argv += [kki for kk, vv in hyper_parameters.items() for kki in ["--" + kk, vv]]
        log.info("Added hyper parameters to sys.argv")
    except IOError:
        log.info("No hyper parameters found!")


class SagemakerCredentials(Credentials):

    def get_credentials(self, resource_id, resource_type="dataset", mode="r"):
        if not "TRAINING_JOB_ARN" in os.environ:
            raise LoginError(f"Error logging in with Sagemaker credentials, Not on Sagemaker")
        try:
            return fetch_aws_credentials()
        except Exception:
            raise LoginError(f"Error logging in with Sagemaker credentials")


def fetch_aws_credentials():
    import boto3
    _, partition, service, region, *_ = os.environ.get("TRAINING_JOB_ARN", "arn:aws:sagemaker:eu-west-1:xx").split(":")
    sess = boto3.session.Session()
    cred = sess.get_credentials()
    s3 = sess.client("s3", region_name=region)
    os.environ["S3_USE_HTTPS"] = "1"
    os.environ["S3_VERIFY_SSL"] = "1"

    return dict(
        access_key=cred.access_key,
        secret_key=cred.secret_key,
        region=region,
        session_token=cred.token,
        endpoint=s3.meta.endpoint_url.split("://", 1)[-1]
    )
