from django.http import HttpResponseServerError
from django.template import RequestContext
from django.template.loader import get_template
import django

def internal_error(request):
    """Error 500 view with context"""
    template = get_template('500.html')
    try:
        result = template.render(RequestContext(request))
    except Exception:
        #if context loading fails, we try to get settings separately
        from askbot.conf import settings as askbot_settings
        data = {'settings': askbot_settings.as_dict()}

        if django.VERSION[:2] == (1, 8):
            result = template.render(request=request, context=data)
        else:
            result = template.render(RequestContext(request, data))

    return HttpResponseServerError(result)
