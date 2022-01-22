import os
import numpy
import inspect

import pyhelios
import pyhelios.toml

from pyhelios.exe import exist, call_latex
from pyhelios.template import get_jinja_latex_template

NUMBER_MAJOR_TICK = 6
NUMBER_MINOR_TICK = 10
COLORS = {
    "b": "blue",
    "n": "orange",
    "r": "red",
    "l": "lightblue",
    "g": "green",
    "y": "yellow",
    "p": "purple",
    "i": "pink",
    "a": "brown",
    "e": "gray",
    "k": "black",
}
LINES = {"-": "solid", "--": "dashed", "m": "only marks", "..": "dotted"}
MARKERS = {
    "o": "mark = *",
    "+": "mark = +",
    "s": "mark = square*",
    "d": "mark = diamond*",
    "t": "mark = triangle*",
    "ow": "mark = *, mark options = {style = solid, fill = white}",
    "sw": "mark = square*, mark options = {style = solid, fill = white}",
    "dw": "mark = diamond*, mark options = {style = solid, fill = white}",
    "tw": "mark = triangle*, mark options = {style = solid, fill = white}",
}
DEFAULT_STYLES = ["k-", "r-ow", "b-sw", "g-o", "a-s"]


def logn(n, x):
    if n == 2:
        return numpy.log2(x)
    elif n == 10:
        return numpy.log10(x)
    else:
        return numpy.log(x) / numpy.log(n)


class Plot:
    def __init__(self, CfgFn, TmpFn, OutputDir="."):
        self.cfg_fn = CfgFn
        self.tmp_fn = TmpFn
        OutputDir = "" if OutputDir == "." else OutputDir
        self.cfg_abspath = os.path.dirname(os.path.abspath(self.cfg_fn))
        # --- Get TOML configuration.
        self.cfg = pyhelios.toml.read(CfgFn)
        pyhelios.logger.log("INFO", f"Reading {CfgFn}")
        # --- Get template.
        if not TmpFn:
            TmpFn = os.path.dirname(inspect.getfile(pyhelios))
            TmpFn = os.path.join(TmpFn, "share", "templates", "plot.tex")
        self.tmp = get_jinja_latex_template(TmpFn)
        pyhelios.logger.log("INFO", f"Reading {TmpFn}")
        # --- Loop over each figure contained in the TOML file.
        for fig in self.cfg["plot"]:
            self.opt = {"fig": ".".join([fig, self.cfg["plot"][fig]["format"]])}
            # --- Define output file name.
            self.out = os.path.join(OutputDir, self.opt["fig"])
            # --- Add keys coming from cfg file.
            self.opt.update(self.cfg["plot"][fig])
            # --- Parse data.
            self.opt["legend"] = True
            for l in self.opt["lines"]:
                data = l["data"]
                l["data"] = os.path.join(self.cfg_abspath, data[0])
                l["x"] = int(data[1])
                l["y"] = int(data[2])
                if l["label"] == None:
                    self.opt["legend"] = False
            # --- Log axis.
            for axis in ["x", "y"]:
                self.opt[axis + "log"] = False
                if "axis" in self.opt:
                    if "log" + axis in self.opt["axis"]:
                        self.opt[axis + "log"] = True
            # --- Define range and ticks.
            for axis in ["x", "y"]:
                self.get_range(axis, self.opt[axis + "log"])
                self.get_tick(axis, self.opt[axis + "log"])
                self.get_minor_tick(axis)
            # --- Parse style.
            self.parse_style()
            # --- Render LaTeX file.
            tex = os.path.splitext(self.out)[0] + ".tex"
            if "pdf" in os.path.splitext(self.out)[1]:
                self.opt["standalone"] = True
            with open(tex, "w") as fid:
                fid.write(self.tmp.render(**self.opt))
            level = "INFO" if exist(tex) else "ERROR"
            pyhelios.logger.log(level, f"Writing {tex}")
            if "pdf" in os.path.splitext(self.out)[1]:
                call_latex(os.path.basename(tex), OutputDir)
                level = "INFO" if exist(self.out) else "ERROR"
                pyhelios.logger.log(level, f"Writing {self.out}")

    def parse_style(self):
        for il, l in enumerate(self.opt["lines"]):
            if "style" not in l:
                l["style"] = DEFAULT_STYLES[il]
            for k, v in COLORS.items():
                if k in l["style"]:
                    l["color"] = v
            for k, v in LINES.items():
                if k in l["style"]:
                    l["line"] = v
            for k, v in MARKERS.items():
                if k in l["style"]:
                    l["marker"] = v

    def get_range(self, axis, log):
        if axis + "min" not in self.opt:
            self.opt[axis + "min"] = float("+inf")
            for l in self.opt["lines"]:
                M = numpy.loadtxt(l["data"])
                m = numpy.amin(M[:, l[axis]])
                self.opt[axis + "min"] = min(self.opt[axis + "min"], m)
        if axis + "max" not in self.opt:
            self.opt[axis + "max"] = float("-inf")
            for l in self.opt["lines"]:
                M = numpy.loadtxt(l["data"])
                m = numpy.amax(M[:, l[axis]])
                self.opt[axis + "max"] = max(self.opt[axis + "max"], m)
        if log:
            for ext in ["min", "max"]:
                self.opt[axis + ext] = logn(10, self.opt[axis + ext])
        delta = self.opt[axis + "max"] - self.opt[axis + "min"]
        for i, ext in enumerate(["max", "min"]):
            self.opt[axis + ext + "ext"] = self.opt[axis + ext]
            self.opt[axis + ext + "ext"] += (-1) ** i * 0.05 * delta
            self.opt[axis + ext + "eps"] = self.opt[axis + ext]
            self.opt[axis + ext + "eps"] += (-1) ** i * 1.0e-3 * delta
        if log:
            for ext in ["minext", "maxext"]:
                self.opt[axis + ext] = 10.0 ** (self.opt[axis + ext])

    def get_tick(self, axis, log):
        if axis + "tick" not in self.opt:
            m = self.opt[axis + "min"]
            M = self.opt[axis + "max"]
            n = NUMBER_MAJOR_TICK
            if log:
                self.opt[axis + "tick"] = numpy.logspace(m, M, n)
            else:
                self.opt[axis + "tick"] = numpy.linspace(m, M, n)

    def get_minor_tick(self, axis):
        key = "minor" + axis + "tick"
        if key not in self.opt:
            siz = len(self.opt[axis + "tick"]) - 1
            self.opt[key] = numpy.zeros(siz * NUMBER_MINOR_TICK)
            for it, t in enumerate(self.opt[axis + "tick"][0:-1]):
                m = self.opt[axis + "tick"][it]
                M = self.opt[axis + "tick"][it + 1]
                n = NUMBER_MINOR_TICK
                beg = it * NUMBER_MINOR_TICK
                end = beg + NUMBER_MINOR_TICK
                self.opt[key][beg:end] = numpy.linspace(m, M, n + 1)[0:-1]
