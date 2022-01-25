from bamboolib.grid import (
    BamGridWidget,
    set_defaults,
    show_grid,
    on as qgrid_on,
    PREVIEW_ROW_COUNT,
)
from traitlets import All
import numpy as np
import pandas as pd
import json


def create_df():
    return pd.DataFrame(
        {
            "A": 1.0,
            "Date": pd.Timestamp("20130102"),
            "C": pd.Series(1, index=list(range(4)), dtype="float32"),
            "D": np.array([3] * 4, dtype="int32"),
            "E": pd.Categorical(["test", "train", "foo", "bar"]),
            "F": ["foo", "bar", "buzz", "fox"],
        }
    )


def create_large_df(size=10000):
    large_df = pd.DataFrame(np.random.randn(size, 4), columns=list("ABCD"))
    large_df["B (as str)"] = large_df["B"].map(lambda x: str(x))
    return large_df


def create_multi_index_df():
    arrays = [
        ["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux"],
        ["one", "two", "one", "two", "one", "two", "one", "two"],
    ]
    return pd.DataFrame(np.random.randn(8, 4), index=arrays)


def create_interval_index_df():
    td = np.cumsum(np.random.randint(1, 15 * 60, 1000))
    start = pd.Timestamp("2017-04-17")
    df = pd.DataFrame([(start + pd.Timedelta(seconds=d)) for d in td], columns=["time"])

    freq = "15Min"
    start = df["time"].min().floor(freq)
    end = df["time"].max().ceil(freq)
    bins = pd.date_range(start, end, freq=freq)
    df["time_bin"] = pd.cut(df["time"], bins)
    return df


def init_event_history(event_names, widget=None):
    event_history = []

    def on_change(event, qgrid_widget):
        event_history.append(event)

    if widget is not None:
        widget.on(event_names, on_change)
    else:
        qgrid_on(event_names, on_change)

    return event_history


def test_set_defaults():
    fake_grid_options_a = {"foo": "bar"}
    set_defaults(show_toolbar=False, precision=4, grid_options=fake_grid_options_a)

    def assert_widget_vals_a(widget):
        assert not widget.show_toolbar
        assert widget.precision == 4
        assert widget.grid_options == fake_grid_options_a

    df = create_df()
    view = show_grid(df)
    assert_widget_vals_a(view)

    view = BamGridWidget(df=df)
    assert_widget_vals_a(view)

    fake_grid_options_b = {"foo": "buzz"}
    set_defaults(show_toolbar=True, precision=2, grid_options=fake_grid_options_b)

    def assert_widget_vals_b(widget):
        assert widget.show_toolbar
        assert widget.precision == 2
        assert widget.grid_options == fake_grid_options_b

    df = create_df()
    view = show_grid(df)
    assert_widget_vals_b(view)

    view = BamGridWidget(df=df)
    assert_widget_vals_b(view)


class MyObject(object):
    def __init__(self, obj):
        self.obj = obj


my_object_vals = [MyObject(MyObject(None)), MyObject(None)]


def test_change_viewport():
    widget = BamGridWidget(df=create_large_df())
    event_history = init_event_history(All)

    top = 7124
    bottom = 7136

    widget._handle_qgrid_msg_helper(
        {"type": "change_viewport", "top": top, "bottom": 7136}
    )

    assert event_history == [
        {
            "name": "json_updated",
            "triggered_by": "change_viewport",
            "range": (top - PREVIEW_ROW_COUNT, top + PREVIEW_ROW_COUNT),
        },
        {
            "name": "viewport_changed",
            "old": (0, PREVIEW_ROW_COUNT),
            "new": (7124, 7136),
        },
    ]


def test_instance_created():
    event_history = init_event_history(All)
    qgrid_widget = show_grid(create_df())

    assert event_history == [{"name": "instance_created"}]
    assert qgrid_widget.id
