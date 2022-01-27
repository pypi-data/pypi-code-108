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

import numpy as np
import copy
import csv
import json

import pandas as pd

from vpv.common import generic_anatomy_label_map_path


# ANATOMY_LABELS_FILE = 'generic_anatomy.csv'


class Lut(object):
    def __init__(self):
        self.base = np.zeros((256, 3), dtype=np.ubyte)
        self.anatomy_lut = self.set_setup_anatomy_label_map()
        self.custom_atlas_lut = None

    def set_setup_anatomy_label_map(self):
        rgb_values = []
        with open(generic_anatomy_label_map_path, 'r') as fh:
            csvreader = csv.reader(fh)
            for row in csvreader:
                rgb = [int(x) for x in row[2].split(',')]
                rgb.append(255)  # add opacity
                rgb_values.append(rgb)
        # Set the first value (background to transparent)
        rgb_values[0][3] = 0.0
        lut = np.array(rgb_values)
        return lut.astype(np.float)

    def set_custom_atlas_colors(self, atlas_metadata: pd.DataFrame):
        """
        If an atlas metadata file is loaded with a 'colour' column use that as the color map
        """
        rgb_values = []

        if 'colour' not in atlas_metadata:
            print('Atlas metadata dataframe does not have a "colour" column')
            self.custom_atlas_lut = None
            return

        # Convert string list to an actual list
        md = atlas_metadata.copy()

        # # If there is a qc_group column in metadata file, group all the colors together
        if 'qc_group' in atlas_metadata:

            gb_qc = md.groupby('qc_group')
            for group_name, gdf in gb_qc:
                # Get the colour of the first label in the group
                col = gdf.iloc[0, gdf.columns.get_loc('colour')]

                # Apply same color to all in group
                md.loc[md.index.isin(gdf.index), 'colour'] = [col] * len(gdf)

        # Convert string representation to list of ints
        md.colour = md.colour.apply(json.loads)

        highest_val = max(atlas_metadata.index) + 1
        for i in range(highest_val):
            if i == 0:
                rgb = (0, 0, 0, 0)
            try:
                rgb = md.at[i, 'colour']
                rgb.append(255)  # add opacity
            except KeyError:
                rgb = (0, 0, 0, 0) # Missing label values

            if len(rgb) != 4:
                raise ValueError
            rgb_values.append(rgb)

        lut = np.array(rgb_values)
        self.custom_atlas_lut = lut.astype(np.float)

    def get_lut(self, lut_name):
        return getattr(self, '_' + lut_name)()

    def lut_list(self):
        return ['red', 'green', 'blue', 'inverted_grey', 'grey', 'cyan', 'yellow', 'magenta', 'anatomy_labels',
                'custom_atlas_labels']

    def heatmap_lut_list(self):
        return ['hot_red_blue', 'hot_all']

    def _hot_all(self):
        colours = (
            (0.00, 0.0, 0.0, 0.0),
            (0.25, 0.5, 0.0, 0.0),
            (0.50, 1.0, 0.0, 0.5),
            (0.75, 1.0, 0.5, 1.0),
            (1.00, 1.0, 1.0, 1.0)
        )
        lut_red = self.interpolate_colors(colours, 256)

        colours = (
            (0.00, 0.0, 0.0, 0.0),
            (0.25, 0.0, 0.0, 0.5),
            (0.50, 0.0, 0.5, 1.0),
            (0.75, 0.5, 1.0, 1.0),
            (1.00, 1.0, 1.0, 1.0)
        )
        lut_blue = self.interpolate_colors(colours, 256)[::-1]
        return lut_red, lut_blue

    def _hot_red_blue(self):
        """

        Returns
        -------
        The red and blue LUTs as a list
        """
        #red
        colours = (
            (0.25, 0.5, 0.0, 0.0),
            (0.25, 1.0, 0.0, 0.0),
            (0.50, 1.0, 0.0, 0.5),
            (0.75, 1.0, 0.5, 1.0),
            (1.00, 1.0, 1.0, 1.0)
        )
        red = self.interpolate_colors(colours, 256)
        red[0][3] = 0.0

        #blue
        colours = (
            (0.25, 0.0, 0.0, 0.5),
            (0.25, 0.0, 0.0, 1.0),
            (0.50, 0.0, 0.5, 1.0),
            (0.75, 0.5, 1.0, 1.0),
            (1.00, 1.0, 1.0, 1.0)
        )
        blue = self.interpolate_colors(colours, 256)[::-1]
        blue[-1][3] = 0.0
        return [red, blue]

    def _custom_atlas_labels(self):
        return self.custom_atlas_lut, 'custom_atlas_labels'

    def transparent(self):
        lut = np.zeros((256, 4), dtype=np.ubyte)
        # lut[:, 2] = np.repeat(255, 256)
        # lut[:, 3] = np.arange(255, -1, -1)
        return lut, 'transparent'

    def _red(self):
        lut = copy.deepcopy(self.base)
        lut[:, 0] = np.arange(0, 256, 1)
        return lut, 'red'

    def _anatomy_labels(self):
        return self.anatomy_lut, 'anatomy_labels'

    def _green(self):
        lut = copy.deepcopy(self.base)
        lut[:, 1] = np.arange(0, 256, 1)
        return lut, 'green'

    def _blue(self):
        lut = copy.deepcopy(self.base)
        lut[:, 2] = np.arange(0, 256, 1)
        return lut, 'blue'

    def _inverted_grey(self):
        lut = copy.deepcopy(self.base)
        lut[:, 0] = np.arange(255, -1, -1)
        lut[:, 1] = np.arange(255, -1, -1)
        lut[:, 2] = np.arange(255, -1, -1)
        return lut, 'inverted_grey'

    def _grey(self):
        lut = copy.deepcopy(self.base)
        lut[:, 0] = np.arange(0, 256, 1)
        lut[:, 1] = np.arange(0, 256, 1)
        lut[:, 2] = np.arange(0, 256, 1)
        return lut, 'grey'

    def _cyan(self):
        lut = copy.deepcopy(self.base)
        lut[:, 1] = np.arange(0, 256, 1)
        lut[:, 2] = np.arange(0, 256, 1)
        return lut, 'cyan'

    def _yellow(self):
        lut = copy.deepcopy(self.base)
        lut[:, 0] = np.arange(0, 256, 1)
        lut[:, 1] = np.arange(0, 256, 1)
        return lut, 'yellow'

    def _magenta(self):
        lut = copy.deepcopy(self.base)
        lut[:, 0] = np.arange(0, 256, 1)
        lut[:, 2] = np.arange(0, 256, 1)
        return lut, 'magenta'


    def interpolate_colors(self, colors, no_colors, nextNum=1, reverse=True):
        # Get name
        # cc = 1
        lut = []

        # Number of colours in each band
        band_cols = int(np.ceil(no_colors / 4))
        noInterpColors = [band_cols] * 4
        noBaseColors = len(colors) - 1

        for i in range(noBaseColors):

            argb1 = colors[i]
            start = np.array([float(c) for c in argb1])

            argb2 = colors[i + 1]
            stop = np.array([float(c) for c in argb2])

            step = (stop - start) / noInterpColors[i]

            for j in range(0, noInterpColors[i]):

                # Compute interpolated colour
                interp = ((start + (j * step)) * 255).astype(int)
                interp = [interp[k] for k in [1, 2, 3, 0]]

                if i + j > 0:
                    lut.append(interp)
                    # nextNum += 1
                    # cc += 1(map(str, interp))
                    lut.append(interp)
        np_lut = np.array(lut).reshape(-1, 4)  # To reshape based just on columns set row to -1
        return np_lut













