import numpy as np

from shapeout2.gui import pipeline_plot


def test_compute_contour_opening_angles():
    contour = [
        [0, 0],
        [1, 0],
        [0.5, np.sqrt(3)/2]
        ]
    plot_state = {"general": {"range x": [0, 1],
                              "range y": [0, 1],
                              "scale x": "linear",
                              "scale y": "linear",
                              }}
    angles = pipeline_plot.compute_contour_opening_angles(
        plot_state=plot_state, contour=contour)
    assert np.allclose(angles, np.pi/3)


def test_compute_contour_opening_angles_shifted():
    contour = [
        [0, 0],
        [1, 0],
        [0.5, np.sqrt(3)/2]
        ]
    contour = np.array(contour) + 1
    plot_state = {"general": {"range x": [0, 1],
                              "range y": [0, 1],
                              "scale x": "linear",
                              "scale y": "linear",
                              }}
    angles = pipeline_plot.compute_contour_opening_angles(
        plot_state=plot_state, contour=contour)
    assert np.allclose(angles, np.pi/3)


def test_compute_contour_opening_angles_advanced():
    contour = [
        [0, 0],
        [0.5, np.sqrt(3) / 2],
        [1, 0],
        [1.5, np.sqrt(3) / 2],
        [0, np.sqrt(3) / 2],
        [0, 0],
        ]
    expected = [np.pi/6, np.pi/3, np.pi/3, np.pi/3, np.pi/2]
    plot_state = {"general": {"range x": [0, 1],
                              "range y": [0, 1],
                              "scale x": "linear",
                              "scale y": "linear",
                              }}
    angles = pipeline_plot.compute_contour_opening_angles(
        plot_state=plot_state, contour=contour)
    assert np.allclose(angles, expected)


def test_compute_contour_opening_angles_log_scale():
    contour = [
        [0, 0],
        [1, 0],
        [0.5, np.sqrt(3)/2]
        ]
    contour = 10**(np.array(contour) + 1)
    plot_state = {"general": {"range x": [0, 1],
                              "range y": [0, 1],
                              "scale x": "log",
                              "scale y": "log",
                              }}
    angles = pipeline_plot.compute_contour_opening_angles(
        plot_state=plot_state, contour=contour)
    assert np.allclose(angles, np.pi/3)
