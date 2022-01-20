# -*- coding: utf-8 -*-

default_profile = "profile-rer.sitesearch:default"
uninstall_profile = "profile-rer.sitesearch:uninstall"


def to_4000(context):
    """ """
    context.runAllImportStepsFromProfile("profile-rer.sitesearch:to_4000")
    context.runImportStepFromProfile(default_profile, "plone.app.registry")
