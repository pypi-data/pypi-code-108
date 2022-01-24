from bokeh.models import LabelSet, CheckboxGroup, LayoutDOM
from bokeh.layouts import column

from shyft.dashboard.base.app import Widget


class LabelSetZoomable:
    def __init__(self, bokeh_args, visibility_range, zoom_state_init):

        super(LabelSetZoomable, self).__init__()

        self.glyph = LabelSet(**bokeh_args)
        self.visibility_range = visibility_range
        self.zoom_range = range(len(visibility_range))
        self.current_font_size = 0
        # initialize data first when visible
        self.has_callback = False
        self.update_callback = None
        self.parent = None
        self.initialized = False

        # init the zoom _state
        self.update_zoom_visibility(zoom_state_init)

    def update_zoom_visibility(self, zoom_state):

        if zoom_state in self.zoom_range:
            self.glyph.text_font_size = self.visibility_range[zoom_state]
            self.current_font_size = float(self.visibility_range[zoom_state].replace('pt', ''))

            if self.current_font_size > 0 and self.has_callback and not self.initialized:
                self.update_callback()
                self.initialized = True

    def set_update_callback(self, callback):
        self.update_callback = callback
        self.has_callback = True


class CheckboxGroupZoomable(Widget):

    def __init__(self, bokeh_args, visibility_range, zoom_state_init, callback, ):

        super(CheckboxGroupZoomable, self).__init__()

        self.checkbox = CheckboxGroup(**bokeh_args)
        self.visibility_range = visibility_range
        self.zoom_range = range(len(visibility_range))
        self.callback = callback
        self.checkbox.on_change("active", callback)

        self.is_active = [int(i) for i in range(len(self.checkbox.labels))]
        self.old_state_active = bokeh_args.get('active', self.is_active)
        self._layout = column(self.checkbox, width=self.checkbox.width, height=self.checkbox.height,
                             sizing_mode=self.checkbox.sizing_mode)
        self.update_zoom_visibility(zoom_state_init)

    @property
    def layout(self) -> LayoutDOM:
        return self._layout

    @property
    def layout_components(self):
        return {'widgets': [self.checkbox], 'figures': []}

    def update_zoom_visibility(self, zoom_state):

        if zoom_state in self.zoom_range:
            if self.visibility_range[zoom_state]:
                if self.checkbox.disabled:
                    self.checkbox.active = self.old_state_active
                    self.checkbox.disabled = False
                #self.checkbox.active = self.is_active

                self.callback('attr', 'old', self.checkbox.active)

            else:
                if not self.checkbox.disabled:
                    self.old_state_active = self.checkbox.active
                self.checkbox.active = []
                self.callback('attr', 'old', self.checkbox.active)
                self.checkbox.disabled = True
