import bmcs_utils.api as bu
import numpy as np
import traits.api as tr
import k3d

class WBCell(bu.Model):
    name = 'Waterbomb cell'

    plot_backend = 'k3d'

    NODES_LABELS = 'k3d_nodes_labels'
    show_node_labels = bu.Bool(False, GEO=True)
    show_wireframe = bu.Bool(True)
    opacity = bu.Float(0.6, GEO=True)

    ipw_view = bu.View(
        bu.Item('show_node_labels'),
    )

    X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_X_Ia(self):
        return np.array([[0., 0., 0.],
                         [1000., 930.99634691, 365.02849483],
                         [-1000., 930.99634691, 365.02849483],
                         [1000., -930.99634691, 365.02849483],
                         [-1000., -930.99634691, 365.02849483],
                         [764.84218728, 0., 644.21768724],
                         [-764.84218728, 0., 644.21768724]])

    I_Fi = tr.Property
    '''Triangle mapping '''
    @tr.cached_property
    def _get_I_Fi(self):
        return np.array([[0, 1, 2], [0, 3, 4], [0, 1, 5], [0, 5, 3], [0, 2, 6], [0, 6, 4]]).astype(np.int32)

    def setup_plot(self, pb):
        wb_mesh = k3d.mesh(self.X_Ia.astype(np.float32),
                                 self.I_Fi.astype(np.uint32),
                                opacity=self.opacity,
                                 color=0x999999,
                                 side='double')
        pb.plot_fig += wb_mesh
        pb.objects['wb_mesh'] = wb_mesh
        if self.show_wireframe:
            wb_mesh_wireframe = k3d.mesh(self.X_Ia.astype(np.float32),
                                            self.I_Fi.astype(np.uint32),
                                            color=0x000000,
                                            wireframe=True)

            pb.plot_fig += wb_mesh_wireframe
            pb.objects['wb_mesh_wireframe'] = wb_mesh_wireframe

        if self.show_node_labels:
            self._add_nodes_labels_to_fig(pb, self.X_Ia)

    def update_plot(self, pb):
        wb_mesh = pb.objects['wb_mesh']
        wb_mesh_wireframe = pb.objects['wb_mesh_wireframe']
        self._assign_mesh_data(wb_mesh)
        if self.show_wireframe:
            self._assign_mesh_data(wb_mesh_wireframe)

        if self.show_node_labels:
            if self.NODES_LABELS in pb.objects:
                pb.clear_object(self.NODES_LABELS)
            self._add_nodes_labels_to_fig(pb, self.X_Ia)
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

    def _assign_mesh_data(self, mesh):
        mesh.vertices = self.X_Ia.astype(np.float32)
        mesh.indices = self.I_Fi.astype(np.uint32)
        mesh.attributes = self.X_Ia[:, 2].astype(np.float32)