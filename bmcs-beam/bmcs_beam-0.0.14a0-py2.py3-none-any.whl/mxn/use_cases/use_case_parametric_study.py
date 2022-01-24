'''
Created on 1. 7. 2014

@author: Vancikv
'''

from traits.api import \
    Instance, Property, \
    List, Str, Trait, Button
from traitsui.api import \
    View, Item, UItem, VGroup, HGroup, spring
from bmcs_beam.mxn.cross_section_component import \
    CrossSectionComponent
from bmcs_beam.mxn.material_types import \
    MTReinfBar, MTReinfFabric, MTMatrixMixture
from bmcs_beam.mxn.mxn_diagram import \
    MxNDiagram
from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode
from bmcs_beam.mxn.utils import \
    KeyRef


class UCPStudyElement(MxNTreeNode):
    '''Class controlling plotting options
    for an instance
    '''
    node_name = Str('<unnamed>')

    color = Trait('black', dict(black='k',
                                cyan='c',
                                green='g',
                                blue='b',
                                yellow='y',
                                magneta='m',
                                red='r')
                  )

    linestyle = Trait('solid', dict(solid='-',
                                    dashed='--',
                                    dash_dot='-.',
                                    dotted=':')
                      )

    tree_view = View(VGroup(Item('node_name', label='label'),
                            Item('linestyle'),
                            Item('color'),
                            label='Plotting options'))

    def plot(self, fig):
        ax = fig.add_subplot(1, 1, 1)
        self.content.plot_custom(ax=ax, color=self.color_, linestyle=self.linestyle_,
                                 label=self.node_name)

    def plot_ax(self, ax):
        self.content.plot_custom(ax=ax, color=self.color_, linestyle=self.linestyle_,
                                 label=self.node_name)


class UCPStudyElementMxN(UCPStudyElement):
    node_name = '<unnamed mxn diagram>'

    tree_node_list = List(Instance(MxNTreeNode))

    def _tree_node_list_default(self):
        return [MxNDiagram()]

    content = Property(depends_on='tree_node_list')

    def _get_content(self):
        return self.tree_node_list[0]

    def _set_content(self, val):
        self.tree_node_list = [val]


class UCPStudyElementFabricLaw(UCPStudyElement, CrossSectionComponent):

    def __init__(self, *args, **metadata):
        if not metadata.get('material', None):
            metadata['material'] = 'default_fabric'
        super(UCPStudyElementFabricLaw, self).__init__(**metadata)

    node_name = '<unnamed fabric law>'
    material = KeyRef('default_fabric', db=MTReinfFabric.db)

    tree_node_list = Property(depends_on='material,material_law')

    def _get_tree_node_list(self):
        return [self.material_law_]

    tree_view = View(VGroup(Item('node_name', label='label'),
                            Item('linestyle'),
                            Item('color'),
                            label='Plotting options'),
                     VGroup(Item('material'),
                            Item('material_law'),
                            label='Law options'))


class UCPStudyElementBarLaw(UCPStudyElement, CrossSectionComponent):

    def __init__(self, *args, **metadata):
        if not metadata.get('material', None):
            metadata['material'] = 'bar_d10'
        super(UCPStudyElementBarLaw, self).__init__(**metadata)

    node_name = '<unnamed bar law>'
    material = KeyRef('bar_d10', db=MTReinfBar.db)

    tree_node_list = Property(depends_on='material,material_law')

    def _get_tree_node_list(self):
        return [self.material_law_]

    tree_view = View(VGroup(Item('node_name', label='label'),
                            Item('linestyle'),
                            Item('color'),
                            label='Plotting options'),
                     VGroup(Item('material'),
                            Item('material_law'),
                            label='Law options'))


class UCPStudyElementMatrixLaw(UCPStudyElement, CrossSectionComponent):

    def __init__(self, *args, **metadata):
        if not metadata.get('material', None):
            metadata['material'] = 'default_mixture'
        super(UCPStudyElementMatrixLaw, self).__init__(**metadata)

    node_name = '<unnamed matrix law>'
    material = KeyRef('default_mixture', db=MTMatrixMixture.db)

    tree_node_list = Property(depends_on='material,material_law')

    def _get_tree_node_list(self):
        return [self.material_law_]

    tree_view = View(VGroup(Item('node_name', label='label'),
                            Item('linestyle'),
                            Item('color'),
                            label='Plotting options'),
                     VGroup(Item('material'),
                            Item('material_law'),
                            label='Law options'))


class UCParametricStudy(MxNTreeNode):
    node_name = Str('Parametric study')

    element_to_add = Trait('mxndiagram', {'mxndiagram':   UCPStudyElementMxN,
                                          'fabric_law':   UCPStudyElementFabricLaw,
                                          'bar_law':   UCPStudyElementBarLaw,
                                          'matrix_law':   UCPStudyElementMatrixLaw,
                                          }
                           )

    add_element = Button('Add')

    def _add_element_fired(self):
        self.append_node(self.element_to_add_())

    tree_view = View(HGroup(UItem('element_to_add', springy=True),
                            UItem('add_element')),
                     spring
                     )

    tree_node_list = List(Instance(MxNTreeNode))

    def _tree_node_list_default(self):
        return []

    def plot(self, fig):
        ax = fig.add_subplot(1, 1, 1)
        for node in self.tree_node_list:
            node.plot_ax(ax=ax)
        ax.legend()
