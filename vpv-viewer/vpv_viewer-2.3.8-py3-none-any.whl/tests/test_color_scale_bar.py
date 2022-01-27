from nose.tools import assert_equals, nottest
import sys
from os.path import join, dirname
sys.path.insert(0, join(dirname(__file__), '..'))
from data_manager import ColorScaleBar
from PyQt5 import QtGui, QtWidgets
from lookup_tables import Lut


def test_color_bar():
    """
    Just runs the color scale bar code. Not a proper test as such. You have to tell whether it's passed by looking
    at the image produced

    Used in development as it's quicker than running an instance of vpv_viewer each time
    """
    lut = Lut()
    hotred = lut._hot_red_blue()[0]
    hotblue = lut._hot_red_blue()[1]

    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('color bar test')
    layout =  QtWidgets.QVBoxLayout()
    w.setLayout(layout)
    cb = ColorScaleBar(layout, hotblue, hotred)
    cb.show()
    cb.update(40, 10, -37, -3)

    w.show()
    sys.exit(app.exec_())
