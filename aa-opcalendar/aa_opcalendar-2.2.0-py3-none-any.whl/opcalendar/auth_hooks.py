from django.utils.translation import ugettext_lazy as _

from allianceauth.services.hooks import MenuItemHook, UrlHook
from allianceauth import hooks

from . import urls


class OpcalendarMenuItem(MenuItemHook):
    """ This class ensures only authorized users will see the menu entry """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Operation Calendar"),
            "far fa-calendar-alt",
            "opcalendar:calendar",
            navactive=["opcalendar:calendar"],
        )

    def render(self, request):
        if request.user.has_perm("opcalendar.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return OpcalendarMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "opcalendar", r"^opcalendar/")


@hooks.register("discord_cogs_hook")
def register_cogs():
    return ["opcalendar.cogs.ops"]
