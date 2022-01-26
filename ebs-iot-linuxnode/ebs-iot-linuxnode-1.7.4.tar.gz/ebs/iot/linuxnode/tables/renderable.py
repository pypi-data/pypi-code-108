

from math import floor, ceil

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout

from ebs.iot.linuxnode.tables.basic import BasicTableEntry, BasicTable
from ebs.iot.linuxnode.widgets.colors import ColorBoxLayout
from ebs.iot.linuxnode.widgets.image import BleedImage
from ebs.iot.linuxnode.widgets.labels import SelfScalingColorLabel


class BasicRenderableTableEntry(BasicTableEntry):
    def __init__(self, data):
        super(BasicRenderableTableEntry, self).__init__(data)

    def build(self, palette=None):
        if not palette:
            palette = self.parent.palette

        _gui_entry = ColorBoxLayout(orientation='horizontal', spacing=10,
                                    bgcolor=palette.grid_background,
                                    size_hint=(1, None),
                                    height=self.parent.spec.row_height)

        _gui_entry.add_widget(BoxLayout(size_hint=(None, None), width=20,
                                        height=self.parent.spec.row_height))

        for colspec in self.parent.spec.column_specs:
            l_font_params = self.parent.spec.font_params
            l_font_params.update({
                'bold': colspec.font_bold
            })
            kwargs = dict(
                text=self.parent.preprocess(getattr(self, colspec.accessor), colspec),
                bgcolor=palette.cell_background,
                color=palette.cell_foreground,
                size_hint=(colspec.width_hint, None),
                height=self.parent.spec.row_height,
                valign='middle', halign=colspec.halign,
                padding_x=15, width=colspec.width,
                markup=colspec.markup,
                **l_font_params
            )
            label = SelfScalingColorLabel(
                **{k: v for k, v in kwargs.items() if v is not None}
            )
            label.bind(size=label.setter('text_size'))
            _gui_entry.add_widget(label)

        _gui_entry.add_widget(BoxLayout(size_hint=(None, None), width=20,
                                        height=self.parent.spec.row_height))
        return _gui_entry


class BasicRenderableTable(BasicTable):
    def __init__(self, node, spec):
        self._gui_table_container = None
        self._gui_table = None
        self._gui_table_title = None
        self._gui_table_header = None
        self._gui_table_entries_container = None
        self._gui_table_entries = None
        self._fallback_image = None
        self._gui_fallback = None
        self._palette = None
        super(BasicRenderableTable, self).__init__(node, spec)

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, value):
        self._palette = value

    def preprocess(self, value, spec=None):
        return str(value)

    @property
    def gui_table_container(self):
        if not self._gui_table_container:
            self._gui_table_container = BoxLayout()
        return self._gui_table_container

    def _build_header(self, palette):
        _gui_table_header = ColorBoxLayout(orientation='horizontal',
                                           spacing=self.spec.row_spacing,
                                           bgcolor=palette.grid_background,
                                           size_hint=(1, None),
                                           height=self.spec.row_height)

        _gui_table_header.add_widget(BoxLayout(size_hint=(None, None), width=20,
                                               height=self.spec.row_height))

        l_font_params = self.spec.font_params
        l_font_params.update({
            'bold': True
        })

        for colspec in self.spec.column_specs:
            kwargs = dict(
                text=self.preprocess(colspec.title),
                bgcolor=palette.header_cell_background,
                color=palette.header_cell_foreground,
                size_hint=(colspec.width_hint, None),
                height=self.spec.row_height,
                valign='middle', halign='center',
                padding_x=15, width=colspec.width,
                **l_font_params
            )
            label = SelfScalingColorLabel(
                **{k: v for k, v in kwargs.items() if v is not None}
            )
            label.bind(size=label.setter('text_size'))
            _gui_table_header.add_widget(label)

        _gui_table_header.add_widget(BoxLayout(size_hint=(None, None), width=20,
                                               height=self.spec.row_height))
        return _gui_table_header

    @property
    def row_pitch(self):
        return self.spec.row_height + self.spec.row_spacing

    @property
    def entries_per_page(self):
        if self._gui_table in self._gui_table_container.children:
            return floor(self._gui_table_entries.height / self.row_pitch) - 1
        else:
            # TODO This is a race condition during GUI construction
            return 6

    @property
    def active_entries(self):
        raise NotImplementedError

    @property
    def total_pages(self):
        return ceil(len(self.active_entries) / self.entries_per_page)

    def page_entities(self, page):
        e_tot = len(self.active_entries)
        p_tot = ceil(e_tot / self.entries_per_page)
        if page == p_tot - 1:
            s = max(0, e_tot - self.entries_per_page)
            e = e_tot
        else:
            s = page * self.entries_per_page
            e = s + self.entries_per_page
        return self.active_entries[s:e]

    def _build_title(self):
        raise NotImplementedError

    @property
    def fallback_image(self):
        return self._fallback_image

    @fallback_image.setter
    def fallback_image(self, value):
        self._fallback_image = value

    def _entries_change_handler(self, _, value):
        if not self._gui_fallback:
            return
        if not len(value):
            if self._gui_table in self._gui_table_container.children:
                self._gui_table_container.remove_widget(self._gui_table)
            if self._gui_fallback not in self._gui_table_container.children:
                self._gui_table_container.add_widget(self._gui_fallback)
        else:
            if self._gui_fallback in self.gui_table_container.children:
                self._gui_table_container.remove_widget(self._gui_fallback)
            if self._gui_table not in self.gui_table_container.children:
                self._gui_table_container.add_widget(self._gui_table)

    def build(self, entries):
        if self.fallback_image:
            self._gui_fallback = BleedImage(
                source=self.fallback_image,
                allow_stretch=True,
                keep_ratio=True,
                bgcolor='auto'
            )
        self._gui_table = ColorBoxLayout(orientation='vertical',
                                         bgcolor=self.palette.grid_background)

        self._gui_table_entries = GridLayout(cols=1, size_hint=(1, None),
                                             spacing=self.spec.row_spacing)
        self._gui_table_entries.bind(children=self._entries_change_handler)

        # # This is required to overlay an animation layer.
        self._gui_table_entries_container = RelativeLayout()
        # self._gui_table_entries_container.bind(size=self._gui_table_entries.setter("size"))
        # self._gui_table_entries_container.bind(pos=self._gui_table_entries.setter("pos"))
        self._gui_table_entries_container.add_widget(self._gui_table_entries)

        _reserved_height = 0

        try:
            self._gui_table_title = self._build_title()
            self._gui_table.add_widget(self._gui_table_title)
            _reserved_height += self._gui_table_title.height
        except NotImplementedError:
            pass

        if self.spec.show_column_header:
            self._gui_table_header = self._build_header(self.palette)
            self._gui_table.add_widget(self._gui_table_header)
            _reserved_height += self._gui_table_header.height

        self._gui_table.add_widget(BoxLayout(size_hint=(1, None),
                                             height=self.spec.row_spacing))
        _reserved_height += self.spec.row_spacing

        def _table_entries_height(_, value):
            self._gui_table_entries.height = value - _reserved_height
        self._gui_table.bind(height=_table_entries_height)

        self.gui_table_container.clear_widgets()
        self.gui_table_container.add_widget(self._gui_table)
        self._gui_table.add_widget(self._gui_table_entries_container)

        self.redraw_entries(entries)
        if hasattr(self, '_alternate_fallback_handler'):
            handler = getattr(self, '_alternate_fallback_handler')
        else:
            handler = self._entries_change_handler
        handler(self._gui_table_entries, self._gui_table_entries.children)
        return self.gui_table_container

    def redraw_entries(self, entries):
        self.log.debug("Redrawing Table, Got {0} Entries".format(len(entries)))
        if hasattr(self, '_alternate_fallback_handler'):
            self._alternate_fallback_handler(None, entries)
        self._gui_table_entries.clear_widgets()
        for entry in entries:
            self._gui_table_entries.add_widget(entry.build(self.palette))
