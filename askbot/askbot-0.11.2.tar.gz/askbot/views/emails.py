from askbot.conf import settings as askbot_settings
from askbot.mail import messages
from askbot.mail.messages import BaseEmail
from askbot.utils.decorators import moderators_only
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
import logging

LOG = logging.getLogger(__name__)

REGISTRY = dict()
def autodiscover():
    if REGISTRY:
        return
    for name in dir(messages):
        item = messages.__dict__[name]
        if item == BaseEmail:
            continue
        if isinstance(item, type) and issubclass(item, BaseEmail):
            REGISTRY[name] = item

autodiscover()

@moderators_only
def list_emails(request):
    #list only enabled emails
    enabled = dict((k, v) for k, v in list(REGISTRY.items()) if v().is_enabled())
    data = {'emails': enabled}#REGISTRY}
    return render(request, 'email/list_emails.html', data)


DEFAULT_PREVIEW_ERROR_MESSAGE = _(
    'Preview failed possibly because of insufficient data '
    'or an error during the rendering'
)

@moderators_only
def preview_email(request, slug):
    if slug not in REGISTRY:
        raise Http404

    data = {
        'subject': None,
        'body': None,
        'error_message': None
    }

    email = REGISTRY[slug]()
    #if email.is_enabled() == False:
    #    raise Http404

    data['samples'] = list()
    for context in email.get_mock_contexts():
        sample = dict()
        try:
            sample['subject'] = email.render_subject(context)
            sample['body'] = email.render_body(context)
        except Exception as e:
            tech_error = str(e)
            LOG.critical(tech_error)
            error_message = getattr(
                        email,
                        'preview_error_message',
                        DEFAULT_PREVIEW_ERROR_MESSAGE
                    )
            error_message += '</br> %s' % tech_error
            sample['error_message'] = error_message
        data['samples'].append(sample)

    data['email'] = email
    return render(request, 'email/preview_email.html', data)
