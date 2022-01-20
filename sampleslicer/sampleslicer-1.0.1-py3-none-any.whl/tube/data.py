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
import matplotlib as mpl
from matplotlib.patches import Rectangle
from matplotlib.transforms import BboxTransform, Bbox, TransformedBbox
import math
from math import floor, ceil

import json
from io import StringIO
import logging

class Tube(list):
    """ Represents a tube to be manipulated. May be serialized or imported from
    a json file.

    rectangle storage:
    ------------------
    time0
       - slice0 - rect0
       - sliceN - rect1
    timeN
       - slice0 - rect0
       - sliceN - rect1

    """
    # data structures/indexes for specific tubes
    angle = 0.0
    ax = None

    actual_depth = -1  # default value but can be overridden using setter
    loaded_depth = -1
    rotated_depth = -1

    # tubes are represented here using center points, width, and height. the
    # overall shape represented is scaled up by 2 to get the full rectangle.

    #
    # stateful tube/rect manipulation (create, select, update)
    #
    def __init__(self, new_rect, new_rect2, angle=0.0, ax=None):
        self.append(new_rect)
        self.append(new_rect2)
        self.angle = angle

        if ax is not None:
            self.set_ax(ax)

        self.set_defaults()

        self.set_tube_transform()

    def set_defaults(self):
        for rect in self:
            rect.set_alpha(0.2)
            rect.set_color('b')
            rect.set_zorder(2)

    @staticmethod
    def set_depth(actual_depth, loaded_depth):
        Tube.actual_depth = actual_depth
        Tube.loaded_depth = loaded_depth

    #
    # math stuff
    #

    # return axis-angle representation for current tube orientation
    def get_axisangle(self):
        d = Tube.loaded_depth
        theta = self.angle
        v = [int(self[1].xy[1] - self[0].xy[1]),
             int(self[1].xy[0] - self[0].xy[0]), int(d / 2)]
        v_np = np.array(v)

        return v_np, theta

    def get_transformed_coords(self, rect_idx):
        rect = self[rect_idx]
        xform = self.trafos(rect_idx)

        coords = xform.transform((rect.get_height(), rect.get_width()))
        return coords

    # returns the vector representing the rectangle
    def get_transformed_rect_vect(self):
        rect = self[1]
        xform = self.trafos[1]

        #rect_vect = (rect.get_height(), rect.get_width(), Tube.loaded_depth/2)
        center_coords = rect.xy
        center_xform = xform.transform((center_coords[0], center_coords[1]))
        rect_vec_xform = xform.transform(
            (center_coords[0], center_coords[1] + rect.get_width()))

        return (rect_vec_xform[0] - center_xform[0],
                rect_vec_xform[1] - center_xform[1])

    # union 2d rectangles to get the crop region after applying transform
    # returns (x, y, z), (w, h, d)
    def get_3d_region(self, rotate=True):
        rect0 = self[0]
        rect1 = self[1]

        trafos = self.get_rect_transforms(rotate)

        bbox_t = []

        # get standard bounding box and translate it (without display)
        for idx, rect in enumerate(self):
            bbox = rect.get_bbox()
            bbox_t.append(TransformedBbox(bbox, trafos[idx]).get_points())

            logging.debug(bbox_t[idx])

        # get data for both bounding boxes of rotated rectangles
        ((b0x0, b0y0), (b0x1, b0y1)) = bbox_t[0]
        ((b1x0, b1y0), (b1x1, b1y1)) = bbox_t[1]

        logging.debug("Bounding box 1 & 2 coordinates:")
        logging.debug(((b0x0, b0y0), (b0x1, b0y1)))
        logging.debug(((b1x0, b1y0), (b1x1, b1y1)))

        # get union of bounding boxes
        x0 = min(b0x0, b1x0)
        y0 = min(b0y0, b1y0)
        x1 = max(b0x1, b1x1)
        y1 = max(b0y1, b1y1)

        # calculate width and height
        w = x1 - x0
        h = y1 - y0

        # cast to int to get manipulable pixels
        return ((int(y0), int(x0), 0), (int(ceil(h)),
                                        int(ceil(w)), Tube.loaded_depth))

    # get vector of euler angles for the tube rotation
    def get_z_angles(self):
        # compute vector from center of start to center of end
        vec = np.array[self[0].xy, self[1].xy]

        # normalize vector
        norm_vec = vec / np.linalg.norm(vec)

        return norm_vec

    #
    # import  / export support
    #

    @staticmethod
    def import_dict(tube_dict):
        td = tube_dict
        logging.debug(td)
        return Tube.new_tube_from_rect(
            td['pt0'], td['pt1'], td['width'], td['height'], td['angle'])

    def serialize_dict(self):
        tube_dict = {}
        #tube_dict['tubeindex'] = self.index

        for idx, rect in enumerate(self):
            tube_dict['pt{}'.format(idx)] = rect.xy

        tube_dict['width'] = rect.get_width() * 2  # total width
        tube_dict['height'] = rect.get_height() * 2  # total height
        tube_dict['angle'] = float(self.angle)
        #tube_dict['length'] = float(self.angle)

        return tube_dict

    # since we're storing and managing quarter definition rectangles we want to
    # scale them up before presenting to the user because matplotlib rectangle
    # patches only use xy, width, height (we are not using built-in angle)
    def set_tube_transform(self):
        self.trafos = self.get_rect_transforms()
    #    trafo = mpl.transforms.Affine2D().translate(  \
    #                     -1*(x+width/2),-1*(y+height/2)
    #                ).scale(2).rotate_around(0,0,np.deg2rad(self.angle)).translate(x,y)
        if self.ax is not None:
            for idx, rect in enumerate(self):
                rect.set_transform(self.trafos[idx] + self.ax.transData)

    def get_rect_transforms(self, rotate=True):
        transforms = []
        for rect in self:
            x = rect.xy[0]
            y = rect.xy[1]
            width = rect.get_width()
            height = rect.get_height()

            # 1. translate to origin
            # 2. scale
            # 3. rotate
            # 4. translate back
            origin_x_dist = x + width / 2
            origin_y_dist = y + height / 2

            rotate_angle = np.deg2rad(self.angle)

            if rotate == True:
                trafo = mpl.transforms.Affine2D().translate(-1 * origin_x_dist, -1 * origin_y_dist). \
                    scale(2).\
                    rotate_around(0, 0, rotate_angle).\
                    translate(x, y)
            else:
                trafo = mpl.transforms.Affine2D().translate(-1 * origin_x_dist, -1 * origin_y_dist). \
                    scale(2).\
                    translate(x, y)
            transforms.append(trafo)

        return transforms

    def set_ax(self, ax):
        if ax is not None:
            self.ax = ax
            # use transform without angle (move to origin, scale, move back)
            for rect in self:
                current_rect = rect
                x = current_rect.xy[0]
                y = current_rect.xy[1]
                height = current_rect.get_height()
                width = current_rect.get_width()

            self.set_tube_transform()

    #
    # tube creation methods (ui vs. deserialization)
    #

    @staticmethod
    # create a rectangle (used during deserialization)
    # xy1 - center point of start rectangle
    # xy2 - center point of end rectangle
    def new_tube_from_rect(xy1, xy2, width, height, angle, ax=None):
        width = width / 2
        height = height / 2
        #x += width
        #y += height
        angle = angle

        # not using built-in angle
        new_rect = Rectangle(xy1, width, height, angle=0.0)
        new_rect2 = Rectangle(xy2, width, height, angle=0.0)

        return Tube(new_rect, new_rect2, angle, ax=ax)

        # add callback for new rectangle

    # creates a compact rectangle from a larger rectangle (typically drawn on
    # the screen)
    @staticmethod
    def new_tube(x1, y1, x2, y2, angle=0.0, ax=None):
        width = x2 - x1
        height = y2 - y1
        angle = 0.0

        new_rect = Rectangle(
            (x1 + width / 2,
             y1 + height / 2),
            width / 2,
            height / 2,
            angle=0.0)
        new_rect2 = Rectangle(
            (x1 + width / 2,
             y1 + height / 2),
            width / 2,
            height / 2,
            angle=0.0)

        return Tube(new_rect, new_rect2, angle=angle, ax=ax)

    #
    # tube manipulation functions
    #

    # translate one end independently of the other
    def translate_end(self, dir, pos, pix=1):
        #logging.debug("translating rect")
        current_rect = self[pos]

        x = current_rect.xy[0]
        y = current_rect.xy[1]
        if dir == "up":
            current_rect.xy = (x, y - pix)
        elif dir == "down":
            current_rect.xy = (x, y + pix)
        elif dir == "left":
            current_rect.xy = (x - pix, y)
        elif dir == "right":
            current_rect.xy = (x + pix, y)

        self.rotate_rect()

    # always expand both ends
    def expand_rect(self, dir):
        for current_rect in self:
            if dir == "up":
                current_rect.set_height(current_rect.get_height() + 10)
            elif dir == "down":
                current_rect.set_height(current_rect.get_height() - 10)
            elif dir == "left":
                current_rect.set_width(current_rect.get_width() - 10)
            elif dir == "right":
                current_rect.set_width(current_rect.get_width() + 10)

        self.rotate_rect()

    # always rotate both ends
    def rotate_rect(self, dir=None, degs=0.1):
        for current_rect in self:
            rotate_angle = float(self.angle)  # np.deg2rad(0.05) # in degrees
            if dir == "clockwise":
                rotate_angle = rotate_angle + degs
            elif dir == "counterclockwise":
                rotate_angle = rotate_angle - degs

            #self.tubeangles[self.selected_tube_idx] = rotate_angle
            self.angle = rotate_angle

            x = current_rect.xy[0]
            y = current_rect.xy[1]
            height = current_rect.get_height()
            width = current_rect.get_width()

            self.set_tube_transform()

    def select(self):
        for rect in self:
            rect.set_color('r')
            rect.set_alpha(0.2)

    # recolor both ends to deselected
    def deselect(self):
        for rect in self:
            rect.set_color('b')
            rect.set_alpha(0.2)

    # send all rectangles to lower z-order (convenience)
    def go_back(self):
        for rect in self:
            rect.set_zorder(1)

    def get_mask(self, shape):
        """Return image mask given by mask creator"""
        h, w = shape
        y, x = np.mgrid[:h, :w]
        points = np.transpose((x.ravel(), y.ravel()))
        mask = self.poly.contains(points)
        return mask.reshape(h, w)

    # def get_angles(self, poly1, poly2):
    # def get_3d_poly(self, poly1, poly2):


# stateful Tube information class
class TubeData():
    microtubes = []  # 2 rectangles per microtube definition
#    tubeangles = []

    selected_tube_idx = -1       # which tube are we looking at?
    #selected_tube = None

    def set_depth(self, actual_depth, loaded_depth):
        Tube.set_depth(actual_depth, loaded_depth)
#        for tube in self.microtubes:
#            tube.set_depth(new_depth)

    def add_new_tube(self, x1, y1, x2, y2, angle=0.0, ax=None):
        new_tube = Tube.new_tube(x1, y1, x2, y2, angle=angle, ax=ax)

        # add new microtube rect
        self.microtubes.append(new_tube)
#        self.tubeangles.append(angle)
        # self.current_rects.append(new_rect)

        return new_tube

    def select_tube(self, tube_idx):
        new_tube = None

        if self.selected_tube_idx != -1:
            self.microtubes[self.selected_tube_idx].deselect()

        self.selected_tube_idx = tube_idx

        # change color of rect
        if self.selected_tube_idx != -1:
            new_tube = self.microtubes[self.selected_tube_idx]
            new_tube.select()

        return new_tube

    # return rect list for a given position (0 or 1)
    def get_rects_at(self, new_position):
        # 0 - rect0
        # 0 < x < 1 : between (interpolate?)
        # 1 - rect1
        rect_list = []

        # if we have initialized the microtube rects at this new location then
        # load them
        if len(self.microtubes) > 0:
            #logging.debug("processing new position {}".format(new_position))
            if new_position == 0:
                rect_list = [rect[int(new_position)]
                             for rect in self.microtubes]
            elif new_position == 1:
                rect_list = [rect[int(new_position)]
                             for rect in self.microtubes]
            else:
                # TODO: interpolate rect (x,y) position from rect[0] and rect[1]
                # can update the transform to temporarily translate them using
                # delta
                rect_list = []  # interpolate if we feel like it

        return rect_list

    def get_tube(self):
        the_rect = None

        # get the currently selected tube
        if len(self.microtubes) > 0 and self.selected_tube_idx != -1:
            the_rect = self.microtubes[self.selected_tube_idx]

        return the_rect

    def import_json(self, tube_data):
        # convert json back to dict
        all_tubes_dict = json.load(tube_data)

        for key in sorted(all_tubes_dict):
            self.microtubes.append(Tube.import_dict(all_tubes_dict[key]))

    def export_json(self, json_file):
        json.dump(self.serialize_dict(), json_file, indent=4, sort_keys=True)

    def print_data(self):
        io = StringIO()
        logging.info(json.dumps(self.serialize_dict()))

    def serialize_dict(self):
        all_tubes_dict = {}

        for idx, tube in enumerate(self.microtubes):
            all_tubes_dict[idx] = tube.serialize_dict()

        # logging.debug(all_tubes_dict)
        return all_tubes_dict

    def set_ax(self, ax):
        self.ax = ax
        for tube in self.microtubes:
            tube.set_ax(ax)
