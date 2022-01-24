
import traits.api as tr

class Item(tr.HasTraits):
    """Item of interaction with a model
    """
    name = tr.Str
    latex = tr.Str
    readonly = tr.Bool

    editor = None
    '''Overload the editor defined in the trait type'''

    def __init__(self, name, **traits):
        self.name = name
        tr.HasTraits.__init__(self, **traits)

    def get_editor(self, value, trait, model):
        if self.editor:
            editor = self.editor
        else:
            # create a new edior using the factory provided by the trait type
            if trait.trait_type.editor_factory is None:
                raise TypeError('no editor for %s with type %s' % (self.name,trait.trait_type) )
            editor = trait.trait_type.editor_factory()
        # use the editor supplied in the item defintion and set its attributes
        editor.name = self.name

        if not editor.label:
            if self.latex:
                editor.label = r'\(%s\)' % self.latex
            else:
                editor.label = self.name

        desc = trait.desc
        if desc:
            editor.tooltip = desc
        else:
            editor.tooltip = self.name
        editor.value = value
        editor.trait = trait
        editor.model = model
        editor.disabled = self.readonly
        return editor
