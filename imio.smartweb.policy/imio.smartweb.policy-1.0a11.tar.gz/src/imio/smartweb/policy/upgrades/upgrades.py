# -*- coding: utf-8 -*-

from imio.smartweb.policy.utils import add_iam_folder
from plone import api
from plone.app.workflow.remap import remap_workflow
import logging

logger = logging.getLogger("imio.smartweb.policy")
PROFILEID = "profile-imio.smartweb.policy:default"


def configure_first_official_release(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile("profile-pas.plugins.imio:default")
    portal_setup.runImportStepFromProfile(PROFILEID, "typeinfo")
    portal_setup.runImportStepFromProfile(PROFILEID, "viewlets")


def reload_types(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runImportStepFromProfile(PROFILEID, "typeinfo")


def transform_old_iam_link_to_iam_folder(context):
    portal = api.portal.get()
    obj = portal.get("i-am") or portal.get("je-suis")
    if obj is not None:
        if obj.portal_type != "Link":
            return
        else:
            api.content.delete(obj=obj)
    current_lang = api.portal.get_current_language()[:2]
    add_iam_folder(portal, current_lang)


def restore_links_workflow(context):
    portal = api.portal.get()
    remap_workflow(portal, type_ids=("Link",), chain="(Default)")


def reload_viewlets(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runImportStepFromProfile(PROFILEID, "viewlets")
