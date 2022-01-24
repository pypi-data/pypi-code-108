#!/usr/bin/env python3
import click


from indico_install.infra.init import init
from indico_install.cluster_manager import ClusterManager
from .setup import aks_setup, ask_for_infra_input
from . import storage, cluster


@click.group("aks")
@click.pass_context
def aks(ctx):
    """
    Indico infrastructure setup and validation for Azure Kubernetes Service
    """
    ctx.ensure_object(dict)
    ctx.obj["TRACKER"] = ClusterManager()


aks.command("init")(init(__name__))


@aks.command("check")
@click.pass_context
def check(ctx):
    """
    Check the state of an existing cluster to validate
    that it meets certain requirements
    """
    aks_setup()
    conf = ctx.obj["TRACKER"].cluster_config
    ask_for_infra_input(conf)
    cluster.check(conf)
    storage.check(conf)
    ctx.obj["TRACKER"].save()


@aks.command("create")
@click.pass_context
def create(ctx, upload=False):
    """
    Configure your AKS installation
    """
    aks_setup()
    conf = ctx.obj["TRACKER"].cluster_config
    ask_for_infra_input(conf)
    cluster.create(conf)
    storage.create(conf)
    ctx.obj["TRACKER"].save()
