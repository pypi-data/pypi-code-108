# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------

"""
This widget displays frame, markers, rois and provide functionality to move markers, rois, as well as center search
"""

import time
import json
import logging

import pyqtgraph as pg
import numpy as np

from datetime import datetime

from PyQt5 import QtCore, QtWidgets, QtGui, QtPrintSupport

from petra_camera.widgets.base_widget import BaseWidget
from petra_camera.gui.FrameViewer_ui import Ui_FrameViewer
from petra_camera.utils.gui_elements import ImageMarker, PeakMarker, LineSegmentItem
from petra_camera.main_window import APP_NAME


WIDGET_NAME = 'FrameViewer'
SAVE_STATE_UIS = ['splitter_y1', 'splitter_y2', 'splitter_x']

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class FrameViewer(BaseWidget):
    """
    """
    new_fps = QtCore.pyqtSignal(float)       # signal, that reports actual FPS to status bar
    cursor_moved = QtCore.pyqtSignal(float, float)  # sends cursor coordinates to status bar

    DEFAULT_IMAGE_EXT = "png"
    FILE_STAMP = "%Y%m%d_%H%M%S"
    DATETIME = "%Y-%m-%d %H:%M:%S"

    LABEL_BRUSH = (30, 144, 255, 170)
    LABEL_COLOR = (255, 255, 255)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """
        """
        super(FrameViewer, self).__init__(parent)

        # ----------------------------------------------------------------------
        #                Variables
        # ----------------------------------------------------------------------

        self._last_frame = None # stores last read frame

        self._acq_started = time.time()
        self._fps_counter = 0
        self._set_new_image = True

        self._view_rect = None

        self._marker_widgets = []
        self._rois_widgets = []

        self._hist = None

        # ----------------------------------------------------------------------
        #                UI setup
        # ----------------------------------------------------------------------

        self._ui = Ui_FrameViewer()
        self._ui.setupUi(self)

        self._ui.image_view.ui.histogram.hide()
        self._ui.image_view.ui.roiBtn.hide()
        self._ui.image_view.ui.menuBtn.hide()
        self._ui.wiProfileY.as_projection_y()

        self.add_remove_roi()
        self.repaint_roi()

        self.add_remove_marker()
        self.repaint_marker()

        # ----------------------------------------------------------------------
        #                Settings
        # ----------------------------------------------------------------------

        self._save_data_folder = self._settings.option("save_folder", "default")
        self._save_image_folder = self._settings.option("save_folder", "default")

        # ----------------------------------------------------------------------
        #                Center search functionality
        # ----------------------------------------------------------------------

        # context menu to perform center search
        self._action_first_point = QtWidgets.QAction('Center search start', self)
        self._action_second_point = QtWidgets.QAction('Set second point', self)
        self._action_second_point.setVisible(False)
        self._action_clear_points = QtWidgets.QAction('Clear points', self)
        self._action_clear_points.setEnabled(False)

        self._context_menu = QtWidgets.QMenu()
        self._context_menu.addAction(self._action_first_point)
        self._context_menu.addAction(self._action_second_point)
        self._context_menu.addAction(self._action_clear_points)

        self._center_search_points = [None, None]
        self._search_in_progress = False

        # center search UI
        self._center_search_item = LineSegmentItem('center', float(self._settings.option("center_search", "cross")),
                                                   float(self._settings.option("center_search", "circle")))
        self._center_search_item.setVisible(False)
        self._ui.image_view.view.addItem(self._center_search_item, ignoreBounds=True)

        # ----------------------------------------------------------------------
        #               Peak search functionality
        # ----------------------------------------------------------------------

        self._peak_markers = PeakMarker()
        self._ui.image_view.view.addItem(self._peak_markers, ignoreBounds=True)

        # ----------------------------------------------------------------------
        #                        Ui signals
        # ----------------------------------------------------------------------
        self._ui.image_view.scene.sigMouseMoved.connect(self._mouse_moved)
        self._ui.image_view.scene.sigMouseClicked.connect(self._mouse_clicked)

        self._ui.image_view.view.sigRangeChanged.connect(self._visible_range_changed)
        self._ui.image_view.view.setMenuEnabled(False)

        self._ui.wiProfileX.cursor_moved.connect(lambda x, y: self.cursor_moved.emit(x, y))
        self._ui.wiProfileY.cursor_moved.connect(lambda x, y: self.cursor_moved.emit(x, y))

        # ----------------------------------------------------------------------
        #                        Labels
        # ----------------------------------------------------------------------
        self._device_label = self._add_label('', self._settings.node("camera_viewer/title_label"), visible=True)
        self._device_label.setText(self._camera_device.device_id)

        self._datetime_label = self._add_label("Time", self._settings.node("camera_viewer/datetime_label"),
                                               visible=True)

        self._load_label = self._add_label("Load image", self._settings.node("camera_viewer/datetime_label"),
                                           visible=False)

        if not self.load_camera():
            raise RuntimeError('Cannot set FrameViewer')

        logger.info("FrameView initialized successfully")

    # ----------------------------------------------------------------------
    def get_image_view(self):
        """

        :return: image item to be set to LUT item
        """
        return self._ui.image_view.imageItem

    # ----------------------------------------------------------------------
    def set_hist(self, hist):
        """

        :param hist: LUT item
        :return: None
        """
        self._hist = hist

    # ----------------------------------------------------------------------
    #                        Setting and changing camera device
    # ----------------------------------------------------------------------
    def load_camera(self):
        """
        called to set new camera
        :return: True or False - success or not
        """
        self._set_new_image = True

        # update center search with last saved for camera
        center_search = self._camera_device.get_settings('center_search', str)
        if center_search != '':
            coordinates = json.loads(center_search)
            if coordinates[0] is not None and coordinates[1] is not None and \
                coordinates[2] is not None and coordinates[3] is not None:

                self._center_search_points = [QtCore.QPointF(coordinates[0], coordinates[1]),
                                              QtCore.QPointF(coordinates[2], coordinates[3])]
                self._action_second_point.setVisible(False)
                self._action_clear_points.setEnabled(True)
                self._center_search_item.setVisible(True)
                self._display_center_search()

                return True

        # self._action_second_point.setVisible(False)
        self._action_clear_points.setEnabled(False)
        self._center_search_item.setVisible(False)
        self._display_center_search()

        return True

    # ----------------------------------------------------------------------
    def close(self, auto_screen):
        """

        :param auto_screen: bool, general settings screen control
        :return:
        """
        logger.debug("Closing FrameViewer")

        if self._camera_device and self._camera_device.is_running():
            self._camera_device.stop(auto_screen)

        super(FrameViewer, self).close()

    # ----------------------------------------------------------------------
    def _visible_range_changed(self, viewBox):
        """
        slot for picture zoom signal
        :param viewBox:
        :return: None
        """
        self._view_rect = viewBox.viewRect()

        self._peak_markers.new_scale(self._view_rect.width(), self._view_rect.height())
        self._center_search_item.new_scale(self._view_rect.width(), self._view_rect.height())

        if self._last_frame is not None:

            self._redraw_projections()
            self._show_labels()
            self._camera_device.calculate_roi_statistics()

    # ----------------------------------------------------------------------
    #                  Start stop functionality
    # ----------------------------------------------------------------------
    def start_stop_live_mode(self, auto_screen):
        """

        :param auto_screen: bool, general settings screen control
        :return:
        """
        if self._camera_device and not self._camera_device.is_running():
            self._start_live_mode(auto_screen)
        else:
            self._stop_live_mode(auto_screen)

    # ----------------------------------------------------------------------
    def _start_live_mode(self, auto_screen):
        """

        :param auto_screen: bool, general settings screen control
        :return:
        """
        if self._camera_device:
            self._acq_started = time.time()
            self._fps_counter = 0
            self._set_new_image = True
            self._camera_device.start(auto_screen)
        else:
            QtWidgets.QMessageBox.warning(self, "Initialization Error",
                                      "{} not yet initialized".format(self._camera_device.device_id))

    # ----------------------------------------------------------------------
    def _stop_live_mode(self, auto_screen):
        """

        :param auto_screen: bool, general settings screen control
        :return:
        """
        if self._camera_device and self._camera_device.is_running():
            self._camera_device.stop(auto_screen)
            logger.debug("{} stopped".format(self._camera_device.device_id))

    # ----------------------------------------------------------------------
    #                 Image set and refresh
    # ----------------------------------------------------------------------
    def new_frame(self):
        """
        slot for new frame signal from camera
        :return:
        """
        if hasattr(self, "_load_label"):
            self._load_label.setVisible(True)

        try:
            self._last_frame = self._camera_device.get_frame()

            picture_size = self._camera_device.get_picture_clip()
            reduction = self._camera_device.get_reduction()

            # preparing kwargs for image set or update
            set_kwargs = {'pos': (picture_size[0], picture_size[1]),
                          'scale': (reduction, reduction)}

            if self._camera_device.levels['auto_levels']:
                set_kwargs['autoRange'] = True
                update_kwargs = {'autoLevels': True}
            else:
                set_kwargs['levels'] = (self._camera_device.levels['levels'][0], self._camera_device.levels['levels'][1])
                update_kwargs = {'levels': (self._camera_device.levels['levels'][0], self._camera_device.levels['levels'][1])}

            # we have to disconnect histogram
            self._parent.block_hist_signals(True)

            if self._set_new_image or self._camera_device.set_new_image:
                self._ui.image_view.setImage(self._last_frame, **set_kwargs)
                self._set_new_image = False
                self._camera_device.set_new_image = False
                try:
                    self._ui.image_view.autoRange()
                except:
                    pass
            else:
                self._ui.image_view.imageItem.updateImage(self._last_frame, **update_kwargs)
                self._camera_device.image_need_repaint = False

            self._parent.block_hist_signals(False)

            if self._camera_device.levels['auto_levels']:
                self._camera_device.levels['levels'] = self._hist.getLevels()

            self._redraw_projections()

            self._peak_markers.new_scale(self._view_rect.width(), self._view_rect.height())
            self._center_search_item.new_scale(self._view_rect.width(), self._view_rect.height())

            self._show_labels()

            # FPS counter
            self._fps_counter += 1
            if time.time() - self._acq_started > 1:
                self.new_fps.emit(self._fps_counter)
                self._fps_counter = 0
                self._acq_started = time.time()

        except Exception as err:
            print('Error during refresh view: {}'.format(err))

        if hasattr(self, "_load_label"):
            self._load_label.setVisible(False)

    # ----------------------------------------------------------------------
    def _redraw_projections(self):
        """
        """
        epsilon = 10
        if (self._ui.wiProfileX.frameSize().height() < epsilon and
                self._ui.wiProfileY.frameSize().width() < epsilon):
            return

        # take into account current view range
        x, y = self._view_rect.x(), self._view_rect.y()
        w, h = self._view_rect.width(), self._view_rect.height()

        frameW, frameH = self._last_frame.shape[:2]
        x, y = int(max(0, x)), int(max(0, y))
        w, h = int(min(w, frameW)), int(min(h, frameH))

        dataSlice = self._last_frame[x:x + w, y:y + h]
        if len(dataSlice.shape) > 2:
            dataSlice = (dataSlice[...,0] * 65536 + dataSlice[...,1] * 256 + dataSlice[...,2])/16777215

        if self._ui.wiProfileX.frameSize().height() > epsilon:
            self._ui.wiProfileX.range_changed(dataSlice, 1, (x, y, w, h))

        if self._ui.wiProfileY.frameSize().width() > epsilon:
            self._ui.wiProfileY.range_changed(dataSlice, 0, (x, y, w, h))

    # ----------------------------------------------------------------------
    def repaint_peak_search(self):
        """
        called after peak search is done
        :return:
        """
        self._peak_markers.new_peaks(self._camera_device.peak_coordinates)

    # ----------------------------------------------------------------------
    #                  Marker functionality
    # ----------------------------------------------------------------------

    def add_remove_marker(self):
        """
        called when new roi added or lod deleted

        :return:
        """
        for widget in self._marker_widgets:
            widget.delete_me()

        self._marker_widgets = []
        for ind, marker in enumerate(self._camera_device.markers):
            marker = ImageMarker(marker['x'], marker['y'], self._ui.image_view)
            marker.new_coordinates.connect(lambda x, y, id = ind: self._new_marker_coordinates(id, x, y))
            self._marker_widgets.append(marker)

        self.repaint_marker()

    # ----------------------------------------------------------------------
    def _new_marker_coordinates(self, id, x, y):
        self._camera_device.set_marker_value(id, 'x', x)
        self._camera_device.set_marker_value(id, 'y', y)

    # ----------------------------------------------------------------------
    def repaint_marker(self):
        """
        called when user moves marker or changes color

        :return:
        """
        for widget, marker in zip(self._marker_widgets, self._camera_device.markers):
            widget.setPos(marker['x'], marker['y'])
            widget.setVisible(marker['visible'])
            widget.setColor(marker['color'])

    # ----------------------------------------------------------------------
    #                  ROI functionality
    # ----------------------------------------------------------------------

    def add_remove_roi(self):
        """
        called when new roi added or lod deleted

        :return: None
        """
        for widget, marker, label in self._rois_widgets:
            self._ui.image_view.view.removeItem(widget)
            self._ui.image_view.view.removeItem(marker)
            self._ui.image_view.view.removeItem(label)

        self._rois_widgets = []
        for ind, values in enumerate(self._camera_device.rois):
            widget = pg.RectROI([values['x'], values['y']], [values['w'], values['h']], pen=(0, 9))
            widget.sigRegionChanged.connect(lambda rect, id=ind: self._roi_changed(rect, id))
            if values['visible']:
                widget.hide()
            else:
                widget.show()

            marker_item = LineSegmentItem('cross')
            marker_item.setVisible(values['visible'])
            self._ui.image_view.view.addItem(marker_item, ignoreBounds=True)

            self._ui.image_view.view.addItem(widget, ignoreBounds=True)
            self._rois_widgets.append([widget, marker_item,
                                       self._add_label("ROI_{}".format(ind+1),
                                                       self._settings.node("camera_viewer/roi_label"),
                                                       visible=values['visible'])])

        self.repaint_roi()

    # ----------------------------------------------------------------------
    def repaint_roi(self):
        """
        called when new statistics calculated, or ROI parameters changed

        :return:
        """
        for ind, (roi, cross, label) in enumerate(self._rois_widgets):

            roi.blockSignals(True)

            roi_info = self._camera_device.rois[ind]
            roi_data = self._camera_device.rois_data[ind]

            roi.setVisible(roi_info['visible'])
            label.setVisible(roi_info['visible'])

            roi.setPos([roi_info['x'], roi_info['y']])
            roi.setSize([roi_info['w'], roi_info['h']])
            if roi_info['color']:
                roi.setPen(roi_info['color'])

            label.setPos(roi_info['x'] + roi_info['w'],
                         roi_info['y'] + roi_info['h'])

            cross.setVisible(False)
            if roi_info['visible']:
                if roi_info['mark'] == 'max':
                    cross.set_pos((roi_data['max_x'], roi_data['max_y']), (roi_data['fwhm_x'], roi_data['fwhm_y']))
                elif roi_info['mark'] == 'min':
                    cross.set_pos((roi_data['min_x'], roi_data['min_y']), (roi_data['fwhm_x'], roi_data['fwhm_y']))
                elif roi_info['mark'] == 'com':
                    cross.set_pos((roi_data['com_x'], roi_data['com_y']), (roi_data['fwhm_x'], roi_data['fwhm_y']))
                cross.setVisible(True)

            roi.blockSignals(False)

    # ----------------------------------------------------------------------
    def _roi_changed(self, rect, ind):
        """
        called when ROI emits sigRegionChanged signal.
        :param rect: new roi rect
        :param ind: ROIs index
        :return:
        """
        if self._last_frame is not None:
            pos, size = rect.pos(), rect.size()
            max_w, max_h = self._last_frame.shape[:2]

            self._camera_device.set_roi_value(ind, 'x', max(int(pos.x()), 0))
            self._camera_device.set_roi_value(ind, 'y', max(int(pos.y()), 0))
            self._camera_device.set_roi_value(ind, 'w', min(int(size.x()), max_w))
            self._camera_device.set_roi_value(ind, 'h', min(int(size.y()), max_h))

            self._camera_device.calculate_roi_statistics()

            self._rois_widgets[ind][2].setPos(pos.x() + size.x(), pos.y() + size.y())

    # ----------------------------------------------------------------------
    #                  Center search functionality
    # ----------------------------------------------------------------------
    def _mouse_moved(self, pos):
        """
        slot for mouse events, utilized for center search
        :param pos: mouse position
        :return:
        """
        pos = self._ui.image_view.view.mapSceneToView(pos)
        self.cursor_moved.emit(pos.x(), pos.y())
        if self._search_in_progress:
            self._center_search_points[1] = pos
            self._display_center_search()

    # ----------------------------------------------------------------------
    def _mouse_clicked(self, event):
        """
        slot for mouse events, mainly utilized for center search
        :param event:
        :return:
        """
        if event.double():
            try:
                self._ui.image_view.autoRange()
            except:
                pass

        elif event.button() == 2:  # right click

            action = self._context_menu.exec_(event._screenPos)

            if action == self._action_first_point:
                self._center_search_points[0] = self._ui.image_view.view.mapSceneToView(event.scenePos())
                self._search_in_progress = True
                self._action_second_point.setVisible(True)
                self._action_clear_points.setEnabled(True)
                self._center_search_item.setVisible(True)

            elif action == self._action_second_point:
                self._center_search_points[1] = self._ui.image_view.view.mapSceneToView(event.scenePos())
                self._action_second_point.setVisible(False)
                self._search_in_progress = False
                self._save_center_search()

            else:
                self._center_search_points = [None, None]
                self._action_second_point.setVisible(False)
                self._action_clear_points.setEnabled(False)
                self._center_search_item.setVisible(False)
                self._search_in_progress = False
                self._save_center_search()

        elif event.button() == 1 and self._search_in_progress:  # left click

            self._center_search_points[1] = self._ui.image_view.view.mapSceneToView(event.scenePos())
            self._action_second_point.setVisible(False)
            self._search_in_progress = False
            self._save_center_search()

        self._display_center_search()

    # ----------------------------------------------------------------------
    def _save_center_search(self):
        """
        drops center search parameters
        :return: None
        """
        if self._center_search_points[0] is not None and self._center_search_points[1] is not None:
            coordinates = [self._center_search_points[0].x(), self._center_search_points[0].y(),
                           self._center_search_points[1].x(), self._center_search_points[1].y()]
        else:
            coordinates = [None, None]
        self._camera_device.save_settings('center_search', json.dumps(coordinates))

    # ----------------------------------------------------------------------
    def _display_center_search(self):
        """

        :return:
        """
        self._center_search_item.set_pos(self._center_search_points)

    # ----------------------------------------------------------------------
    # ---------------- Image save and print functionality ------------------
    # ----------------------------------------------------------------------

    def _show_labels(self):
        """
        """
        if hasattr(self, "_device_label"):
            self._show_label(0.5, 0.04, self._device_label)

        if hasattr(self, "_datetime_label"):
            msg = datetime.now().strftime(self.DATETIME)
            self._datetime_label.setText(msg)

            self._show_label(0.85, 0.9, self._datetime_label)

        if hasattr(self, "_load_label"):
            self._show_label(0.85, 0.04, self._load_label)

    # ----------------------------------------------------------------------
    def _add_label(self, text, style=None, visible=True):
        """

        :param text: str
        :param style: style sheet
        :param visible: bool
        :return: pg text item
        """
        if not style:
            color = self.LABEL_COLOR
            fill = self.LABEL_BRUSH
            font = QtGui.QFont("Arial", 10)
        else:
            color = tuple(int(v) for v in style.getAttribute("fg_color").split(","))
            fill = tuple(int(v) for v in style.getAttribute("bg_color").split(","))
            font = style.getAttribute("font").split(",")
            font = QtGui.QFont(font[0], int(font[1]))

        item = pg.TextItem(text=text, color=color, fill=fill)
        item.setFont(font)
        item.setVisible(visible)

        self._ui.image_view.view.addItem(item, ignoreBounds=True)

        return item

    # ----------------------------------------------------------------------
    def _show_label(self, x, y, label):
        """
        Args:
            x, y (float), normalized to 0-1 range position
        """
        [[xMin, xMax], [yMin, yMax]] = self._ui.image_view.view.viewRange()

        deltaX = abs(xMax - xMin)
        textX = xMax - deltaX * (1. - x)

        deltaY = abs(yMax - yMin)
        textY = yMax - deltaY * (1. - y)

        label.setPos(textX, textY)

    # ----------------------------------------------------------------------
    # ---------------- Image save and print functionality ------------------
    # ----------------------------------------------------------------------
    def save_to_image(self):
        """
        """
        self.stop_live_mode()

        fileName = self._get_image_file_name("Save Image")
        if fileName:
            pixmap = QtGui.QScreen.grabWidget(self._ui.image_view)
            pixmap.save(fileName)

    # ----------------------------------------------------------------------

    def save_to_file(self, fmt):
        """Saves to text file or numpy's npy/npz.
        """
        self.stop_live_mode()

        fmt = fmt.lower()
        defaultName = "data_{}.{}".format(datetime.now().strftime(self.FILE_STAMP),
                                          fmt)

        fileTuple, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save To File", self._save_data_folder + defaultName,
                                                             filter=(self.tr("Ascii Files (*.csv)")
                                                              if fmt == "csv" else
                                                              self.tr("Numpy Files (*.npy)")))

        self._save_data_folder = QtCore.QFileInfo(fileTuple).path() + '/'

        fileName = str(fileTuple)
        fileName = fileName.strip()

        if fileName:
            data, scale = self._camera_device.get_frame()  # sync with data acq! TODO

            if fmt.lower() == "csv":
                np.savetxt(fileName, data)
            elif fmt.lower() == "npy":
                np.save(fileName, data)
            else:
                raise ValueError("Unknown format '{}'".format(fmt))

    # ---------------------------------------------------------------------- 
    def print_image(self):
        """
        """
        self.stop_live_mode()

        self._printer = QtPrintSupport.QPrinter()

        if QtPrintSupport.QPrintDialog(self._printer).exec_() == QtWidgets.QDialog.Accepted:
            self._printPainter = QtGui.QPainter(self._printer)
            self._printPainter.setRenderHint(QtGui.QPainter.Antialiasing)

            self._ui.image_view.view.render(self._printPainter)

    # ---------------------------------------------------------------------- 
    def to_clipboard(self):
        """NOTE that the content of the clipboard is cleared after program's exit.
        """
        self.stop_live_mode()

        pixmap = QtGui.QScreen.grabWidget(self._ui.image_view)
        QtWidgets.qApp.clipboard().setPixmap(pixmap)

    # ----------------------------------------------------------------------
    def _get_image_file_name(self, title):
        """
        """
        filesFilter = ";;".join(["(*.{})".format(ffilter) for ffilter in
                                 QtGui.QImageWriter.supportedImageFormats()])

        defaultName = "image_{}.{}".format(datetime.now().strftime(self.FILE_STAMP),
                                           self.DEFAULT_IMAGE_EXT)
        fileTuple, _ = QtWidgets.QFileDialog.getSaveFileName(self, title, self._save_image_folder + defaultName,
                                                             filesFilter)

        self._save_image_folder = QtCore.QFileInfo(fileTuple).path() + '/'

        return str(fileTuple)
