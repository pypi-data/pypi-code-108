from .structures import chrome_manifest as template

class chrome_manifest(object):
    """docstring for chrome_manifest"""

    def __init__(self, secure_name, locales, toolBtnData):
        super(chrome_manifest, self).__init__()
        self.template = template.chrome_manifest
        self.toolbar_style = template.customize_toolbar_style
        self.secure_name = secure_name
        self.locales = self.__build_locales__(locales)

        if not self.locales:
            self.template = self.template.replace("locales_here", "")
        else:
            self.template = self.template.replace("locales_here", self.locales)

        if toolBtnData['type']:
            self.template = self.template.replace("customize_toolbar_style", self.toolbar_style)
        else:
            self.template = self.template.replace("customize_toolbar_style", "")

        self._set_secure_name__()

    def _set_secure_name__(self):
        self.template = self.template.replace("addon_secure_name", self.secure_name)

    def __build_locales__(self, locales):
        out = []
        line = "locale    addon_secure_name {0} chrome/locale/{0}/"

        output = [line.format(locale) for locale in locales]

        return '\n'.join(output) # Each locale in new line

    def build(self):
        return self.template

