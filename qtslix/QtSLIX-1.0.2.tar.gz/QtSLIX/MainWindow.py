from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, \
                            QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QCloseEvent

from .ClusterWidget import ClusterWidget
from .ParameterGeneratorWidget import ParameterGeneratorWidget
from .VisualizationWidget import VisualizationWidget

__all__ = ['MainWindow']


class MainWindow(QMainWindow):
    """
    MainWindow class.
    """
    def __init__(self):
        super().__init__()

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = None
        self.helpmenu = None
        self.tab_bar = None

        self.parameter_generator_widget = None
        self.visualization_widget = None
        self.cluster_widget = None

        self.setWindowTitle('QtSLIX')
        self.setMinimumSize(1280, 720)

        # Prevent that the window becomes too large. This
        # might happen if Qt loads an image into a QLabel
        # Check all screens in case that one screen is larger than
        # the other.
        screens = QApplication.screens()
        max_width = 0
        max_height = 0
        for screen in screens:
            max_width = max(screen.availableSize().width(), max_width)
            max_height = max(screen.availableSize().height(), max_height)
        self.setMaximumSize(max_width, max_height)

        self.setup_ui()
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        """
        Override the close event.

        Args:
            a0: The close event.

        Returns:
             None
        """
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            a0.accept()
            if self.tab_bar:
                del self.tab_bar
            if self.parameter_generator_widget:
                del self.parameter_generator_widget
            if self.cluster_widget:
                del self.cluster_widget
            if self.visualization_widget:
                del self.visualization_widget
        else:
            a0.ignore()

    def setup_ui(self) -> None:
        """
        Set up the user interface.

        Returns:
             None
        """
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.tab_bar = QTabWidget()
        self.parameter_generator_widget = ParameterGeneratorWidget()
        self.tab_bar.addTab(self.parameter_generator_widget, 'Parameter Generator')
        self.visualization_widget = VisualizationWidget()
        self.tab_bar.addTab(self.visualization_widget, 'Visualization')
        self.cluster_widget = ClusterWidget()
        self.tab_bar.addTab(self.cluster_widget, 'Clustering')
        self.layout.addWidget(self.tab_bar)

        self.create_menu_bar()

    def create_menu_bar(self) -> None:
        """
        Create the menu bar.

        Returns:
             None
        """
        self.helpmenu = self.menuBar().addMenu('&Help')
        self.helpmenu.addAction('&About', self.about)
        self.helpmenu.addAction('&License', self.license)
        self.helpmenu.addAction('&Credits', self.credits)
        self.helpmenu.addAction('&About Qt', self.about_qt)

    def close(self) -> None:
        """
        Close the application.

        Returns:
             None
        """
        QApplication.quit()

    def about(self) -> None:
        """
        Show information about the application.

        Returns:
             None
        """
        pass

    def license(self) -> None:
        """
        Show information about the license.

        Returns:
             None
        """
        url = QUrl('https://jugit.fz-juelich.de/inm-1/fa/sli/tools/qtslix/-/blob/main/LICENSE')
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Open Url', 'Could not open url')

    def credits(self) -> None:
        """
        Show information about the authors.

        Returns:
             None
        """
        QMessageBox.information(self, 'Credits', '')

    def about_qt(self) -> None:
        """
        Show information about Qt.

        Returns:
             None
        """
        QApplication.aboutQt()
