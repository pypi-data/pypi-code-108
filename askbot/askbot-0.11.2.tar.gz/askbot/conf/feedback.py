"""Feedback form settings
"""
import re
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_email, ValidationError
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import LOGIN_USERS_COMMUNICATION
from livesettings import values as livesettings

FEEDBACK = livesettings.ConfigurationGroup(
    'FEEDBACK',
    _('Feedback settings'),
    super_group=LOGIN_USERS_COMMUNICATION
)

FEEDBACK_MODE_CHOICES = (
    ('open', _('Anyone')),
    ('auth-only', _('Only authenticated users')),
    ('disabled', _('Nobody, disable feedback form'))
)

settings.register(
    livesettings.StringValue(
        FEEDBACK,
        'FEEDBACK_MODE',
        default='open',
        choices=FEEDBACK_MODE_CHOICES,
        description=_('Who can send feedback')
    )
)


settings.register(
    livesettings.StringValue(
        FEEDBACK,
        'FEEDBACK_SITE_URL',
        description=_('Feedback site URL'),
        help_text=_(
            'If left empty, a simple internal feedback form '
            'will be used instead'
        )
    )
)

settings.register(
    livesettings.LongStringValue(
        FEEDBACK,
        'FEEDBACK_PAGE_MESSAGE',
        localized=True,
        description=_('Message on the feedback page'),
        default=_(
            '**Dear {{ USER_NAME }}**, we look forward to hearing your '
            'feedback. Please type and send us your message below.'
        ),
        help_text=_(
            'Save, then <a href="http://validator.w3.org/">use HTML validator</a> '
            'on the "terms" page to check your input.'
        )
    )
)
