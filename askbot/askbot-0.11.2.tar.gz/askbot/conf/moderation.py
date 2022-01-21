"""Settings to control content moderation"""

from django.utils.translation import ugettext_lazy as _
from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import DATA_AND_FORMATTING
from livesettings.values import ConfigurationGroup
from livesettings.values import BooleanValue
from livesettings.values import LongStringValue
from livesettings.values import StringValue

MODERATION = ConfigurationGroup(
    'MODERATION',
    _('Content moderation'),
    super_group=DATA_AND_FORMATTING
)

CONTENT_MODERATION_MODE_CHOICES = (
    ('flags', _('audit flagged posts')),
    ('audit', _('audit flagged posts and watched users')),
    ('premoderation', _('pre-moderate watched users and audit flagged posts')),
)

settings.register(
    StringValue(
        MODERATION,
        'CONTENT_MODERATION_MODE',
        choices=CONTENT_MODERATION_MODE_CHOICES,
        default='flags',
        description=_('Content moderation method'),
        help_text=_(
            "Audit is made after the posts are published, pre-moderation "
            "prevents publishing before moderator's decision.")
    )
)

settings.register(
    LongStringValue(
        MODERATION,
        'FORBIDDEN_PHRASES',
        default='',
        description=_('Reject all posts with these phrases'),
        help_text=_(
            'Enter one phrase per line (case-insensitive). '
            'Posts with these phrases will be rejected '
            'without moderation.'
        )
    )
)

settings.register(
        LongStringValue(
            MODERATION,
            'INVITED_MODERATORS',
            default='',
            description=_('Invited moderators'),
            help_text=_('Use one line per user; on each line enter '
                        'email address and user name separated by spaces')
            )
        )

settings.register(
    BooleanValue(
        MODERATION,
        'MODERATE_IMAGES',
        default=False,
        description=_('Enable image moderation')
    )
)

settings.register(
    BooleanValue(
        MODERATION,
        'MODERATE_LINKS',
        default=False,
        description=_('Enable link moderation')
    )
)

settings.register(
    BooleanValue(
        MODERATION,
        'ENABLE_TAG_MODERATION',
        default=False,
        description=_('Enable tag moderation'),
        help_text=_(
            'If enabled, any new tags will not be applied '
            'to the questions, but emailed to the moderators. '
            'To use this feature, tags must be optional.'
        )
    )
)
