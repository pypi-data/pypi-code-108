"""
Copyright (C) 2018-2022 John W. Williams

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import quaternion

import matplotlib
import matplotlib.pyplot as pyplot
from scipy.ndimage import affine_transform

from math import sin, cos, sqrt

import gc
import os
import psutil
import logging

from .data import Tube  # for depth storage


class TubeExtractor():
    """ TubeExtractor performs the actual extraction of the sub tube from the
    dataset. This is used for the final run and also for sanity checks during
    the metadata definition.
    """

    def __init__(self, ss, ax=None):
        self.ss = ss
        self.ax = ax
        #self.td = td
        self.process = psutil.Process(os.getpid())

    def display_fixed_tube(self, tube):
        return self.get_fixed_tube(tube, display=True)

    def get_fixed_tube(self, tube, image, display=False):
        #
        # setup
        #

        # logging.debug(tube dimensions)
        # sometimes we need a specific depth for sub-sampling
        d_A = Tube.actual_depth
        d_L = Tube.loaded_depth

        # making the tube, this is used throughout this function
        bbox_region = tube.get_3d_region(rotate=True)
        ((y, x, z), (h, w, d)) = bbox_region

        # define source center of rotation (tube-axis)
        c_in = (int(h / 2), int(w / 2), int((d_L) / 2))  # rotate about center
        logging.debug("Position of rotation center: {}".format(c_in))

        logging.debug("3d region: {}".format(bbox_region))
        logging.debug("Tube dimensions: {}".format(((x, y, z), (w, h, d_L))))
        logging.debug(
            "Current memory used: {} MB".format(
                self.process.memory_info().rss >> 20))

        current_image = image
        if current_image.shape[0] == h and current_image.shape[1] == w:
            # if we were passed in a cropped image we don't need to crop
            tube_crop = image
        else:
            # if we were passed something larger (assume global)
            if x < 0 or y < 0:
                tube_crop = np.zeros(shape=(h, w, d_L), dtype=np.uint8)

                def fix_w(x): return np.abs(x) if x < 0 else 0

                def fix_r(x): return 0 if x < 0 else x

                def fix_rb(x, w): return w - np.abs(x) if x < 0 else w

                x_n = fix_r(x)
                y_n = fix_r(y)
                w_n = fix_rb(x, w)
                h_n = fix_rb(y, h)

                tube_crop[fix_w(y):fix_w(y) +
                          h_n, fix_w(x):fix_w(x) +
                          w_n, z:z +
                          d_L] = current_image[y_n: y_n +
                                               h_n, x_n: x_n +
                                               w_n, z: z +
                                               d_L]
            else:
                tube_crop = current_image[y: y + h, x: x + w, z: z + d_L]

        # display the current view if we're in GUI mode
        if display == True:
            # show pre-crop
            fig, ax = pyplot.subplots(3, 1)
            im = ax[0].imshow(
                tube_crop[:, :, int(Tube.loaded_depth * .9)], cmap='binary_r')
            im = ax[1].imshow(
                tube_crop[:, :, int(Tube.loaded_depth / 2)], cmap='binary_r')
            im = ax[2].imshow(
                tube_crop[:, :, int(Tube.loaded_depth * .1)], cmap='binary_r')

            pyplot.show(block=False)

        logging.debug("Image shape: {}".format(current_image.shape))
        logging.debug(current_image.shape)
        logging.debug("Cropped shape: {}".format(tube_crop.shape))

        #
        # get values needed for computation
        #

        # get the measured rotation angle
        v, theta_pre = tube.get_axisangle()
        norm_v = self.normalize(v)
        logging.debug(
            "Adjusting by v: {} ({}), theta_pre: {}".format(
                v, norm_v, theta_pre))

        # 1. Rotate to fix microtube skew in z-direction
        # q1 = (axis = v X z), (angle = v . z)
        # x,y,z reorient

        # calculate v X z to get axis of rotation
        z_vec = np.array([0., 0., d_A / 2])
        z_vec_norm = z_vec / np.linalg.norm(z_vec)
        rot_vec = np.cross(z_vec_norm, norm_v)
        rot_vec_norm = np.array(self.normalize(rot_vec))

        # 2. calculate angle of rotation between microtube vector and z-axis (in
        # 3d)
        c = np.dot(z_vec, v) / np.linalg.norm(v) / np.linalg.norm(z_vec)
        rot_rad = np.arccos(np.clip(c, -1.0, 1.0))

        # convert axis-angle to quaternion
        qlog = quaternion.from_rotation_vector((rot_rad / 2) * rot_vec_norm)
        q1 = np.exp(qlog)
        logging.debug(
            "1. Vec = {}, Rads = {}, Degs = {}".format(
                rot_vec, rot_rad, np.rad2deg(rot_rad)))
        logging.info(
            "Rotating {} degress to origin, roll of {} degress".format(
                np.rad2deg(rot_rad), theta_pre))
        logging.debug(quaternion.as_rotation_matrix(q1))

        m1 = quaternion.as_rotation_matrix(q1)

        # 3. calculate theta_post by getting the angle between the rotation of the rotation vector (z) and
        # get the target rectangle and get the vector for h/2,w/2 after rotating
        # by theta_pre

        # get the vector for the rotated rectangle (to midpoint) and rotate it
        # to get residual angle
        rotated_rect_vect = tube.get_transformed_rect_vect()
        logging.debug(
            "Rotated rect vect for angle adjustment: {}".format(rotated_rect_vect))
        rot_rect = np.matmul(m1, np.array(
            [rotated_rect_vect[0], rotated_rect_vect[1], d_L / 2]))
        # get the new angle with the z-axis
        rot_rot_rect = np.dot(rot_rect, [0, 0, 1]) / np.linalg.norm(rot_rect)
        theta_post_rad = np.arccos(np.clip(rot_rot_rect, -1.0, 1.0))
        theta_post_deg = np.rad2deg(theta_post_rad)

        logging.debug(
            "Calculated residual roll angle as: {} rad, {} degs".format(
                theta_post_rad, theta_post_deg))

        # 4. Roll by microtube angle theta_pre
        q2 = np.exp(quaternion.quaternion(0, 0, 1)
                    * -1 * np.deg2rad(theta_pre) / 2)
        logging.debug(quaternion.as_rotation_matrix(q2))

        # 5. compute rotation matrix from 3 rotations (order q1, q2, q3)
        m = quaternion.as_rotation_matrix(q1 * q2)

        logging.debug("Using rotation matrix:")
        logging.debug(m)

        # calculate new depth d_dest = | rot_vec * p | where p is the target point
        # this formula uses the bounding box of the rotated rectangles as a
        # reference frame
        pts = [(np.ceil(h / 2), np.ceil(w / 2)), (-h / 2, np.ceil(w / 2)),
               (np.ceil(h / 2), -w / 2), (-h / 2, -w / 2)]
        max_d = 0
        max_ds = []
        for pt in pts:
            # rotate the test points per the computed matrix
            rot_tst = np.matmul(m, np.array([pt[0], pt[1], d_L / 2]))
            pt_d = int(np.ceil(np.linalg.norm(rot_tst)))
            logging.debug(
                "pt_d for {}: {}, pt_d(z): {}".format(
                    pt, pt_d, rot_tst[2]))
            max_ds.append(np.ceil(rot_tst[2]))

        max_ds = np.sort(max_ds)
        max_d = max_ds[3]
        delta_d = max_d - int(d_L / 2)
        logging.debug(
            "max_d/2: {}, d_L/2: {}, Delta d: {}".format(max_d, d_L / 2, delta_d))
        rot_d = int(d_L + 2 * delta_d)  # symmetric rotation
        logging.debug("New depth: {}".format(rot_d))

        tube.rotated_depth = rot_d
        #
        # Set up and execute transform using computed matrix
        #

        transform = m  # use transformation matrix as computed above
#        d = Tube.loaded_depth

        #((y,x,z),(h,w,d)) = tube.get_3d_region(rotate = False)

        # define destination shape based on the original rectangle dimensions
        # (expected after rotation)
        dest_shape = (2 * int(np.ceil(tube[0].get_height())),
                      2 * int(np.ceil(tube[0].get_width())),
                      rot_d)  # bbox rectangle shape

        # define center of transformed object based on anticipated shape
        c_out = (int(0.5 * dest_shape[0]),
                 int(0.5 * dest_shape[1]),
                 int(0.5 * dest_shape[2]))

        # traslate back using transformed computed offset
        offset = c_in - np.dot(transform, c_out)

        logging.debug("Source center: {}".format(c_in))
        logging.debug("Destination shape: {}".format(dest_shape))
        logging.debug("Destination center: {}".format(c_out))

        fixed_tube = affine_transform(tube_crop,
                                      transform,
                                      offset=offset,
                                      output_shape=dest_shape,
                                      order=1,
                                      prefilter=False)

        logging.debug("Transformed shape: {}".format(fixed_tube.shape))
        d_new = fixed_tube.shape[2]

        if display == True:
            # display transformed tube in window
            fig, ax = pyplot.subplots(3, 1)
            im = ax[0].imshow(
                fixed_tube[:, :, int(d_new * .9 - 1)], cmap='binary_r')
            im = ax[1].imshow(fixed_tube[:, :, int(d_new / 2)], cmap='binary_r')
            im = ax[2].imshow(
                fixed_tube[:, :, int(d_new * .1)], cmap='binary_r')

            pyplot.show(block=False)

        return fixed_tube

    def normalize(self, v, tolerance=0.00001):
        mag2 = sum(n * n for n in v)
        if abs(mag2 - 1.0) > tolerance:
            mag = sqrt(mag2)
            v = tuple(n / mag for n in v)
        return v


#        mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(s),
#                            plane_orientation='x_axes',
#                            slice_index=10,
#                        )
#        mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(s),
#                                    plane_orientation='y_axes',
#                                    slice_index=10,
#                                )
#        mlab.outline()
#
