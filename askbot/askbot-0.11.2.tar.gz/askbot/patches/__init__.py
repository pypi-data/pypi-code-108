"""module for monkey patching that is
necessary for interoperability of different
versions of various components used in askbot
"""
import django
from askbot.patches import django_patches

def patch_django():
    (major, minor, micro, _, __) = django.VERSION

    if major == 1 and minor > 5:
        django_patches.add_hashcompat()

    if major == 1 and minor == 8:
        django_patches.patch_django_template()
