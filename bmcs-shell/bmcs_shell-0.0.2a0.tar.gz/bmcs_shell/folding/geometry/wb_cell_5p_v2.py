import bmcs_utils.api as bu
import k3d
import traits.api as tr
import numpy as np
from bmcs_shell.folding.geometry.wb_cell import WBCell
from numpy import sin, cos, sqrt


class WBElem5ParamV2(WBCell):
    name = 'waterbomb cell 5p v2'

    plot_backend = 'k3d'

    gamma = bu.Float(np.pi / 6, GEO=True)
    beta = bu.Float(np.pi / 3, GEO=True)
    a = bu.Float(500, GEO=True)
    b = bu.Float(750, GEO=True)
    c = bu.Float(400, GEO=True)

    continuous_update = True

    ipw_view = bu.View(
        bu.Item('gamma', latex=r'\gamma', editor=bu.FloatRangeEditor(
            low=1e-6, high=np.pi / 2, n_steps=100, continuous_update=continuous_update)),
        bu.Item('beta', latex=r'\beta', editor=bu.FloatRangeEditor(
            low=1e-6, high=np.pi - 1e-6, n_steps=100, continuous_update=continuous_update)),
        bu.Item('a', latex='a', editor=bu.FloatRangeEditor(
            low=1e-6, high=2000, n_steps=100, continuous_update=continuous_update)),
        bu.Item('b', latex='b', editor=bu.FloatRangeEditor(
            low=1e-6, high=2000, n_steps=100, continuous_update=continuous_update)),
        bu.Item('c', latex='c', editor=bu.FloatRangeEditor(
            low=1e-6, high=2000, n_steps=100, continuous_update=continuous_update)),
        *WBCell.ipw_view.content,
    )

    X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''

    @tr.cached_property
    def _get_X_Ia(self):
        return self.get_cell_vertices()

    def get_cell_vertices(self, a=0.5, b=0.75, c=0.4, gamma=np.pi / 6, beta=np.pi / 3):
        a = self.a
        b = self.b
        c = self.c
        gamma = self.gamma
        beta = self.beta

        # phi1 is angle between OU_ur line and z axis
        cos_psi1 = ((b ** 2 - a ** 2) - a * sqrt(a ** 2 + b ** 2) * cos(beta)) / (b * sqrt(a ** 2 + b ** 2) * sin(beta))
        sin_psi1 = sqrt(
            a ** 2 * (3 * b ** 2 - a ** 2) + 2 * a * (b ** 2 - a ** 2) * sqrt(a ** 2 + b ** 2) * cos(beta) - (
                    a ** 2 + b ** 2) ** 2 * cos(beta) ** 2) / (b * sqrt(a ** 2 + b ** 2) * sin(beta))
        cos_psi5 = (sqrt(a ** 2 + b ** 2) * cos(beta) - a * cos(2 * gamma)) / (b * sin(2 * gamma))
        sin_psi5 = sqrt(b ** 2 + 2 * a * sqrt(a ** 2 + b ** 2) * cos(beta) * cos(2 * gamma) - (a ** 2 + b ** 2) * (
                cos(beta) ** 2 + cos(2 * gamma) ** 2)) / (b * sin(2 * gamma))
        cos_psi6 = (a - sqrt(a ** 2 + b ** 2) * cos(beta) * cos(2 * gamma)) / (
                sqrt(a ** 2 + b ** 2) * sin(beta) * sin(2 * gamma))
        sin_psi6 = sqrt(b ** 2 + 2 * a * sqrt(a ** 2 + b ** 2) * cos(beta) * cos(2 * gamma) - (a ** 2 + b ** 2) * (
                cos(beta) ** 2 + cos(2 * gamma) ** 2)) / (sqrt(a ** 2 + b ** 2) * sin(beta) * sin(2 * gamma))
        cos_psi1plus6 = cos_psi1 * cos_psi6 - sin_psi1 * sin_psi6
        sin_psi1plus6 = sin_psi1 * cos_psi6 + cos_psi1 * sin_psi6

        cos_phi1 = cos_psi1plus6
        cos_phi2 = cos_psi5
        cos_phi3 = cos_psi5
        cos_phi4 = cos_psi1plus6
        sin_phi1 = sin_psi1plus6
        sin_phi2 = sin_psi5
        sin_phi3 = sin_psi5
        sin_phi4 = sin_psi1plus6

        U_ur = np.array(
            [a * sin(gamma) - b * cos_phi1 * cos(gamma), b * sin_phi1, a * cos(gamma) + b * cos_phi1 * sin(gamma)])
        U_ul = np.array(
            [-a * sin(gamma) + b * cos_phi2 * cos(gamma), b * sin_phi2, a * cos(gamma) + b * cos_phi2 * sin(gamma)])
        U_lr = np.array(
            [a * sin(gamma) - b * cos_phi3 * cos(gamma), -b * sin_phi3, a * cos(gamma) + b * cos_phi3 * sin(gamma)])
        U_ll = np.array(
            [-a * sin(gamma) + b * cos_phi4 * cos(gamma), -b * sin_phi4, a * cos(gamma) + b * cos_phi4 * sin(gamma)])
        V_r = np.array([c * sin(gamma), 0, c * cos(gamma)])
        V_l = np.array([-c * sin(gamma), 0, c * cos(gamma)])

        X_Ia = np.vstack((np.zeros(3), U_lr, U_ll, U_ur, U_ul, V_r, V_l)).astype(np.float32)
        return X_Ia
