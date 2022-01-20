from napari_labelling_assistant import LabellingAssistant, fetch_data
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

def test_data_fetching(make_napari_viewer, capsys):
    viewer = make_napari_viewer()

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
    viewer.add_labels(label_array)

    data, num_labels, num_layers = fetch_data(viewer.layers)
    assert np.array_equal(data[0], label_array)
    assert num_labels == 3
    assert num_layers == 1
