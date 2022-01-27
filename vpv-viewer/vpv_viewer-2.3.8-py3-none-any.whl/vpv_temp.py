#!/usr/bin/env python3

# Copyright 2016 Medical Research Council Harwell.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# @author Neil Horner <n.horner@har.mrc.ac.uk>

# I distribute VPV as an installer with a bundled version of WinPython
# In at least one case, the paths are not correctly set. So the following hack attempts to set correct paths


WINPYTHON_DIR = 'WinPython-64bit-3.6.3.0Zero'
PYTHON_DIR = 'python-3.6.3.amd64'

import os
import sys
from pathlib import Path
import logging
from os.path import join, isdir
from typing import Iterable, List, Tuple
p = sys.path

from PyQt5 import QtGui, QtCore, QtWidgets
from functools import partial
from vpv import common
from vpv.ui.controllers import importer

from vpv.ui.controllers import log_viewer

try:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
except AttributeError:
    logging.info("High DPI scaling not available. QT >=5.6 is needed for this ")

if os.name == 'nt':
    # check where vpv_viewer has been installed
    vpv_installation_dir = os.path.dirname(os.path.realpath(__file__))
    winpython_path = os.path.join(vpv_installation_dir, WINPYTHON_DIR, PYTHON_DIR)
    if os.path.isdir(winpython_path):
        dll_path = os.path.join(winpython_path, 'DLLs')
        lib_path = os.path.join(winpython_path, 'Lib')
        site_packages_path = os.path.join(lib_path, 'site-packages')
        sys.path.insert(0, dll_path)
        sys.path.insert(0, lib_path)
        sys.path.insert(0, site_packages_path)
    else:
        logging.info('cannot find winpython folder: {}'.format(winpython_path))

import pandas as pd

from vpv.ui.controllers.dock_widget_manager import ManagerDockWidget
from vpv.model.model import DataModel
from vpv.utils.appdata import AppData
from vpv.common import Orientation, Layers, log_path, error_dialog
from vpv.display.slice_view_widget import SliceWidget
from vpv.ui.controllers.data_manager import ManageData
from vpv.ui.controllers.options_tab import OptionsTab
from vpv.annotations.annotations_widget import AnnotationsWidget
from vpv.model.coordinate_mapper import Coordinate_mapper
from vpv.ui.controllers import main_window
from vpv.ui.controllers.qc_tab import QC
from vpv.ui.controllers.label_filter import LabelFilter
from vpv.utils import github


try:
    from vpv.ui.controllers.console import Console
    console_imported = True
except ImportError as e:
    logging.info('cannot import qtconsole, so diabling console widget tab\n{e}')
    console_imported = False
except Exception:  # I thnk it might not be an ImportError? look into it
    logging.info('cannot import qtconsole, so diabling console widget tab')
    console_imported = False

from vpv.ui.controllers.gradient_editor import GradientEditor
import zipfile
from vpv.lib import addict
import tempfile
import csv
import logging.config
from vpv.common import log_path


class Vpv(QtCore.QObject):
    """The entry point to VPV. Acts a bit like a controller taking signals from the different views and propogating
    them to other views.
    """
    data_processing_finished_signal = QtCore.pyqtSignal()
    crosshair_visible_signal = QtCore.pyqtSignal()
    crosshair_invisible_signal = QtCore.pyqtSignal()
    volume_pixel_signal = QtCore.pyqtSignal(float)
    volume2_pixel_signal = QtCore.pyqtSignal(float)
    atlas_label_over_signal = QtCore.pyqtSignal(str)
    heatmap_pixel_signal = QtCore.pyqtSignal(float)
    # volume_position_signal = QtCore.pyqtSignal(int, int, int)

    def __init__(self):
        super(Vpv, self).__init__()

        self.voxel_size = 28.0
        self.view_scale_basrs = False
        self.view_id_counter = 0
        self.appdata = AppData()

        print(self.appdata.data)
        self.mainwindow = main_window.Mainwindow(self, self.appdata)
        # self.mainwindow.showFullScreen()
        self.model = DataModel()
        self.model.updating_started_signal.connect(self.updating_started)
        self.model.updating_finished_signal.connect(self.updating_finished)
        self.model.updating_msg_signal.connect(self.display_update_msg)
        self.views = {}

        # Initialise the QC tab
        self.qc = QC(self, self.mainwindow, self.appdata)
        self.qc.load_specimen_signal.connect(self.load_volumes)
        self.last_selected_label = 0 # This is updated everytime mouse hovers over label
        self.volume2_pixel_signal.connect(self.set_current_label)

        # display and views now created in manage_views
        self.data_manager = ManageData(self, self.model, self.mainwindow, self.appdata)
        self.data_manager.gradient_editor_signal.connect(self.gradient_editor)

        self.annotations_manager = AnnotationsWidget(self, self.mainwindow)
        self.annotations_manager.annotation_highlight_signal.connect(self.show_saved_annotations)
        self.annotations_manager.annotation_radius_signal.connect(self.annotation_radius_changed)
        self.annotations_manager.roi_highlight_off_signal.connect(self.reset_roi)

        self.mainwindow.d_pressed_signal.connect(self.annotations_manager.d_pressed_slot)
        self.mainwindow.key_up_down_signal.connect(self.annotations_manager.sroll_annotations)
        self.mainwindow.toggle_volume1_visibility_signal.connect(
            partial(self.data_manager.modify_layer, Layers.vol1, 'toggle_visibility'))
        self.mainwindow.toggle_volume2_visibility_signal.connect(
            partial(self.data_manager.modify_layer, Layers.vol2, 'toggle_visibility'))
        self.mainwindow.key_event_signal.connect(self.key_events)

        self.volume_pixel_signal.connect(self.mainwindow.set_volume_pix_intensity)
        self.volume2_pixel_signal.connect(self.mainwindow.set_volume2_pix_intensity)
        self.atlas_label_over_signal.connect(self.mainwindow.set_current_label)
        self.heatmap_pixel_signal.connect(self.mainwindow.set_data_pix_intensity)

        self.options_tab = OptionsTab(self.mainwindow, self.appdata)
        self.options_tab.flip_signal.connect(self.update_slice_views)

        self.filter_widget = LabelFilter(self.mainwindow)
        self.filter_widget.filter_label_signal.connect(self.filter_label)
        self.filter_widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.options_tab.toggle_filter_widget_signal.connect(self.filter_widget.toggle_visibility)


        # Sometimes QT console is a pain to install. If not availale do not make console tab
        if console_imported:
            self.console = Console(self.mainwindow, self)
        else:
            self.console = None

        self.dock_widget = ManagerDockWidget(self.model, self.mainwindow, self.appdata, self.data_manager,
                                             self.annotations_manager, self.options_tab, self.console, self.qc)
        self.dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)

        # Create the initial 3 orthogonal views. plus 3 hidden for the second row
        inital_views = [
            [Orientation.sagittal, 'red', 0, 1, False],
            [Orientation.coronal, 'blue', 0, 2, False],
            [Orientation.axial, 'green', 0, 3, False],
            [Orientation.sagittal, 'orange', 1, 1, True],
            [Orientation.coronal, 'grey', 1, 2, True],
            [Orientation.axial, 'cyan', 1, 3, True]
        ]

        self.mapper = Coordinate_mapper(self.views, self.appdata.get_flips())

        for v in inital_views:
            self.setup_views(*v)
        self.current_view = self.views[0]

        self.crosshair_visible = False

        self.data_manager.roi_signal.connect(self.mapper.roi_to_view)

        self.any_data_loaded = False
        self.crosshair_permanent = False
        self.gradient_editor_widget = None

        self.options_tab.set_orientations()

        self.annotation_radius_changed(self.appdata.annotation_circle_radius)

        self.check_vpv_version()

        self.atlas_meta = None

        self.data_manager.load_metadata_signal.connect(self.load_atlas_meta)

    def key_events(self, event:QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_F:
            self.filter_widget.toggle_visibility()


    def load_atlas_meta(self) ->Tuple[pd.DataFrame, str]:
        """
        Atlases loaded into the volume2 slot can be assigned label names and color information using a metadata file

        Returns
        -------
        Metadata file with (minimally) following columns
            label: int
            label_name: str
            colour: rgb (eg. 255,0,0) - optional

        The name of the metadata file
        """
        file_ = QtWidgets.QFileDialog.getOpenFileName(self.mainwindow, 'Load atlas metadata',
                                            self.appdata.last_atlas_metadata_file)
        if file_:
            self.appdata.last_atlas_metadata_file = str(file_[0])
            meta = pd.read_csv(file_[0], index_col=0)
            self.atlas_meta = meta

            # Todo, we need only one instace of LUT, not one in each SliceWidget
            # self.data_manager.luts.set_custom_atlas_colors(self.atlas_meta)
            self.data_manager.modify_layer(Layers.vol2, 'set_custom_labels', meta)

            return self.atlas_meta, Path(file_[0]).name

    def filter_label(self, labels: Iterable[int]):
        """
        Recieves a label to show. Pass to slice views

        Parameters
        ----------
        labels
            the label numbers to show, if 0 set to view all

        """
        for v in self.views.values():
            v.filter_label(labels)

    def set_orientation_visibility(self, visible: bool):
        for view in self.views.values():
            view.set_orientation_labels_visiblility(visible)

    def check_vpv_version(self):
        """
        Check the mpi2 github page for new versions
        If newer version available, set the link in a label on the data manager tab
        """
        # Catch all exceptions as we don't want this to cause problems for the rest of the app
        try:
            new_version = github.get_latest_github_version()
        except Exception:
            return

        if new_version:
            self.data_manager.ui.labelNewVersion.setText('New verion available\n{}'.format(new_version))

    def show_log(self):
        """
        Show the log in a scrossable window
        """

        log_viewer.Logview(self.mainwindow, log_path)

    def on_slice_view_mouse_move(self, x: int, y: int, z: int, src_view: SliceWidget):
        """
        Given coordinates of mouse hover position, emit signals to update the voxel value indicators.
        If shift key is pressed, activate synchronised viewing

        Parameters
        ----------
        src_view
            the emitting slice view widge
        x, y
            the hover coordinates in the 2D slice view
        z
            The current slice index of the slice view
        """

        vol = src_view.main_volume
        vol2 = src_view.secondary_volume
        hm = src_view.heatmap_volume

        if not vol:
            return

        if any(i < 0 for i in (x, y, z)):
            return

        # map to the volume space
        vol_points = self.mapper.view_to_volume(x, y, z, src_view.orientation, src_view.main_volume.shape_xyz())

        x1 = src_view.main_volume.shape_xyz()[0] - vol_points[0]

        self.mainwindow.set_mouse_position_indicator(*vol_points)

        # Get any flips that have been applied to the data
        flipx, flipy, flipz = src_view.get_flips()
        # Get the values of the voxels underneath the mouse pointer
        try:
            vol_hover_voxel_value = vol.get_data(Orientation.axial, vol_points[2],
                                                 xy=[x1, vol_points[1]])

        except IndexError:
            pass
        else:
            if x > 0 and x > 0:
                self.volume_pixel_signal.emit(round(float(vol_hover_voxel_value), 2))
                if vol2:
                    vol2_hover_voxel_value = vol2.get_data(Orientation.axial, vol_points[2], xy=[x1, vol_points[1]])
                    self.volume2_pixel_signal.emit((round(float(vol2_hover_voxel_value), 4)))

                if hm:
                    hm_hover_voxel_value = hm.get_data(Orientation.axial, vol_points[2], xy=[x1, vol_points[1]])
                    self.heatmap_pixel_signal.emit((round(float(hm_hover_voxel_value), 4)))

        # # If shift is pressed emit signal to get other views to get to the same or interscting slice
        modifiers = QtGui.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ShiftModifier:

            # With mouse move signal, also send current vol.
            # If veiews are not synchronised, syncyed slicing only occurs within the same volumes
            self.mouse_shift(x, y, z, src_view)

    def set_current_label(self, value):
        self.last_selected_label = value

        if self.atlas_meta is not None and value >=1:
            label_name = self.atlas_meta.at[int(value), 'label_name']
        else:
            label_name = ''
        self.atlas_label_over_signal.emit(label_name)

    def update_qc(self, *args, **kwargs):
        """
        We don't need all these parameters, but I'm just sharing a signal with the annotaitons for the time being
        """
        if self.qc.is_active:
            self.qc.label_clicked_slot(self.last_selected_label)


    def map_annotation_signal_view_to_view(self, slice_idx: int, x: int, y: int, src_view: SliceWidget,
                                           color: tuple=(255, 0, 0), radius: int=10, reverse: bool=False):
        """
        Upon getting a mouse click on a SliceWidget region, it will emit info here including position and the
        emitting view.  Map the coordinates between views so that they are correctly positioned

        Parameters
        ----------
        slice_idx: the current slice index of the emitting view
        x: the y position of the view clicked
        y: the y position of the view clicked
        src_view: the emitting view
        color: rgb color of the annotation marker
        radius: radius of the annotation marker
        reverse:

        """

        if not self.current_annotation_volume():
            self.annotations_manager.reset_roi()
            return

        if not self.annotations_manager.annotating:
            return
        dims = self.current_annotation_volume().shape_xyz()
        for dest_view in self.views.values():
            # First map the annotation marker between views
            dest_x, dest_y, dest_index = self.mapper.view_to_view(x, y, slice_idx, src_view.orientation,
                                                                  dest_view.orientation, dims)

            dest_view.set_slice(dest_index)
            # Set the annotation marker. Red for pre-annoation, green indicates annotation save
            dest_view.show_annotation_marker(dest_x, dest_y, color)

            # Add the coordinates to the AnnotationsWidget
            # The coordinates need to be in axial space do map back to them if necessary
            if dest_view.orientation == Orientation.axial:
                # Now map it back to image coordinates
                xa, ya, idxa = self.mapper.view_to_volume(x, y, slice_idx, src_view.orientation, dims)
                self.annotations_manager.set_annotation_position_label(xa, ya, idxa)

    def mouse_shift(self, x, y, z, src_view):
        """
        Gets mouse moved signal. Sets corresponding slices in other views if linked

        Parameters
        ----------
        z: int
            the current slice of the calling view
        x: int
            the x position of the mouse
        y: int
            the y position of the mouse
        src_view: SliceWidget
            the calling view
        """

        if not self.current_annotation_volume():
            return

        dims = self.current_annotation_volume().shape_xyz()

        for dest_view in self.views.values():

            dest_x, dest_y, dest_z = self.mapper.view_to_view(x, y, z, src_view.orientation, dest_view.orientation, dims)

            try:
                dest_view.set_slice(dest_z, crosshair_xy=(dest_x, dest_y))
            except IndexError:
                pass

    def current_annotation_volume(self):
        """
        Get the volume currently visible in the annotation view
        
        Returns 
        -------
        model.ImageVolume instance
        """
        if not self.current_view:
            return None
        return self.current_view.layers[Layers.vol1].vol

    def on_console_enter_pressesd(self):
        self.update_slice_views()

    def take_screen_shot(self):
        """
        Take screenshot of the slice views.
        Hide the sliders, take screenshot, then show slider
        Copy to clipboard and ask if it should be saved as a png

        """
        sshot = self.mainwindow.ui.centralwidget.grab()
        QtGui.QApplication.clipboard().setPixmap(sshot)



        if common.question_dialog(self.mainwindow, "Screenshot copied to clipboard", 'Save to file?'):

            path = QtWidgets.QFileDialog.getSaveFileName(self.mainwindow, 'Save screen shot',
                                                  self.appdata.last_screen_shot_dir)
            print(path)
            if path[0]:
                self.appdata.last_screen_shot_dir = str(Path(path[0]).parent)
                sshot.save(path[0])



    def volume_changed(self, vol_name):
        self.data_manager.volume_changed(vol_name)

    def set_current_view(self, slice_id):
        self.current_view = self.views[slice_id]

    def reset_roi(self):
        for view in self.views.values():
            view.switch_off_annotation()

    def current_orientation(self):
        return self.current_view.orientation

    def annotation_radius_changed(self, radius):
        for view in self.views.values():
            view.annotation_radius_changed(radius)

    def tab_changed(self, indx: int):
        """
        When changing to annotations tab, make sure all views are linked
        """
        self.data_manager.link_views = True
        self.annotations_manager.tab_changed(indx)

    def updating_started(self):
        self.updating_dlg = QtGui.QMessageBox()

    def updating_finished(self):
        self.updating_dlg.close()

    def display_update_msg(self, msg: str):
        self.updating_dlg.setText(msg)

    def set_view_controls_visibility(self, visible):
        for view in self.views.values():
            view.show_index_slider(visible)

    def show_color_scale_bars(self, visible):

        self.data_manager.show_color_scale_bars(visible)

    def show_scale_bars(self, visible):
        for view in self.views.values():
            view.update()
            view.show_scale_bar(visible)

    def update_slice_views(self):

        for view in self.views.values():
            view.update_view()

    def setup_views(self, orientation: Orientation, color: tuple, row: int, column: int, hidden: bool=False):
        """
        Create all the orthogonal views and setup the signals and slots
        """
        view = self.add_view(self.view_id_counter, orientation, color, self.mapper)
        # view.mouse_shift.connect(self.mouse_shift)
        # view.mouse_pressed_signal.connect(self.dock_widget.mouse_pressed)
        view.mouse_pressed_annotation_signal.connect(self.map_annotation_signal_view_to_view)
        view.mouse_pressed_annotation_signal.connect(self.update_qc)
        view.crosshair_visible_signal.connect(self.crosshair_visible_slot)
        view.scale_changed_signal.connect(self.zoom_changed)
        view.slice_index_changed_signal.connect(self.index_changed)
        view.move_to_next_vol_signal.connect(self.move_to_next_vol)
        self.data_manager.scale_bar_color_signal.connect(view.set_scalebar_color)
        self.crosshair_visible_signal.connect(view.show_crosshair)
        self.crosshair_invisible_signal.connect(view.hide_crosshair)
        self.view_id_counter += 1
        self.mainwindow.add_slice_view(view, row, column)
        view.setHidden(hidden)

        # Connect the mouse moving so we can get pixel/label value and position
        view.mouse_moved_signal.connect(self.on_slice_view_mouse_move)

    def gradient_editor(self):
        # Activeated 6 times on one click so bogdge for now
        self.ge = GradientEditor(self)
        self.ge.sigFinished.connect(self.set_heatmap_luts)
        self.ge.show()

    def set_heatmap_luts(self, luts):
        for view in self.views.values():
            if view.layers[Layers.heatmap].vol:
                view.layers[Layers.heatmap].vol.pos_lut = luts[0]
                #view.display[Layer.heatmap].vol.neg_lut = luts[1]
                view.layers[Layers.heatmap].update()

    def move_to_next_vol(self, view_id, reverse=False):
        if self.data_manager.link_views:
            for view in self.views.values():
                view.move_to_next_volume(reverse)
        else:
            self.views[view_id].move_to_next_volume(reverse)
        self.data_manager.switch_selected_view(view_id)

    def recalc_connected_components(self):
        self.current_view.layers[Layers.heatmap].vol.find_largest_connected_components()
        self.data_manager.update_connected_components(self.current_view.layers[Layers.heatmap].vol.name)

    def add_view(self, id_, orientation, color, mapper):
        """
        Setup each orthogonal viewer

        Parameters
        ----------
        id_: int
        orientation: Orientation
        Initial orientation
        color: str
            just a color word at the moment eg: red
        mapper coordinate_mapper.Coordinate_mapper
            Hold info such as whether the current orientation should have flips applied

        Returns
        -------
        SliceWidget

        """
        view = SliceWidget(orientation, self.model, color, mapper)
        view.manage_views_signal.connect(self.update_manager)
        self.views[id_] = view
        return view

    def toggle_dock_widget_visibility(self):
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.update_manager()

    def toggle_link_views(self):
        if self.data_manager.link_views:
            link = False
        else:
            link = True
        self.data_manager.on_link_views(link)

    def update_manager(self, slice_id=0):  # called from data_manager:update_manager
        """
        update the slice manager with data from a slice view
        :param slice_id: Id of the SliceWidget that this current widget was activated from
        """
        self.current_view = self.views[slice_id]
        self.data_manager.switch_selected_view(slice_id)
        self.mainwindow.show_manager(self.dock_widget)
        self.mainwindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.show()

    def remove_views(self, row, column):
        self.mainwindow.remove_view(row, column)

    def index_changed(self, orientation, id_, idx):
        orientation = str(orientation)
        if not self.data_manager.link_views:
            return
        for view in self.views.values():
            if view.id == id_:  # The view that emiited the signal
                continue
            if orientation == view.orientation: # For now, only zoom views with the same orientation
                view.set_slice(idx)

    def zoom_changed(self, orientation, id_, ranges):
        """
        Called when a slice view zooms in.
        Parameters
        ----------
        orientation: string
            orientation of the calling slice view
        id: int
            id of the calling slice view
        scale: list
            [[xstart, xend], [ystart, yend]]
        """
        if not self.data_manager.link_views:
            return
        for view in self.views.values():
            if view.id == id_:  # The view that emiited the signal
                continue
            if orientation == view.orientation: # For now, only zoom views with the same orientation
                view.set_zoom(ranges[0], ranges[1])

    def crosshair_visible_slot(self, visible):
        if visible:
            self.crosshair_visible_signal.emit()
        elif not self.crosshair_permanent:
            self.crosshair_invisible_signal.emit()

    def set_crosshair_permanent(self, is_visible_always):
        self.crosshair_permanent = is_visible_always
        self.crosshair_invisible_signal.emit()

    def data_labels_visible(self, visible):
        for view in self.views.values():
            view.set_data_label_visibility(visible)

    def data_processing_finished_slot(self):
        self.data_processing_finished_signal.emit()

    def show_saved_annotations(self, x: int, y: int, z: int, color: list, radius: int):
        """
        When clicking on a saved annotation  from the table, highlight in 'color' the location
        Bit of a bodge this. Need to move some of it to coordinate mapper


        Parameters
        ----------
        x
        y
        z
        color
        radius

        Returns
        -------

        """
        dims = self.current_annotation_volume().shape_xyz()
        for dest_view in self.views.values():
            dest_x, dest_y, dest_z = self.mapper.view_to_view(x, y, z, Orientation.axial, dest_view.orientation,
                                                              dims, from_saved=True)
            dest_view.set_slice(dest_z)
            dest_view.show_annotation_marker(dest_x, dest_y, color)

    def control_visiblity(self, visible):
        for slice_ in self.slice_widgets.values():
            slice_.show_controls(visible)

    def scale_bar_visible(self, visible):
        pass
        for slice_ in self.slice_widgets.values():
            slice_.scale_bar_visible(visible)

    def load_data_slot(self, dragged_files=None):
        """

        Parameters
        ----------
        dragged_files

        Returns
        -------

        """
        last_dir = self.appdata.get_last_dir_browsed()
        # Convert QStrings to unicode in case they contain special characters
        files = [x for x in dragged_files]
        importer.Import(self.mainwindow, self.importer_callback, self.virtual_stack_callback, last_dir, self.appdata,
                        files)

    def check_non_ras(self):
        return
        for vol in self.model.all_volumes():
            if vol.dir_ != common.RAS_DIRECTIONS:
                common.info_dialog(self.mainwindow, "Image format warning!",
                                   "At lease one of your loaded volumes is not in RAS format For IMPC annotation enure HARP v2.3.0 or aboave. Or use download data from the DCC")
                break

    def browse_files(self):
        last_dir = self.appdata.get_last_dir_browsed()
        if last_dir:
            last_dir = last_dir[0]
            if not os.path.isdir(last_dir):
                files = QtWidgets.QFileDialog.getOpenFileNames(self.mainwindow, "Select files to load")
            else:
                files = QtWidgets.QFileDialog.getOpenFileNames(self.mainwindow, "Select files to load", last_dir)
        self.load_data_slot(files[0])

    def clear_views(self):
        self.model.clear_data()
        for view in self.views.values():
            view.clear_layers()
        self.data_manager.clear()
        self.annotations_manager.clear()
        self.any_data_loaded = False
        # self.update()

    def virtual_stack_callback(self, file_paths, last_dir):
        if len(file_paths) > 0:
            self.appdata.set_last_dir_browsed(last_dir)
            try:
                self.model.add_volume(file_paths, 'virtual_stack', memory_map=True)
            except ValueError:
                QtGui.QMessageBox.warning(self.mainwindow, 'Loading error',
                    "Virtual stack could not be loaded\nAre all images the same dimension?", QtGui.QMessageBox.Ok)
            else:
                self.appdata.set_last_dir_browsed(last_dir)
                if self.dock_widget.isVisible():
                    self.dock_widget.update()
                if not self.any_data_loaded:
                    #  Load up one of the volumes just loaded into the bottom layer
                    self.add_initial_volume()
                    self.any_data_loaded = True

    def add_initial_volume(self):
        """
        Called when loading in volumes for the first time, to get a volume displayed without havong to manually set it
        """
        try:
            init_vol = self.model.volume_id_list()[0]
            for view in self.views.values():
                view.layers[Layers.vol1].set_volume(init_vol, initial=True)
                # view.display[Layer.vol1].update()  # This should make sure 16bit images are scaled correctly at loading?
                view.update_view()
        except IndexError:  # No Volume objects have been loaded
            logging.warn('No volumes loaded')

        try:  # See if we have any Data objects loaded
            init_vol = self.model.data_id_list()[0]
            for view in self.views.values():
                view.layers[Layers.heatmap].set_volume(init_vol, initial=True)
        except IndexError:  # No Volume objects have been loaded
            pass

    def importer_callback(self, volumes, heatmaps, annotations, vector_files, image_series,
                          impc_analysis, last_dir, memory_map=False, distribute:bool=False):
        """
        Recieves a list of files to open from the Importer widget

        Parameters
        ----------
        dual_datafiles: str
            path to config file for loading paired tval/pval files
        :return:
        """
        if len(impc_analysis) > 0:
            self.load_impc_analysis(impc_analysis[0])
        if len(volumes) > 0:
            self.load_volumes(volumes, 'vol', memory_map)
        if len(heatmaps) > 0:
            self.load_volumes(heatmaps, 'heatmap', memory_map, fdr_thresholds=False)
        if len(vector_files) > 0:
            self.load_volumes(vector_files, 'vector', memory_map)
        if len(image_series) > 0:
            self.model.load_image_series(image_series, memory_map)
            if not self.any_data_loaded:
                self.add_initial_volume()

        # Now load the annotations from the Importer. Only load if there is a corresponding volume with the same id
        if len(annotations) > 0:
            self.load_annotations(annotations) # From importer

        self.appdata.set_last_dir_browsed(last_dir)
        self._auto_load_annotations(volumes)

        if self.dock_widget.isVisible():
            self.data_manager.update()
            self.annotations_manager.update()

        if distribute:
            self.distribute_volumes_across_views()

    def distribute_volumes_across_views(self):
        """
        When loading a volume, the same volume is loaded into into Slice view .
        This method tries to distribute amongs the views and set sets them to all the same orientation

        """
        # Get the available volumes
        vol_list = self.model.volume_id_list()

        if len(vol_list) < 2:
            return

        else:
            for i, view in self.views.items():
                view.layers[Layers.vol1].set_volume(vol_list[i])
                view.set_orientation(Orientation.sagittal)
                if len(vol_list) < 4:
                    if i >= 2:
                        return
                else:
                    if i >= 5:
                        self.data_manager.show2Rows(True)
                        return

    def _auto_load_annotations(self, volumes):
        """
        Look for previously-written annotation files in  the annotation directory (folder with same name as loaded img)
        If present try to load
        """
        import fnmatch

        annotation_xml_files = []

        for vol_path in volumes:

            # The annotation dir path will be the same as the image minus the file extension
            ann_dir = os.path.splitext(vol_path)[0]

            if not ann_dir:
                return

            if not isdir(ann_dir):
                logging.info("{}, is not a valid annotation directory".format(ann_dir))
                continue

            ann_files = os.listdir(ann_dir)
            xml_annotation_file = None

            for af in ann_files:
                if fnmatch.fnmatch(af, '*experiment.impc.xml'):
                    xml_annotation_file = join(ann_dir, af)
                    break

            if xml_annotation_file:
                annotation_xml_files.append(xml_annotation_file)

        if annotation_xml_files:
            self.load_annotations(annotation_xml_files)

    def load_annotations(self, annotation_file_list):
        """
        Load annotations that were previously saved as xml

        Parameters
        ----------
        annotation_file_list

        Returns
        -------

        """
        non_loaded = []
        for path in annotation_file_list:  # At this point looked_at set to True
            error = self.model.load_annotation(path)
            if error:
                non_loaded.append(path)
                common.error_dialog(self.mainwindow, 'Annotations not loaded', error)
            else:
                # Load annotations - these should be called within self.model.load_annotation
                self.annotations_manager.populate_available_terms()
                self.annotations_manager.update()
        if not non_loaded:
            common.info_dialog(self.mainwindow, 'Load success', 'Annotations loaded')

    def load_volumes(self, file_list, data_type, memory_map=False, fdr_thresholds=False) -> List:
        """
        Load volumes from a list of paths.

        Parameters
        ----------
        file_list: list
            list of paths to volumes
        data_type: str
            vol data etc
        memory_map: bool
            whether to memory map after reading
        fdr_thresholds: dict
            q -> t statistic mappings
                {0.01: 3.4,
                0.05:, 3.1}
        Returns
        -------
        List of uunique volume ids.
        """

        non_loaded = []
        loaded_ids = []

        for i, vol_path in enumerate(file_list):
            try:

                loaded_id = self.model.add_volume(vol_path, data_type, memory_map, fdr_thresholds)
                self.appdata.add_used_volume(vol_path)
                if not self.any_data_loaded:
                    #  Load up one of the volumes just loaded into the bottom layer
                    self.add_initial_volume()
                    self.any_data_loaded = True
            except (IOError, RuntimeError) as e:  # RT error Raised by SimpleITK
                print(e)
                non_loaded.append(vol_path)
            else:
                loaded_ids.append(loaded_id)
        if len(non_loaded) > 0:
            common.error_dialog(self.mainwindow, 'Volumes not loaded', '\n'.join(non_loaded))
        # self.any_data_loaded
        self.check_non_ras()
        self._auto_load_annotations(file_list)
        return loaded_ids

    def img_ids(self):
        return self.model.volume_id_list(sort=False)

    def load_impc_analysis(self, impc_zip_file):
        """
        Load a zip file containing the results of the IMPC automated analysis (TCP pipeline)
        Parameters
        ----------
        impc_zip_file: str
            path tho analysis results zip
        """
        try:
            zf = zipfile.ZipFile(impc_zip_file)
        except zipfile.BadZipFile as e:
            common.error_dialog(self.mainwindow, 'Zip file error', 'Cannot read IMPC analysis zip file\nThe zip may be corrupted')
            return
        names = zf.namelist()

        file_names = addict.Dict(
            {'intensity_tstats_file': None,
             'jacobians_tstats_file': None,
             'qvals_intensity_file': None,
             'qvals_jacobians_file': None,
             'popavg_file': None}
        )

        files_remaining = []
        for name in names:
            name_lc = name.lower()
            if 'intensities-tstats' in name_lc:
                file_names.intensity_tstats_file = name
            elif 'jacobians-tstats' in name_lc:
                file_names.jacobians_tstats_file = name
            elif 'qvals-intensities' in name_lc:
                file_names.qvals_intensity_file = name
            elif 'qvals-jacobians' in name_lc:
                file_names.qvals_jacobians_file = name
            elif 'popavg' in name_lc:
                file_names.popavg_file = name
            else:
                files_remaining.append(name)

        if all(file_names.values()):
            td = tempfile.TemporaryDirectory()
            zf.extractall(td.name)
            popavg = join(td.name, file_names.popavg_file)
            self.load_volumes([popavg], 'vol')

            # get the trhesholds from the csv files
            qval_int_csv = join(td.name, file_names.qvals_intensity_file)
            intensity_fdr_thresh = self.extract_fdr_thresholds(qval_int_csv)

            inten_tstat = join(td.name, file_names.intensity_tstats_file)

            self.load_volumes([inten_tstat], 'heatmap', memory_map=False,
                              fdr_thresholds=intensity_fdr_thresh)

            qval_jac_csv = join(td.name, file_names.qvals_jacobians_file)
            jacobian_fdr_thresh = self.extract_fdr_thresholds(qval_jac_csv)

            jac_tstat = join(td.name, file_names.jacobians_tstats_file)

            self.load_volumes([jac_tstat], 'heatmap', memory_map=False,
                              fdr_thresholds=jacobian_fdr_thresh)

            # Load any other volumes in the zip. Probably will be mutants
            mutants = [join(td.name, x) for x in files_remaining if x.endswith('nrrd')]
            self.load_volumes(mutants, 'vol', memory_map=False)

            if not intensity_fdr_thresh:
                common.info_dialog(self.mainwindow, "No hits",
                                   "There are no hits in the intensity heatmap. The threshold is set to max")
            if not jacobian_fdr_thresh:
                common.info_dialog(self.mainwindow, "No hits",
                                   "There are no hits in the jacobian heatmap. The threshold is set to max")
        else:
            failed = []
            for key, name in file_names.items():
                if not name:
                    failed.append(key)
            common.error_dialog(self.mainwindow, 'Error loading file', 'The following files could not be found in the zip\n {}'.format('\n'.join(failed)))
            print('IMPC analysis data failed to load. The following files could not be found in the zip')
            print(failed)

    @staticmethod
    def extract_fdr_thresholds(stats_info_csv):
        """
        Given a csv path containing the stats summary from the TCP pipeline (or LAMA)
        read the fdr threshold q value and corresponding t-statsitc into a dict

        Parameters
        ----------
        stats_info_csv: str
            path to csv
        Returns
        -------
        dict of q to t mappings
            {0.1: 2.6,
            0.2: 2.2...}
        None if there are no t-thresholds for any given q-value cutoff
        """
        from collections import OrderedDict
        q_t = OrderedDict()

        with open(stats_info_csv, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            reader.__next__()  # remove header

            for line in reader:

                try:
                    q = float(line[0])
                except ValueError:
                    print("There is a problem with the stats info file. Cannot read the q-value '{}'from file {}".format(
                        line[0], stats_info_csv
                    ))
                    return {}  # return an empty dict
                try:
                    t = float(line[3])
                except ValueError:  # NAs are here when there are below the minimu, threshold
                    t = None
                q_t[q] = t
        if any(q_t.values()):
            return q_t
        else:
            return None  # No t thresholds. Proably no hits in this heatmap

    def activate_view_manager(self, view_widget_id):
        """
        :param sliceid: int ,
        :return:
        """
        self.dock_widget.show(view_widget_id)

    def close(self):
        print('saving settings to {}'.format(self.appdata.app_data_file))
        self.appdata.write_app_data()
        self.model.write_temporary_annotations_metadata()
        print('exiting')

    def on_view_new_screen(self):

        # Work out how to maximize on anotehr screen
        # dtw = QtGui.QDesktopWidget()
        # current_screen = dtw.screenNumber(self.mainwindow)
        # print 'scree', dtw.screenGeometry(3)

        pass
        # self.mainwindow2 = main_window.Main(self, self.app_data)
        # self.mainwindow2.setWindowTitle('Harwell vol viewer (2)')
        #
        # self.slice_sag2 = SliceWidget('sagittal', self.model, 'yellow')
        # self.slice_axi2 = SliceWidget('axial', self.model, 'magenta')
        # self.slice_cor2 = SliceWidget('coronal', self.model, 'orange')
        #
        # self.slice_cor2.manage_views_signal.connect(self.activate_view_manager)
        # self.slice_axi2.manage_views_signal.connect(self.activate_view_manager)
        # self.slice_sag2.manage_views_signal.connect(self.activate_view_manager)
        #
        # self.slice_widgets2 = [self.slice_sag2, self.slice_cor2, self.slice_axi2]
        #
        # self.mainwindow2.add_slice_views(self.slice_widgets2)
        # self.model.register_slice_widgets(self.slice_widgets2)


def update_check():
    pass


