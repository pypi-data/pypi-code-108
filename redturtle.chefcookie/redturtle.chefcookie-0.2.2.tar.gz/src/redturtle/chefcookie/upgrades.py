# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-redturtle.chefcookie:default"


def update_profile(context, profile, run_dependencies=True):
    context.runImportStepFromProfile(DEFAULT_PROFILE, profile, run_dependencies)


def update_registry(context):
    update_profile(context, "plone.app.registry", run_dependencies=False)
    logger.info("Update registry")
