PROFILE_ID = 'profile-Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow'


def apply_full_profile(context):
    context.runAllImportStepsFromProfile(PROFILE_ID)
