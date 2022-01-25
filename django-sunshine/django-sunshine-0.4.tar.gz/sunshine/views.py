# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import sys
import logging
from pathlib import Path

from django import get_version as django_version
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import FileResponse
from django.contrib.auth import logout as django_logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

import humanize

from .common import jsonp
from .common import find_module_info
from .context_processors import is_developer
from .__version__ import __version__

MEDIA_ROOT = Path(settings.MEDIA_ROOT)  # also for serving CDN
SUNSHINE_CDN_PERMISSIONS = getattr(settings, "SUNSHINE_CDN_PERMISSIONS", {})
SUNSHINE_TITLE = getattr(settings, "SUNSHINE_DEFAULT_TITLE", "Sunshine Portal Index")
SUNSHINE_PUBLIC_WELCOME = getattr(settings, "SUNSHINE_PUBLIC_WELCOME", "")


SUNSHINE_HOME = getattr(settings, 'SUNSHINE_HOME', '')
LOGIN_URL = getattr(settings, 'LOGIN_URL', '/login')


def index(request):
    ''' Default entry point for the public '''
    if request.user.is_authenticated and SUNSHINE_HOME:
        return redirect(SUNSHINE_HOME)
    else:
        context = {'title': SUNSHINE_TITLE,
                   'SUNSHINE_PUBLIC_WELCOME': SUNSHINE_PUBLIC_WELCOME,
                   'version': __version__}
        return render(request, 'sunshine/public.html', context)


def public(request):
    context = {'title': SUNSHINE_TITLE,
               'SUNSHINE_PUBLIC_WELCOME': SUNSHINE_PUBLIC_WELCOME,
               'version': __version__}
    return render(request, 'sunshine/public.html', context)


@login_required()
def home(request):
    return render(request, 'sunshine/home.html',
                  {'version': __version__})


@login_required()
def profile(request):
    return render(request, 'sunshine/profile.html',
                  {'version': __version__})
    

def logout(request):
    django_logout(request)
    return redirect(LOGIN_URL)


# ------------------------------------------------------------------------------
# Alerts
# ------------------------------------------------------------------------------

@jsonp
@csrf_protect
@login_required()
def api_fetch_notifications(request):
    return {'alerts': [], 'inbox': []}
    # return notifications


# ------------------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------------------

@jsonp
@csrf_protect
@login_required()
def api_sidebar_toggle(request, status=0):
    try:
        request.session['sidebar_toggle'] = (status != 0)
        return {'status': True, 'state': request.session.get('sidebar_toggle', False)}
    except Exception:
        logging.getLogger(__name__).exception("Sidebar API error")
        return {'status': False, 'state': request.session.get('sidebar_toggle', False)}


# ------------------------------------------------------------------------------
# System tools
# ------------------------------------------------------------------------------

@login_required()
@csrf_protect
@user_passes_test(is_developer)
def system_dashboard(request):
    context = {"sunshine_version": __version__,
               'django_version': django_version(),
               'python_version': sys.version}
    # find modules
    modules = []
    for m in find_module_info():
        name = getattr(m, 'verbose_name', '')
        if not name:
            name = getattr(m, 'name')
        version = getattr(m, 'version', 'N/A')
        build = getattr(m, 'version_build', '')
        modules.append({'name': name,
                        'version': version,
                        'build': build})
    context['modules'] = modules
    # show free space
    try:
        statvfs = os.statvfs(MEDIA_ROOT)
        context['space_used'] = humanize.naturalsize(statvfs.f_frsize * statvfs.f_blocks)     # Size of filesystem in bytes
        context['space_free'] = humanize.naturalsize(statvfs.f_frsize * statvfs.f_bfree)      # Actual number of free bytes
        context['space_usable'] = humanize.naturalsize(statvfs.f_frsize * statvfs.f_bavail)
        # Number of free bytes that ordinary users
        # are allowed to use (excl. reserved space)
    finally:
        pass
    return render(request, 'sunshine/system_dashboard.html', context)


# ------------------------------------------------------------------------------
# Basic built-in CDN
# ------------------------------------------------------------------------------

def cdn_home(request):
    return render(request, 'sunshine/cdn_index.html')


@login_required()
def cdn_serve_avatar(request, username):
    context = {'module': 'avatars',
               'res_id': username}
    options = [MEDIA_ROOT / "avatars" / username,
               MEDIA_ROOT / "avatars" / f"{username}.jpg",
               MEDIA_ROOT / "avatars" / f"{username}.png",
               MEDIA_ROOT / "avatars" / "_default_.png"]
    for f in options:
        if f.is_file():
            return FileResponse(f.open(mode='rb'))
    else:
        return render(request, 'sunshine/cdn_403.html', context)


def cdn_serve(request, module, res_id, ext=''):
    ''' serve an uploaded content '''
    context = {
        'module': module,
        'res_id': res_id}
    if not request.user.is_authenticated:
        logging.getLogger(__name__).warning(f"CDN_BLOCKED: unauthorized access to {module} -- {res_id}")
        return render(request, 'sunshine/cdn_403.html', context)
        # return redirect(home)
    else:
        if module in SUNSHINE_CDN_PERMISSIONS:
            if request.user.groups.filter(name__in=SUNSHINE_CDN_PERMISSIONS[module]).exists():
                logging.getLogger(__name__).info(f"CDN_GRANTED: user {request.user} requested {module} -- {res_id}")
                f = MEDIA_ROOT / module / str(res_id)
                if f.exists():
                    return FileResponse(f.open(mode='rb'))
                else:
                    return render(request, 'sunshine/cdn_404.html', context)
            else:
                logging.getLogger(__name__).warning(f"CDN_BLOCKED: user {request.user} requested {module} -- {res_id}")
                return render(request, 'sunshine/cdn_403.html', context)
        else:
            return render(request, 'sunshine/cdn_403.html', context)
    return render(request, 'sunshine/cdn_403.html', context)
