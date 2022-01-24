'''
Created on 9. 7. 2014

@author: Vancikv

This module contains tree nodes defined for specific classes
as oposed to the two generic node types defined in mxn_tree_view
that are sufficient for displaying the tree structure but
don't provide different classes with specific node behaviour.
'''

import os
import pickle

from traits.etsconfig.api import ETSConfig
from traitsui.api import \
    TreeNode
from traitsui.menu import \
    Menu

from bmcs_beam.mxn.cross_section import \
    CrossSection
from bmcs_beam.mxn.ecb_calib import \
    ECBCalib
from bmcs_beam.mxn.material_types import \
    MaterialTypeBase
from bmcs_beam.mxn.mxn_class_extension import \
    MxNClassExt
from bmcs_beam.mxn.mxn_diagram import \
    MxNDiagram
from bmcs_beam.mxn.mxn_tree_node import \
    ReinfLayoutTreeNode
from bmcs_beam.mxn.reinf_layout import \
    RLCTexLayer, RLCTexUniform, RLCBar
from bmcs_beam.mxn.use_cases import \
    UCDatabase, UCPStudyElementMxN, UCParametricStudy, \
    UseCaseContainer
from bmcs_beam.mxn.utils import \
    get_outfile
from .mxn_tree_view_handler import \
    plot_self, new_material, del_material


if ETSConfig.toolkit == 'wx':
    from traitsui.wx.tree_editor import \
        NewAction, DeleteAction, CopyAction, PasteAction
if ETSConfig.toolkit == 'qt4':
    from traitsui.qt4.tree_editor import \
        NewAction, DeleteAction, CopyAction, PasteAction
else:
    raise ImportError("tree actions for %s toolkit not availabe" % \
        ETSConfig.toolkit)


# =========================================================================
# Special TreeNode classes
# =========================================================================


class UCCTreeNode(TreeNode):

    def append_child(self, object_, child):
        """ Overriding this method ensures that upon dropping an
        object merely its copy is appended. Necessary to avoid
        multiple references to the same object in tree structure
        that would occur upon drag-n-dropping a child of
        SingleChildTreeNode onto the use case container.
        """
        copy_file = get_outfile(folder_name='.mxn',
                                file_name='temp.pkl')
        file_ = open(copy_file, 'wb')
        pickle.dump(child, file_, 1)
        file_.close()
        file_ = open(copy_file, 'rb')
        new_child = pickle.load(file_)
        file_.close()
        os.remove(copy_file)

        getattr(object_, self.children).append(new_child)


class SingleChildTreeNode(TreeNode):

    def append_child(self, object_, child):
        """ Overriding this method ensures that there is
        always only one child and that upon dropping an object
        merely its copy is assigned.
        """
        copy_file = get_outfile(folder_name='.mxn',
                                file_name='temp.pkl')
        file_ = open(copy_file, 'wb')
        pickle.dump(child, file_, 1)
        file_.close()
        file_ = open(copy_file, 'rb')
        new_child = pickle.load(file_)
        file.close()
        os.remove(copy_file)

        setattr(object, self.children, [new_child])

    def delete_child(self, object_, index):
        """ Overriding the delete method in order to ensure
        that a dragged object does not remove itself from its
        original location, i.e. the method does nothing because
        there should always be one child.
        """
        pass

# =========================================================================
# Use cases and enveloping nodes
# =========================================================================

use_case_container_node = UCCTreeNode(
    node_for=[UseCaseContainer],
    auto_open=True,
    children='tree_node_list',
    label='node_name',
    view='tree_view',
    menu=Menu(NewAction, PasteAction),
    add=[MxNDiagram, UCParametricStudy,
         ECBCalib],
)

parametric_study_node = TreeNode(
    node_for=[UCParametricStudy],
    auto_open=True,
    children='tree_node_list',
    label='node_name',
    view='tree_view',
    menu=Menu(plot_self,
              DeleteAction,
              ),
    add=[],
)

mxn_diagram_container_node = SingleChildTreeNode(
    node_for=[UCPStudyElementMxN],
    auto_open=True,
    children='tree_node_list',
    label='node_name',
    view='tree_view',
    menu=Menu(plot_self,
              PasteAction,
              DeleteAction),
    add=[MxNDiagram],
)

mxn_diagram_node = SingleChildTreeNode(node_for=[MxNDiagram],
                                       auto_open=True,
                                       children='tree_node_list',
                                       label='node_name',
                                       view='tree_view',
                                       add=[CrossSection],
                                       menu=Menu(plot_self,
                                                 CopyAction,
                                                 PasteAction,
                                                 DeleteAction),
                                       )

ecb_calib_node = SingleChildTreeNode(node_for=[ECBCalib],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     add=[CrossSection],
                                     menu=Menu(plot_self,
                                               CopyAction,
                                               PasteAction,
                                               DeleteAction),
                                     )
# =========================================================================
# Database and subordinate nodes
# =========================================================================

''' Generic nodes are used for constitutive laws
'''

database_node = TreeNode(node_for=[UCDatabase],
                         auto_open=False,
                         children='tree_node_list',
                         label='node_name',
                         view='tree_view',
                         menu=Menu(DeleteAction),
                         )

database_subnode = TreeNode(node_for=[MxNClassExt],
                            auto_open=True,
                            children='tree_node_list',
                            label='node_name',
                            view='tree_view',
                            menu=Menu(new_material),
                            )

material_type_node = TreeNode(node_for=[MaterialTypeBase],
                              auto_open=False,
                              children='tree_node_list',
                              label='node_name',
                              view='tree_view',
                              menu=Menu(del_material),
                              )

# =========================================================================
# Cross section and subordinate nodes
# =========================================================================

''' Generic nodes are used for MatrixCrossSection and for constitutive laws
'''

cross_section_node = TreeNode(node_for=[CrossSection],
                              auto_open=True,
                              children='tree_node_list',
                              label='node_name',
                              view='tree_view',
                              menu=Menu(CopyAction, plot_self),
                              )

reinf_layout_node = TreeNode(node_for=[ReinfLayoutTreeNode],
                             auto_open=True,
                             children='tree_node_list',
                             label='node_name',
                             view='tree_view',
                             menu=Menu(plot_self, NewAction),
                             add=[RLCTexUniform,
                                   RLCTexLayer,
                                   RLCBar]
                             )

reinf_tex_uniform_node = TreeNode(node_for=[RLCTexUniform],
                                  auto_open=False,
                                  children='tree_node_list',
                                  label='node_name',
                                  view='tree_view',
                                  menu=Menu(plot_self, DeleteAction),
                                  )

reinf_tex_layer_node = TreeNode(node_for=[RLCTexLayer],
                                auto_open=False,
                                children='tree_node_list',
                                label='node_name',
                                view='tree_view',
                                menu=Menu(plot_self, DeleteAction),
                                )

reinf_bar_node = TreeNode(node_for=[RLCBar],
                          auto_open=False,
                          children='tree_node_list',
                          label='node_name',
                          view='tree_view',
                          menu=Menu(plot_self, DeleteAction),
                          )

# =========================================================================
# List of all custom nodes
# =========================================================================

custom_node_list = [mxn_diagram_container_node, mxn_diagram_node,
                    cross_section_node, material_type_node,
                    reinf_layout_node, reinf_tex_uniform_node,
                    reinf_tex_layer_node, reinf_bar_node,
                    database_node, database_subnode, ecb_calib_node,
                    use_case_container_node, parametric_study_node]
