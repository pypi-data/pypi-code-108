"""

"""
import bmcs_utils.api as bu
import k3d
from bmcs_shell.folding.geometry.wb_cell_4p import \
    WBElem4Param as WBElem, axis_angle_to_q, qv_mult
import traits.api as tr
import numpy as np
import json
import time


class WBTessellation(bu.InteractiveModel):
    name = 'Waterbomb shell'

    wb_cell = tr.Instance(WBElem, ())

    tree = ['wb_cell']

    plot_backend = 'k3d'

    n_phi_plus = bu.Int(4, GEO=True)
    n_x_plus = bu.Int(4, GEO=True)
    alpha = bu.Float(1e-5, GEO=True)
    a = bu.Float(1000, GEO=True)
    a_high = bu.Float(2000)
    b = bu.Float(1000, GEO=True)
    b_high = bu.Float(2000)
    c = bu.Float(1000, GEO=True)
    c_high = bu.Float(2000)

    show_wireframe = bu.Bool(True, GEO=True)
    show_nodes = bu.Bool(False, GEO=True)
    show_node_labels = bu.Bool(False, GEO=True)
    WIREFRAME = 'k3d_mesh_wireframe'
    NODES = 'k3d_nodes'
    NODES_LABELS = 'k3d_nodes_labels'

    @tr.observe('+GEO', post_init=True)
    def update_wb_cell(self, event):
        self.wb_cell.trait_set(
            alpha=self.alpha,
            a=self.a,
            a_high=self.a_high,
            b=self.b,
            b_high=self.b_high,
            c=self.c,
            c_high = self.c_high,
        )

    ipw_view = bu.View(
        bu.Item('alpha', latex=r'\alpha', editor=bu.FloatRangeEditor(
            low=1e-3, high=np.pi/2, n_steps=100, continuous_update=True)),
        bu.Item('a', latex='a', editor=bu.FloatRangeEditor(low=1e-3, high_name='a_high', n_steps=100,
                                                           continuous_update=True)),
        bu.Item('b', latex='b', editor=bu.FloatRangeEditor(low=1e-3, high_name='b_high', n_steps=100,
                                                           continuous_update=True)),
        bu.Item('c', latex='c', editor=bu.FloatRangeEditor(low=1e-3, high_name='c_high', n_steps=100,
                                                           continuous_update=True)),
        bu.Item('n_phi_plus', latex = r'n_\phi'),
        bu.Item('n_x_plus', latex = r'n_x'),
        bu.Item('show_wireframe'),
        bu.Item('show_node_labels'),
        bu.Item('show_nodes')
    )

    def get_phi_range(self, delta_phi):
        return np.arange(-(self.n_phi_plus - 1), self.n_phi_plus) * delta_phi

    def get_X_phi_range(self,delta_phi, R_0):
        """Given an array of angles and radius return an array of coordinates
        """
        phi_range = self.get_phi_range((delta_phi))
        return np.array([np.fabs(R_0) * np.sin(phi_range),
                         np.fabs(R_0) * np.cos(phi_range) + R_0]).T

    def get_X_x_range(self,delta_x):
        return np.arange(-(self.n_x_plus - 1), self.n_x_plus) * delta_x

    cell_map = tr.Property
    def _get_cell_map(self):
        delta_x = self.wb_cell.delta_x
        delta_phi = self.wb_cell.delta_phi
        R_0 = self.wb_cell.R_0

        X_x_range = self.get_X_x_range(delta_x)
        X_phi_range = self.get_X_phi_range(delta_phi, R_0)
        n_idx_x = len(X_x_range)
        n_idx_phi = len(X_phi_range)
        idx_x = np.arange(n_idx_x)
        idx_phi = np.arange(n_idx_phi)

        idx_x_ic = idx_x[(n_idx_x) % 2::2]
        idx_x_id = idx_x[(n_idx_x + 1) % 2::2]
        idx_phi_ic = idx_phi[(n_idx_phi) % 2::2]
        idx_phi_id = idx_phi[(n_idx_phi + 1) % 2::2]

        n_ic = len(idx_x_ic) * len(idx_phi_ic)
        n_id = len(idx_x_id) * len(idx_phi_id)

        n_cells = n_ic + n_id
        return n_cells, n_ic, n_id, idx_x_ic, idx_x_id, idx_phi_ic, idx_phi_id

    n_cells = tr.Property
    def _get_n_cells(self):
        n_cells, _, _, _, _, _, _ = self.cell_map
        return n_cells

    X_cells_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates of uncoupled cells
    I - node, a - dimension
    '''
    @tr.cached_property
    def _get_X_cells_Ia(self):

        delta_x = self.wb_cell.delta_x
        delta_phi = self.wb_cell.delta_phi
        R_0 = self.wb_cell.R_0

        X_Ia_wb_rot = np.copy(self.wb_cell.X_Ia)
        X_Ia_wb_rot[...,2] -= R_0
        X_cIa = np.array([X_Ia_wb_rot], dtype=np.float_)
        rotation_axes = np.array([[1, 0, 0]], dtype=np.float_)
        rotation_angles = self.get_phi_range(delta_phi)
        q = axis_angle_to_q(rotation_axes, rotation_angles)
        X_dIa = qv_mult(q, X_cIa)
        X_dIa[...,2] += R_0

        X_x_range = self.get_X_x_range(delta_x)
        X_phi_range = self.get_X_phi_range(delta_phi, R_0)
        n_idx_x = len(X_x_range)
        n_idx_phi = len(X_phi_range)
        idx_x = np.arange(n_idx_x)
        idx_phi = np.arange(n_idx_phi)

        idx_x_ic = idx_x[(n_idx_x) % 2::2]
        idx_x_id = idx_x[(n_idx_x + 1) % 2::2]
        idx_phi_ic = idx_phi[(n_idx_phi) % 2::2]
        idx_phi_id = idx_phi[(n_idx_phi + 1) % 2::2]

        X_E = X_x_range[idx_x_ic]
        X_F = X_x_range[idx_x_id]

        X_CIa = X_dIa[idx_phi_ic]
        X_DIa = X_dIa[idx_phi_id]

        expand = np.array([1,0,0])
        X_E_a = np.einsum('i,j->ij', X_E, expand)
        X_ECIa = X_CIa[np.newaxis,:,:,:] + X_E_a[:,np.newaxis,np.newaxis,:]
        X_F_a = np.einsum('i,j->ij', X_F, expand)
        X_FDIa = X_DIa[np.newaxis,:,:,:] + X_F_a[:,np.newaxis,np.newaxis,:]

        X_Ia = np.vstack([X_ECIa.flatten().reshape(-1,3), X_FDIa.flatten().reshape(-1,3)])
        return X_Ia

    I_cells_Fi = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_I_cells_Fi(self):
        I_Fi_cell = self.wb_cell.I_Fi
        n_I_cell = self.wb_cell.n_I
        n_cells = self.n_cells
        i_range = np.arange(n_cells) * n_I_cell
        I_Fi = (I_Fi_cell[np.newaxis,:,:] + i_range[:, np.newaxis, np.newaxis]).reshape(-1,3)
        return I_Fi

    X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_X_Ia(self):
        idx_unique, idx_remap = self.unique_node_map
        return self.X_cells_Ia[idx_unique]

    I_Fi = tr.Property(depends_on='+GEO')
    '''Facet - node mapping
    '''
    @tr.cached_property
    def _get_I_Fi(self):
        _, idx_remap = self.unique_node_map
        return idx_remap[self.I_cells_Fi]

    node_match_threshold = tr.Property(depends_on='+GEO')
    def _get_node_match_threshold(self):
        min_length = np.min([self.a,self.b,self.c])
        return min_length * 1e-4

    unique_node_map = tr.Property(depends_on='+GEO')
    '''Property containing the mapping between the crease pattern nodes
    with duplicate nodes and pattern with compressed nodes array.
    The criterion for removing a node is geometric, the threshold
    is specified in node_match_threshold.
    '''
    def _get_unique_node_map(self):
        # reshape the coordinates in array of segments to the shape (n_N, n_D
        x_0 = self.X_cells_Ia
        # construct distance vectors between every pair of nodes
        x_x_0 = x_0[:, np.newaxis, :] - x_0[np.newaxis, :, :]
        # calculate the distance between every pair of nodes
        dist_0 = np.sqrt(np.einsum('...i,...i', x_x_0, x_x_0))
        # identify those at the same location
        zero_dist = dist_0 < self.node_match_threshold
        # get their indices
        i_idx, j_idx = np.where(zero_dist)
        # take only the upper triangle indices
        upper_triangle = i_idx < j_idx
        idx_multi, idx_delete = i_idx[upper_triangle], j_idx[upper_triangle]
        # construct a boolean array with True at valid and False at deleted
        # indices
        idx_unique = np.ones((len(x_0),), dtype='bool')
        idx_unique[idx_delete] = False
        # Boolean array of nodes to keep - includes both those that
        # are unique and redirection nodes to be substituted for duplicates
        idx_keep = np.ones((len(x_0),), dtype=np.bool_)
        idx_keep[idx_delete] = False
        # prepare the enumeration map map
        ij_map = np.ones_like(dist_0, dtype=np.int_) + len(x_0)
        i_ = np.arange(len(x_0))
        # indexes of nodes that are being kept
        idx_row = i_[idx_keep]
        # enumerate the kept nodes by putting their number onto the diagonal
        ij_map[idx_keep, idx_keep] = np.arange(len(idx_row))
        # broadcast the substitution nodes into the interaction positions
        ij_map[i_idx, j_idx] = ij_map[i_idx, i_idx]
        # get the substitution node by picking up the minimum index within ac column
        idx_remap = np.min(ij_map, axis=0)

        return idx_unique, idx_remap

    I_CDij = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_I_CDij(self):
        n_cells, n_ic, n_id, _, x_cell_idx, _, y_cell_idx = self.cell_map
        x_idx, y_idx = x_cell_idx / 2, y_cell_idx / 2
        n_x_, n_y_ = len(x_idx), len(y_idx)
        I_cell_offset = (n_ic + np.arange(n_x_ * n_y_).reshape(n_x_, n_y_)) * self.wb_cell.n_I
        I_CDij_map = (I_cell_offset.T[:, :, np.newaxis, np.newaxis] +
                      self.wb_cell.I_boundary[np.newaxis, np.newaxis, :, :])
        return I_CDij_map

    I_Li = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_I_Li(self):
        self.I_Fi


    def setup_plot(self, pb):
        X_Ia = self.X_Ia.astype(np.float32)
        I_Fi = self.I_Fi.astype(np.uint32)

        I_M = self.I_CDij[(0, -1), :, (0, -1), :]
        _, idx_remap = self.unique_node_map
        J_M = idx_remap[I_M]
        X_Ma = X_Ia[J_M.flatten()]

        k3d_mesh = k3d.mesh(X_Ia,
                                 I_Fi,
                                 color=0x999999,
                                 side='double')

        pb.objects['k3d_mesh'] = k3d_mesh
        pb.plot_fig += k3d_mesh

        if self.show_nodes:
            self._add_nodes_to_fig(pb, X_Ma)

        if self.show_node_labels:
            self._add_nodes_labels_to_fig(pb, X_Ia)

        if self.show_wireframe:
            self._add_wireframe_to_fig(pb, X_Ia, I_Fi)

    def update_plot(self, pb):
        X_Ia = self.X_Ia.astype(np.float32)
        I_Fi = self.I_Fi.astype(np.uint32)

        I_M = self.I_CDij[(0, -1),:,(0, -1),:]
        _, idx_remap = self.unique_node_map
        J_M = idx_remap[I_M]
        X_Ma = X_Ia[J_M.flatten()]

        mesh = pb.objects['k3d_mesh']
        mesh.vertices = X_Ia
        mesh.indices = I_Fi

        if self.show_nodes:
            if self.NODES in pb.objects:
                pb.objects[self.NODES].positions = X_Ma
            else:
                self._add_nodes_to_fig(pb, X_Ma)
        else:
            if self.NODES in pb.objects:
                pb.clear_object(self.NODES)

        if self.show_wireframe:
            if self.WIREFRAME in pb.objects:
                wireframe = pb.objects[self.WIREFRAME]
                wireframe.vertices = X_Ia
                wireframe.indices = I_Fi
            else:
                self._add_wireframe_to_fig(pb, X_Ia, I_Fi)
        else:
            if self.WIREFRAME in pb.objects:
                pb.clear_object(self.WIREFRAME)

        if self.show_node_labels:
            if self.NODES_LABELS in pb.objects:
                pb.clear_object(self.NODES_LABELS)
            self._add_nodes_labels_to_fig(pb, X_Ia)
        else:
            if self.NODES_LABELS in pb.objects:
                pb.clear_object(self.NODES_LABELS)

    def _add_nodes_labels_to_fig(self, pb, X_Ia):
        text_list = []
        for I, X_a in enumerate(X_Ia):
            k3d_text = k3d.text('%g' % I, tuple(X_a), label_box=False, size=0.8, color=0x00FF00)
            pb.plot_fig += k3d_text
            text_list.append(k3d_text)
        pb.objects[self.NODES_LABELS] = text_list

    def _add_wireframe_to_fig(self, pb, X_Ia, I_Fi):
        k3d_mesh_wireframe = k3d.mesh(X_Ia,
                                      I_Fi,
                                      color=0x000000,
                                      wireframe=True)
        pb.plot_fig += k3d_mesh_wireframe
        pb.objects[self.WIREFRAME] = k3d_mesh_wireframe

    def _add_nodes_to_fig(self, pb, X_Ma):
        k3d_points = k3d.points(X_Ma, point_size=100)
        pb.objects[self.NODES] = k3d_points
        pb.plot_fig += k3d_points

    def _show_or_hide_fig_object(self, pb, show_obj, obj_name, obj_add_fun, obj_update_fun):
        if show_obj:
            if obj_name in pb.objects:
                obj_update_fun()
            else:
                obj_add_fun()
        else:
            if obj_name in pb.objects:
                pb.clear_object(obj_name)

    def export_fold_file(self, path=None):
        # See https://github.com/edemaine/fold/blob/master/doc/spec.md for fold file specification
        # Viewer: https://edemaine.github.io/fold/examples/foldviewer.html

        output_data = {
            "file_spec": 1,
            "file_creator": "BMCS software suite",
            "file_author": "RWTH Aachen - Institute of Structural Concrete",
            "file_title": "Preliminary Base",
            "file_classes": ["singleModel"],
            "frame_title": "Preliminary Base Crease Pattern",
            "frame_classes": ["creasePattern"],
            "vertices_coords": self.X_Ia.tolist(),
            "faces_vertices": self.I_Fi.tolist(),
            # To be completed
        }

        if path is None:
            path = time.strftime("%Y%m%d-%H%M%S") + '-shell.fold'

        with open(path, 'w') as outfile:
            json.dump(output_data, outfile, sort_keys=True, indent=4)
