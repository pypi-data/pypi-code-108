from .libs import data_replace
from .structures import overlay_xul as template

class overlay_xul(object):
    """docstring for overlay_xul"""

    def __init__(self, addon_name, secure_name, toolBtnData):
        super(overlay_xul, self).__init__()
        self.template = template.overlay_xul
        self.toolbar_button = template.toolbar_button
        self.menu_popup = template.menu_popup

        self.addon_name = addon_name
        self.secure_name = secure_name
        self.toolBtnData = toolBtnData

        if toolBtnData['type']:
            tags = {
                "addon_name":self.addon_name,
                "button_type": toolBtnData['type'],
                "button_tooltip": toolBtnData['tooltip'],
            }

            self.toolbar_button = data_replace(tags, self.toolbar_button)

            if toolBtnData['type'] in ["menu", "menu-button"]:
                menu_items = __build_menu_items__(toolBtnData['options'])
                self.toolbar_button = self.toolbar_button.replace("{popup_menu}", menu_items)
            else:
                self.toolbar_button = self.toolbar_button.replace("{popup_menu}", "")
                self.template = self.template.replace("{toolbar_button}", self.toolbar_button)
        else:
            self.template = self.template.replace("{toolbar_button}", "")

        self.__set_secure_name__()

    def __set_secure_name__(self):
        self.template = self.template.replace("addon_secure_name", self.secure_name)

    def __build_menu_items__(self, options):
        out = []
        line = "<menuitem label='{0}' />"

        output = [line.format(option) for option in options]

        return '\n           '.join(output) # Each option (menuitem) in new line

    def build(self):
        return self.template

