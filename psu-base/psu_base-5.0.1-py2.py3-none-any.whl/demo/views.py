from django.shortcuts import render
from django.http import HttpResponse
from psu_base.classes.Log import Log
from psu_base.services import template_service
from psu_base.services import message_service, auth_service, utility_service

log = Log()


def index(request):
    """
    A landing page
    """
    log.trace()

    # Get Official PSU colors to display on example template
    psu_colors = {}
    for color_name, rgb in template_service.HTML_COLORS.items():
        if color_name.startswith('psu'):
            psu_colors[color_name] = template_service.hex_from_rgb(rgb).upper()

    log.end()
    return render(
        request, 'landing.html',
        {'psu_colors': psu_colors.items()}
    )


def sub_app_demo(request):
    """
    A landing page for sub-apps
    """
    log.trace()

    administrators = auth_service.get_authorized_users('admin')
    return render(
        request, 'sub_app_landing.html',
        {'administrators': administrators}
    )


def alert_message(request):
    log.trace()
    alert = "alerts sent"
    msg = request.POST.get('msg')

    message_service.post_info(msg)
    message_service.post_success(msg)
    message_service.post_warning(msg)
    message_service.post_error(msg)

    log.end()
    return HttpResponse(alert)
