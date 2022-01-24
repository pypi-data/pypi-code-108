"""
This module implements the ``LabellingAssitant`` class
inheriting from QWidget.
"""
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import (QWidget, QGridLayout,
                            QPushButton, QCheckBox)

import numpy as np
import matplotlib.pyplot as plt

from napari.layers.labels.labels import Labels

class LabellingAssistant(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # Prints stats as stdout
        btn = QPushButton("Print stats to stdout")
        btn.clicked.connect(self._std_stats)

        # Generates a figure
        bar = QPushButton("View pixel distribution")
        bar.clicked.connect(self._generate_plot)

        # Boolean for excluding unlabelled region
        self.exclude_unlabelled = QCheckBox("Exclude unlabelled data")
        self.exclude_unlabelled.setChecked(False)
        self.exclude_unlabelled.toggled.connect(self.onClicked)

        # Boolean for excluding background labelled region
        self.exclude_bg_label = QCheckBox("Exclude background labels (iff BG ID == 1)")
        self.exclude_bg_label.setChecked(False)
        self.exclude_bg_label.toggled.connect(self.onClicked)

        # Boolean for verbose stdout
        self.verbose_output = QCheckBox("Verbose")
        self.verbose_output.setChecked(False)
        self.verbose_output.toggled.connect(self.onClicked)

        self.setLayout(QGridLayout())
        self.layout().addWidget(self.verbose_output)
        self.layout().addWidget(btn)
        self.layout().addWidget(bar)
        self.layout().addWidget(self.exclude_unlabelled)
        self.layout().addWidget(self.exclude_bg_label)

    def onClicked(self):
        _ = self.sender()

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

    def _std_stats(self):
        get_stats(self.viewer.layers, self.verbose_output.isChecked())
    
    def _generate_plot(self):
        view_stats(self.viewer.layers,
                   self.exclude_unlabelled.isChecked(),
                   self.exclude_bg_label.isChecked(),
                   self.verbose_output.isChecked())


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return LabellingAssistant, {'area': 'left'}

def fetch_data(label_layers):
    data = []
    num_labels = 0
    num_layers = 0
    for i, layer in enumerate(label_layers):
        if type(layer) == Labels:
            num_layers += 1
            array = layer.data
            data.append(array)
            num_labels = max(num_labels, array.max() + 1)
        else:
            continue
    return data, num_labels, num_layers

def get_counts(label_array, max_labels, verbose):
    label_list = list(range(max_labels))

    u, c = np.unique(label_array, return_counts=True)

    if verbose:
        print(f"unique labels: {u}\ncount (in pixels): {c}")

    count_list = []
    for i in label_list:
        if i not in u:
            if verbose:
                print('missing label: ', i)
            count_list.append(0)
        else:
            count_list.append(c[np.where(i == u)[0][0]])

    return label_list, count_list

def get_counts_from_labels(labels_data, num_labels, verbose):
    if verbose:
        print("\nLayer 0")
    unique, counts = get_counts(labels_data[0], num_labels, verbose)
    for i in range(1, len(labels_data)):
        if verbose:
            print(f"\nLayer: {i}")
        label_array = labels_data[i]
        u, c = get_counts(label_array, num_labels, verbose)
        assert unique == u, 'Number of label IDs mismatched!'
        counts = [a + b for a, b in zip(counts, c)] #element-wise addition

    return unique, counts

def get_stats(label_layers, verbose):
    labels_data, num_labels, num_layers = fetch_data(label_layers)
    print("--------------- Generating stats ------------------")
    print(f"Number of labelling layers being analysed: {num_layers}")
    unique, counts = get_counts_from_labels(labels_data, num_labels, verbose)
    print(f"\nAggregated statistics over {num_layers} layers:")
    for i, c in zip(unique, counts):
        if i == 0:
            print(f"Label ID: {i} | Count (in Pixels): {c} | unlabelled pixels")
        elif i == 1:
            print(f"Label ID: {i} | Count (in Pixels): {c} | background pixels")
        else:
            print(f"Label ID: {i} | Count (in Pixels): {c}")
    print("--------------- done ------------------")

def view_stats(label_layers, exclude_unlabelled_pixels, exclude_background_pixels, verbose):
    labels_data, num_labels, num_layers = fetch_data(label_layers)
    colors_dict = get_colors(num_labels, label_layers[0])
    unique, counts = get_counts_from_labels(labels_data, num_labels, verbose)

    if exclude_background_pixels: # will also exclude unlabelled pixels
        start_with = 2
    elif exclude_unlabelled_pixels:
        start_with = 1
    else:
        start_with = 0

    colors_list = []
    if start_with == 0:
        # Unlabelled data has no colour assigned, choosing black
        colors_list.append(np.array([0.0, 0.0, 0.0]))

    for i in range(start_with, num_labels):
        if i == 0:
            continue
        else:
            colors_list.append(colors_dict[str(i)])
    plot_bar(unique[start_with:], counts[start_with:], num_layers, colors_list)

def plot_bar(unique, counts, num_layers, color_list):
    _, _ = plt.subplots(figsize=(15,5))
    LABELS = [str(a) for a in unique] 
    plt.bar(unique, counts, color=color_list)
    plt.xticks(unique, LABELS)
    plt.xlabel('Label ID')
    plt.ylabel('Labels count (in Pixels)')
    plt.title(f'Aggregated labelled pixels over {num_layers} layers')
    plt.show()

def get_colors(num_labels, layer):
    """
    label = viewer.layers[0]
        select any one of the layers
    """
    colors_dict = {}
    for i in range(1, num_labels+1):
        colors_dict[str(i)] = np.round(layer.get_color(label=i)[:3], 4)
    return colors_dict
