from bmcs_utils.trait_types import \
    Float, Int, Bool, FloatRangeEditor, Instance, Range, ProgressEditor, FloatEditor
from bmcs_utils.model import Model
from bmcs_utils.item import Item
from bmcs_utils.view import View
import numpy as np
import time
import traits.api as tr
import k3d

from bmcs_utils.demo.layout_model import LayoutModel

class ModelWithVolume(Model):
    """Example model with a cross sectional shape"""
    name = 'volume'

    plot_backend = 'k3d'

    layout = tr.Instance(LayoutModel,())

    tree = ['layout']

    b = Float(5)

    ipw_view = View(
        Item('b', latex=r'b'),
    )

    def setup_plot(self, pb):
        k3d_plot = pb.plot_fig
        self.X_Ia = np.array([
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
        self.I_Fi = np.array([
            [0,1,2],
            [3,1,2],
            [4, 5, 6],
            [5, 6, 7],
        ])

        wb_mesh = k3d.mesh(self.X_Ia.astype(np.float32),
                           self.I_Fi.astype(np.uint32),
                           color=0x999999,
                           side='double')
        k3d_plot += wb_mesh
        pb.objects = {'mesh':wb_mesh}

    def update_plot(self, pb):
        mesh = pb.objects['mesh']
        mesh.vertices = self.X_Ia.astype(np.float32)
        mesh.indices = self.I_Fi.astype(np.uint32)
        mesh.attributes = self.X_Ia[:, 2].astype(np.float32)

