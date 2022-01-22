import os
import pathlib
import inspect
import flatdict
import itertools
import ninja.ninja_syntax


import pyhelios
import pyhelios.exe
import pyhelios.toml
import pyhelios.template


class GNinja(ninja.ninja_syntax.Writer):
    def __init__(self, output):
        ninja.ninja_syntax.Writer.__init__(self, output)
        template = os.path.dirname(inspect.getfile(pyhelios))
        template = os.path.join(template, "share", "templates", "build.ninja")
        with open(template, "r") as fid:
            rules = fid.read()
        self.output.write(rules)


def parametric_study(template, toml, output_dir):
    cases_list = []
    data = flatdict.FlatDict(pyhelios.toml.read(toml), delimiter="_")
    cases = list(itertools.product(*data.values()))
    for c in cases:
        d = dict(zip(data.keys(), list(str(item) for item in c)))
        d["parameters_case_name"] = "_".join(d.values())
        d["parameters_output"] = os.path.join(output_dir, d["parameters_case_name"])
        pyhelios.exe.mkdir(d["parameters_output"])
        d["parameters_output"] = os.path.join(
            d["parameters_output"], os.path.basename(template)
        )
        pyhelios.template.render(template, d["parameters_output"], d)
        cases_list.append(d)
    return cases_list
