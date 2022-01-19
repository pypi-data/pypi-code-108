# message_views.py
#
#   These are views that are used for sending messages to the user
#

from django.shortcuts import render
from psu_base.classes.Log import Log
import time

log = Log()


def messages(request):

    return render(
        request, "_components/messages.html", {"message_birth_date": int(time.time())}
    )


def xss_prevention(request):
    return render(request, "errors/xss.html", {"path": request.path})


def xss_lock(request):
    return render(request, "errors/xss_lock.html", {})
