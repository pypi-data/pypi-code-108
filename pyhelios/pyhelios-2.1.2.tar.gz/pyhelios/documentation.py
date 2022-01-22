import os
import inspect
import pyhelios
import xmltodict
import collections

from pyhelios.template import get_jinja_latex_template
from pyhelios.highlight import pygments_latex_render, pygments_latex_defines


def to_list(item):
    return [item] if isinstance(item, collections.OrderedDict) else item


class Define:
    def __init__(self, template, m):
        self.template = template
        self.prototype = "#define " + m["name"]
        if "param" in m:
            args = []
            m["param"] = to_list(m["param"])
            for p in m["param"]:
                args.append(p["defname"])
            self.prototype += "(" + ", ".join(args) + ")"

    def render(self):
        self.prototype = pygments_latex_render(self.prototype)
        return self.template.render(**self.__dict__)


class Typedef:
    def __init__(self, template, m):
        self.template = template
        self.prototype = m["definition"] + ";"

    def render(self):
        self.prototype = pygments_latex_render(self.prototype)
        return self.template.render(**self.__dict__)


class Structure:
    def __init__(self, template, s):
        self.template = template
        compounddef = s["compounddef"]
        self.prototype = "struct " + compounddef["compoundname"]
        self.members = []
        if compounddef["briefdescription"]:
            if compounddef["briefdescription"]["para"]:
                self.brief = compounddef["briefdescription"]["para"]
        if compounddef["detaileddescription"]:
            if compounddef["detaileddescription"]["para"]:
                self.long = compounddef["detaileddescription"]["para"]

        if compounddef["@kind"] == "struct":
            if "sectiondef" in compounddef:
                sectiondef = to_list(compounddef["sectiondef"])
                for s in sectiondef:
                    if s["@kind"] == "public-attrib":
                        memberdef = to_list(s["memberdef"])
                        for m in memberdef:
                            if m["@kind"] == "variable":
                                if m["detaileddescription"]:
                                    if m["detaileddescription"]["para"]:
                                        self.members.append(
                                            [
                                                m["definition"].replace(
                                                    compounddef["compoundname"] + "::",
                                                    "",
                                                ),
                                                m["name"].replace("_", "\_"),
                                                m["detaileddescription"][
                                                    "para"
                                                ].replace("_", "\_"),
                                            ]
                                        )

    def render(self):
        self.prototype += "{" + ", ".join([e[0] for e in self.members]) + "};"
        self.prototype = pygments_latex_render(self.prototype)
        return self.template.render(**self.__dict__)


class Function:
    def __init__(self, template, m):
        self.template = template
        self.prototype = m["definition"] + m["argsstring"] + ";"
        self.description = None
        if m["briefdescription"]:
            self.description = m["briefdescription"]["para"].replace("_", "\_")
        self.parameters = []
        if m["detaileddescription"]:
            if m["detaileddescription"]["para"]:
                parameterlist = m["detaileddescription"]["para"]["parameterlist"]
                if parameterlist["@kind"] == "param":
                    parameteritem = parameterlist["parameteritem"]
                    parameteritem = to_list(parameteritem)
                    for p in parameteritem:
                        self.parameters.append(
                            [
                                p["parameternamelist"]["parametername"][
                                    "#text"
                                ].replace("_", "\_"),
                                p["parameternamelist"]["parametername"][
                                    "@direction"
                                ].replace("_", "\_"),
                                p["parameterdescription"]["para"].replace("_", "\_"),
                            ]
                        )
        self.returns = None
        if m["detaileddescription"]:
            if m["detaileddescription"]["para"]:
                if "simplesect" in m["detaileddescription"]["para"]:
                    simplesect = m["detaileddescription"]["para"]["simplesect"]
                    if simplesect["@kind"] == "return":
                        self.returns = simplesect["para"].replace("_", "\_")

    def render(self):
        self.prototype = pygments_latex_render(self.prototype)
        return self.template.render(**self.__dict__)


class Doxygen:
    def __init__(self, xml_dir, output_dir):
        self.files = {}
        self.defines = {}
        self.typedefs = {}
        self.functions = {}
        self.structures = {}

        # -- LaTeX template.
        with open(os.path.join(output_dir, "pygments_defines.tex"), "w") as fid:
            fid.write(pygments_latex_defines())

        # -- Get the LaTeX template for defines.
        template = os.path.dirname(inspect.getfile(pyhelios))
        template = os.path.join(template, "share", "templates", "define.tex")
        self.define_template = get_jinja_latex_template(template)

        # -- Get the LaTeX template for typedefs.
        template = os.path.dirname(inspect.getfile(pyhelios))
        template = os.path.join(template, "share", "templates", "typedef.tex")
        self.typedef_template = get_jinja_latex_template(template)

        # -- Get the LaTeX template for structures.
        template = os.path.dirname(inspect.getfile(pyhelios))
        template = os.path.join(template, "share", "templates", "structure.tex")
        self.structure_template = get_jinja_latex_template(template)

        # -- Get the LaTeX template for functions.
        template = os.path.dirname(inspect.getfile(pyhelios))
        template = os.path.join(template, "share", "templates", "function.tex")
        self.function_template = get_jinja_latex_template(template)

        # -- Parse the Doxygen index.
        with open(os.path.join(xml_dir, "index.xml"), "r") as fid:
            doxygenindex = xmltodict.parse(fid.read())["doxygenindex"]
            for compound in doxygenindex["compound"]:
                if compound["@kind"] == "file":
                    xml = os.path.join(xml_dir, compound["@refid"] + ".xml")
                    self.files[compound["name"]] = xml

        # -- Parse the defines.
        for header, xml_file in self.files.items():
            self.defines[header] = []
            with open(xml_file, "r") as fid:
                doxygen = xmltodict.parse(fid.read())["doxygen"]
                compounddef = doxygen["compounddef"]
                if compounddef["@kind"] == "file":
                    if "sectiondef" in compounddef:
                        sectiondef = to_list(compounddef["sectiondef"])
                        for s in sectiondef:
                            if s["@kind"] == "define":
                                memberdef = to_list(s["memberdef"])
                                for m in memberdef:
                                    if m["@kind"] == "define":
                                        d = Define(self.define_template, m)
                                        self.defines[header].append(d.render())
            output_file = os.path.join(
                output_dir, os.path.splitext(header)[0] + "_define.tex"
            )
            with open(output_file, "w") as fid:
                for d in self.defines[header]:
                    fid.write(d)

        # -- Parse the typedefs.
        for header, xml_file in self.files.items():
            self.typedefs[header] = []
            with open(xml_file, "r") as fid:
                doxygen = xmltodict.parse(fid.read())["doxygen"]
                compounddef = doxygen["compounddef"]
                if compounddef["@kind"] == "file":
                    if "sectiondef" in compounddef:
                        sectiondef = to_list(compounddef["sectiondef"])
                        for s in sectiondef:
                            if s["@kind"] == "typedef":
                                memberdef = to_list(s["memberdef"])
                                for m in memberdef:
                                    if m["@kind"] == "typedef":
                                        t = Typedef(self.typedef_template, m)
                                        self.typedefs[header].append(t.render())
            output_file = os.path.join(
                output_dir, os.path.splitext(header)[0] + "_typedef.tex"
            )
            with open(output_file, "w") as fid:
                for t in self.typedefs[header]:
                    fid.write(t)

        # -- Parse the structures.
        for header, xml_file in self.files.items():
            self.structures[header] = []
            with open(xml_file, "r") as fid:
                doxygen = xmltodict.parse(fid.read())["doxygen"]
                compounddef = doxygen["compounddef"]
                if compounddef["@kind"] == "file":
                    if "innerclass" in compounddef:
                        innerclass = to_list(compounddef["innerclass"])
                        for ic in innerclass:
                            file_name = os.path.join(xml_dir, ic["@refid"] + ".xml")
                            with open(file_name, "r") as fid:
                                d = xmltodict.parse(fid.read())["doxygen"]
                                s = Structure(self.structure_template, d)
                                self.structures[header].append(s.render())
            output_file = os.path.join(
                output_dir, os.path.splitext(header)[0] + "_structure.tex"
            )
            with open(output_file, "w") as fid:
                for s in self.structures[header]:
                    fid.write(s)

        # -- Parse the functions.
        for header, xml_file in self.files.items():
            self.functions[header] = []
            with open(xml_file, "r") as fid:
                doxygen = xmltodict.parse(fid.read())["doxygen"]
                compounddef = doxygen["compounddef"]
                if compounddef["@kind"] == "file":
                    if "sectiondef" in compounddef:
                        sectiondef = to_list(compounddef["sectiondef"])
                        for s in sectiondef:
                            if s["@kind"] == "func":
                                memberdef = to_list(s["memberdef"])
                                for m in memberdef:
                                    if m["@kind"] == "function":
                                        f = Function(self.function_template, m)
                                        self.functions[header].append(f.render())
            output_file = os.path.join(output_dir, os.path.splitext(header)[0] + ".tex")
            with open(output_file, "w") as fid:
                for f in self.functions[header]:
                    fid.write(f)
