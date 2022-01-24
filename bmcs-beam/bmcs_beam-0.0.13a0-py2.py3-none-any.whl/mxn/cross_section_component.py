'''
Created on Sep 4, 2012

@todo: introduce the dock feature for the views
@todo: classify the state changes and provide examples.

@author: rch
'''
from traits.api import \
    HasStrictTraits, Property, \
    Event, on_trait_change, WeakRef, \
    Constant, cached_property, Bool

from bmcs_beam.mxn.cross_section_state import \
    CrossSectionState

from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode

from .utils import \
    KeyRef

COMPONENT_CHANGE = '+geo_input,geo.changed,material_changed,law_changed,material,material_law'


class CrossSectionComponent(MxNTreeNode):

    '''Cross section component supplying the normal force and moment..
    '''

    def __init__(self, *args, **metadata):
        default_material = metadata.get('material', None)
        if default_material:
            self.material = default_material
        else:
            print('Warning: material not specified for object %s' % self)
        '''It is necessary to set default value of material here to ensure
        it has been assigned when its editor is requested by the UI
        '''

        self.add_trait(
            'material_law', KeyRef(db=self.material_.named_mtrl_laws))
        self.on_trait_change(
            self._refresh_material_law, 'material,material_changed')
        '''The scope of material laws is dependent on the chosen material
        '''

        default_material_law = metadata.get(
            'material_law', list(self.material_.named_mtrl_laws.keys())[0])
        self.material_law = default_material_law

        super(CrossSectionComponent, self).__init__(**metadata)

    def _refresh_material_law(self):
        '''material_law is redefined upon change of material
        '''
        named_laws = self.material_.named_mtrl_laws
        val = self.material_law
        self.add_trait('material_law', KeyRef(db=named_laws))
        del self.material_law
        try:
            self.material_law = val
        except:
            self.material_law = list(self.material_.named_mtrl_laws.keys())[0]

    state = WeakRef(CrossSectionState, transient=True)
    '''Strain state of a cross section
    '''

    def __getstate__(self):
        '''Overriding __getstate__ because of WeakRef usage
        '''
        state = super(CrossSectionComponent, self).__getstate__()

        for key in ['state', 'state_']:
            if key in state:
                del state[key]

        return state

    def __setstate__(self, state):
        '''Overriding __setstate__ to ensure dynamic attributes exist.
        '''
        self.__init__(**state)

    unit_conversion_factor = Constant(1000.0)

    material_changed = Event
    '''Notifier set to True when internal values of material change
    '''

    law_changed = Event
    '''Notifier set to True when internal values of constitutive law change
    '''
    eps_changed = Event
    '''State notifier that is set to true if the cross section state has changed
    upon modifications of eps_lo and eps_up
    '''

    @on_trait_change(COMPONENT_CHANGE)
    def notify_change(self):
        '''Propagate the change of the component geometry or stress-strain
        law to the cross section state.
        '''
        if self.state:
            self.state.changed = True

    #=========================================================================
    # Cross-sectional stress resultants
    #=========================================================================

    N = Property()
    '''Resulting normal force.
    '''

    M = Property()
    '''Resulting moment.
    '''

    #=========================================================================
    # Auxiliary methods for tree editor
    #=========================================================================
    tree_node_list = Property(depends_on='material,material_law')

    @cached_property
    def _get_tree_node_list(self):
        return [self.material_law_]

if __name__ == '__main__':
    pass
