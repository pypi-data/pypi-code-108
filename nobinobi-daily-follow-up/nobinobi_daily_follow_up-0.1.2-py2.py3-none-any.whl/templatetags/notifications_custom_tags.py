#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


from django.template import Library
from django.utils import timezone
from django.utils.html import format_html
from nobinobi_core.templatetags.notifications_tags_custom import user_context

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse  # pylint: disable=no-name-in-module,import-error

register = Library()


@register.simple_tag
def live_notify_list_bootstrap(list_class='live_notify_list'):
    html = "<div class='{list_class}'></div>".format(list_class=list_class)
    return format_html(html)


@register.simple_tag(takes_context=True)
def dfu_live_notify_badge(context, badge_class='live_notify_badge'):
    user = user_context(context)
    if not user:
        return ''

    html = "<span class='{badge_class}'>{unread}</span>".format(
        badge_class=badge_class,
        unread=user.notifications.filter(public=True, timestamp__lte=timezone.localtime()).count()
    )
    return format_html(html)


@register.simple_tag(takes_context=True)
def dfu_live_unread(context, badge_class='dfu_live_unread'):
    user = user_context(context)
    if not user:
        return ''

    return user.notifications.filter(public=True, timestamp__lte=timezone.localtime()).count()


# Requires vanilla-js framework - http://vanilla-js.com/
@register.simple_tag
def dfu_register_notify_callbacks(badge_class='live_notify_badge',
                                  # pylint: disable=too-many-arguments,missing-docstring
                                  menu_class='live_notify_list',
                                  refresh_period=15,
                                  callbacks='',
                                  api_name='list',
                                  fetch=5):
    refresh_period = int(refresh_period) * 1000

    if api_name == 'list':
        api_url = reverse('nobinobi_daily_follow_up:dfu_live_all_notification_list')
    elif api_name == 'count':
        api_url = reverse('nobinobi_daily_follow_up:dfu_live_all_notification_count')
    else:
        return ""
    definitions = """
        notify_badge_class='{badge_class}';
        notify_menu_class='{menu_class}';
        notify_api_url='{api_url}';
        notify_fetch_count='{fetch_count}';
        notify_unread_url='{unread_url}';
        notify_mark_all_unread_url='{mark_all_unread_url}';
        notify_refresh_period={refresh};
    """.format(
        badge_class=badge_class,
        menu_class=menu_class,
        refresh=refresh_period,
        api_url=api_url,
        unread_url=reverse('notifications:unread'),
        mark_all_unread_url=reverse('notifications:mark_all_as_read'),
        fetch_count=fetch
    )

    script = "<script>" + definitions
    for callback in callbacks.split(','):
        script += "register_notifier(" + callback + ");"
    script += "</script>"
    return format_html(script)
