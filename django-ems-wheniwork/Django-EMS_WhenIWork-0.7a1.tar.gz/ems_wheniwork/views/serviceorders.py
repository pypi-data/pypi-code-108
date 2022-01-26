import logging
import os
from time import localtime, strftime, time, tzset

from authz_group import Group
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

logger = logging.getLogger(__name__)


@login_required
def index(request, template='ems_wheniwork/serviceorders.html'):
    user = request.user.username
    if not Group().is_member_of_group(user, settings.EMSTOOLS_SCHEDULER_GROUP):
        return HttpResponseRedirect("/")

    status_code = 200

    os.environ['TZ'] = 'America/Los_Angeles'
    tzset()

    context = {
        'todays_date': strftime("%Y-%m-%d"),
        'thirty_date': strftime("%Y-%m-%d", localtime(time() + 60*60*24*30)),
        'STATIC_URL': settings.STATIC_URL,
    }

    return render(request, template, context, status=status_code)
