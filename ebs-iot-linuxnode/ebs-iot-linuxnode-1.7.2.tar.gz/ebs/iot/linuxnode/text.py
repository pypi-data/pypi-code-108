

import os
from kivy.core.text import FontContextManager

from hoshi.i18n import TranslationManager

from .basemixin import BaseMixin
from .config import ConfigMixin
from .log import NodeLoggingMixin
from .basemixin import BaseGuiMixin


class AdvancedTextMixin(NodeLoggingMixin, ConfigMixin, BaseMixin):
    _supported_languages = ['en_US']

    def __init__(self, *args, **kwargs):
        super(AdvancedTextMixin, self).__init__(*args, **kwargs)
        self._i18n = TranslationManager(self.i18n_supported_languages,
                                        self._i18n_catalog_dirs)

    @property
    def _i18n_catalog_dirs(self):
        return [os.path.join(x, 'locale') for x in self.config.roots]

    @property
    def i18n_supported_languages(self):
        """
        Return the list of languages supported by the application. The list contains
        locale codes of the form 'en_US'. This is largely intended for use by code
        which requires i18n support. Such code should use this list to create and
        install a suitable set of i18n_contexts.
        """
        return self._supported_languages

    @property
    def i18n(self):
        return self._i18n

    def install(self):
        super(AdvancedTextMixin, self).install()
        self._i18n.install()


class AdvancedTextGuiMixin(AdvancedTextMixin, BaseGuiMixin):
    def __init__(self, *args, **kwargs):
        self._text_font_context = None
        super(AdvancedTextGuiMixin, self).__init__(*args, **kwargs)

    @property
    def text_font_context(self):
        if not self._text_font_context and self.config.text_use_fcm:
            self._text_create_fcm()
        return self._text_font_context

    def _text_create_fcm(self):
        fc = self._appname
        if self.config.text_fcm_system:
            fc = "system://{0}".format(fc)
        self._text_font_context = fc
        self.log.info("Creating FontContextManager {0} using fonts in {1}"
                      .format(fc, self.config.text_fcm_fonts))
        FontContextManager.create(fc)

        for filename in os.listdir(self.config.text_fcm_fonts):
            self.log.debug("Installing Font {0} to FCM {1}".format(filename, self._text_font_context))
            FontContextManager.add_font(fc, os.path.join(self.config.text_fcm_fonts, filename))

    @property
    def text_font_params(self):
        params = {}
        if self.text_font_context:
            params.update({
                'font_context': self._text_font_context
            })
        else:
            params.update({
                'font_name': self.config.text_font_name
            })
        return params
