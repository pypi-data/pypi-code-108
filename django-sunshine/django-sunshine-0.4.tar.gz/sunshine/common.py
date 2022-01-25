# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

from datetime import datetime
import logging
import json
import uuid
from collections.abc import Sequence, Mapping

from django.conf import settings
from django.utils.timezone import make_aware
from django.http import HttpResponse
from django.contrib.admin.models import LogEntry
from django.contrib.admin.models import ADDITION, DELETION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.urls import include, path


TIME_ZONE_DST = settings.TIME_ZONE_DST


def datetime_now():
    ''' Generate aware datetime object of current time (now) '''
    return make_aware(datetime.now(), is_dst=TIME_ZONE_DST)


def read_settings(key, default_value=''):
    return getattr(settings, key, default_value)


def log_action(request, instance, **kwargs):
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(instance).pk,
        object_id=instance.id,
        object_repr=repr(instance),
        **kwargs)


def log_add(request, instance, **kwargs):
    log_action(request, instance, action_flag=ADDITION, **kwargs)


def log_update(request, instance, **kwargs):
    log_action(request, instance, action_flag=CHANGE, **kwargs)


def log_delete(request, instance, **kwargs):
    log_action(request, instance, action_flag=DELETION, **kwargs)


def jsonp(func):
    ''' JSON/JSONP decorator '''
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        # ignore HttpResponse
        if isinstance(objects, HttpResponse):
            return objects
        # JSON/JSONP response
        data = json.dumps(objects)
        if 'callback' in request.GET:
            callback = request.GET['callback']
        elif 'callback' in request.POST:
            callback = request.POST['callback']
        else:
            return HttpResponse(data, "application/json")
        # is JSONP
        # logging.debug("A jsonp response")
        data = '{c}({d});'.format(c=callback, d=data)
        return HttpResponse(data, "application/javascript")
    return decorator


def random_filename(ext=''):
    ''' Generate a random file name '''
    if ext:
        return str(uuid.uuid4()) + ext
    else:
        return str(uuid.uuid4())


def find_module_info():
    modules = []
    for app in apps.get_app_configs():
        app_path = getattr(app, "sunshine_path", None)
        if app_path:
            app_url = f"{app.module.__name__}.urls"
            logging.getLogger(__name__).info(f"Loading sunshine module [{app}] | URL mapping: {repr(app_path)} ==> {repr(app_url)}")
            modules.append(app)
    return modules


def find_modules():
    potentials = []
    for app in apps.get_app_configs():
        app_path = getattr(app, "sunshine_path", None)
        if app_path:
            app_url = f"{app.module.__name__}.urls"
            app_ns = getattr(app, "namespace", None)
            logging.getLogger(__name__).info(f"Loading sunshine module [{app}] | URL mapping: {repr(app_path)} ==> {repr(app_url)}")
            if app_ns:
                potentials.append(path(app_path, include(app_url, namespace=app_ns)))
            else:
                potentials.append(path(app_path, include(app_url)))
    return potentials


def find_menuitems():
    menu_items = []
    for app in apps.get_app_configs():
        app_menu = getattr(app, "sunshine_menu", None)
        if app_menu:
            for item in app_menu:
                if isinstance(item, Sequence):
                    menu_items.append(Menu(*item))
                elif isinstance(item, Mapping):
                    menu_items.append(Menu(**item))
                else:
                    raise ValueError(f"Unknown menu mapping found ({item})")
    return menu_items


def build_menu(request=None):
    items = find_menuitems()
    menu = {'name': '', 'items': [], 'children': {}}
    uid = 1
    for idx, item in enumerate(items, start=1):
        if request is not None:
            item.request = request
            if not item.has_access:
                continue
        current = menu
        if item.groups:
            for group in item.groups:
                current = current['children'].setdefault(group, {'name': group, 'items': [], 'children': {}, 'div_id': uid})
                uid += 1
        # add this menu item to this group
        current['items'].append(item)
    return menu


class Menu:
    def __init__(self, name, verify=None, title='', icon='', groups=None, type='', div_id=None):
        self.__name = name
        self.__verify = verify
        self.__request = None
        self.__title = title
        self.__icon = icon
        self.__menu_type = '' if not type else str(type).lower()
        self.__groups = tuple(groups) if groups else {}
        self.__div_id = div_id

    @property
    def name(self):
        return self.__name

    @property
    def groups(self):
        return self.__groups

    @property
    def title(self):
        return self.__title if self.__title else self.name

    @property
    def menu_type(self):
        return self.__menu_type

    @property
    def icon(self):
        return self.__icon if self.__icon else 'fa-cog'

    @property
    def verify(self):
        return self.__verify if self.__verify else lambda x: True

    @property
    def has_access(self):
        return self.verify is not None and self.verify(self.request)

    @property
    def request(self):
        return self.__request

    @request.setter
    def request(self, request):
        self.__request = request

    def __repr__(self):
        menu_type = self.menu_type + '::' if self.menu_type else ''
        if self.name != self.title:
            return f"<{menu_type}{self.name}>[{self.title}]"
        else:
            return f"<{menu_type}{self.name}>"

    def __str__(self):
        return repr(self)
