# Rewrote a lot of this. Keeping this around as an interface to new code
# and to keep the diff simple

from askbot.conf import settings as askbot_settings
from askbot.skins.askbot_environments import SkinEnvironment
from askbot.skins.askbot_environments import AppDirectoryEnvironment
import askbot.skins.shortcuts

def get_skin():
    return SkinEnvironment.get_skin()

# this is now askbot.skins.jinja2_environment.factory and I don't think this
# is supposed to be called.
def load_skins(language_code):
    pass

def get_askbot_template(template):
    return SkinEnvironment.get_skin().get_template(template)

def render_into_skin_as_string(template, data, request):
    return askbot.skins.shortcuts.render_into_skin_as_string(template, data, request)

def render_text_into_skin(text, data, request):
    return askbot.skins.shortcuts.render_text_into_skin(text, data, request)
