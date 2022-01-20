# -*- coding: utf-8 -*-
from typing import Union

import urllib3
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from functools import partial
from kubernetes import client, watch
from logzero import logger

from chaosk8s import create_k8s_api_client
from chaosk8s.pod.probes import read_pod_logs

from p2.driver.k8s import k8s

__all__ = ["all_deployments_available_and_healthy"]


def all_deployments_available_and_healthy(
        context: str = None,
        ns: str = "default",
        label_selector: str = None,
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Gets all deployments for namespace ns and checks their status.
    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected or something went wrong.
    """
    try:
        api = k8s.Api(context=context)
        deployments = api.deployments_for_namespace(ns)
        for name in deployments:
            if deployments[name]["status"]["available_replicas"] != \
                    deployments[name]["status"]["replicas"]:
                raise ActivityFailed(f"Deployment '{name}' is not healthy")
    except:
        raise ActivityFailed(f"Namespace {ns} deployments health could not be tested")

    return True
