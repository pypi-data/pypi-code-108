import bmcs_utils.api as bu

from bmcs_shell.folding.geometry.wb_cell import WBCell
from bmcs_shell.folding.geometry.wb_cell_5p import WBElem5Param
from bmcs_shell.folding.geometry.wb_cell_5p_v2 import \
    WBElem5ParamV2
import traits.api as tr
import numpy as np
from scipy.optimize import minimize
import k3d
import random

class WBNumericalTessellation(WBElem5ParamV2):
    name = 'WB Numerical Tessellation'

    # wb_cell = bu.Instance(WBCell, (), GEO=True)
    # X_Ia = tr.DelegatesTo('wb_cell')
    # I_Fi = tr.DelegatesTo('wb_cell')
    # tree = ['wb_cell']

    plot_backend = 'k3d'

    rot_br = bu.Float(0.5)
    rot_ur = bu.Float(0.5)
    investigate_rot = bu.Bool

    # show_wireframe = bu.Bool(True, GEO=True)
    show_node_labels = bu.Bool(False, GEO=True)

    br_X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    # @tr.cached_property
    def _get_br_X_Ia(self):
        return self.get_cell_matching_v1_to_v2(self.X_Ia, np.array([4, 6]), np.array([5, 1]))

    ur_X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    # @tr.cached_property
    def _get_ur_X_Ia(self):
        return self.get_cell_matching_v1_to_v2(self.X_Ia, np.array([6, 2]), np.array([3, 5]))

    ipw_view = bu.View(
        *WBElem5ParamV2.ipw_view.content,
        # *wb_cell.ipw_view.content,

        # bu.Item('n_x', latex=r'n_x'),
        # bu.Item('n_y', latex=r'n_y'),
        bu.Item('rot_br', latex=r'rot~br', editor=bu.FloatRangeEditor(low=0, high=2 * np.pi, n_steps=150,
                                                                      continuous_update=True)),
        bu.Item('rot_ur', latex=r'rot~ur', editor=bu.FloatRangeEditor(low=0, high=2 * np.pi, n_steps=150,
                                                                      continuous_update=True)),
        bu.Item('investigate_rot'),
        # bu.Item('show_wireframe'),
        bu.Item('show_node_labels'),
    )

    # Source:
    # https://github.com/nghiaho12/rigid_transform_3D
    # http://nghiaho.com/?page_id=671
    # Input: expects 3xN matrix of points
    # Returns R,t
    # R = 3x3 rotation matrix
    # t = 3x1 column vector

    def get_best_rot_and_trans_3d(self, A, B):
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

    def get_rot_matrix_around_vector(self, v, angle):
        c = np.cos(angle)
        s = np.sin(angle)
        v_norm = v / np.sqrt(sum(v * v))

        # See: Rotation matrix from axis and angle (https://en.wikipedia.org/wiki/Rotation_matrix)
        cross_product_matrix = np.cross(v_norm, np.identity(v_norm.shape[0]) * -1)
        return c * np.identity(3) + s * cross_product_matrix + (1 - c) * np.outer(v_norm, v_norm)

    def get_cell_matching_v1_to_v2(self, X_Ia, v1_ids, v2_ids):
        v1_2a = np.array([X_Ia[v1_ids[0]], X_Ia[v1_ids[1]]])
        v2_2a = np.array([X_Ia[v2_ids[0]], X_Ia[v2_ids[1]]])
        rot, trans = self.get_best_rot_and_trans_3d(v1_2a.T, v2_2a.T)
        translated_X_Ia = trans.flatten() + np.einsum('ba, Ia -> Ib', rot, X_Ia)

        ####### Rotating around vector #######
        # Bringing back to origin (because rotating is around a vector originating from origin)
        translated_X_Ia1 = translated_X_Ia - translated_X_Ia[v1_ids[1]]

        # Rotating
        rot_around_v1 = self.get_rot_matrix_around_vector(translated_X_Ia1[v1_ids[0]] - translated_X_Ia1[v1_ids[1]], np.pi * 1)
        translated_X_Ia1 = np.einsum('ba, Ia -> Ib', rot_around_v1, translated_X_Ia1)

        # Bringing back in position
        return translated_X_Ia1 + translated_X_Ia[v1_ids[1]]

    def rotate_cell(self, cell_X_Ia, v1_ids, angle=np.pi):
        ####### Rotating around vector #######
        # Bringing back to origin (because rotating is around a vector originating from origin)
        cell_X_Ia_copy = np.copy(cell_X_Ia)
        cell_X_Ia = cell_X_Ia_copy - cell_X_Ia_copy[v1_ids[1]]

        # Rotating
        rot_around_v1 = self.get_rot_matrix_around_vector(cell_X_Ia[v1_ids[0]] - cell_X_Ia[v1_ids[1]], angle)
        cell_X_Ia = np.einsum('ba, Ia -> Ib', rot_around_v1, cell_X_Ia)

        # Bringing back in position
        return cell_X_Ia + cell_X_Ia_copy[v1_ids[1]]

    def rotate_and_get_diff(self, rotations):
        br_X_Ia_rot = self.rotate_cell(self.br_X_Ia, np.array([4, 6]), rotations[0])
        ur_X_Ia_rot = self.rotate_cell(self.ur_X_Ia, np.array([6, 2]), rotations[1])
        diff = ur_X_Ia_rot[1] - br_X_Ia_rot[3]
        dist = np.sqrt(np.sum(diff * diff))
        #     print('dist=', dist)
        return dist

    sol = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_sol(self):
        return self.minimize_dist()

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

    def setup_plot(self, pb):
        pb.clear_fig()
        sol = self.sol
        X_Ia = self.X_Ia
        I_Fi = self.I_Fi
        self.add_cell_to_pb(pb, X_Ia, I_Fi, 'X_Ia')
        self.add_cell_to_pb(pb, self.rotate_cell(self.br_X_Ia, np.array([4, 6]), sol[0]), I_Fi, 'br_X_Ia')
        self.add_cell_to_pb(pb, self.rotate_cell(self.ur_X_Ia, np.array([6, 2]), sol[1]), I_Fi, 'ur_X_Ia')

    k3d_mesh = {}
    k3d_wireframe = {}
    k3d_labels = {}

    def update_plot(self, pb):
        sol = self.sol
        if self.k3d_mesh:
            self.k3d_mesh['X_Ia'].vertices = self.X_Ia.astype(np.float32)
            self.k3d_mesh['br_X_Ia'].vertices = self.rotate_cell(self.br_X_Ia, np.array([4, 6]),
                                                                 self.rot_br if self.investigate_rot else sol[
                                                                     0]).astype(np.float32)
            self.k3d_mesh['ur_X_Ia'].vertices = self.rotate_cell(self.ur_X_Ia, np.array([6, 2]),
                                                                 self.rot_ur if self.investigate_rot else sol[
                                                                     1]).astype(np.float32)
            self.k3d_wireframe['X_Ia'].vertices = self.X_Ia.astype(np.float32)
            self.k3d_wireframe['br_X_Ia'].vertices = self.rotate_cell(self.br_X_Ia, np.array([4, 6]),
                                                                      self.rot_br if self.investigate_rot else sol[
                                                                          0]).astype(np.float32)
            self.k3d_wireframe['ur_X_Ia'].vertices = self.rotate_cell(self.ur_X_Ia, np.array([6, 2]),
                                                                      self.rot_ur if self.investigate_rot else sol[
                                                                          1]).astype(np.float32)
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