# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

from django.urls import reverse
from django.http import HttpResponseRedirect
from yangsuite.apps import FAILED_APPS


def send_to_plugins_once_if_plugin_errors(get_response):
    # One-time configuration and initialization would go here

    def middleware(request):
        # Execute this code before the view or any later middleware are called
        if request.user.is_authenticated and FAILED_APPS:
            if not request.session.get('already_reported_plugin_errors',
                                       False):
                request.session['already_reported_plugin_errors'] = True
                return HttpResponseRedirect(reverse('plugins'))

        # Pass it on
        response = get_response(request)

        # Anything to do after the view has been called
        if not FAILED_APPS:
            if 'already_reported_plugin_errors' in request.session:
                del request.session['already_reported_plugin_errors']

        # Done
        return response

    return middleware
