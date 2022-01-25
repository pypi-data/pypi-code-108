# from kfputils.run import Runner, _display_run
from kfp import Client
from os import environ


def get_access_token():
    with open(environ["KF_PIPELINES_SA_TOKEN_PATH"]) as f:
        return f.read()


def get_kfp_client_inside_cluster():
    return Client(
        existing_token=get_access_token(),
        host="http://ml-pipeline.kubeflow.svc.cluster.local:8888",
    )
