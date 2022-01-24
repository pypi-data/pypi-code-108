import sys

from xmldt import XmlDt
import argparse
import re


def build_skel(files, name="proc",
               indent=False,
               debug=False,
               average_pcdata=False):
    skel = Skel()
    skel.flags = {"debug": debug}
    for filename in files:
        skel(filename=filename)

    code = [
f"""#!/usr/bin/python3
from xmldt import XmlDt, toxml
import sys
class {name} (XmlDt):
    pass

    # def __default__(s, e): 
    #     return f"[tag: {{e.tag}}, contents: {{e.c}}, attr: {{e.v}}]"
"""]

    for tag in skel.order:
        v = skel.data[tag]
        attrs = str.join(" ", [f"{a}({v[a]})" for a in v.keys() - {":count", ":pcdata"}])
        if ":pcdata" in v:
            pcdatalen = ""
            if average_pcdata:
                pcdatalen = v[':pcdata'] // v[':count']
                pcdatalen = f" len({pcdatalen})"

            cont = f"{v[':count']} {attrs} PCDATA{pcdatalen}"
        else:
            cont = f"{v[':count']} {attrs}"
        indentation = "   " * len(skel.ans[tag]) if indent else ""

        method = re.sub("[.]", "_", tag)
        if method != tag:
            code.append(f"""    # @XmlDt.tag("{tag}")""")
        code.append(f"    # def {indentation}{method}(s, e):   # {cont}")

    code.append("")
    code.append("file = sys.argv[1]")
    code.append(f"print({name}(filename=file))")

    return "\n".join(code)


def _ensure_path(seq, path):
    for i in range(len(path)):
        t = tuple(path[:i+1])
        if t not in seq:
            seq.append(t)


class Skel (XmlDt):
    data = {}              # tag → (attr | # → int)
    ans = {}               # ancestors tag → tag-path  (of first oco)
    suns = {}              # tag → set(tag)
    order = []             # list(tag)
    path_order = []
    flags = {}

    def _debug(self, *msgs):
        if self.flags["debug"]:
            print("DEBUG: ", *msgs, file=sys.stderr)

    def __pcdata__(self, e):
        if e.isspace(): return ""
        self["path"][-1][":pcdata"] = (self["path"][-1][":pcdata"] or 0) + len(e)

        self._debug(f"{e} {len(e)}")

    def __default__(self, e):
        if e.tag not in self.data:
            p = self.ans[e.tag] = [a.tag for a in self["path"]]
            for tag in p+[e.tag]:
                if tag in self.order: continue 
                self.order.append(tag)
            self.data[e.tag] = {":count": 0}
        self.data[e.tag][":count"] += 1
        for key in e.attrs.keys():
            if key not in self.data[e.tag]:
                self.data[e.tag][key] = 0
            if key == ":pcdata":
                self.data[e.tag][key] += e[":pcdata"]  # len of text
            else:
                self.data[e.tag][key] += 1


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename", type=str, nargs='+', help="the XML files to use as model")
    arg_parser.add_argument("-i", "--indent", action=argparse.BooleanOptionalAction,
                            default=False, help="Indent element tree")
    arg_parser.add_argument("-n", "--name", type=str, help="the name for the resulting class")
    arg_parser.add_argument("-d", "--debug", action=argparse.BooleanOptionalAction,
                            default=False, help="activate debug")
    arg_parser.add_argument("-a", "--average-pcdata",  action=argparse.BooleanOptionalAction,
                            default=False, help="compute pcdata length average")
    args = arg_parser.parse_args()
    name = args.name if args.name else "proc"

    print(build_skel(args.filename,
                     indent=args.indent,
                     average_pcdata=args.average_pcdata,
                     name=name,
                     debug=args.debug))
