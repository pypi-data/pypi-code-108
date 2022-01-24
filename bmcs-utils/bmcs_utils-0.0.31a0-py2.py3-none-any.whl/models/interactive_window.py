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

ipw_map = \
    {
        tr.Float: ipw.FloatSlider,
        tr.Int: ipw.IntSlider,
        tr.Bool: ipw.ToggleButton
    }


class Item(tr.HasTraits):
    """Item of interaction with a model
    """
    name = tr.Str
    latex = tr.Str
    minmax = tr.Tuple

    editor = None
    '''Overload the editor defined in the trait type'''

    latex_str = tr.Property

    def _get_latex_str(self):
        if self.latex:
            return r'\(%s\)' % self.latex
        else:
            return self.name

    def __init__(self, name, **traits):
        self.name = name
        tr.HasTraits.__init__(self, **traits)

    def get_editor(self, value, trait, model):
        if self.editor:
            editor = self.editor
        else:
            # create a new edior using the factory provided by the trait type
            if trait.trait_type.editor_factory == None:
                raise TypeError('no editor for %s with type %s' % (self.name,trait.trait_type) )
            editor = trait.trait_type.editor_factory()
        # use the editor supplied in the item defintion and set its attributes
        editor.name = self.name
        editor.label = self.latex_str
        desc = trait.desc
        print('DESC', self.name, trait, trait.desc)
        if desc:
            print('addeing tooltip', desc)
            editor.tooltip = desc
        else:
            editor.tooltip = self.name
        editor.value = value
        editor.trait = trait
        editor.model = model
        return editor


class View(tr.HasTraits):
    """Container of IPWItems
    """
    content = tr.List(Item)
    item_names = tr.List(tr.Str)

    # -------------------------------------------------------------------------
    #  Initializes the object:
    # -------------------------------------------------------------------------

    def __init__(self, *values, **traits):
        """ Initializes the object.
        """
        tr.HasTraits.__init__(self, **traits)
        for item in values:
            self.content.append(item)
            self.item_names.append(item.name)

    simulator = tr.Str
    """Name of the method running the model simulation
    """

class IInteractiveModel(tr.Interface):
    """Interface of interactive bmcs_utils"""


@tr.provides(IInteractiveModel)
class InteractiveModel(tr.HasTraits):
    """Base class for interactive bmcs_utils
    """

    name = tr.Str("<unnamed>")

    def subplots(self, fig):
        return fig.subplots(1, 1)

    def plot(self, axes):
        '''Alias to update plot - to be overloaded by subclasses'''
        self.update_plot(axes)

    def update_plot(self, axes):
        raise NotImplementedError()

    def interact(self):
        return InteractiveWindow(self).interact()


class InteractiveWindow(tr.HasTraits):
    '''Container class synchronizing the interaction elements with plotting area.
    It is equivalent to the traitsui.View class
    '''
    models = tr.List(InteractiveModel)

    ipw_model_tabs = tr.List

    figsize = tr.Tuple(8, 3)

    def __init__(self, models, **kw):
        super(InteractiveWindow, self).__init__(**kw)
        if not (type(models) in [list, tuple]):
            models = [models]
        self.models = models
        self.ipw_model_tabs = [
            ModelTab(model=model, interactor=self, index=i)
            for i, model in enumerate(models)
        ]
        self.output = ipw.Output()
        with self.output:
            f = plt.figure(figsize=self.figsize, constrained_layout=True)
        f.canvas.toolbar_position = 'top'
        f.canvas.header_visible = False
        self.fig = f
        self.axes = self.models[0].subplots(self.fig)

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
        self.update_plot(index)

    def update_plot(self, index):
        '''update the visualization with updated bmcs_utils'''
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


from traits.trait_base import is_none


class ModelTab(tr.HasTraits):
    '''Base class for tabs within an interaction window.'''

    index = tr.Int

    model = tr.Instance(IInteractiveModel)

    interactor = tr.WeakRef

    def set_interactor(self, interactor):
        self.interactor = interactor

    n_steps = tr.Int(20)

    # @todo: an alternative implementation - analogy to traitsui.View
    def get_editors(self):
        ipw_view = self.model.ipw_view
        item_names = ipw_view.item_names
        items = ipw_view.content
        # The traits named in ipw_view are fetched from the model
        # one could directly call `traits` - but then also transient
        # traits like properties would be be accessed. This would disable
        # lazy evaluation of properties.
        # Using the self.traits(transient=is_none) does not work either
        # as then no Buttons could be used - they are also transient.
        # The result is a three step reteirval
        # 1) - use trait_get to obtain the values, transient values are empty
        values = [self.model.trait_get(name) for name in item_names]
        # 2) - convert the list of dictionaries to a single dictionary
        val_dict = {k: v for d in values for k, v in d.items()}
        # 3) - construct a list ordered according to `item_names` with
        #      values of transient traits set to none
        values_ = [val_dict.get(name, None) for name in item_names]
        # 4) - order the corresponding traits according item_names
        traits_ = [self.model.trait(name) for name in item_names]
        # construct a dictionary of editors that can be rendered
        editors = {
            item.name: item.get_editor(value_, trait_, self.model)
            for (item, trait_, value_) in
            zip(items, traits_, values_)
        }
        return editors

    def ipw_editor_changed(self, change):
        name = change.owner.name
        val = change.new
        keyval = {name: val}
        self.model.trait_set(**keyval)
        self.interactor.update_plot(self.index)

    def widget_layout(self):

        vlist = []

        ipw_view = self.model.ipw_view
        if ipw_view.simulator:
            run_sim = getattr(self.model, ipw_view.simulator)
            button = ipw.Button(description=ipw_view.simulator,
                                tooltip='Run the simulation with a progress bar',
                                layout=ipw.Layout(width='20%', height='30px'))
            button.style.button_color = 'darkgray'
            progress_bar = ipw.FloatProgress(min=0, max=1,
                                             layout=ipw.Layout(width='80%', height='30px'))
            def update_progress(value):
                progress_bar.value = value
            def button_clicked(change):
                run_sim(update_progress)
                self.interactor.update_plot(self.index)
            button.on_click(button_clicked)
            progress_box = ipw.HBox([button, progress_bar], layout=ipw.Layout(padding='5px'))
            vlist.append(progress_box)
            ft = ipw.FloatText(value=10,description='another',tooltip="my tooltip")
            vlist.append(ft)

        editors = self.get_editors()
        ipw_editors = {}
        for name, editor in editors.items():
            ipw_editor = editor.render()
            ipw_editor.name = name
            ipw_editor.observe(self.ipw_editor_changed, 'value')
            ipw_editors[name] = ipw_editor

        # Originally, the interactive_ouput widget was used
        # here. But in this way, the update method was called
        # earlier than the tab change observer of the interactor
        # This caused problems if axes object did not correspond
        # to the model's update_plot method. Therefore,
        # slider observer is now used , augmented with the trait name.
        # out = ipw.interactive_output(self.update, sliders);

        layout = ipw.Layout(grid_template_columns='1fr 1fr', padding='6px', width='100%')
        ipw_view = self.model.ipw_view
        item_names = ipw_view.item_names
        item_editors_list = [ipw_editors[name] for name in item_names]
        grid = ipw.GridBox(item_editors_list, layout=layout)

        vlist.append(grid)
        frame = ipw.VBox(vlist)
        return frame

    def subplots(self, fig):
        return self.model.subplots(fig)

    def update_plot(self, axes):
        self.model.update_plot(axes)
