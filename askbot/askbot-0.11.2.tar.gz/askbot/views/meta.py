"""
:synopsis: remaining "secondary" views for askbot

This module contains a collection of views displaying all sorts of secondary and mostly static content.
"""
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings as django_settings
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render
from django.template import RequestContext
from django.template import Template
from django.template.loader import get_template
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views import static
from django.views.decorators import csrf
from django.db.models import Max, Count
from askbot import skins
from askbot.conf import settings as askbot_settings
from askbot.forms import FeedbackForm
from askbot.forms import PageField
from askbot.utils.url_utils import get_login_url
from askbot.utils.forms import get_next_url, get_next_jwt
from askbot.utils.functions import encode_jwt
from askbot.mail.messages import FeedbackEmail
from askbot.models import get_users_by_role, BadgeData, Award, User, Tag
from askbot.models import badges as badge_data
from askbot.skins.shortcuts import render_text_into_skin
from askbot.utils.decorators import moderators_only
from askbot.utils.forms import get_next_url
from askbot.utils import functions
from askbot.utils.markup import markdown_input_converter
import re

def generic_view(request, template=None, page_class=None, context=None):
    """this may be not necessary, since it is just a rewrite of render"""
    if request is None:  # a plug for strange import errors in django startup
        return render_to_response('django_error.html')
    context = context or {}
    context['page_class'] = page_class
    return render(request, template, context)

def markdown_flatpage(request, page_class=None, setting_name=None):
    value = getattr(askbot_settings, setting_name)
    content = markdown_input_converter(value)
    context = {
        'content': content,
        'title': askbot_settings.get_description(setting_name)
    }
    return generic_view(
        request, template='askbot_flatpage.html',
        page_class=page_class, context=context
    )


PUBLIC_VARIABLES = ('CUSTOM_CSS', 'CUSTOM_JS')

def config_variable(request, variable_name = None, content_type=None):
    """Print value from the configuration settings
    as response content. All parameters are required.
    """
    if variable_name in PUBLIC_VARIABLES:
        #todo add http header-based caching here!!!
        output = getattr(askbot_settings, variable_name, '')
        return HttpResponse(output, content_type=content_type)
    else:
        return HttpResponseForbidden()

def about(request, template='static_page.html'):
    title = _('About %(site)s') % {'site': askbot_settings.APP_SHORT_NAME}
    data = {
        'title': title,
        'page_class': 'meta',
        'content': askbot_settings.FORUM_ABOUT
    }
    return render(request, template, data)

def page_not_found(request, template='404.html'):
    return generic_view(request, template)

def server_error(request, template='500.html'):
    return generic_view(request, template)

def help(request):
    if askbot_settings.FORUM_HELP.strip() != '':
        data = {
            'title': _('Help'),
            'content': askbot_settings.FORUM_HELP,
            'page_class': 'meta',
            'active_tab': 'help',
        }
        return render(request, 'static_page.html', data)
    else:
        data = {
            'active_tab': 'help',
            'app_name': askbot_settings.APP_SHORT_NAME,
            'page_class': 'meta'
        }
        return render(request, 'help_static.html', data)

def faq(request):
    if askbot_settings.FORUM_FAQ.strip() != '':
        data = {
            'title': _('FAQ'),
            'content': askbot_settings.FORUM_FAQ,
            'page_class': 'meta',
            'active_tab': 'faq',
        }
        return render(request, 'static_page.html', data)
    else:
        data = {
            'gravatar_faq_url': reverse('faq') + '#gravatar',
            'ask_question_url': reverse('ask'),
            'page_class': 'meta',
            'active_tab': 'faq',
        }
        return render(request, 'faq_static.html', data)

@csrf.csrf_protect
def feedback(request):
    if askbot_settings.FEEDBACK_MODE == 'auth-only':
        if request.user.is_anonymous:
            message = _('Please sign in or register to send your feedback')
            request.user.message_set.create(message=message)
            next_jwt = encode_jwt({'next_url': request.path})
            return HttpResponseRedirect(get_login_url() + '?next=' + next_jwt)
    elif askbot_settings.FEEDBACK_MODE == 'disabled':
        raise Http404

    data = {'page_class': 'meta'}
    form = None

    if request.method == "POST":
        form = FeedbackForm(user=request.user, data=request.POST)
        if form.is_valid():

            data = {
                'message': form.cleaned_data['message'],
                'name': form.cleaned_data.get('name'),
                'ip_addr': request.META.get('REMOTE_ADDR', _('unknown')),
                'user': request.user
            }

            if request.user.is_authenticated:
                data['email'] = request.user.email
            else:
                data['email'] = form.cleaned_data.get('email', None)

            email = FeedbackEmail(data)
            email.send(get_users_by_role('recv_feedback'))

            message = _('Thanks for the feedback!')
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(get_next_url(request))
    else:
        form = FeedbackForm(user=request.user,
                            initial={'next': get_next_jwt(request)})

    data['form'] = form
    return render(request, 'feedback.html', data)
feedback.CANCEL_MESSAGE=ugettext_lazy('We look forward to hearing your feedback! Please, give it next time :)')

def privacy(request):
    data = {
        'title': _('Privacy policy'),
        'page_class': 'meta',
        'content': askbot_settings.FORUM_PRIVACY
    }
    return render(request, 'static_page.html', data)

def badges(request):#user status/reputation system
    #todo: supplement database data with the stuff from badges.py
    if askbot_settings.BADGES_MODE != 'public':
        raise Http404
    known_badges = list(badge_data.BADGES.keys())
    badges = BadgeData.objects.filter(slug__in=known_badges) #pylint: disable=no-member

    badges = [v for v in badges if v.is_enabled()]

    my_badge_ids = list()
    if request.user.is_authenticated:
        my_badge_ids = Award.objects.filter( #pylint: disable=no-member
                                user=request.user
                            ).values_list(
                                'badge_id', flat=True
                            ).distinct()

    data = {
        'active_tab': 'badges',
        'badges' : badges,
        'page_class': 'meta',
        'my_badge_ids' : my_badge_ids
    }
    return render(request, 'badges.html', data)

def badge(request, id):
    #todo: supplement database data with the stuff from badges.py
    badge = get_object_or_404(BadgeData, id=id)

    all_badge_recipients = User.objects.filter(
        award_user__badge = badge
    ).annotate(
        last_awarded_at = Max('award_user__awarded_at'),
        award_count = Count('award_user')
    ).order_by(
        '-last_awarded_at'
    )

    objects_list = Paginator(all_badge_recipients, askbot_settings.USERS_PAGE_SIZE)
    page = PageField().clean(request.GET.get('page'))

    try:
        badge_recipients = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        badge_recipients = objects_list.page(objects_list.num_pages)

    paginator_data = {
        'is_paginated' : (objects_list.num_pages > 1),
        'pages': objects_list.num_pages,
        'current_page_number': page,
        'page_object': badge_recipients,
        'base_url' : reverse('badge', kwargs={'id': badge.id}) + '?'
    }
    paginator_context = functions.setup_paginator(paginator_data)

    data = {
        'active_tab': 'badges',
        'badge_recipients': badge_recipients,
        'badge' : badge,
        'page_class': 'meta',
        'paginator_context': paginator_context
    }
    return render(request, 'badge.html', data)

@moderators_only
def list_suggested_tags(request):
    """moderators and administrators can list tags that are
    in the moderation queue, apply suggested tag to questions
    or cancel the moderation reuest."""
    if askbot_settings.ENABLE_TAG_MODERATION == False:
        raise Http404
    tags = Tag.objects.filter(
                    status = Tag.STATUS_SUGGESTED,
                    language_code=translation.get_language()
                )
    tags = tags.order_by('-used_count', 'name')
    #paginate moderated tags
    paginator = Paginator(tags, 20)

    page_no = PageField().clean(request.GET.get('page'))

    try:
        page = paginator.page(page_no)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    paginator_context = functions.setup_paginator({
        'is_paginated' : True,
        'pages': paginator.num_pages,
        'current_page_number': page_no,
        'page_object': page,
        'base_url' : request.path
    })

    data = {
        'tags': page.object_list,
        'active_tab': 'tags',
        'tab_id': 'suggested',
        'page_class': 'moderate-tags-page',
        'page_title': _('Suggested tags'),
        'paginator_context' : paginator_context,
    }
    return render(request, 'list_suggested_tags.html', data)
