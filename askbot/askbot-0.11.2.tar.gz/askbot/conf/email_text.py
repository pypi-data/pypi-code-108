from django.utils.translation import ugettext_lazy as _

from askbot.conf.settings_wrapper import settings
from askbot.conf.super_groups import LOGIN_USERS_COMMUNICATION
from livesettings import values as livesettings

EMAIL_TEXT = livesettings.ConfigurationGroup(
            'EMAIL_TEXT',
            _('Email template phrases'),
            super_group=LOGIN_USERS_COMMUNICATION
        )

settings.register(
    livesettings.StringValue(
        EMAIL_TEXT,
        'EMAIL_TEXT_SHORT_WELCOME',
        description=_('Short welcome message, for subject line'),
        default=_('Welcome to {{ SITE_NAME }}!'),
        help_text=_('<b>NOTE: All email text settings allow placeholders: '
                    '{{ USER_NAME }}, {{ SITE_NAME }} and {{ SITE_LINK }}.</b>')
    )
)

settings.register(
    livesettings.LongStringValue(
        EMAIL_TEXT,
        'EMAIL_TEXT_LONG_WELCOME',
        description=_('Longer welcome message, for email body'),
        default=_('<p>Please visit {{ SITE_NAME }} at {{ SITE_LINK }}, we '
                  'look forward to your posts.</p>'),
    )
)

settings.register(
    livesettings.LongStringValue(
        EMAIL_TEXT,
        'EMAIL_TEXT_FOOTER',
        description=_('Email footer'),
        default=_('<p>Sincerely,<br>{{ SITE_NAME }} Administrator</p>')
    )
)

settings.register(
    livesettings.LongStringValue(
        EMAIL_TEXT,
        'EMAIL_TEXT_BATCH_ALERT_HEADER',
        description=_('Header for the batch email alerts'),
        default=_("""<p>Dear {{ USER_NAME }},</p>
<p>{{ SITE_NAME }} has these updates, please have a look:</p>""")
    )
)
