from PyQt5 import QtGui
import pyqtgraph as pg
import numpy as np
from .layer import Layer


class HeatmapLayer(Layer):
    def __init__(self, *args):
        super(HeatmapLayer, self).__init__(*args)
        self.neg_image_item = pg.ImageItem(autoLevels=False)
        self.neg_image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self.neg_image_item.setLookupTable(self.lt._hot_red_blue()[1])
        self.image_items.append(self.neg_image_item)

        self.pos_image_item = pg.ImageItem(autoLevels=False)
        self.pos_image_item.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self.pos_image_item.setLookupTable(self.lt._hot_red_blue()[0])
        self.image_items.append(self.pos_image_item)

    def update(self, auto_levels=False):
        """
        :param orientation:
        :param auto_levels:
        :return:
        """
        if self.vol and self.vol != 'None':
            self.neg_image_item.setLookupTable(self.vol.negative_lut)
            self.pos_image_item.setLookupTable(self.vol.positive_lut)
            self.neg_image_item.setLevels(self.vol.neg_levels, update=False)
            self.pos_image_item.setLevels(self.vol.pos_levels, update=False)
            self.reload()

    def reload(self):
        """
        """
        # need to work out if this is needed. It currently puts heatmap data in wrong flip at first view
        if self.vol:
            self.set_slice(self.parent.current_slice_idx)
           
    def set_volume(self, volname):
        """
        :param vol, Volume object from model.py
        """
        if volname == "None":
            self.volume_label_signal.emit("None")
            self.clear()
            self.vol = None
            return

        self.volume_label_signal.emit(volname)
        self.vol = self.model.getvol(volname)
        self.neg_image_item.setLookupTable(self.vol.negative_lut)
        self.pos_image_item.setLookupTable(self.vol.positive_lut)
        self.set_slice(self.parent.current_slice_idx)

    def set_slice(self, index: int):
        """Set the heatmap layer to the specified index

        Parameters
        ----------
        index: int
            the index to set

        """
        opacity = 1.0 if self.isvisible else 0.0
        if self.vol and self.vol != "None":

            flip_x, flip_y, flip_z = self.parent.get_flips()

            try:
                slices = self.vol.get_data(self.parent.orientation, index - 1,
                                           flip_x, flip_z, flip_y)
            except IndexError as e:
                print(e)
                return

            for i, ii in enumerate(self.image_items):
                ii.setImage(slices[i], autoLevels=False, opacity=opacity)

    def set_t_threshold(self, t):
        if self.vol:
            # This takes a while, so let's have a progress indicator
            self.vol.set_t_threshold(t)

    def clear(self):
        """
        Override as we have multiple imageitems for
        :return:
        """
        self.vol = None
        # #clear the image item with an empty array
        #
        self.image_items[0].setImage(opacity=0.0)
        self.image_items[1].setImage(opacity=0.0)
        # self.item = None
