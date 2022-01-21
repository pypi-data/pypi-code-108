"""
Q&A forum flatpages (about, etc.)
"""
from django.utils.translation import ugettext_lazy as _
from django.utils.text import format_lazy
from askbot.conf.settings_wrapper import settings
from livesettings.values import ConfigurationGroup, LongStringValue
from askbot.conf.super_groups import CONTENT_AND_UI

FLATPAGES = ConfigurationGroup(
    'FLATPAGES',
    _('Messages and pages - about, privacy policy, etc.'),
    super_group=CONTENT_AND_UI
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'FORUM_ABOUT',
        description=_('Text of the Q&amp;A forum About page (html format)'),
        default='',
        localized=True,
        help_text=_('Save, then <a href="http://validator.w3.org/">'
                    'use HTML validator</a> on the "about" page to check '
                    'your input.')
    )
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'AUTHENTICATION_PAGE_MESSAGE',
        description=_('Message to display on the authentication pages'),
        default='',
        localized=True,
        help_text=_('Markdown format is accepted')
    )
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'FORUM_HELP',
        description=_('Text of the Help page (html format)'),
        default='',
        localized=True,
        help_text=_('Save, then <a href="http://validator.w3.org/">'
                    'use HTML validator</a> on the "help" page to '
                    'check your input.')
    )
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'FORUM_FAQ',
        description=_('Text of the Q&amp;A forum FAQ page (html format)'),
        default='',
        localized=True,
        help_text=_('Save, then <a href="http://validator.w3.org/">'
                    'use HTML validator</a> on the "faq" page to check '
                    'your input.')
    )
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'QUESTION_INSTRUCTIONS',
        description=_('Instructions on how to ask questions'),
        localized=True,
        help_text=_('HTML is allowed. Save, then '
                    '<a href="http://validator.w3.org/">use HTML validator</a>'
                    ' on the "ask" page to check your input.')

    )
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'FORUM_PRIVACY',
        description=_('Text of the Q&amp;A forum Privacy Policy (html format)'),
        localized=True,
        help_text=_('Save, then <a href="http://validator.w3.org/">'
                    'use HTML validator</a> on the "privacy" page to check '
                    'your input.')
    )
)

settings.register(
    LongStringValue(
        FLATPAGES,
        'TERMS',
        description=_('Terms and conditions'),
        localized=True,
        help_text=format_lazy('{} {}',
            _('Save, then <a href="http://validator.w3.org/">'
              'use HTML validator</a> on the "terms" page to check '
              'your input.'),
            settings.get_related_settings_info(
                ('LOGIN_PROVIDERS', 'TERMS_ACCEPTANCE_REQUIRED', False))
        )
    )
)

# TODO: merge this with mandatory tags
settings.register(  # this field is not editable manually
    LongStringValue(
        FLATPAGES,
        'CATEGORY_TREE',
        description='Category tree',  # No need to translate
        localized=True,
        default='[["dummy",[]]]',  # Empty array of arrays in json
        help_text=_('Do not edit this field manually!!!')
        # hidden = True
    )
)
