
import traits.api as tr
from bmcs_utils.item import Item
import ipywidgets as ipw
import time
from bmcs_utils.editors.editors import EditorFactory

class View(tr.HasTraits):
    """Container of IPWItems
    """
    content = tr.List(Item)
    item_names = tr.List(tr.Str)
    eager_plot_update = tr.Bool(True)
    time_editor = tr.Instance(EditorFactory)
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


    def get_editors(self, model, controller):
        """Return a list of editors linked to a model ordered
        according to the view specification"""
        item_names = self.item_names
        items = self.content
        # The traits named in ipw_view are fetched from the model
        # one could directly call `traits` - but then also transient
        # traits like properties would be accessed. This would disable
        # lazy evaluation of properties.
        # Using the self.traits(transient=is_none) does not work either
        # as then no Buttons could be used - they are also transient.
        # The result is a three step retrieval
        # 1) - use trait_get to obtain the values, transient values are empty
        values = [model.trait_get(name) for name in item_names]
        # 2) - convert the list of dictionaries to a single dictionary
        val_dict = {k: v for d in values for k, v in d.items()}
        # 3) - construct a list ordered according to `item_names` with
        #      values of transient traits set to none
        values_ = [val_dict.get(name, None) for name in item_names]
        # 4) - order the corresponding traits according item_names
        traits_ = [model.trait(name) for name in item_names]
        # construct a dictionary of editors that can be rendered
        editors = {
            item.name: item.get_editor(value_, trait_, model)
            for (item, trait_, value_) in
            zip(items, traits_, values_)
        }
        for editor in editors.values():
            editor.controller = controller
        return editors

    def get_editor_widgets(self, model, controller):
        '''Render the widgets and attach them with change observers
        '''
        editors = self.get_editors(model, controller)
        ipw_editors = {}
        for name, editor in editors.items():
            ipw_editor = editor.render()
            ipw_editor.name = name
            ipw_editor.observe(controller.ipw_editor_changed, 'value')
            ipw_editors[name] = ipw_editor
            editor.model.observe(controller.notify_change, name)

        return ipw_editors

    def get_time_editor_widget(self, model, controller):
        if self.time_editor == None:
            return []
        self.time_editor.trait_set(model=model, controller=controller)
        return [self.time_editor.render()]

