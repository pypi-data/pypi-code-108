# ripped from askbot.skins.loaders as we do not want to use that module anymore
from askbot.skins.askbot_environments import SkinEnvironment

from django.template import RequestContext

def render_into_skin_as_string(template, data, request):
    context = RequestContext(request, data)
    template = SkinEnvironment.get_template(template)
    return template.render(context)

def render_text_into_skin(text, data, request):
    context = RequestContext(request, data)
    template = SkinEnvironment.from_string(text)
    return template.render(context)
