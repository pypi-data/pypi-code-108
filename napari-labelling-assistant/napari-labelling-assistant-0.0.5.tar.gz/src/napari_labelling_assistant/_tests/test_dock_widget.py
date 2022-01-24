from napari_labelling_assistant import LabellingAssistant, fetch_data, get_colors
import numpy as np

# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer.add_labels(np.random.choice([0,1,2], (100,100), p=[0.6, 0.3, 0.1]))

    # create our widget, passing in the viewer
    my_widget = LabellingAssistant(viewer)

    # call our widget method
    my_widget._on_click()

    # read captured output and check that it's as we expected
    captured = capsys.readouterr()
    assert captured.out == "napari has 1 layers\n"

def get_label_array():
    label_array = np.array([[1, 0, 0, 1, 1, 1, 0, 1, 0, 1],
                            [1, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 2, 1, 2, 1, 1, 0, 0, 2],
                            [2, 0, 0, 1, 2, 2, 1, 1, 1, 1],
                            [1, 2, 1, 1, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 1, 0, 1, 2, 0, 2],
                            [0, 0, 2, 1, 2, 1, 0, 2, 1, 0],
                            [1, 0, 0, 1, 2, 1, 0, 0, 0, 2],
                            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [1, 0, 0, 0, 0, 0, 0, 1, 2, 1]])
    return label_array


def test_data_fetching(make_napari_viewer):
    viewer = make_napari_viewer()
    label_array = get_label_array()
    viewer.add_labels(label_array)

    data, num_labels, num_layers = fetch_data(viewer.layers)
    assert np.array_equal(data[0], label_array)
    assert num_labels == 3
    assert num_layers == 1

def test_label_colors_order(make_napari_viewer):
    viewer = make_napari_viewer()
    label_array = get_label_array()
    viewer.add_labels(label_array)

    default_color_dict = {
        '1': np.array([0.4706, 0.1461, 0.0273]),
        '2': np.array([0.3592, 0.8379, 0.9764]),
        '3': np.array([0.5731, 0.5387, 0.9131]),
        '4': np.array([0.6125, 0.3799, 0.1865]),
        '5': np.array([0.2805, 0.2282, 0.6264]),
        '6': np.array([0.6724, 0.9271, 0.5439]),
        '7': np.array([0.707 , 0.4909, 0.7428]),
        '8': np.array([0.5278, 0.5672, 0.6043]),
        '9': np.array([0.9988, 0.9687, 0.1099])
    }
    num_labels = 9
    colors_dict = get_colors(num_labels, viewer.layers[0])
    for i in range(1, num_labels+1):
        assert np.array_equal(default_color_dict[str(i)], colors_dict[str(i)])
