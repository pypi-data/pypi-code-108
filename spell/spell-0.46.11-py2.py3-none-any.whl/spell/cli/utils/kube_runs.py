import os

import spell.cli.utils  # for __file__ introspection
from spell.cli.utils.cluster_utils import kubectl

RUNS_MANIFEST_DIR = os.path.join(os.path.dirname(spell.cli.utils.__file__), "kube_manifests", "spell-run")

#########################
# Runs
#########################


# must be executed with elevated permissions (crd)
def add_argo():
    kubectl(
        "apply",
        "-f",
        os.path.join(RUNS_MANIFEST_DIR, "argo"),
        "-n",
        "spell-run",
    )


def delete_resource(namespace, resource, name):
    kubectl(
        "delete",
        resource,
        name,
        "-n",
        namespace,
        "--ignore-not-found",
    )


def create_resource(namespace, resource, name, paths):
    kubectl(
        "create",
        resource,
        name,
        "-n",
        namespace,
        *[f"--from-file={path}" for path in paths],
    )


def create_build_run_configmap(namespace):
    # Delete if it exists
    delete_resource(namespace, "configmap", "k8s-build")
    create_resource(
        namespace,
        "configmap",
        "k8s-build",
        [os.path.join(RUNS_MANIFEST_DIR, "build.sh")],
    )


def create_run_configmap(namespace):
    # Delete if it exists
    delete_resource(namespace, "configmap", "k8s-run")
    create_resource(
        namespace,
        "configmap",
        "k8s-run",
        [
            os.path.join(RUNS_MANIFEST_DIR, "run.sh"),
            os.path.join(RUNS_MANIFEST_DIR, "runlog.py"),
        ],
    )


def create_build_artifacts_pvc(namespace):
    kubectl("apply", "-n", namespace, "-f", os.path.join(RUNS_MANIFEST_DIR, "build_artifacts_pvc.yaml"))
