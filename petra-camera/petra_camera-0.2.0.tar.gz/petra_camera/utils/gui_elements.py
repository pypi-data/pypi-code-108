# Created by matveyev at 27.08.2021
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore

from petra_camera.utils.functions import rotate


# ----------------------------------------------------------------------
class ImageMarker(QtCore.QObject):
    """Infinite lines cross
    """

    new_coordinates = QtCore.pyqtSignal(int, int)

    # ----------------------------------------------------------------------
    def __init__(self, x, y, image_view):
        super(ImageMarker, self).__init__()

        self.image_view = image_view

        self._markerV = pg.InfiniteLine(pos=x, movable=True)
        self._markerV.sigPositionChanged.connect(self._new_coordinates)
        self.image_view.addItem(self._markerV, ignoreBounds=True)

        self._markerH = pg.InfiniteLine(pos=y, angle=0, movable=True)
        self._markerH.sigPositionChanged.connect(self._new_coordinates)
        self.image_view.addItem(self._markerH, ignoreBounds=True)

    # ----------------------------------------------------------------------
    def _new_coordinates(self):
        self.new_coordinates.emit(int(self._markerV.pos().x()), int(self._markerH.pos().y()))

    # ----------------------------------------------------------------------
    def setPos(self, x, y):
        """
        """

        self._markerV.sigPositionChanged.disconnect()
        self._markerH.sigPositionChanged.disconnect()
        self._markerV.setPos(x)
        self._markerH.setPos(y)
        self._markerV.sigPositionChanged.connect(self._new_coordinates)
        self._markerH.sigPositionChanged.connect(self._new_coordinates)

    # ----------------------------------------------------------------------
    def setVisible(self, flag):
        """
        """
        self._markerV.setVisible(flag)
        self._markerH.setVisible(flag)

    # ----------------------------------------------------------------------
    def visible(self):
        """
        """
        return self._markerV.isVisible() and self._markerH.isVisible()

    # ----------------------------------------------------------------------
    def delete_me(self):

        self.image_view.removeItem(self._markerH)
        self.image_view.removeItem(self._markerV)

    # ----------------------------------------------------------------------
    def setColor(self, color):

        self._markerH.setPen(pg.mkPen(color))
        self._markerV.setPen(pg.mkPen(color))


# ----------------------------------------------------------------------
class PeakMarker(pg.GraphicsObject):
    """
        Circle object
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PeakMarker, self).__init__()
        pg.GraphicsObject.__init__(self)
        self._picture = QtGui.QPicture()
        self._positions = ()
        self._size = 0

    # ----------------------------------------------------------------------
    def new_peaks(self, positions):
        self._positions = positions
        self._draw()

    # ----------------------------------------------------------------------
    def new_scale(self, picture_w, picture_h):
        self._size = int(0.01*min(picture_w, picture_h))
        self._draw()

    # ----------------------------------------------------------------------
    def _draw(self):

        p = QtGui.QPainter(self._picture)
        p.setPen(pg.mkPen('r', width=2))

        for x, y in self._positions:
            p.drawEllipse(QtCore.QPoint(x, y), self._size, self._size)

        p.end()

    # ----------------------------------------------------------------------
    def paint(self, p, *args):
        p.drawPicture(0, 0, self._picture)

    # ----------------------------------------------------------------------
    def boundingRect(self):
        return QtCore.QRectF(self._picture.boundingRect())


# ----------------------------------------------------------------------
class LineSegmentItem(pg.GraphicsObject):

    def __init__(self, mode, cross_size=1., circle=0.):
        pg.GraphicsObject.__init__(self)
        self._mode = mode
        self._picture = QtGui.QPicture()

        self._scaled_circle_size = 0

        self._line1_end1 = QtCore.QPoint(0, 0)
        self._line1_end2 = QtCore.QPoint(0, 0)
        self._line2_end1 = QtCore.QPoint(0, 0)
        self._line2_end2 = QtCore.QPoint(0, 0)

        self._draw_lines = False
        self._draw_point1 = False
        self._draw_point2 = False

        self._cross_size = cross_size/2
        self._circle_size = circle

        self.generate_picture()

    # ----------------------------------------------------------------------
    def set_pos(self, *argin):
        """

        :param argin:
        :return:
        """
        if self._mode == 'cross':
            # here we get argin[0] - center position
            # here we get argin[1] - line length

            if not (None in argin[0] or None in argin[1]):
                self._line1_end1 = QtCore.QPoint(int(argin[0][0] - argin[1][0]/2), int(argin[0][1]))
                self._line1_end2 = QtCore.QPoint(int(argin[0][0] + argin[1][0]/2), int(argin[0][1]))

                self._line2_end1 = QtCore.QPoint(int(argin[0][0]), int(argin[0][1] - argin[1][1]/2))
                self._line2_end2 = QtCore.QPoint(int(argin[0][0]), int(argin[0][1] + argin[1][1]/2))

                self._draw_lines = True
                self._draw_point1 = False
                self._draw_point2 = False

        else:

            self._draw_lines = True
            self._draw_point1 = False
            self._draw_point2 = False

            if argin[0][0] is not None:
                self._line1_end1 = argin[0][0]
                self._draw_point1 = True
            else:
                self._draw_lines = False

            if argin[0][1] is not None:
                self._line1_end2 = argin[0][1]
                self._draw_point2 = True
            else:
                self._draw_lines = False

            if self._draw_lines:
                center = ((self._line1_end1.x() + self._line1_end2.x()) / 2,
                          (self._line1_end1.y() + self._line1_end2.y()) / 2)

                point = (self._line1_end1.x() * (0.5 + self._cross_size) + self._line1_end2.x() * (0.5 - self._cross_size),
                         self._line1_end1.y() * (0.5 + self._cross_size) + self._line1_end2.y() * (0.5 - self._cross_size))

                p1 = rotate(center, point, 1.57)
                p2 = rotate(center, point, -1.57)

                self._line2_end1 = QtCore.QPoint(p1[0], p1[1])
                self._line2_end2 = QtCore.QPoint(p2[0], p2[1])

        self.generate_picture()

    # ----------------------------------------------------------------------
    def new_scale(self, w, h):
        self._scaled_circle_size = int(self._circle_size*min(w, h))
        self.generate_picture()

    # ----------------------------------------------------------------------
    def generate_picture(self):

        p = QtGui.QPainter(self._picture)
        p.setPen(pg.mkPen('r', width=2, style=QtCore.Qt.DotLine))

        if self._draw_lines:
            # Horizontal
            p.drawLine(self._line1_end1, self._line1_end2)

            # Vertical
            p.drawLine(self._line2_end1, self._line2_end2)

        p.setPen(QtCore.Qt.NoPen)
        p.setBrush(pg.mkBrush('r'))

        if self._draw_point1:
            p.drawEllipse(self._line1_end1, self._scaled_circle_size, self._scaled_circle_size)

        if self._draw_point2:
            p.drawEllipse(self._line1_end2, self._scaled_circle_size, self._scaled_circle_size)

        p.end()

    # ----------------------------------------------------------------------
    def paint(self, p, *args):
        p.drawPicture(0, 0, self._picture)

    # ----------------------------------------------------------------------
    def boundingRect(self):
        return QtCore.QRectF(self._picture.boundingRect())