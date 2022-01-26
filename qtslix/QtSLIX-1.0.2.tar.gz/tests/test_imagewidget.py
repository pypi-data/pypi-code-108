import pytest
import numpy
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import qRed, qGreen, qBlue, qAlpha
from PyQt5.QtWidgets import QScrollBar

from QtSLIX import ImageWidget


class TestImageWidget:
    @pytest.mark.parametrize("shapes", [(10, 10), (10, 10, 1)])
    def test_convert_numpy_to_qimage_grayscale(self, shapes):
        # Test for a 2D grayscale image
        image = numpy.zeros(shapes, dtype=float)
        image[0:5, 0:5] = 1

        qimage = ImageWidget.convert_numpy_to_qimage(image)
        assert len(qimage) == 1
        converted_image = qimage[0]
        assert converted_image.width() == 10
        assert converted_image.height() == 10
        assert converted_image.format() == QtGui.QImage.Format_Grayscale8
        for i in range(5):
            for j in range(5):
                assert qRed(converted_image.pixel(i, j)) == 255
                assert qGreen(converted_image.pixel(i, j)) == 255
                assert qBlue(converted_image.pixel(i, j)) == 255

    def test_convert_numpy_to_qimage_rgb(self):
        # Test for a 3D RGB image
        image = numpy.zeros((10, 10, 3), dtype=float)
        image[0:5, 0:5, 0] = 0.5
        image[0:5, 0:5, 1] = 1
        image[0:5, 0:5, 2] = 0.2

        qimage = ImageWidget.convert_numpy_to_qimage(image)
        assert len(qimage) == 1
        converted_image = qimage[0]
        assert converted_image.width() == 10
        assert converted_image.height() == 10
        assert converted_image.format() == QtGui.QImage.Format_RGB888
        for i in range(5):
            for j in range(5):
                assert qRed(converted_image.pixel(i, j)) == 127
                assert qGreen(converted_image.pixel(i, j)) == 255
                assert qBlue(converted_image.pixel(i, j)) == 51

    def test_convert_numpy_to_qimage_rgba(self):
        # Test for a 3D RGB image
        image = numpy.zeros((10, 10, 4), dtype=float)
        image[0:5, 0:5, 0] = 0.5
        image[0:5, 0:5, 1] = 1
        image[0:5, 0:5, 2] = 0.2
        image[0:5, 0:5, 3] = 0.4

        qimage = ImageWidget.convert_numpy_to_qimage(image)
        assert len(qimage) == 1
        converted_image = qimage[0]
        assert converted_image.width() == 10
        assert converted_image.height() == 10
        assert converted_image.format() == QtGui.QImage.Format_RGBA8888
        for i in range(5):
            for j in range(5):
                assert qRed(converted_image.pixel(i, j)) == 127
                assert qGreen(converted_image.pixel(i, j)) == 255
                assert qBlue(converted_image.pixel(i, j)) == 51
                assert qAlpha(converted_image.pixel(i, j)) == 102

    @pytest.mark.parametrize("nmeasurements", [24, 60, 72, 360])
    def test_convert_numpy_to_qimage_measurement(self, nmeasurements):
        image = numpy.zeros((1, 1, nmeasurements), dtype=float)
        qimage = ImageWidget.convert_numpy_to_qimage(image)
        assert len(qimage) == nmeasurements

    def test_set_image(self, qtbot):
        image = numpy.zeros((10, 10, 3), dtype=float)
        image[0:5, 0:5, 0] = 0.5
        qimage = ImageWidget.convert_numpy_to_qimage(image)

        widget = ImageWidget.ImageWidget()
        qtbot.addWidget(widget)
        assert widget.image is not None
        widget.set_image(qimage)
        assert widget.image is not None
        assert widget.image[0].width() == 10
        assert widget.image[0].height() == 10
        assert widget.image[0].format() == QtGui.QImage.Format_RGB888
        for i in range(5):
            for j in range(5):
                assert qRed(widget.image[0].pixel(i, j)) == 255
                assert qGreen(widget.image[0].pixel(i, j)) == 0
                assert qBlue(widget.image[0].pixel(i, j)) == 0

        assert widget.image_label.pixmap() is not None

    def test_use_scrollbar(self, qtbot):
        image = numpy.zeros((10, 10, 10), dtype=float)
        image[..., 0] = 0.5
        image[..., 1] = 1
        qimage = ImageWidget.convert_numpy_to_qimage(image)

        widget = ImageWidget.ImageWidget()
        qtbot.addWidget(widget)
        assert widget.image is not None
        widget.set_image(qimage)
        assert widget.image is not None

        assert widget.image_label.pixmap() is not None
        assert widget.image_scroll_bar is not None

        assert widget.image_scroll_bar.value() == 0
        qtbot.mouseClick(widget.image_scroll_bar, QtCore.Qt.LeftButton)
        assert widget.image_scroll_bar.value() == 1
        qtbot.mouseClick(widget.image_scroll_bar, QtCore.Qt.LeftButton)
        assert widget.image_scroll_bar.value() == 2
