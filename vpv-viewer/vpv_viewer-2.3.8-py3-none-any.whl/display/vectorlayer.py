from PyQt5 import QtGui
import pyqtgraph as pg
from vpv.common import Orientation
import numpy as np
import math


class VectorLayer(object):
    def __init__(self, viewbox, parent, model):
        # Create dummy vectors
        self.model = model
        self.parent = parent
        self.orientation = self.parent.orientation
        self.slice_change_function = None
        self.arrows = []
        self.viewbox = viewbox
        self.def_field = None
        self.drawn = False
        self.item = None
        self.arrow_angle = 50
        self.plt = pg.PlotItem()
        self.plt.hideAxis('left')
        self.plt.hideAxis('right')
        self.plt.hideAxis('bottom')
        self.plt.hideAxis('top')
        self.vol = None
        self.arrow_color = "22E300"
        self.vec_mag_min = 0.0
        self.vec_mag_max = 5.0

    def set_magnitude_cutoff(self, min_, max_):
        self.vec_mag_min = min_
        self.vec_mag_max = max_
        self.set_slice(self.current_index)

    def register_slice_change_function(self):
        if self.orientation == Orientation.coronal:
            return self.vol.get_coronal
        elif self.orientation == Orientation.sagittal:
            return self.vol.get_sagittal
        elif self.orientation == Orientation.axial:
            return self.vol.get_axial

    def set_volume(self, volname):
        if volname == "None":
            self.volume_label_signal.emit("None")
            self.vol = None
            if self.item:
                self.viewbox.removeItem(self.item)
            return
        self.volume_label_signal.emit(volname)

        self.parent.overlay.set_vector_label(volname)

        self.vol = self.model.getvol(volname)
        orientation = self.parent.orientation
        self.slice_change_function = self.register_slice_change_function()
        self.name = self.vol.name
        dim_len = self.vol.dimension_length(orientation)
        self.current_index = dim_len / 2
        midslice = self.slice_change_function(dim_len / 2)
        self.shape = midslice.shape

        self.plt.hideAxis('left')
        self.plt.hideAxis('right')
        self.plt.hideAxis('bottom')
        self.plt.hideAxis('top')
        self.plt.hideButtons()
        self.plt.setRange(xRange=(0, self.shape[0]), yRange=(0, self.shape[1]))
        # self.plt.yRange(shape[2])
        self.viewbox.addItem(self.plt)

        self.set_orientation()

        self.set_slice(dim_len / 2)

    def set_orientation(self):
        """
        set which 2 axes to take from the 3D vector.
        """
        if self.parent.orientation == Orientation.axial:
            self.vector_axes = (1, 0)
        elif self.parent.orientation == Orientation.coronal:
            self.vector_axes = (0, 2)
        elif self.parent.orientation == Orientation.sagittal:
            self.vector_axes = (1, 2)

    def set_slice(self, index=None, flip=None):
        # The flip has not been tested for vector display and is probably broke
        # if not self.vol:
        #     if self.item:
        #         self.viewbox.removeItem(self.item)
        #     print 'not vol'
        #     return

        if index < 0:
            return
        if not index:
            index = self.current_index
        else:
            self.current_index = index - 1

        c = self.vol.subsampling
        scale = self.vol.scale

        if self.item:
            self.viewbox.removeItem(self.item)

        # Get the slice and 2D vectors for this orientation
        slice_ = self.slice_change_function(index)

        # Get the 2d vector for this plane
        slice_2d_vec = slice_.take(self.vector_axes, axis=2)

        x_points = []
        y_points = []
        connect = []

        for y in range(0, slice_.shape[0] - c, c):
            for x in range(0, slice_.shape[1] -c, c):

                try:

                    subsmapled_box = slice_2d_vec[y: y+c, x: x+c, :]
                except IndexError:
                    print("fell off")
                else:
                    x1 = x + (c/2)
                    y1 = y + (c/2)

                    x_magnitude, y_magnitude = np.mean(subsmapled_box, axis=(0, 1))
                    magnitude = np.linalg.norm((x_magnitude, y_magnitude))
                    if magnitude < self.vec_mag_min:
                        continue
                    if self.orientation == Orientation.axial:
                        x_magnitude, y_magnitude = self.rotate_vector((x_magnitude, y_magnitude), -90.0)

                    x_points.append(x1)
                    y_points.append(y1)
                    connect.append(1)

                    # Draw a line to end of arrow
                    x2 = x1 + (x_magnitude * scale)
                    y2 = y1 + (y_magnitude * scale)

                    x_points.append(x2)
                    y_points.append(y2)
                    connect.append(1)

                    arrow_Xs, arrow_ys = self.draw_arrow_head(x2, x1, y2, y1)

                    x_points.append(arrow_Xs[0])
                    y_points.append(arrow_ys[0])
                    connect.append(0)

                    x_points.append(arrow_Xs[1])
                    y_points.append(arrow_ys[1])
                    connect.append(1)

                    # Back to arrow tip
                    x_points.append(x2)
                    y_points.append(y2)
                    connect.append(0)

        path = pg.arrayToQPath(np.array(x_points), np.array(y_points), np.array(connect))
        self.item = QtGui.QGraphicsPathItem(path)
        self.item.setPen(pg.mkPen({'color': self.arrow_color, 'width': 1}))
        self.viewbox.addItem(self.item)

    def rotate_vector(self, vector, theta):
        x_temp = np.copy(vector[0])
        theta = math.radians(theta)
        x = vector[0] * math.cos(theta) - vector[1] * math.sin(theta)
        y = x_temp * math.sin(theta) + vector[1] * math.cos(theta)
        return x, y

    def draw_arrow_head(self, tipX, tailX, tipY, tailY):
        """
        This is the function that needs speeding up
        :param tipX:
        :param tailX:
        :param tipY:
        :param tailY:
        :return:
        """
        arrowLength = 1
        dx = tipX - tailX
        dy = tipY - tailY

        theta = math.atan2(dy, dx)

        rad = math.radians(20)
        x = tipX - arrowLength * math.cos(theta + rad)
        y = tipY - arrowLength * math.sin(theta + rad)


        phi2 = math.radians(-20)
        x2 = tipX - arrowLength * math.cos(theta + phi2)
        y2 = tipY - arrowLength * math.sin(theta + phi2)

        arrowYs = []
        arrowYs.append(y)
        arrowYs.append(y2)

        arrowXs = []
        arrowXs.append(x)
        arrowXs.append(x2)

        return arrowXs, arrowYs

    def set_subsampling(self, value):
        self.vol.subsampling = int(value)
        self.update()

    def set_scale(self, value):
        self.vol.scale = int(value)
        self.update()

    def set_arrow_color(self, color):
        self.arrow_color = color

    def clear(self):
        pass

    def update(self):
        self.set_orientation()
        self.set_slice(self.current_index)

    def reload(self):
        pass
