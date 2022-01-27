'''
This file defines a variety of preferences that must be set in the DB,
but can be changed dynamically.
'''

from django.utils.translation import gettext_lazy as _

from dynamic_preferences.types import (
    BooleanPreference, Section
)
from dynamic_preferences.registries import global_preferences_registry

# we create some section objects to link related preferences together
registration = Section('registration', _('Registration'))


@global_preferences_registry.register
class EnableDancerVaxLookup(BooleanPreference):
    section = registration
    name = 'enableDancerVaxLookup'
    verbose_name = _('Enable DancerVax Lookups')
    help_text = _(
        'Uncheck this if you wish to disable lookups using DancerVax.'
    )
    default = True
