#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
import gr3
import glfw
from OpenGL.GL import glEnable, glClear, glViewport, GL_DEPTH_BUFFER_BIT, GL_COLOR_BUFFER_BIT, GL_MULTISAMPLE

from pyflosic2 import parameters
from pyflosic2.io.flosic_io import atoms_from_xyz
from pyflosic2.atoms.atoms import Atoms, symbol2number
from pyflosic2.atoms.bonds import Bonds
from pyflosic2.atoms.bondorder import get_guess_bond_order

import numpy as np
import numpy.linalg as la

# Ref.:
#       - find events (mouse, key press etc)
#         https://github.com/FlorianRhiem/pyGLFW/blob/master/glfw/GLFW.py
#       - wx
#         https://gr-framework.org/tutorials/gr3_wx.html
# NOTE: the core is mogli
#       - [14.05.2021]: rewrite mogli as class, remove global variables

# Atom color rgb tuples (used for rendering, may be changed by users)
ATOM_COLORS = np.array([(0, 0, 0),  # Avoid atomic number to index conversion
                        (255, 255, 255), (217, 255, 255), (204, 128, 255),
                        (194, 255, 0), (255, 181, 181), (144, 144, 144),
                        (48, 80, 248), (255, 13, 13), (144, 224, 80),
                        (179, 227, 245), (171, 92, 242), (138, 255, 0),
                        (191, 166, 166), (240, 200, 160), (255, 128, 0),
                        (255, 255, 48), (31, 240, 31), (128, 209, 227),
                        (143, 64, 212), (61, 225, 0), (230, 230, 230),
                        (191, 194, 199), (166, 166, 171), (138, 153, 199),
                        (156, 122, 199), (224, 102, 51), (240, 144, 160),
                        (80, 208, 80), (200, 128, 51), (125, 128, 176),
                        (194, 143, 143), (102, 143, 143), (189, 128, 227),
                        (225, 161, 0), (166, 41, 41), (92, 184, 209),
                        (112, 46, 176), (0, 255, 0), (148, 255, 255),
                        (148, 224, 224), (115, 194, 201), (84, 181, 181),
                        (59, 158, 158), (36, 143, 143), (10, 125, 140),
                        (0, 105, 133), (192, 192, 192), (255, 217, 143),
                        (166, 117, 115), (102, 128, 128), (158, 99, 181),
                        (212, 122, 0), (148, 0, 148), (66, 158, 176),
                        (87, 23, 143), (0, 201, 0), (112, 212, 255),
                        (255, 255, 199), (217, 225, 199), (199, 225, 199),
                        (163, 225, 199), (143, 225, 199), (97, 225, 199),
                        (69, 225, 199), (48, 225, 199), (31, 225, 199),
                        (0, 225, 156), (0, 230, 117), (0, 212, 82),
                        (0, 191, 56), (0, 171, 36), (77, 194, 255),
                        (77, 166, 255), (33, 148, 214), (38, 125, 171),
                        (38, 102, 150), (23, 84, 135), (208, 208, 224),
                        (255, 209, 35), (184, 184, 208), (166, 84, 77),
                        (87, 89, 97), (158, 79, 181), (171, 92, 0),
                        (117, 79, 69), (66, 130, 150), (66, 0, 102),
                        (0, 125, 0), (112, 171, 250), (0, 186, 255),
                        (0, 161, 255), (0, 143, 255), (0, 128, 255),
                        (0, 107, 255), (84, 92, 242), (120, 92, 227),
                        (138, 79, 227), (161, 54, 212), (179, 31, 212),
                        (179, 31, 186), (179, 13, 166), (189, 13, 135),
                        (199, 0, 102), (204, 0, 89), (209, 0, 79),
                        (217, 0, 69), (224, 0, 56), (230, 0, 46),
                        (235, 0, 38), (255, 0, 255), (255, 0, 255),
                        (255, 0, 255), (255, 0, 255), (255, 0, 255),
                        (255, 0, 255), (255, 0, 255), (255, 0, 255),
                        (255, 0, 255)], dtype=np.float32) / 255.0

# Atom valence radii in Å (used for bond calculation)
ATOM_VALENCE_RADII = np.array([220,  # Avoid atomic number to index conversion
                               230, 930, 680, 350, 830, 680, 680, 680, 640,
                               1120, 970, 1100, 1350, 1200, 750, 1020, 990,
                               1570, 1330, 990, 1440, 1470, 1330, 1350, 1350,
                               1340, 1330, 1500, 1520, 1450, 1220, 1170, 1210,
                               1220, 1210, 1910, 1470, 1120, 1780, 1560, 1480,
                               1470, 1350, 1400, 1450, 1500, 1590, 1690, 1630,
                               1460, 1460, 1470, 1400, 1980, 1670, 1340, 1870,
                               1830, 1820, 1810, 1800, 1800, 1990, 1790, 1760,
                               1750, 1740, 1730, 1720, 1940, 1720, 1570, 1430,
                               1370, 1350, 1370, 1320, 1500, 1500, 1700, 1550,
                               1540, 1540, 1680, 1700, 2400, 2000, 1900, 1880,
                               1790, 1610, 1580, 1550, 1530, 1510, 1500, 1500,
                               1500, 1500, 1500, 1500, 1500, 1500, 1600, 1600,
                               1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600,
                               1600, 1600, 1600, 1600, 1600, 1600],
                              dtype=np.float32) / 1000.0
# Prevent unintentional changes
ATOM_VALENCE_RADII.flags.writeable = False

# Atom radii in Å (used for rendering, scaled down by factor 0.4, may be
# changed by users)
ATOM_RADII = np.array(ATOM_VALENCE_RADII, copy=True) * 0.4


class SVIEW():
    """
        Simplified molecular viewer (sview)
        -----------------------------------
        Based on mogli.py, gr, gr3, OpenGL.
        Allows to visualize Nuclei as well as FODs.
        Added bonds based on FODs.

        References:
        -----------
                - [1] https://github.com/FlorianRhiem/mogli
                - [2] https://github.com/sciapp/python-gr/blob/master/gr3/__init__.py

        Parameters
        ----------
        atoms: Atoms(), atoms object/instance
    """

    def __init__(self,
                 p,
                 atoms,
                 width=500,
                 height=500,
                 show_bonds=True,
                 bonds_method='radii',
                 bonds_param=None,
                 camera=None,
                 title='sview',
                 radii=ATOM_RADII,
                 color=ATOM_COLORS):
        self.p = p
        self.atoms = atoms
        self.atoms.positions -= np.mean(self.atoms.positions, axis=0)
        # Shift positions
        #self.bonds = Bonds(self.p, self.atoms)
        #self.bonds.kernel(eps_val=eps_val, eps_cor=eps_cor)
        self.title = title
        self.width = width
        self.height = height
        self.show_bonds = show_bonds
        self.bond_method = bonds_method
        self.bonds_param = bonds_param
        self._mouse_dragging = False
        self._previous_mouse_position = None
        self._camera = camera
        self.radii = radii
        self.color = color
        self.show()

    def _mouse_move_callback(self, window, x, y):
        if self._mouse_dragging and self._camera is not None:
            width, height = glfw.get_window_size(window)
            dx = (x - self._previous_mouse_position[0]) / width
            dy = (y - self._previous_mouse_position[1]) / height
            rotation_intensity = la.norm((dx, dy)) * 2
            eye, center, up = self._camera
            camera_distance = la.norm(center - eye)
            forward = (center - eye) / camera_distance
            right = np.cross(forward, up)
            rotation_axis = (up * dx + right * dy)
            rotation_matrix = self._create_rotation_matrix(-rotation_intensity,
                                                           rotation_axis[0],
                                                           rotation_axis[1],
                                                           rotation_axis[2])
            forward = np.dot(rotation_matrix, forward)
            up = np.dot(rotation_matrix, up)
            eye = center - forward * camera_distance
            self._camera = eye, center, up
            self._previous_mouse_position = (x, y)

    def show(self):
        """
            Show
            ----
            Show the atoms (Nuclei + FODs) and bonds.
        """
        atoms = self.atoms
        atoms.positions -= np.mean(atoms.positions, axis=0)
        self.max_atom_distance = np.max(la.norm(atoms.positions, axis=0))
        self.camera_distance = -self.max_atom_distance * 2.5

        # If GR3 was initialized earlier, it would use a different context, so
        # it will be terminated first.
        gr3.terminate()

        # Initialize GLFW and create an OpenGL context
        glfw.init()
        # Sample influences the quality of the exported png
        # 16 is the orginal value.
        # I increased it to 64.
        glfw.window_hint(glfw.SAMPLES, 64)
        window = glfw.create_window(self.width, self.height, self.title, None, None)
        glfw.make_context_current(window)
        glEnable(GL_MULTISAMPLE)

        # Set up the camera (it will be changed during mouse rotation)
        if self._camera is None:
            self._zoom()

        # Create the GR3 scene
        gr3.setbackgroundcolor(255, 255, 255, 0)

        # Draw the scene (molecule, bonds)
        self._create_gr3_scene(atoms, self.show_bonds)
        if self.show_bonds:
            self._draw_bonds()

        # Configure GLFW
        glfw.set_cursor_pos_callback(window, self._mouse_move_callback)
        glfw.set_mouse_button_callback(window, self._mouse_click_callback)
        glfw.set_key_callback(window, self._key_callback)
        glfw.swap_interval(1)

        # Start the GLFW main loop
        while not glfw.window_should_close(window):
            glfw.poll_events()
            width, height = glfw.get_window_size(window)
            glViewport(0, 0, width, height)
            self._set_gr3_camera()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            gr3.drawimage(0, width, 0, height,
                          width, height, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)
            glfw.swap_buffers(window)
        glfw.terminate()
        gr3.terminate()

    def _zoom(self, zoom=1):
        """
            Zoom
            ----
            Will be triggered by key events (up,down,numblock-PLUS,numblock-MINUS).

            Input
            -----
            zoom: float(), scaling value for zoom
        """

        camera_distance = self.camera_distance * zoom
        camera = ((0, 0, camera_distance),
                  (0, 0, 0),
                  (0, 1, 0))
        camera = np.array(camera)
        self._camera = camera
        self.camera_distance = camera_distance

    def _set_gr3_camera(self):
        """
            Set the GR3 camera,
            -------------------
            Set the GR3 camera, using the global _camera variable.
        """
        eye, center, up = self._camera
        gr3.cameralookat(eye[0], eye[1], eye[2],
                         center[0], center[1], center[2],
                         up[0], up[1], up[2])

    def _create_gr3_scene(self, atoms, show_bonds=True):
        """
            Create the GR3 scene
            --------------------
            Create the GR3 scene from the provided molecule and - if show_bonds is
            True (default) - the atomic bonds in the molecule.
        """
        gr3.clear()
        num_atoms = len(atoms.symbols)
        color_numbers = []
        radii_numbers = []
        for s in atoms.symbols:
            # Nuclei color
            if s != atoms._elec_symbols[0] and s != atoms._elec_symbols[1]:
                color_numbers.append(symbol2number[s])
                radii_numbers.append(symbol2number[s])
            # FOD1 color: green (17), size as H
            if s == atoms._elec_symbols[0]:
                color_numbers.append(17)
                radii_numbers.append(1)
            # FOD2 color: red (26), size a bit smaller then H
            # - smaller size omits overlapping colors
            #   if a FOD guess is spin paired
            if s == atoms._elec_symbols[1]:
                color_numbers.append(26)
                radii_numbers.append(0)
        gr3.drawspheremesh(num_atoms,
                           atoms.positions,
                           self.color[color_numbers],
                           self.radii[radii_numbers])

    def _mouse_click_callback(self, window, button, status, modifiers):
        """
            Mouse click event handler (GLFW)
            --------------------------------
        """
        if button == glfw.MOUSE_BUTTON_LEFT:
            if status == glfw.RELEASE:
                self._mouse_dragging = False
                self._previous_mouse_position = None
            elif status == glfw.PRESS:
                self._mouse_dragging = True
                self._previous_mouse_position = glfw.get_cursor_pos(window)

    def _key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_KP_SUBTRACT or key == glfw.KEY_UP:
            self._zoom(zoom=-1.1)
        if key == glfw.KEY_KP_ADD or key == glfw.KEY_DOWN:
            self._zoom(zoom=-0.9)
        if key == glfw.KEY_S:
            self._save_png()
        if key == glfw.KEY_H:
            self._save_html()

    def _create_rotation_matrix(self, angle, x, y, z):
        """
            Creates a 3x3 rotation matrix.
        """
        if la.norm((x, y, z)) < 0.0001:
            return np.eye(3, dtype=np.float32)
        x, y, z = np.array((x, y, z)) / la.norm((x, y, z))
        matrix = np.zeros((3, 3), dtype=np.float32)
        cos = np.cos(angle)
        sin = np.sin(angle)
        matrix[0, 0] = x * x * (1 - cos) + cos
        matrix[1, 0] = x * y * (1 - cos) + sin * z
        matrix[0, 1] = x * y * (1 - cos) - sin * z
        matrix[2, 0] = x * z * (1 - cos) - sin * y
        matrix[0, 2] = x * z * (1 - cos) + sin * y
        matrix[1, 1] = y * y * (1 - cos) + cos
        matrix[1, 2] = y * z * (1 - cos) - sin * x
        matrix[2, 1] = y * z * (1 - cos) + sin * x
        matrix[2, 2] = z * z * (1 - cos) + cos
        return matrix

    def _draw_bonds(self):
        # simple distance bond order
        nuclei = self.atoms[[atom.index for atom in self.atoms if atom.symbol not in self.atoms._elec_symbols]]
        nn, bo = get_guess_bond_order(nuclei)
        for i in range(len(nn)): 
            for j in range(len(nn)):
                if bo[i,j] > 0: 
                    num_bonds = 1
                    bond_positions = self.atoms[i].position 
                    bond_directions = self.atoms[j].position - self.atoms[i].position
                    bond_lengths = la.norm(bond_directions)
                    bond_directions /= bond_lengths
                    bond_radii = np.ones(num_bonds, dtype=np.float32) * 0.02
                    bond_colors = np.ones((num_bonds, 3), dtype=np.float32) * 0.3
                    gr3.drawcylindermesh(num_bonds, bond_positions, bond_directions,
                                         bond_colors[0], bond_radii, bond_lengths)
        
        # FLO-SIC bond order 
        ## FOD1
        #if self.bonds.fod1 is not None:
        #    for f in self.bonds.fod1:
        #        if f._info[0] == 'bond-FOD':
        #            num_bonds = 1
        #            bond_positions = f._info[1].position
        #            bond_directions = f._info[2].position - f._info[1].position
        #            bond_lengths = la.norm(bond_directions)
        #            bond_directions /= bond_lengths
        #            bond_radii = np.ones(num_bonds, dtype=np.float32) * 0.02
        #            bond_colors = np.ones((num_bonds, 3), dtype=np.float32) * 0.3
        #            gr3.drawcylindermesh(num_bonds, bond_positions, bond_directions,
        #                                 bond_colors[0], bond_radii, bond_lengths)
        ## FOD2 if unrestricted
        #if self.bonds.fod2 is not None:
        #    for f in self.bonds.fod2:
        #        if f._info[0] == 'bond-FOD':
        #            num_bonds = 1
        #            bond_positions = f._info[1].position
        #            bond_directions = f._info[2].position - f._info[1].position
        #            bond_lengths = la.norm(bond_directions)
        #            bond_directions /= bond_lengths
        #            bond_radii = np.ones(num_bonds, dtype=np.float32) * 0.02
        #            bond_colors = np.ones((num_bonds, 3), dtype=np.float32) * 0.3
        #            gr3.drawcylindermesh(num_bonds, bond_positions, bond_directions,
        #                                 bond_colors[0], bond_radii, bond_lengths)

    def _export(self, file_name):
        """
            Save: current scene (html or png)
            ---------------------------------
        """
        gr3.setquality(gr3.GR3_Quality.GR3_QUALITY_OPENGL_16X_SSAA)
        gr3.export(file_name, self.width, self.height)

    def _save_html(self, file_name='sview.html'):
        """
            Save: current scene as html
            ---------------------------
        """
        self._export(file_name)

    def _save_png(self, file_name='sview.png'):
        """
            Save: current scene as png
            --------------------------
        """
        self._export(file_name)


def GUI(input_data, p=None):
    """
        PyFLOSIC_dev: GUI
         
        | GUI to visualize nuclei as well as
        | classical electron positions, i.e., Fermi-orbital descriptors (FODs).

        Parameters
        ----------
        input_data: str() or Atoms() 
             str(), FLO-SIC xyz file

             Atoms(), Atoms object/instance
        p: Parameters() 
            Parameters object/instance 

        Examples
        --------

        >>> from pyflosic2 import GUI
        >>> from pyflosic2.systems.uflosic_systems import H2O 
        >>> atoms = H2O()  
        >>> GUI(atoms)

    """
    if p is None:
        p = parameters(log_name='GUI.log')
    if isinstance(input_data, str):
        # xyz file case
        atoms = atoms_from_xyz(input_data, verbose=4)
    if isinstance(input_data, Atoms):
        # system case
        atoms = input_data
    SVIEW(p, atoms)


if __name__ == '__main__':
    from pyflosic2.systems.uflosic_systems import H2O  # , COH2, CH4
    atoms = H2O()  # COH2() #CH4()
    sv = SVIEW(atoms)
    # sv.save_html()
    # sv.save_png()
    # commandline usage: python3 view.py [name].xyz
    # import sys
    # f_name = sys.argv[1]
    # GUI(f_name)
