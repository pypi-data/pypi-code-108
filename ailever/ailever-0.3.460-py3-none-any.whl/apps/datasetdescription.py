from PyQt5.QtWidgets import QApplication, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from .UIAilever import Ui_MainWindow


class MPLCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MPLCanvas, self).__init__(fig)


class DatasetDescription(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(DatasetDescription, self).__init__(parent)
        self.setupUi(self)
        
        description = MPLCanvas(self, width=5, height=4, dpi=100)
        description.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.graphicsView.setCentralWidget(description)


