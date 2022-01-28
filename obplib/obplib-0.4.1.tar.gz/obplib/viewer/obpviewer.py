# SPDX-FileCopyrightText: 2022 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

"""OBP data viewer.

usage: obpviewer.py [-h] [--slice-size SLICE_SIZE] [--index INDEX] obp_file

Use the mouse or keyboard to navigate.

supported objects:
  Line, AcceleratingLine, Curve, AcceleratingCurve,
  Restore and SyncPoint.

not supported:
  TimedPoints, Metadata and vendor_setup.

keyboard shortcuts:

  right        step forward
  shift+right  step forward 10 steps
  ctrl+right   step forward 100 steps
  alt+right    step forward 1000 steps

  left         step backward
  shift+left   step backward 10 steps
  ctrl+left    step backward 100 steps
  alt+left     step backward 1000 steps

  p            same as right
  n            same as left

  a            jump to start of file
  e            jump to end of file

  s            jump to spot size change
  b            jump to beam power change
  r            jump to restore point

  0-9          jump to sync point change (digit specifies
               sync point: 1st, 2nd, ..., etc)

positional arguments:
  obp_file              Path to obp file.

optional arguments:
  -h, --help            show this help message and exit
  --slice-size SLICE_SIZE
                        Initial slice size (default: 100).
  --index INDEX         Initial index (default: 100).
"""

# Built-in
import argparse
import dataclasses
import pathlib
import tkinter
from tkinter import ttk

# PyPI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure
from matplotlib.ticker import EngFormatter

from matplotlib.path import Path
import matplotlib.collections as mcoll

import numpy as np
from obplib import OBP_pb2 as obp
from google.protobuf.internal.decoder import _DecodeVarint32

plt.style.use("dark_background")


def load_obp_objects(filepath):
    """Deserialize obp data and yield protobuf messages"""
    with open(filepath, "rb") as fh:
        data = fh.read()
    consumed = new_pos = 0
    while consumed < len(data):
        msg_len, new_pos = _DecodeVarint32(data, consumed)
        msg_buf = data[new_pos : new_pos + msg_len]
        consumed = new_pos + msg_len
        packet = obp.Packet()
        packet.ParseFromString(msg_buf)
        attr = packet.WhichOneof("payload")
        yield getattr(packet, attr)


@dataclasses.dataclass
class Data:
    paths: list
    speeds: list
    spotsizes: list
    beampowers: list
    syncpoints: dict
    restores: list


def load_artist_data(obp_objects) -> Data:
    """Return data used when drawing matplotlib artists"""
    paths = list()
    speeds = list()
    spotsizes = list()
    beampowers = list()
    syncpoints = dict()
    _lastseen = dict()  # last seen sync points
    restores = list()
    _restore = 0
    for obj in obp_objects:
        if isinstance(obj, (obp.Line, obp.AcceleratingLine)):
            paths.append(
                Path(
                    np.array([[obj.x0, obj.y0], [obj.x1, obj.y1]]) / 1e6,
                    (Path.MOVETO, Path.LINETO),
                )
            )
        elif isinstance(obj, (obp.Curve, obp.AcceleratingCurve)):
            paths.append(
                Path(
                    np.array(
                        [
                            [obj.p0.x, obj.p0.y],
                            [obj.p1.x, obj.p1.y],
                            [obj.p2.x, obj.p2.y],
                            [obj.p3.x, obj.p3.y],
                        ]
                    )
                    / 1e6,
                    [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4],
                )
            )
        elif isinstance(obj, obp.SyncPoint):
            if obj.endpoint not in syncpoints:
                # Catch up with zeros when seen for the first time
                syncpoints[obj.endpoint] = [0] * len(paths)
            # Update _lastseen with endpoint's new sync value
            _lastseen[obj.endpoint] = int(obj.value)
            continue
        elif isinstance(obj, obp.Restore):
            _restore = 1
            continue
        else:
            continue
        try:
            speeds.append(obj.speed / 1e6)
        except AttributeError:
            speeds.append(obj.sf / 1e6)
        spotsizes.append(obj.params.spot_size)
        beampowers.append(obj.params.beam_power)
        for k, v in _lastseen.items():
            syncpoints[k].append(v)
        restores.append(_restore)
        _restore = 0
    for key in syncpoints:
        syncpoints[key] = np.array(syncpoints[key])
    return Data(
        paths,
        np.array(speeds),
        np.array(spotsizes),
        np.array(beampowers),
        syncpoints,
        np.array(restores),
    )


class ObpFrame(ttk.Frame):
    def __init__(self, master, data, slice_size, index=None, **kwargs):
        """Initialization of ObpFrame"""
        super().__init__(master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.data = data
        if index is None:
            index = slice_size

        def cap(i):  # Prevents IndexError
            return max(0, min(len(self.data.paths) - 1, int(i)))

        self.cap = cap

        index = cap(index)
        slice_ = slice(cap(index + 1 - slice_size), cap(index) + 1)

        # Matplotlib artists and canvas
        fig = Figure(figsize=(9, 8), constrained_layout=True)
        ax = fig.add_subplot(111)
        ax.axhline(0, linewidth=1, zorder=0)  # horizontal center line
        ax.axvline(0, linewidth=1, zorder=0)  # vertical center line
        radius = 0.05  # meters
        ax.set_xlim([-radius, radius])
        ax.set_ylim([-radius, radius])
        si_meter = EngFormatter(unit="m")
        ax.xaxis.set_major_formatter(si_meter)
        ax.yaxis.set_major_formatter(si_meter)
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8)

        self.path_collection = mcoll.PathCollection(
            self.data.paths[slice_],
            fc="none",
            transform=ax.transData,
            cmap=plt.cm.rainbow,
            norm=plt.Normalize(vmin=0, vmax=max(self.data.speeds)),
        )
        self.path_collection.set_array(self.data.speeds[slice_])
        ax.add_collection(self.path_collection)

        ticks = list(sorted(set(self.data.speeds)))
        if len(ticks) > 10:
            ticks = None
        cbar = fig.colorbar(
            self.path_collection,
            ax=ax,
            pad=0,
            aspect=60,
            format=EngFormatter(unit="m/s"),
            ticks=ticks,
        )
        cbar.ax.tick_params(axis="x", labelsize=8)
        cbar.ax.tick_params(axis="y", labelsize=8)
        seg = self.data.paths[index]
        self.marker = ax.scatter(*seg.vertices[-1], c="white", marker="*", zorder=2)

        self.canvas = canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.mpl_connect("key_press_event", self.keypress)

        # Slice size
        self._slice_size = tkinter.IntVar(value=slice_size)
        self._slice_size_spinbox = ttk.Spinbox(
            self,
            from_=0,
            to=len(self.data.paths) - 1,
            textvariable=self._slice_size,
            command=self.update_index,
            width=6,
        )
        self._slice_size_spinbox.bind("<KeyRelease>", self.update_index)

        # Index
        self._index = tkinter.IntVar(value=index)
        self._index_scale = tkinter.Scale(
            self,
            from_=0,
            to=len(self.data.paths) - 1,
            orient=tkinter.HORIZONTAL,
            variable=self._index,
            command=self.update_index,
        )
        self._index_spinbox = ttk.Spinbox(
            self,
            from_=0,
            to=len(self.data.paths) - 1,
            textvariable=self._index,
            command=self.update_index,
            width=6,
        )
        self._index_spinbox.bind("<KeyRelease>", self.update_index)

        self.toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        self.toolbar.update()

        self.info_value = tkinter.StringVar(value=",  ".join(self.get_info(index)))
        self.info_label = ttk.Label(self, textvariable=self.info_value)

        self.button_quit = tkinter.Button(self, text="Quit", command=self.master.quit)

    def keypress(self, event):
        stepsize = 1
        parts = event.key.split("+")
        if len(parts) == 2:
            prefix, key = parts
        else:
            prefix, key = "", parts[0]

        if prefix == "shift" or key in {"P", "N"}:
            stepsize = 10
        elif prefix == "ctrl":
            stepsize = 100
        elif prefix == "alt":
            stepsize = 1000
        if key in {"right", "p", "P"}:
            self._index.set(self.cap(self._index.get() + stepsize))
        elif key in {"left", "n", "N"}:
            self._index.set(self.cap(self._index.get() - stepsize))
        elif event.key == "a":
            self._index.set(0)
        elif event.key == "e":
            self._index.set(len(self.data.paths))
        elif event.key.isdigit():
            n = int(event.key)
            for i, key in enumerate(self.data.syncpoints):
                if i + 1 == n:
                    self.nextdifferent(self.data.syncpoints[key])
        elif event.key == "r":
            self.nextdifferent(self.data.restores)
        elif event.key == "b":
            self.nextdifferent(self.data.beampowers)
        elif event.key == "s":
            self.nextdifferent(self.data.spotsizes)
        else:
            print(event.key)
            return
        self.update_index()

    def nextdifferent(self, array):
        start = self.cap(self._index.get())
        bools = array[start:] != array[start]
        self._index.set(start + np.argmax(bools))

    def update_index(self, new_index=None):
        if new_index is None:
            new_index = self._index.get()
        elif isinstance(new_index, tkinter.Event):
            if new_index.keysym != "Return":
                return
            self.canvas.get_tk_widget().focus_force()
            new_index = self._index.get()
        index = self.cap(new_index)
        ss = self._slice_size.get() or 1

        # Update artists
        slice_ = slice(self.cap(index + 1 - ss), self.cap(index) + 1)
        segs = self.data.paths[slice_]
        if len(segs):
            self.path_collection.set_paths(segs)
            self.path_collection.set_array(self.data.speeds[slice_])
            self.marker.set_offsets(segs[-1].vertices[-1])
            self.canvas.draw()

        # Update labels
        self.info_value.set(",  ".join(self.get_info(index)))

    def get_info(self, index):
        info = [f"{k}={v[index]}" for k, v in self.data.syncpoints.items()]
        info.append(f"Restore={int(self.data.restores[index])}")
        info.append(f"BeamPower={int(self.data.beampowers[index])}")
        info.append(f"SpotSize={int(self.data.spotsizes[index])}")
        return info

    def setup_grid(self):
        self.canvas.get_tk_widget().grid(row=0, columnspan=4, sticky="NSWE")

        self._index_scale.grid(row=1, columnspan=4, sticky="NSWE")

        self.info_label.grid(row=2, column=0, sticky="SW")
        self._slice_size_spinbox.grid(row=2, column=1, sticky="SE")
        self._index_spinbox.grid(row=2, column=2, sticky="SE")
        self.button_quit.grid(row=2, column=3, sticky="SE")

        self.toolbar.grid(row=3, columnspan=4, sticky="NSWE")


parser = argparse.ArgumentParser(
    description="""OBP data viewer.

Use the mouse or keyboard to navigate.

supported objects:
  Line, AcceleratingLine, Curve, AcceleratingCurve,
  Restore and SyncPoint.

not supported:
  TimedPoints, Metadata and vendor_setup.

keyboard shortcuts:

  right        step forward
  shift+right  step forward 10 steps
  ctrl+right   step forward 100 steps
  alt+right    step forward 1000 steps

  left         step backward
  shift+left   step backward 10 steps
  ctrl+left    step backward 100 steps
  alt+left     step backward 1000 steps

  p            same as right
  n            same as left

  a            jump to start of file
  e            jump to end of file

  s            jump to spot size change
  b            jump to beam power change
  r            jump to restore point

  0-9          jump to sync point change (digit specifies
               sync point: 1st, 2nd, ..., etc)
""",
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "obp_file",
    type=pathlib.Path,
    help="Path to obp file.",
)
parser.add_argument(
    "--slice-size",
    type=int,
    default=100,
    help="Initial slice size (default: %(default)s).",
)
parser.add_argument(
    "--index",
    type=int,
    default=100,
    help="Initial index (default: %(default)s).",
)


def _main(args):

    obp_objects = load_obp_objects(args.obp_file)
    data = load_artist_data(obp_objects)

    root = tkinter.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.title(f"obpviewer - {args.obp_file.name}")
    root.option_add("*tearOff", tkinter.FALSE)
    frame = ObpFrame(root, data, args.slice_size, args.index)
    frame.grid(row=0, column=0, sticky="NSWE", padx=5, pady=5)
    frame.setup_grid()
    tkinter.mainloop()


def main():
    args = parser.parse_args()
    _main(args)


if __name__ == "__main__":
    main()
