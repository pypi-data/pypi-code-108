from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls
from .app_settings import MEMBERAUDIT_APP_NAME, MEMBERAUDIT_BASE_URL
from .models import Character


class MemberauditMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            MEMBERAUDIT_APP_NAME,
            "far fa-address-card fa-fw fa-fw",
            "memberaudit:index",
            navactive=["memberaudit:"],
        )

    def render(self, request):
        if request.user.has_perm("memberaudit.basic_access"):
            app_count = Character.objects.unregistered_characters_of_user_count(
                request.user
            )
            self.count = app_count if app_count and app_count > 0 else None
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return MemberauditMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(
        urls, "memberaudit", r"^{base_url}/".format(base_url=MEMBERAUDIT_BASE_URL)
    )
