import bmcs_utils.api as bu
from bmcs_shell.folding.geometry.wb_cell_5p_v2 import \
    WBElem5ParamV2
import traits.api as tr
import numpy as np
from numpy import cos, sin, tan, arctan, sqrt
from scipy.optimize import minimize
import k3d
import random

class WB5PTessellation(WBElem5ParamV2):
    name = 'WB Numerical Tessellation'

    # wb_cell = tr.Instance(WBElem5Param, ())
    # tree = ['wb_cell']
    # X_Ia = tr.DelegatesTo('wb_cell')
    # I_Fi = tr.DelegatesTo('wb_cell')

    plot_backend = 'k3d'

    n_y = bu.Int(3, GEO=True)
    n_x = bu.Int(3, GEO=True)

    rot_br = bu.Float(0.5)
    rot_ur = bu.Float(0.5)
    investigate_rot = bu.Bool
    calc_analytically = bu.Bool
    sigma_sol_num = bu.Int(-1, GEO=True)
    rho_sol_num = bu.Int(-1, GEO=True)

    # show_wireframe = bu.Bool(True, GEO=True)
    show_node_labels = bu.Bool(False, GEO=True)

    # br_X_Ia = tr.Property(depends_on='+GEO')
    # '''Array with nodal coordinates I - node, a - dimension
    # '''
    # # @tr.cached_property
    def _get_br_X_Ia(self, X_Ia, rot=None):
        br_X_Ia = self._get_cell_matching_v1_to_v2(X_Ia, np.array([4, 6]), np.array([5, 1]))
        return self.rotate_cell(br_X_Ia, np.array([4, 6]), -self.sol[0] if rot is None else rot)

    # ur_X_Ia = tr.Property(depends_on='+GEO')
    # '''Array with nodal coordinates I - node, a - dimension
    # '''
    # # @tr.cached_property
    def _get_ur_X_Ia(self, X_Ia, rot=None):
        ur_X_Ia = self._get_cell_matching_v1_to_v2(X_Ia, np.array([6, 2]), np.array([3, 5]))
        return self.rotate_cell(ur_X_Ia, np.array([6, 2]), -self.sol[1] if rot is None else rot)

    def _get_ul_X_Ia(self, X_Ia, rot=None):
        br_X_Ia = self._get_cell_matching_v1_to_v2(X_Ia, np.array([5, 1]), np.array([4, 6]))
        return self.rotate_cell(br_X_Ia, np.array([5, 1]), self.sol[0] if rot is None else rot)

    def _get_bl_X_Ia(self, X_Ia, rot=None):
        br_X_Ia = self._get_cell_matching_v1_to_v2(X_Ia, np.array([3, 5]), np.array([6, 2]))
        return self.rotate_cell(br_X_Ia, np.array([3, 5]), self.sol[1] if rot is None else rot)

    ipw_view = bu.View(
        *WBElem5ParamV2.ipw_view.content,
        bu.Item('n_x', latex=r'n_x'),
        bu.Item('n_y', latex=r'n_y'),
        bu.Item('rot_br', latex=r'rot~br', editor=bu.FloatRangeEditor(low=0, high=2 * np.pi, n_steps=150,
                                                                      continuous_update=True)),
        bu.Item('rot_ur', latex=r'rot~ur', editor=bu.FloatRangeEditor(low=0, high=2 * np.pi, n_steps=150,
                                                                      continuous_update=True)),
        bu.Item('investigate_rot'),
        bu.Item('calc_analytically'),
        # bu.Item('show_wireframe'),
        bu.Item('show_node_labels'),
        bu.Item('sigma_sol_num'),
        bu.Item('rho_sol_num'),
    )

    # Source:
    # https://github.com/nghiaho12/rigid_transform_3D
    # http://nghiaho.com/?page_id=671
    # Input: expects 3xN matrix of points
    # Returns R,t
    # R = 3x3 rotation matrix
    # t = 3x1 column vector

    def _get_best_rot_and_trans_3d(self, A, B):
        assert A.shape == B.shape

        num_rows, num_cols = A.shape
        if num_rows != 3:
            raise Exception(f"matrix A is not 3xN, it is {num_rows}x{num_cols}")

        num_rows, num_cols = B.shape
        if num_rows != 3:
            raise Exception(f"matrix B is not 3xN, it is {num_rows}x{num_cols}")

        # find mean column wise
        centroid_A = np.mean(A, axis=1)
        centroid_B = np.mean(B, axis=1)

        # ensure centroids are 3x1
        centroid_A = centroid_A.reshape(-1, 1)
        centroid_B = centroid_B.reshape(-1, 1)

        # subtract mean
        Am = A - centroid_A
        Bm = B - centroid_B

        H = Am @ np.transpose(Bm)

        # sanity check
        # if linalg.matrix_rank(H) < 3:
        #    raise ValueError("rank of H = {}, expecting 3".format(linalg.matrix_rank(H)))

        # find rotation
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T

        # special reflection case
        if np.linalg.det(R) < 0:
            # print("det(R) < R, reflection detected!, correcting for it ...")
            Vt[2, :] *= -1
            R = Vt.T @ U.T

        t = -R @ centroid_A + centroid_B

        return R, t

    def _get_rot_matrix_around_vector(self, v, angle):
        c = np.cos(angle)
        s = np.sin(angle)
        v_norm = v / np.sqrt(sum(v * v))

        # See: Rotation matrix from axis and angle (https://en.wikipedia.org/wiki/Rotation_matrix)
        cross_product_matrix = np.cross(v_norm, np.identity(v_norm.shape[0]) * -1)
        return c * np.identity(3) + s * cross_product_matrix + (1 - c) * np.outer(v_norm, v_norm)

    def _get_cell_matching_v1_to_v2(self, X_Ia, v1_ids, v2_ids):
        # v1_2a = np.array([X_Ia[v1_ids[0]], X_Ia[v1_ids[1]]])
        # v2_2a = np.array([X_Ia[v2_ids[0]], X_Ia[v2_ids[1]]])
        # rot, trans = self.get_best_rot_and_trans_3d(v1_2a.T, v2_2a.T)

        v1_2a = np.array([X_Ia[v1_ids[0]], X_Ia[v1_ids[1]], X_Ia[0]]).T
        v2_2a = np.array([X_Ia[v2_ids[0]], X_Ia[v2_ids[1]], X_Ia[v2_ids[0]] + X_Ia[v2_ids[1]] - X_Ia[0]]).T
        rot, trans = self._get_best_rot_and_trans_3d(v1_2a, v2_2a)

        translated_X_Ia = trans.flatten() + np.einsum('ba, Ia -> Ib', rot, X_Ia)

        ####### Rotating around vector #######
        # Bringing back to origin (because rotating is around a vector originating from origin)
        translated_X_Ia1 = translated_X_Ia - translated_X_Ia[v1_ids[1]]

        # Rotating
        rot_around_v1 = self._get_rot_matrix_around_vector(translated_X_Ia1[v1_ids[0]] - translated_X_Ia1[v1_ids[1]], np.pi * 1)
        translated_X_Ia1 = np.einsum('ba, Ia -> Ib', rot_around_v1, translated_X_Ia1)

        # Bringing back in position
        return translated_X_Ia1 + translated_X_Ia[v1_ids[1]]

    def rotate_cell(self, cell_X_Ia, v1_ids, angle=np.pi):
        ####### Rotating around vector #######
        # Bringing back to origin (because rotating is around a vector originating from origin)
        cell_X_Ia_copy = np.copy(cell_X_Ia)
        cell_X_Ia = cell_X_Ia_copy - cell_X_Ia_copy[v1_ids[1]]

        # Rotating
        rot_around_v1 = self._get_rot_matrix_around_vector(cell_X_Ia[v1_ids[0]] - cell_X_Ia[v1_ids[1]], angle)
        cell_X_Ia = np.einsum('ba, Ia -> Ib', rot_around_v1, cell_X_Ia)

        # Bringing back in position
        return cell_X_Ia + cell_X_Ia_copy[v1_ids[1]]

    def rotate_and_get_diff(self, rotations):
        br_X_Ia_rot = self._get_br_X_Ia(self.X_Ia, rot=rotations[0])
        ur_X_Ia_rot = self._get_ur_X_Ia(self.X_Ia, rot=rotations[1])
        diff = ur_X_Ia_rot[1] - br_X_Ia_rot[3]
        dist = np.sqrt(np.sum(diff * diff))
        #     print('dist=', dist)
        return dist

    sol = tr.Property(depends_on='+GEO, calc_analytically')
    @tr.cached_property
    def _get_sol(self):
        # print('---------------------------')
        # sol = self.minimize_dist()
        # # Transfer angles to range [-pi, pi] (to avoid having angle > 2pi so we can do the comparison that follows)
        # sol = np.arctan2(np.sin(sol), np.cos(sol))
        # print('num_sol=', sol)
        # if self.calc_analytically:
        #     rhos, sigmas = self.get_3_cells_angles()
        #     print('original sigmas=', sigmas)
        #     print('original rhos=', rhos)
        #     # rhos = 2 * np.pi - rhos
        #     # sigmas = 2 * np.pi - sigmas
        #     rhos = -rhos
        #     sigmas = -sigmas
        #     print('sigmas=', sigmas)
        #     print('rhos=', rhos)
        #
        #     if self.sigma_sol_num != -1 and self.rho_sol_num != -1:
        #         print('Solution {} was used.'.format(self.sigma_sol_num))
        #         sol = np.array([sigmas[self.sigma_sol_num - 1], rhos[self.rho_sol_num - 1]])
        #         return sol
        #
        #     sigma_sol_idx = np.argmin(np.abs(sigmas - sol[0]))
        #     rho_sol_idx = np.argmin(np.abs(rhos - sol[1]))
        #
        #     if sigma_sol_idx != rho_sol_idx:
        #         print('Warning: sigma_sol_idx != rho_sol_idx, num solution is picked!')
        #     else:
        #         diff = np.min(np.abs(sigmas - sol[0])) + np.min(np.abs(rhos - sol[1]))
        #         print('Solution {} was picked (nearst to numerical sol), diff={}'.format(sigma_sol_idx + 1, diff))
        #         sol = np.array([sigmas[sigma_sol_idx], rhos[rho_sol_idx]])
        # return sol

        # Solving with only 4th solution
        rhos, sigmas = self.get_3_cells_angles(sol_num=4)
        sol = np.array([sigmas[0], rhos[0]])
        return sol

    def get_3_cells_angles(self, sol_num=None):
        a = self.a
        b = self.b
        c = self.c
        gamma = self.gamma
        beta = self.beta

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

        sin_phi1 = sin_psi1plus6
        sin_phi2 = sin_psi5
        sin_phi3 = sin_psi5
        sin_phi4 = sin_psi1plus6

        cos_phi1 = cos_psi1plus6
        cos_phi2 = cos_psi5
        cos_phi3 = cos_psi5
        cos_phi4 = cos_psi1plus6

        # ALWAYS USE THIS TO FIND DEFINITE ANGLE IN [-pi, pi] from sin and cos
        phi1 = np.arctan2(sin_phi1, cos_phi1)
        phi2 = np.arctan2(sin_phi2, cos_phi2)
        phi3 = phi2
        phi4 = phi1

        W = 2 * a * (1 - cos(phi1 + phi3)) * (
                    sin(2 * gamma) ** 2 * a * c ** 2 - (cos(phi2) + cos(phi4)) * (cos(2 * gamma) - 1) * sin(
                2 * gamma) * b * c ** 2 - 2 * (cos(phi2) + cos(phi4)) * sin(2 * gamma) * a * b * c - 2 * a * c * (
                                2 * a - c) * (cos(2 * gamma) + 1) + 2 * a * b ** 2 * (cos(phi1 + phi3) + 1)) - (
                        ((a - c) ** 2 + b ** 2) * (cos(phi2) ** 2 + cos(phi4) ** 2) - 2 * cos(phi4) * cos(phi2) * (
                            (a - c) ** 2 + cos(phi1 + phi3) * b ** 2)) * c ** 2 * sin(2 * gamma) ** 2

        T_rho = ((a - c) ** 2 + b ** 2) * (cos(phi1 + phi3) - 1) * (
                    a * (2 * b ** 2 * (cos(phi1 + phi3) + 1) + 4 * a * (a - c)) * cos(2 * gamma)
                    + 2 * b * sin(2 * gamma) * (b ** 2 * cos(phi2) * (cos(phi1 + phi3) + 1) + (a - c) * (
                        (a - c) * cos(phi2) + a * cos(phi2) + c * cos(phi4))) + 2 * a * (
                                2 * a * (a - c) - b ** 2 * (cos(phi1 + phi3) + 1)))

        T_sigma = ((a - c) ** 2 + b ** 2) * (cos(phi1 + phi3) - 1) * (
                    a * (2 * b ** 2 * (cos(phi1 + phi3) + 1) + 4 * a * (a - c)) * cos(2 * gamma)
                    + 2 * b * sin(2 * gamma) * (b ** 2 * cos(phi4) * (cos(phi1 + phi3) + 1) + (a - c) * (
                        (a - c) * cos(phi4) + a * cos(phi4) + c * cos(phi2))) + 2 * a * (
                                2 * a * (a - c) - b ** 2 * (cos(phi1 + phi3) + 1)))

        rhos = []
        sigmas = []
        get_angle = lambda x: np.arctan(x) * 2

        if sol_num == 1 or sol_num is None:
            sol_P1_t_1 = (2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                        a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                            ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi2) - cos(phi4) * (
                                (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                    phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          + (cos(phi1 + phi3) - 1) * (2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (a ** 2 + b ** 2) * (
                                    cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                         (2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_rho))

            sol_Q1_u_1 = (2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                    a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                    ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi4) - cos(phi2) * (
                    (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          + (cos(phi1 + phi3) - 1) * (
                                      2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (
                                    a ** 2 + b ** 2) * (
                                cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                             (2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_sigma))
            rhos.append(get_angle(sol_P1_t_1))
            sigmas.append(get_angle(sol_Q1_u_1))

        if sol_num == 2 or sol_num is None:
            sol_P1_t_2 = (2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                        a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                            ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi2) - cos(phi4) * (
                                (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                    phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          - (cos(phi1 + phi3) - 1) * (2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (a ** 2 + b ** 2) * (
                                    cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                         (2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_rho))

            sol_Q1_u_2 = (2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                    a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                    ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi4) - cos(phi2) * (
                    (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          - (cos(phi1 + phi3) - 1) * (
                                      2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (
                                    a ** 2 + b ** 2) * (
                                cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                             (2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_sigma))
            rhos.append(get_angle(sol_P1_t_2))
            sigmas.append(get_angle(sol_Q1_u_2))

        if sol_num == 3 or sol_num is None:
            sol_P2_t_1 = (-2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                        a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                            ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi2) - cos(phi4) * (
                                (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                    phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          + (cos(phi1 + phi3) - 1) * (2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (a ** 2 + b ** 2) * (
                                    cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                         (-2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_rho))

            sol_Q2_u_1 = (-2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                    a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                    ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi4) - cos(phi2) * (
                    (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          + (cos(phi1 + phi3) - 1) * (
                                      2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (
                                    a ** 2 + b ** 2) * (
                                cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                             (-2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_sigma))
            rhos.append(get_angle(sol_P2_t_1))
            sigmas.append(get_angle(sol_Q2_u_1))

        if sol_num == 4 or sol_num is None:
            sol_P2_t_2 = (-2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                        a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                            ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi2) - cos(phi4) * (
                                (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                    phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          - (cos(phi1 + phi3) - 1) * (2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (a ** 2 + b ** 2) * (
                                    cos(phi2) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                         (-2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_rho))

            sol_Q2_u_2 = (-2 * b * (a - c) * (cos(phi1 + phi3) - 1) * sqrt((a - c) ** 2 + b ** 2) * sqrt(W) - 2 * b * (
                        a * b * c * sin(phi1 + phi3) * (cos(phi1 + phi3) - 1) * cos(2 * gamma) + (
                            ((a - c) ** 2 + b ** 2 * cos(phi1 + phi3)) * cos(phi4) - cos(phi2) * (
                                (a - c) ** 2 + b ** 2)) * sin(phi1 + phi3) * c * sin(2 * gamma) + a * b * sin(
                    phi1 + phi3) * (cos(phi1 + phi3) - 1) * (2 * a - c)) * sqrt((a - c) ** 2 + b ** 2)
                          - (cos(phi1 + phi3) - 1) * (2 * b ** 2 * cos(phi1 + phi3) + 4 * (a - c) ** 2 + 2 * b ** 2) * sqrt(
                        (a - c) ** 2 + b ** 2) * sqrt(
                        4 * a * b ** 2 * (cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) - (a ** 2 + b ** 2) * (
                                    cos(phi4) * sin(2 * gamma) * b + (cos(2 * gamma) + 1) * a) ** 2)) / (
                         (-2 * b * ((a - c) ** 2 + b ** 2) * sin(phi1 + phi3) * sqrt(W) - T_sigma))
            rhos.append(get_angle(sol_P2_t_2))
            sigmas.append(get_angle(sol_Q2_u_2))

        # sol_P is tan(rho/2), sol_Q is tan(sigma/2)

        return np.array(rhos), np.array(sigmas)

    def minimize_dist(self):
        x0 = np.array([np.pi, np.pi])
        try:
            res = minimize(self.rotate_and_get_diff, x0, tol=1e-4)
        except:
            print('Error while minimizing!')
            return np.array([0, 0])
        smallest_dist = res.fun
        print('smallest_dist=', smallest_dist)
        sol = res.x
        return sol

    # def setup_plot(self, pb):
    #     pb.clear_fig()
    #     sol = self.sol
    #     I_Fi = self.I_Fi
    #     X_Ia = self.X_Ia
    #     br_X_Ia = self._get_br_X_Ia(X_Ia)
    #     ur_X_Ia = self._get_ur_X_Ia(X_Ia)
    #
    #     self.add_cell_to_pb(pb, X_Ia, I_Fi, 'X_Ia')
    #
    #     # if self.n_x > 1 or self.n_y > 1:
    #     #     self.add_cell_to_pb(pb, br_X_Ia, I_Fi, 'br_X_Ia')
    #     #     self.add_cell_to_pb(pb, ur_X_Ia, I_Fi, 'ur_X_Ia')
    #     #
    #     #     # for i in range(self.n_y - 1):
    #
    #     if self.n_x > 1:
    #         central_cell_X_Ia = X_Ia
    #         for j in range(self.n_x - 1):
    #             if (j + 2) % 2 == 0:
    #                 # Cell number is even
    #                 # New central cell is ur_X_Ia
    #                 br_cell_X_Ia = self._get_br_X_Ia(central_cell_X_Ia)
    #                 ur_cell_X_Ia = self._get_ur_X_Ia(central_cell_X_Ia)
    #
    #                 self.add_cell_to_pb(pb, br_cell_X_Ia, I_Fi, '')
    #                 self.add_cell_to_pb(pb, ur_cell_X_Ia, I_Fi, '')
    #                 central_cell_X_Ia = np.copy(ur_cell_X_Ia)
    #             else:
    #                 # Cell number is odd
    #                 # New central cell is ur_X_Ia
    #
    #                 ul_cell_X_Ia = self._get_ul_X_Ia(central_cell_X_Ia)
    #                 bl_cell_X_Ia = self._get_bl_X_Ia(central_cell_X_Ia)
    #                 self.add_cell_to_pb(pb, ul_cell_X_Ia, I_Fi, '')
    #                 self.add_cell_to_pb(pb, bl_cell_X_Ia, I_Fi, '')
    #                 central_cell_X_Ia = np.copy(br_cell_X_Ia)
    #
    #                 # br_cell_X_Ia = self._get_br_X_Ia(central_cell_X_Ia)
    #                 # self.add_cell_to_pb(pb, br_cell_X_Ia, I_Fi, '')
    #                 # central_cell_X_Ia = np.copy(br_cell_X_Ia)


    def setup_plot(self, pb):
        pb.clear_fig()
        I_Fi = self.I_Fi
        X_Ia = self.X_Ia

        y_base_cell_X_Ia = X_Ia
        next_y_base_cell_X_Ia = X_Ia
        base_cell_X_Ia = X_Ia
        next_base_cell_X_Ia = X_Ia

        for i in range(self.n_y):
            i_row_is_even = (i + 1) % 2 == 0

            add_br = True  # to switch between adding br and ur
            add_bl = True  # to switch between adding bl and ul

            for j in range(self.n_x):
                if j == 0:
                    self.add_cell_to_pb(pb, base_cell_X_Ia, I_Fi, '')
                    continue
                if (j + 1) % 2 == 0:
                    # Number of cell_to_add is even (add right from base cell)
                    if add_br:
                        cell_to_add = self._get_br_X_Ia(base_cell_X_Ia)
                        self.add_cell_to_pb(pb, cell_to_add, I_Fi, '')
                    else:
                        cell_to_add = self._get_ur_X_Ia(base_cell_X_Ia)
                        self.add_cell_to_pb(pb, cell_to_add, I_Fi, '')
                    add_br = not add_br
                    base_cell_X_Ia = next_base_cell_X_Ia
                    next_base_cell_X_Ia = cell_to_add
                else:
                    # Number of cell_to_add is odd (add left from base cell)
                    if add_bl:
                        cell_to_add = self._get_bl_X_Ia(base_cell_X_Ia)
                        self.add_cell_to_pb(pb, cell_to_add, I_Fi, '')
                    else:
                        cell_to_add = self._get_ul_X_Ia(base_cell_X_Ia)
                        self.add_cell_to_pb(pb, cell_to_add, I_Fi, '')
                    add_bl = not add_bl
                    base_cell_X_Ia = next_base_cell_X_Ia
                    next_base_cell_X_Ia = cell_to_add

            if i_row_is_even:
                # Next row is odd (change y_base_cell_X_Ia to a cell below base cell)
                base_cell_X_Ia = self._get_bl_X_Ia(self._get_br_X_Ia(next_y_base_cell_X_Ia))
                next_base_cell_X_Ia = base_cell_X_Ia
                next_y_base_cell_X_Ia = y_base_cell_X_Ia
                y_base_cell_X_Ia = base_cell_X_Ia
            else:
                # Next row is even (change y_base_cell_X_Ia to a cell above base cell)
                base_cell_X_Ia = self._get_ul_X_Ia(self._get_ur_X_Ia(next_y_base_cell_X_Ia))
                next_base_cell_X_Ia = base_cell_X_Ia
                next_y_base_cell_X_Ia = y_base_cell_X_Ia
                y_base_cell_X_Ia = base_cell_X_Ia

    k3d_mesh = {}
    k3d_wireframe = {}
    k3d_labels = {}

    def update_plot(self, pb):
        sol = self.sol
        if self.k3d_mesh:
            pass
            # self.k3d_mesh['X_Ia'].vertices = self.X_Ia.astype(np.float32)
            # self.k3d_mesh['br_X_Ia'].vertices = self._get_br_X_Ia(self.X_Ia,
            #                                                      self.rot_br if self.investigate_rot else -sol[
            #                                                          0]).astype(np.float32)
            # self.k3d_mesh['ur_X_Ia'].vertices = self._get_ur_X_Ia(self.X_Ia,
            #                                                      self.rot_ur if self.investigate_rot else -sol[
            #                                                          1]).astype(np.float32)
            # self.k3d_wireframe['X_Ia'].vertices = self.X_Ia.astype(np.float32)
            # self.k3d_wireframe['br_X_Ia'].vertices = self._get_br_X_Ia(self.X_Ia,
            #                                                           self.rot_br if self.investigate_rot else -sol[
            #                                                               0]).astype(np.float32)
            # self.k3d_wireframe['ur_X_Ia'].vertices = self._get_ur_X_Ia(self.X_Ia,
            #                                                           self.rot_ur if self.investigate_rot else -sol[
            #                                                               1]).astype(np.float32)
        else:
            self.setup_plot(pb)

    def add_cell_to_pb(self, pb, X_Ia, I_Fi, obj_name):
        plot = pb.plot_fig

        wb_mesh = k3d.mesh(X_Ia.astype(np.float32),
                           I_Fi.astype(np.uint32),
                           opacity=0.8,
                           color=0x999999,
                           side='double')
        rand_color = random.randint(0, 0xFFFFFF)
        plot += wb_mesh

        self.k3d_mesh[obj_name] = wb_mesh

        # wb_points = k3d.points(X_Ia.astype(np.float32),
        #                          color=0x999999,
        #                        point_size=100)
        # plot +=wb_points

        if self.show_node_labels:
            texts = []
            for I, X_a in enumerate(X_Ia):
                k3d_text = k3d.text('%g' % I, tuple(X_a), label_box=False, size=0.8, color=rand_color)
                plot += k3d_text
                texts.append(k3d_text)
            self.k3d_labels[obj_name] = texts

        wb_mesh_wireframe = k3d.mesh(X_Ia.astype(np.float32),
                                     I_Fi.astype(np.uint32),
                                     color=0x000000,
                                     wireframe=True)
        plot += wb_mesh_wireframe
        self.k3d_wireframe[obj_name] = wb_mesh_wireframe


    def add_cell(self, plot, X_Ia, I_Fi):
        wb_mesh = k3d.mesh(X_Ia.astype(np.float32),
                           I_Fi.astype(np.uint32),
                           opacity=0.8,
                           color=0x999999,
                           side='double')
        rand_color = random.randint(0, 0xFFFFFF)
        plot += wb_mesh

        # wb_points = k3d.points(X_Ia.astype(np.float32),
        #                          color=0x999999,
        #                        point_size=100)
        # plot +=wb_points

        if self.show_node_labels:
            for I, X_a in enumerate(X_Ia):
                k3d_text = k3d.text('%g' % I, tuple(X_a), label_box=False, size=0.8, color=rand_color)
                plot += k3d_text

        wb_mesh_wireframe = k3d.mesh(X_Ia.astype(np.float32),
                                     I_Fi.astype(np.uint32),
                                     color=0x000000,
                                     wireframe=True)
        plot += wb_mesh_wireframe