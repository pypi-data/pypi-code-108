import os
import inspect
import pyhelios

from pyhelios.template import get_jinja_latex_template

HLS_LOW_MEDIUM_COVERAGE = 0.75
HLS_MEDIUM_HIGH_COVERAGE = 0.90

HLS_LOW_COVERAGE_COLOR = "red"
HLS_MEDIUM_COVERAGE_COLOR = "orange"
HLS_HIGH_COVERAGE_COLOR = "green"


class Coverage:
    def __init__(self, fn, output_dir):
        self.coverage = {}
        template = os.path.dirname(inspect.getfile(pyhelios))
        template = os.path.join(template, "share", "templates", "coverage.tex")
        self.template = get_jinja_latex_template(template)
        with open(fn, "r") as fid:
            self.fn = fid.read()
        for f in self.fn.split("end_of_record"):
            lines = f.split("\n")
            for l in lines:
                if l.startswith("SF:"):
                    file_name = os.path.basename(l.split("SF:")[-1])
                    mod_name = "hls_" + file_name.split("_")[1].split(".")[0]
                    file_name = file_name.replace("_", "\_")
                elif l.startswith("FNH:"):
                    cov_func = l.split("FNH:")[-1]
                elif l.startswith("FNF:"):
                    cov_func_tot = l.split("FNF:")[-1]
                elif l.startswith("LH:"):
                    cov_line = l.split("LH:")[-1]
                elif l.startswith("LF:"):
                    cov_line_tot = l.split("LF:")[-1]
            if not mod_name in self.coverage:
                self.coverage[mod_name] = []
            cov_line_percent = float(cov_line) / float(cov_line_tot)
            cov_func_percent = float(cov_func) / float(cov_func_tot)
            self.coverage[mod_name].append(
                [
                    file_name,
                    cov_line,
                    cov_line_tot,
                    cov_line_percent,
                    self.color(cov_line_percent),
                    cov_func,
                    cov_func_tot,
                    cov_func_percent,
                    self.color(cov_func_percent),
                ]
            )
        for mod_name in self.coverage:
            data = {
                "coverage": self.coverage[mod_name],
                "mod_name": mod_name.replace("_", "\_"),
            }
            fn = os.path.join(output_dir, mod_name + "__coverage.tex")
            with open(fn, "w") as fid:
                fid.write(self.template.render(data))

    def color(self, value):
        if value < HLS_LOW_MEDIUM_COVERAGE:
            return HLS_LOW_COVERAGE_COLOR
        elif value < HLS_MEDIUM_HIGH_COVERAGE:
            return HLS_MEDIUM_COVERAGE_COLOR
        else:
            return HLS_HIGH_COVERAGE_COLOR
