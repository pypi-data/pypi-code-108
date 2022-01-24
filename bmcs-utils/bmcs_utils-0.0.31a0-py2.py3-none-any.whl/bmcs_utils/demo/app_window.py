"""
This module demonstrates the concept applied
in the implementation of the main application window.

The tree of the model hierarchy can be used
to select individual model components and edit them.
Plotting of the model components is done using
the predefined the backends.

Currently a model must decide for a single
backend.
"""

import ipywidgets as ipw
import matplotlib.pylab as plt
import k3d
import ipytree as ipt
import traits.api as tr
import numpy as np

print_output = ipw.Output(layout=ipw.Layout(width="100%"))

class PlotBackend(tr.HasTraits):
    plot_widget = tr.Instance(ipw.Output)
    plot_fig = tr.Any

class MPLBackend(PlotBackend):

    def __init__(self, *args, **kw):
        super().__init__(*args,**kw)
        self.plot_widget = ipw.Output(layout=ipw.Layout(width="100%",height="100%"))
        with self.plot_widget:
            self.plot_fig = plt.figure(figsize=(5, 2), constrained_layout=True)

    def clear_fig(self):
        self.plot_fig.clf()
    def show_fig(self):
        self.plot_fig.canvas.draw()

class K3DBackend(PlotBackend):

    def __init__(self, *args, **kw):
        super().__init__(*args,**kw)
        self.plot_widget = ipw.Output(layout=ipw.Layout(width="100%", height="100%"))
        self.plot_fig = k3d.Plot()
        self.plot_fig.layout = ipw.Layout(width="100%",height="100%")
        with self.plot_widget:
            display(self.plot_fig)
        self.plot_fig.outputs.append(self.plot_widget)

    def clear_fig(self):
        for obj in self.plot_fig.objects:
            self.plot_fig -= obj
        for obj in self.plot_fig.objects:
            self.plot_fig -= obj
        self.objects = {}
    def show_fig(self):
        pass

class MPLNode(ipt.Node):
    backend = 'mpl'

    def setup_plot(self, pb):
        pb.axes = pb.plot_fig.subplots(1,1)

    def update_plot(self, pb):
        pb.axes.plot([0,1],[0,1])

class K3DNode(ipt.Node):
    backend = 'k3d'

    def setup_plot(self, pb):

        X_Ia = np.array([
            [0,0,0],#0
            [1,0,0],#1
            [0,1,0],#2
            [1,1,0],#3
            [0,0,1],#4
            [1,0,1],#5
            [0,1,1],#6
            [1,1,1],#7
            ],
            dtype=np.float_
        )
        I_Fi = np.array([
            [0,1,2],
            [3,1,2],
            [4, 5, 6],
            [5, 6, 7],
        ])

        wb_mesh = k3d.mesh(X_Ia.astype(np.float32),
                                I_Fi.astype(np.uint32),
                                 color=0x999999,
                                 side='double')

        pb.objects = {'wb_mesh', wb_mesh}
        pb.plot_fig += wb_mesh

    def update_plot(self, pb):
        mesh = pb.objects['wb_mesh']
        mesh.vertices = self.X_Ia.astype(np.float32)
        mesh.indices = self.I_Fi.astype(np.uint32)
        mesh.attributes = self.X_Ia[:, 2].astype(np.float32)

class AppWindow(tr.HasTraits):

    tree = tr.Instance(ipt.Tree)
    def _tree_default(self):
        tree = ipt.Tree()
        node1 = MPLNode(name='one' )
        node2 = MPLNode(name='two' )
        node3 = K3DNode(name='three' )
        node4 = K3DNode(name='four', nodes=[node3])
        node5 = K3DNode(name='five', nodes=[node4])
        tree.add_node(node1)
        tree.add_node(node2)
        tree.add_node(node5)

        for node in [node1, node2, node3, node4, node5]:
            node.observe(self.node_selected,'selected')

        return tree

    def node_selected(self, event):
        if event['old']:
            return
        node = event['owner']
        name = node.name
        backend = node.backend
        self.set_plot_backend(backend)
        self.setup_plot_fig(node)
        self.update_plot_fig(node)

    current_plot_backend = tr.Str

    def set_plot_backend(self, backend):
        if self.current_plot_backend == backend:
            return
        self.current_plot_backend = backend
        pb = self.plot_backend_table[backend]
        self.plot_pane.children = [pb.plot_widget]

    def setup_plot_fig(self, model):
        pb = self.plot_backend_table[self.current_plot_backend]
        pb.clear_fig()
        model.setup_plot(pb)

    def update_plot_fig(self, model):
        pb = self.plot_backend_table[self.current_plot_backend]
        model.update_plot(pb)
        pb.show_fig()

    plot_backend_table = tr.Dict
    def _plot_backend_table_default(self):
        return{'mpl': MPLBackend(), 'k3d': K3DBackend()}

    def render(self):
        tree = self.tree
        self.plot_pane = ipw.VBox([],layout=ipw.Layout(width="100%"))
        self.tree.layout=ipw.Layout(width="300px")
        main_pane = ipw.HBox([self.tree, self.plot_pane],
                       layout=ipw.Layout(
                           width="100%",
                            border = 'solid 1px black',
        ))
        app = ipw.VBox([main_pane, print_output],layout=ipw.Layout(width="100%"))
        return app
