# 2021-07-31. Leonardo Molina.
# 2022-01-21. Last modified.

from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore
from walkway.capture import Capture
from walkway.flexible import Flexible

import argparse
import cv2
import json
import logging
import sys
import walkway.flir as flir

class GUI(QtWidgets.QDialog):
    """
    GUI for capturing high frame rate videos. See Capture.
    """
    
    
    def get(self, key):
        p = self.__private
        return p.capture.get(key)
        
        
    def __init__(self, capture, profile=None, parent=None):
        super(GUI, self).__init__(parent)
        p = self.__private = Flexible()
        
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        
        if profile is None:
            p.profilePath = str(Path.home() / "Documents" / "walkway-settings.json")
        else:
            p.profilePath = str(profile)
            
        p.capture = capture
        p.nodemap = capture.get("Camera").GetNodeMap()
        
        p.acquisitionWidgets = {}
        p.detectionWidgets = {}
        
        p.cameraPanel = QtWidgets.QGroupBox("Camera settings")
        layout = QtWidgets.QGridLayout()
        p.cameraPanel.setLayout(layout)
        row = 0
        
        label = "Acquisition frame rate"
        alias = "AcquisitionFrameRate"
        widget = QtWidgets.QDoubleSpinBox(p.cameraPanel)
        minimun, maximum = flir.getRange(p.nodemap, alias)
        widget.setMinimum(minimun)
        widget.setMaximum(maximum)
        widget.setSingleStep(5)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        label = "Exposure time"
        alias = "ExposureTime"
        widget = QtWidgets.QDoubleSpinBox(p.cameraPanel)
        minimun, maximum = flir.getRange(p.nodemap, alias)
        widget.setMinimum(minimun)
        widget.setMaximum(maximum)
        widget.setSingleStep(50)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        label = "Gain"
        alias = "Gain"
        widget = QtWidgets.QDoubleSpinBox(p.cameraPanel)
        minimun, maximum = flir.getRange(p.nodemap, alias)
        widget.setMinimum(minimun)
        widget.setMaximum(maximum)
        widget.setSingleStep(0.5)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        
        label = "Gamma"
        alias = "Gamma"
        widget = gammaWidget = QtWidgets.QDoubleSpinBox(p.cameraPanel)
        minimun, maximum = flir.getRange(p.nodemap, alias)
        widget.setMinimum(minimun)
        widget.setMaximum(maximum)
        widget.setSingleStep(0.05)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        
        widget = QtWidgets.QLabel(label)
        layout.addWidget(widget, row, 0)
        widget.mousePressEvent = lambda e: self.__gammaEnable()
        
        row += 1
        
        # Retrieve min and max width and height when offsets are zero.
        offsetX = flir.getValue(p.nodemap, "OffsetX")
        offsetY = flir.getValue(p.nodemap, "OffsetY")
        capture.set(OffsetX=0, OffsetY=0)
        minimunWidth, maximumWidth = flir.getRange(p.nodemap, "Width")
        minimunHeight, maximumHeight = flir.getRange(p.nodemap, "Height")
        capture.set(OffsetX=offsetX, OffsetY=offsetY)
        
        label = "Width"
        alias = "Width"
        widget = QtWidgets.QSpinBox(p.cameraPanel)
        widget.setMinimum(minimunWidth)
        widget.setMaximum(maximumWidth)
        widget.setSingleStep(8)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        label = "Height"
        alias = "Height"
        widget = QtWidgets.QSpinBox(p.cameraPanel)
        widget.setMinimum(minimunHeight)
        widget.setMaximum(maximumHeight)
        widget.setSingleStep(8)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        label = "Offset X"
        alias = "OffsetX"
        widget = QtWidgets.QSpinBox(p.cameraPanel)
        widget.setMinimum(0)
        widget.setMaximum(maximumWidth)
        widget.setSingleStep(8)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        label = "Offset Y"
        alias = "OffsetY"
        widget = QtWidgets.QSpinBox(p.cameraPanel)
        widget.setMinimum(0)
        widget.setMaximum(maximumHeight)
        widget.setSingleStep(8)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.acquisitionWidgets[alias] = widget
        row += 1
        
        label = "Center"
        widget = QtWidgets.QPushButton(p.cameraPanel, default=False, autoDefault=False)
        widget.setText(label)
        widget.clicked.connect(self.__onCenterImage)
        layout.addWidget(widget, row, 1)
        row += 1
        
        label = "Apply"
        widget = QtWidgets.QPushButton(p.cameraPanel, default=False, autoDefault=False)
        widget.setText(label)
        widget.clicked.connect(self.__onApplyAcquisitionSettings)
        layout.addWidget(widget, row, 1)
        
        
        p.detectionPanel = QtWidgets.QGroupBox("Detection settings")
        layout = QtWidgets.QGridLayout()
        p.detectionPanel.setLayout(layout)
        row = 0

        label = "Prefix"
        alias = "Prefix"
        prefixWidget = QtWidgets.QLineEdit(p.cameraPanel)
        prefixWidget.setSizePolicy(widget.sizePolicy())
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(prefixWidget, row, 1, 1, 1)
        row += 1

        
        label = "Output quality"
        alias = "OutputQuality"
        widget = QtWidgets.QSpinBox(p.cameraPanel)
        widget.setMinimum(0)
        widget.setMaximum(100)
        widget.setSingleStep(5)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Output frame rate"
        alias = "OutputFrameRate"
        widget = QtWidgets.QDoubleSpinBox(p.cameraPanel)
        widget.setMinimum(1)
        widget.setMaximum(1000)
        widget.setSingleStep(5)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Speed threshold"
        alias = "SpeedThreshold"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1e-9)
        widget.setMaximum(100)
        widget.setSingleStep(0.1)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Locomotion threshold"
        alias = "LocomotionThreshold"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1e-9)
        widget.setMaximum(100)
        widget.setSingleStep(0.01)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Quiescence threshold"
        alias = "QuiescenceThreshold"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1e-9)
        widget.setMaximum(100)
        widget.setSingleStep(0.01)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Min duration"
        alias = "MinDuration"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1e-9)
        widget.setMaximum(2)
        widget.setSingleStep(0.1)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Max duration"
        alias = "MaxDuration"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1e-9)
        widget.setMaximum(100)
        widget.setSingleStep(0.2)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Area proportion"
        alias = "AreaProportion"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1e-9)
        widget.setMaximum(1)
        widget.setSingleStep(0.05)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Buffer size"
        alias = "BufferSize"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(1)
        widget.setMaximum(1000)
        widget.setSingleStep(1)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        label = "Blur size"
        alias = "BlurSize"
        widget = QtWidgets.QDoubleSpinBox(p.detectionPanel)
        widget.setMinimum(0)
        widget.setMaximum(1)
        widget.setSingleStep(0.05)
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        layout.addWidget(widget, row, 1)
        p.detectionWidgets[alias] = widget
        row += 1
        
        p.settingsWidgets = {**p.acquisitionWidgets, **p.detectionWidgets}
        
        # Initialize all widget values. All widgets save.
        for alias, widget in p.settingsWidgets.items():
            value = self.get(alias)
            if value is not None:
                widget.editingFinished.connect(self.__save)
                widget.setValue(value)

        # Unlike acquisition widgets, detection widgets submit changes after user input.
        for alias, widget in p.detectionWidgets.items():
            widget.editingFinished.connect(lambda alias=alias, widget=widget: self.__submit(**{alias: widget.value()}))
        
        # QLineEdit has different signals & methods than QSpinBox.
        value = self.get("Prefix")
        if value is not None:
            prefixWidget.setText(value)
        prefixWidget.editingFinished.connect(self.__save)
        prefixWidget.editingFinished.connect(lambda: self.__submit(Prefix=prefixWidget.text()))
        
        p.logPanel = QtWidgets.QGroupBox("Log")
        layout = QtWidgets.QGridLayout()
        p.logPanel.setLayout(layout)
        
        logTextBox = QTextEditLogger(p.logPanel)
        logTextBox.widget.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        logTextBox.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S"))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)
        layout.addWidget(logTextBox.widget)
        
        
        p.controlPanel = QtWidgets.QGroupBox("Control")
        layout = QtWidgets.QHBoxLayout()
        p.controlPanel.setLayout(layout)
        widget = folderWidget = QtWidgets.QPushButton(p.controlPanel, default=False, autoDefault=False)
        widget.setText("Output folder")
        widget.clicked.connect(self.__onSelectFolder)
        layout.addWidget(widget)
        widget = QtWidgets.QPushButton(p.controlPanel, default=False, autoDefault=False)
        widget.setText("Select user profile")
        widget.clicked.connect(self.__onSelectProfile)
        layout.addWidget(widget)
        
        widget = armWidget = QtWidgets.QCheckBox("&Arm detector")
        widget.stateChanged.connect(lambda state: capture.arm(state > 0))
        layout.addWidget(widget)
        
        widget = recordWidget = QtWidgets.QCheckBox("&Record continuously")
        widget.toggled.connect(lambda state, widget=widget: widget.setChecked(capture.record(state > 0)))
        layout.addWidget(widget)
        
        widget = QtWidgets.QCheckBox("&Save")
        widget.toggled.connect(lambda state, widget=widget: capture.save(state > 0))
        layout.addWidget(widget)
        
        
        p.renderPanel = QtWidgets.QGroupBox("Camera")
        layout = QtWidgets.QVBoxLayout()
        p.renderPanel.setLayout(layout)
        
        widget = QtWidgets.QLabel(p.renderPanel)
        widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(widget)
        p.renderTimer = QtCore.QTimer()
        p.renderTimer.timeout.connect(lambda widget=widget: self.__updateFrame(qLabel=widget))
        p.renderTimer.start(1000. / 24)
        
        
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(p.cameraPanel, 0, 0, 1, 1)
        mainLayout.addWidget(p.detectionPanel, 0, 1, 1, 1)
        mainLayout.addWidget(p.logPanel, 0, 2, 1, 2)
        mainLayout.addWidget(p.controlPanel, 1, 0, 1, 4)
        mainLayout.addWidget(p.renderPanel, 2, 0, 1, 4)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("Walkway")
        logging.info("Output folder is '%s'" % capture.get("Folder"))
        p.widgets = {**p.acquisitionWidgets, **p.detectionWidgets, "window":self, "folder":folderWidget, "arm":armWidget, "record":recordWidget, "prefix":prefixWidget}
        
        if Path(p.profilePath).is_file():
            self.__loadProfile(p.profilePath)
        
        capture.subscribe("recording", lambda capture, filename, state: recordWidget.setChecked(state == "start"))
        capture.start(armed=False)
    
    
    def __gammaEnable(self, enable=None):
        p = self.__private
        if enable is None:
            enable = not p.widgets["Gamma"].isEnabled()
        p.widgets["Gamma"].setEnabled(enable)
    
    
    def __updateFrame(self, qLabel):
        p = self.__private
        im = p.capture.frame
        if im is not None:
            p.capture.decorate(im, message=True, trail=0.05)
            frame = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_RGB888)
            qLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            p.renderPanel.setTitle("Camera (fps:%.1f, unsaved:%i)" % (p.capture.fps, p.capture.bufferSize))
    
    
    def __onCenterImage(self):
        p = self.__private
        dx = p.acquisitionWidgets["Width"].value()
        mx = p.acquisitionWidgets["Width"].maximum()
        dy = p.acquisitionWidgets["Height"].value()
        my = p.acquisitionWidgets["Height"].maximum()
        p.acquisitionWidgets["OffsetX"].setValue(((mx - dx) / 2) // 8 * 8)
        p.acquisitionWidgets["OffsetY"].setValue(((my - dy) / 2) // 8 * 8)
    
    
    def __onApplyAcquisitionSettings(self):
        p = self.__private
        settings = {alias: widget.value() for (alias, widget) in p.acquisitionWidgets.items()}
        settings = {"GammaEnable":p.widgets["Gamma"].isEnabled(), **settings}
        p.capture.set(**settings)
        
        
    def __onSelectFolder(self):
        p = self.__private
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", p.capture.get("Folder"), QtWidgets.QFileDialog.ShowDirsOnly)
        if len(path) > 0:
            p.capture.set(Folder=path)
        
        
    def __onSelectProfile(self):
        p = self.__private
        defaultFolder = str(Path(p.profilePath).parent)
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Select Profile", defaultFolder, "JSON file (*.json)")[0]
        if len(path) > 0:
            self.__loadProfile(path)
    
    def __loadProfile(self, path):
        p = self.__private
        logging.info("Loading profile '%s'" % path)
        try:
            fid = open(path)
            settings = json.load(fid)
            fid.close()
            success = True
        except Exception as ex:
            exception = str(ex)
            success = False
        if success:
            p.profilePath = path
            self.__setGUI(**settings)
            self.__submit(**settings)
        else:
            logging.warning("Could not load profile '%s' ==> %s" % (path, exception))
        
    
    
    def __submit(self, **settings):
        p = self.__private
        p.capture.set(**settings)
        
    
    def __save(self):
        p = self.__private
        if len(p.profilePath) > 0:
            settings = {"GammaEnable": p.widgets["Gamma"].isEnabled()}
            settings = {**settings, **{alias: widget.value() for (alias, widget) in p.settingsWidgets.items()}}
            with open(p.profilePath, 'w', encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
    
    
    def __setGUI(self, **settings):
        p = self.__private
        valueSettings = {key: value for key, value in settings.items() if key in p.settingsWidgets.keys()}
        for key, value in valueSettings.items():
            p.settingsWidgets[key].setValue(value)
        if "GammaEnable" in settings:
            p.widgets["Gamma"].setEnabled(settings["GammaEnable"])
    
    
    @property
    def widgets(self):
        p = self.__private
        return p.widgets
    
    
    def closeEvent(self, event):
        p = self.__private
        logging.info("Exiting...")
        p.capture.dispose()
        event.accept()
    

class QTextEditLogger(logging.Handler, QtCore.QObject):
    appendPlainText = QtCore.pyqtSignal(str)
    
    
    def __init__(self, parent):
        super().__init__()
        QtCore.QObject.__init__(self)
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendHtml)
    
    
    def emit(self, record):
        if record.levelname == 'DEBUG':
            record.msg = "<span style='color:blue;'>%s</span>" % record.msg
        if record.levelname == 'ERROR':
            record.msg = "<span style='color:red;'>%s</span>" % record.msg
        if record.levelname == 'WARNING':
            record.msg = "<span style='color:orange;'>%s</span>" % record.msg
        msg = self.format(record)
        self.appendPlainText.emit(msg)
        

if __name__ == '__main__':
    appContext = QtWidgets.QApplication([])
    parser = argparse.ArgumentParser(description=GUI.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-id', type=int, default=0, help="Camera index")
    args = parser.parse_args()
    
    capture = Capture(args.id)
    if capture.connect():
        gui = GUI(capture=capture)
        gui.show()
        result = appContext.exec()
        capture.dispose()
    else:
        capture.dispose()
        result = -1
        message = "Camera not detected."
        dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Critical error", message, QtWidgets.QMessageBox.Ok, QtWidgets.QApplication.activeWindow())
        dialog.show()
        result = appContext.exec()
    sys.exit(result)