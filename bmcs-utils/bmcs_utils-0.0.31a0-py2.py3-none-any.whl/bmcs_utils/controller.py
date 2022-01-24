import traits.api as tr
from bmcs_utils.i_model import IModel
import ipywidgets as ipw


class Controller(tr.HasTraits):
    """Model controller is constructed automatically when
     a model is accessed from an application window."""

    index = tr.Int

    model = tr.Instance(IModel)

    app_window = tr.WeakRef

    def set_app_window(self, app_window):
        self.app_window = app_window

    n_steps = tr.Int(20)

    freeze_editors = tr.Bool(False)

    def ipw_editor_changed(self, change):
        if self.freeze_editors:
            return

        name = change.owner.name
        val = change.new
        keyval = {name: val}
        self.model.trait_set(**keyval)
        ipw_view = self.model.ipw_view
        if ipw_view.eager_plot_update:
            # If there is a simulator defined within the model
            # do not automatically update the plot. The plot event
            # is then triggered by the simulator itself.
            self.app_window.update_plot(self.model)

    def notify_change(self, event):
        value = event.new
        ipw_editor = self.ipw_editors[event.name]
        self.freeze_editors = True
        ipw_editor.value = value
        self.freeze_editors = False

    menu = tr.Property

    @tr.cached_property
    def _get_menu(self):
        ipw_menu = self.model.ipw_menu
        return ipw_menu.get_menu(model=self.model, ui_pane=self)

    ipw_editors = tr.Property
    @tr.cached_property
    def _get_ipw_editors(self):
        ipw_view = self.model.ipw_view
        ipw_editors = ipw_view.get_editor_widgets(model=self.model,
                                                  controller=self)
        return ipw_editors

    model_editor = tr.Property
    @tr.cached_property
    def _get_model_editor(self):
        ipw_editors = self.ipw_editors
        ipw_view = self.model.ipw_view
        item_names = ipw_view.item_names
        ipw_editors_list = [ipw_editors[name] for name in item_names]
        box_layout = ipw.Layout(display='flex',
                            flex_flow='column',
                            align_items='stretch',
                            width='100%')
        items_layout = ipw.Layout(width='auto')  # override the default width of the button to 'auto' to let the button grow
        for ipw_editor in ipw_editors_list:
            ipw_editor.layout = items_layout

        box = ipw.VBox(ipw_editors_list, layout=box_layout)
        frame = ipw.VBox([box], layout=box_layout)
        return frame

    time_editor = tr.Property
    @tr.cached_property
    def _get_time_editor(self):
        ipw_view = self.model.ipw_view
        return ipw_view.get_time_editor_widget(model=self.model,
                                               controller=self)

    def plot_k3d(self, k3d_plot):
        self.model.plot_k3d(k3d_plot)

    def subplots(self, fig):
        return self.model.subplots(fig)

    def update_plot(self, axes):
        self.model.update_plot(axes)
