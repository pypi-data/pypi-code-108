from .libs import data_replace
from .structures import overlay_css as template

class overlay_css(object):
    """docstring for overlay_css"""

    def __init__(self, secure_name, toolBtnData):
        super(overlay_css, self).__init__()
        self.template = template.overlay_css
        self.toolbar_button_css = template.toolbar_button_css

        self.secure_name = secure_name
        self.toolBtnData = toolBtnData

        if toolBtnData['type']:
            self.template = self.template.replace("toolbar_button_css", self.toolbar_button_css)
        else:
            self.template = self.template.replace("toolbar_button_css", "")

        self.__set_secure_name__()

    def __set_secure_name__(self):
        self.template = self.template.replace("addon_secure_name", self.secure_name)

    def build(self):
        return self.template

