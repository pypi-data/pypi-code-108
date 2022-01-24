'''
Matplotlib enhanced with interactive plotting using ipywidgets.

 - The IPWInteract class can generate a simple interface to a model that
   inherits from InteractiveModel. The parameters specified in `param_names`
   are included in the interactive interface.

   Further, the order of param_names can be used to transform the traits
   of the model into a tuple that calls that can be called the lambdified
   functions. This feature is useful for direct integration of function
   derived symbolically using sympy.

   @todo: define param_names as
   - ipw_interact = ['a', 'b'] as a specifier which values are to be included in the interaction
   - ipw_observe = ['d', 'e' ]

   @todo: use ipwidget metadata attribute to overload the ipw_map
'''

import ipywidgets as ipw
import traits.api as tr
import matplotlib.pylab as plt
import k3d

from bmcs_utils.controller import Controller
from bmcs_utils.i_model import IModel


class InteractiveWindow(tr.HasTraits):
    '''Container class synchronizing the interactionjup elements with plotting area.
    It is equivalent to the traitsui.View class
    '''
    models = tr.List(IModel)

    ipw_model_tabs = tr.List

    figsize = tr.Tuple(8, 3)

    def __init__(self, models, **kw):
        super(InteractiveWindow, self).__init__(**kw)
        if not (type(models) in [list, tuple]):
            models = [models]
        self.models = models
        self.ipw_model_tabs = [
            Controller(model=model, interactor=self, index=i)
            for i, model in enumerate(models)
        ]
        self.output = ipw.Output()

        self.plot_backend = self.models[0].plot_backend
        if self.plot_backend == 'mpl':
            with self.output:
                f = plt.figure(figsize=self.figsize, constrained_layout=True)
            f.canvas.toolbar_position = 'top'
            f.canvas.header_visible = False
            self.fig = f
            self.axes = self.models[0].subplots(self.fig)
        elif self.plot_backend == 'k3d':
            self.k3d_plot = k3d.plot()
            self.output.append_display_data(self.k3d_plot)
            self.models[0].subplots(k3d.plot())
        else:
            raise NameError(self.plot_backend + ' is not a valid plot_backend!')

    def __del__(self):
        plt.close(self.fig)

    def interact(self):
        tab = self.widget_layout()
        vb = ipw.VBox([self.output, tab])
        display(vb)

    def widget_layout(self):
        self.tab = ipw.Tab()
        keyval = [(elem.model.name, elem) for elem in self.ipw_model_tabs]
        self.tab.children = tuple(value.widget_layout() for _, value in keyval)
        [self.tab.set_title(i, key) for i, (key, val) in enumerate(keyval)]
        self.tab.observe(self.change_tab, 'selected_index')
        self.change_tab()
        return self.tab

    def change_tab(self, change=None):
        index = self.tab.selected_index
        # clean k3d
        if self.plot_backend == 'mpl':
            self.update_plot(index)
        if self.plot_backend == 'k3d':
            # TODO: why the first loop is not removing all the objects! clean this!
            for obj in self.k3d_plot.objects:
                self.k3d_plot -= obj
            for obj in self.k3d_plot.objects:
                self.k3d_plot -= obj
            self.ipw_model_tabs[index].plot_k3d(self.k3d_plot)

    def update_plot(self, index):
        if self.plot_backend == 'mpl':
            """update the visualization with updated bmcs_utils"""
            self.fig.clf()
            self.axes = self.ipw_model_tabs[index].subplots(self.fig)
            _axes = self.axes
            if not hasattr(_axes, '__iter__'):
                _axes = [_axes]
            for ax in _axes:
                ax.clear()
            self.ipw_model_tabs[index].update_plot(self.axes)
            if len(self.tab.children) > index:
                self.tab.selected_index = index
            self.fig.canvas.draw()
        elif self.plot_backend == 'k3d':
            # TODO: why the first loop is not removing all the objects! clean this!
            self.ipw_model_tabs[index].update_plot(self.k3d_plot)
        else:
            raise NameError(self.plot_backend + ' is not a valid plot_backend!')

