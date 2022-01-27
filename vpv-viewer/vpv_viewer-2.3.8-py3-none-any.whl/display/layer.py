from PyQt5 import QtCore, Qt
from vpv.utils.lookup_tables import Lut
import numpy as np


class Layer(Qt.QObject):

    volume_label_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent, layer_type, model):
        """
        The base class that controls the display of of one layer of data. Is extended to display heatmap data and vector
        data. The main function is to get data into a pytgraph ImageItem object which is then displayed.

        Attributes
        ----------
        model: model.model
            contains all the data
        parent: display.SliceWidget
            the parent view widget
        image_item: pyqtgrapgh.ImageItem
            The image to be displayed is put in here

        """
        super(Layer, self).__init__()
        # If it's a data volume, dont add slider, add number box to filter q-values
        self.model = model
        self.parent = parent
        self.image_items = []
        self.image_item = None  # Set in the subclasses
        self.vol = None  # When setting to "None" in the view manager we get problems. Needs rewriting
        self.layer_type = layer_type # this should be unique
        self.lt = Lut()  # Used in subcalsses
        self.isvisible = True
        self.opacity = 1.0
        self._show_labels = [0]  # show all labels to start with (if label layer)

    @property
    def show_labels(self):
        return self._show_labels

    @show_labels.setter
    def show_labels(self, labels):
        self._show_labels = labels

    def clear(self):
        """
        To clear the pg.imageitem set the slice to all zeros
        Returns
        -------

        """
        slice_ = np.copy(self.image_item.image)
        try:
            slice_[:] = 0
        except IndexError:
            return
        self.image_item.setImage(slice_)

    def update(self, auto_levels=False):
        """
        Sets the orientation and centres the image at the mid-slice
        :param orientation:
        :param auto_levels:
        :return:
        """
        if self.vol and self.vol != 'None':
            self.image_item.setLevels(self.vol.levels, update=False)
            self.image_item.setLookupTable(self.lut[0])
            self.reload()

    def reload(self):
        """
        reload the current image. For example when the orientation has changed
        """
        self.set_slice(self.parent.current_slice_idx)

    def set_volume(self, volname, initial=False):
        """
        :param vol, Volume object from model.py
        """

        if volname == "None" or volname is None:
            self.volume_label_signal.emit("None")
            self.clear()  # This clears the image
            self.vol = None
            return

        self.volume_label_signal.emit(volname)

        self.vol = self.model.getvol(volname)
        if not self.vol:
            print(f'cannot find vol: {volname}')
            return

        # self.set_series_slider()

        orientation = self.parent.orientation
        self.name = self.vol.name
        self.image_item.setZValue(self.layer_type.value)

        dim_len = self.vol.dimension_length(orientation)

        # Try setting the new volume to the slice index of the current volume. If out of bounds, set to midslice
        if self.parent.current_slice_idx + 1 > dim_len or initial:
            slice_indx = dim_len / 2
        else:
            slice_indx = self.parent.current_slice_idx
        # slice_ = self.vol.get_data(orientation, int(slice_indx))  # DELETE
        self.parent.set_slice_slider(dim_len, slice_indx)

        # This fixes problem with linked zooming
        if initial:
            self.parent.viewbox.autoRange()
        self.parent.scalebar.updateBar()

    def set_slice(self, index: int):
        opacity = self.opacity if self.isvisible else 0.0
        flip_x, flip_y, flip_z = self.parent.get_flips()

        if self.vol:

            try:
                slice_ = self.vol.get_data(self.parent.orientation, index,
                                                       flip_x, flip_z, flip_y)

                if self._show_labels != [0]:
                    slice_ = np.copy(slice_)
                    slice_[~np.isin(slice_, self._show_labels)] = 0

                self.image_item.setImage(slice_, autoLevels=False, opacity=opacity)

            except IndexError as e:
                print(e)

    def set_series_slider(self):
        if not self.vol or self. vol == 'None':
            return
        if self.vol.data_type == 'series':
            num_vols_in_series = len(self.vol.images)
            self.parent.ui.seriesSlider.setRange(0, num_vols_in_series - 1)
            self.parent.ui.seriesSlider.valueChanged.connect(self.series_slider_changed)
            self.parent.ui.seriesSlider.show()
            self.parent.ui.labelImageSeriesNumber.show()
        else:
            self.parent.ui.seriesSlider.hide()
            self.parent.ui.labelImageSeriesNumber.hide()

    def series_slider_changed(self, idx):
        self.vol.set_image(idx)
        self.parent.ui.labelImageSeriesNumber.setText(str(idx))
        self.reload()

    def set_visibility(self, isvisible: bool):
        self.isvisible = isvisible

    def toggle_visibility(self):
        if self.isvisible:
            self.isvisible = False
        else:
            self.isvisible = True

    def set_opacity(self, opacity: float):
        self.opacity = opacity
