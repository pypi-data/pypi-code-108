# -*- coding: utf-8 -*-
import re
from typing import Union
from time import sleep

import urllib3
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from functools import partial
from kubernetes import client, watch
from logzero import logger

from chaosk8s.deployment.actions import scale_deployment
from chaosk8s.deployment.probes import deployment_available_and_healthy

from p2.driver.k8s import k8s

__all__ = ["scale_one_down_up", "scale_all_down_up"]

def scale_one_down_up(
        name: str,
        context: str = None,
        ns: str = "default",
        delay: int = 1,
        secrets: Secrets = None):
    """
    Get the number of desired replicas for the deployment name
    Scale deployment down, waits for a delay and then
    scale it up back to the desired replicas
    """
    api = k8s.Api(context=context)
    deployments = api.deployments_for_namespace(ns)
    if name in deployments:
        replicas = deployments[name]["DESIRED_REPLICAS"]
        logger.info("Desired replicas: {}".format(replicas))

        try:
            scale_deployment(
                    name=name,
                    replicas=0,
                    ns=ns,
                    secrets=secrets
            )

            logger.info(f"Deployment {name} scaled down to 0 replicas")
            logger.info(f"Now sleeping for {delay} seconds...")
            sleep(delay)

            scale_deployment(
                    name=name,
                    replicas=replicas,
                    ns=ns,
                    secrets=secrets
            )
            logger.info(f"Deployment {name} scaled up to {replicas} replicas")
            return replicas

        except Exception as e:
            logger.error(f"Error: not able to scale deployment {name}: {e}")
            raise ActivityFailed(
                "Failed to scale deployment '{s}': {e}".format(s=name, e=str(e)))

    else:
        raise ActivityFailed(f"Could not find deployment {name} in {ns}")


def scale_all_down_up(
        context: str = None,
        ns: str = "default",
        skip: list = [],
        delay: int = 1,
        secrets: Secrets = None):
    """
    for all deployments:
        Next if name in skip list (deployments to skip).
        Get the number of desired replicas for the deployment name
        Scale deployment down, waits for a delay and then
        scale it up back to the desired replicas
    """
    try:
        api = k8s.Api(context=context)
        deployments = api.deployments_for_namespace(ns)
        replicas = dict()
        for name in deployments:
            if deployment_to_skip(skip, name):
                continue
            replicas[name] = deployments[name]["DESIRED_REPLICAS"]
            logger.info("Desired replicas for deployment {}: {}".format(name, replicas[name]))

            scale_deployment(
                    name=name,
                    replicas=0,
                    ns=ns,
                    secrets=secrets
            )
            logger.info(f"Deployment {name} scaled down to 0 replicas")

        logger.info(f"Now sleeping for {delay} seconds...")
        sleep(delay)

        for name in deployments:
            scale_deployment(
                    name=name,
                    replicas=replicas[name],
                    ns=ns,
                    secrets=secrets
            )
            logger.info("Deployment {} scaled up to {} replicas".format(name, replicas[name]))
        return 1

    except Exception as e:
        logger.error("Error: not able to scale namespace {}: {}".format(ns, str(e)))
        raise ActivityFailed(
            "Failed to scale namespace '{ns}': {e}".format(ns=ns, e=str(e)))

def deployment_to_skip(skip: list, name: str):
    for token in skip:
        if re.search(token, name):
            return True
    return False
