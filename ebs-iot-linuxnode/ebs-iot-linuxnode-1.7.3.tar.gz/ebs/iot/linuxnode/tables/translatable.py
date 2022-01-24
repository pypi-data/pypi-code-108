import kivy.uix.boxlayout

from ebs.iot.linuxnode.tables.renderable import BasicRenderableTable
from ebs.iot.linuxnode.tables.spec import BasicTableSpec


class TranslatableTableSpec(BasicTableSpec):
    def __init__(self, *args, **kwargs):
        self._languages = kwargs.pop('languages', [])
        self._next_language = -1
        self._metadata = kwargs.pop('i18n_metadata', {})
        super(TranslatableTableSpec, self).__init__(*args, **kwargs)

    def install_metadata(self, metadata):
        self._metadata.update(metadata)

    def install(self):
        super(TranslatableTableSpec, self).install()
        self._i18n_install_languages()

    def _i18n_install_languages(self):
        for language in self._languages:
            self.parent.log.debug("Installing Language {0} for Table {1}".format(language, self.name))
            self.i18n_install_language(language)

    @property
    def i18n_metadata(self):
        if not self._metadata:
            self._metadata = {
                'project': None,
                'version': None,
                'msgid_bugs_address': None,
                'language_team': None,
                'last_translator': None,
                'copyright_holder': None,
            }
        return self._metadata

    def i18n_install_language(self, language):
        if language not in self._languages:
            self._languages.append(language)
        self.parent.node.i18n.install_context(self.name, language, metadata=self.i18n_metadata)

    @property
    def languages(self):
        return self._languages

    @property
    def next_language(self):
        self._next_language += 1
        if self._next_language == len(self._languages):
            self._next_language = 0
        return self._languages[self._next_language]

    def i18n_translator(self, language):
        return self.parent.node.i18n.translator(self.name, language)


class TranslatableRenderableTable(BasicRenderableTable):
    def __init__(self, *args, **kwargs):
        self._i18n_current = None
        self._i18n_language = None
        self._i18n_handlers = []
        super(TranslatableRenderableTable, self).__init__(*args, **kwargs)

    def install_language_change_handler(self, handler):
        self._i18n_handlers.append(handler)

    def install(self):
        super(TranslatableRenderableTable, self).install()
        self.language = self.spec.next_language
        self.install_language_change_handler(self._redraw_title)
        self.install_language_change_handler(self._redraw_header)

    @property
    def spec(self) -> TranslatableTableSpec:
        return self._spec

    @property
    def language(self):
        return self._i18n_language
    
    @language.setter
    def language(self, value):
        if value not in self.spec.languages:
            raise ValueError("Language '{0}' not installed!".format(value))
        self._i18n_language = value
        self._i18n_current = self.spec.i18n_translator(value)
        for handler in self._i18n_handlers:
            handler(self, value)

    def next_language(self):
        self.language = self.spec.next_language

    @property
    def i18n(self):
        return self._i18n_current

    def preprocess(self, value, spec=None):
        if spec and hasattr(spec, 'i18n') and not spec.i18n:
            return value
        else:
            return self.i18n(value)

    def _redraw_title(self, *_):
        pass

    def _redraw_header(self, *_):
        new_header = self._build_header(palette=self.palette)
        self._gui_table.remove_widget(self._gui_table.children[2])
        self._gui_table.add_widget(new_header, 2)
