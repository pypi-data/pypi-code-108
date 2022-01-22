import sys

from xmldt import XmlDt
import argparse
import re


def build_skel(filename, name="DTSkel"):
    data = Skel(filename=filename)
    code = [f"""from xmldt import XmlDt
import sys


class {name} (XmlDt):

    def __default__(self, element):
          return f"[tag: {{element.tag}}, contents: {{element.contents}}]"
"""]
    for tag in data:
        method = re.sub("[.]", "_", tag)
        attr_count = str.join(" ", [f"{a}: {data[tag][a]}" for a in data[tag].keys() if a != ":count"])
        if method != tag:
            code.append(f"""    # @XmlDt.tag("{tag}")""")
        code.append(f"""    # def {method}(self, e): return e.tag # {data[tag][":count"]} occs   {attr_count}\n\n""")
    code.append(f"""
    
file = sys.argv[1]
dt = {name}()
print(dt(filename=file))\n""")
    return "\n".join(code)


def build_skel_jj(files, name="proc"):
    #skel = Skeljj(filename=filename) --->FIXME: dá None

    ### claro que sim. o __default__ nao tme return
    ### ver a minha solucao abaixo

    skel = Skeljj()
    for filename in files:
        skel(filename=filename)
    print(
f"""#!/usr/bin/python3
from xmldt import XmlDt, toxml
import sys
class {name} (XmlDt):
    pass

    # def __default__(s, e): 
    #     return f"[tag: {{e.tag}}, contents: {{e.c}}, attr: {{e.v}}]"
""")
    done = set()
    for tag in skel.order:
        v=skel.data[tag]
        attrs = str.join(" ", [f"{a}({v[a]})" for a in v.keys()-{":count",":pcdata"}])
        if ":pcdata" in v:
            pcdatalen = v[':pcdata'] // v[':count']
            cont= f"{v[':count']} {attrs} PCDATAlen({pcdatalen})"
        else:
            cont= f"{v[':count']} {attrs}" 
        indent="   "*(len(skel.ans[tag]))

        print( f"    # def {indent}{tag}(s, e):   # {cont}" )
#        for sun in skel.suns.get(tag,[]):
#            print( f"    # ...    {indent}{sun}")
    print()
    print("file = sys.argv[1]")
    print(f"print({name}(filename=file))")

#    for t in (skel.pathorder):
#        print(":".join(t))

def ensurepath(seq,path):
    for i in range(len(path)):
        t = tuple(path[:i+1])
        if t not in seq:
            seq.append(t)

class Skeljj (XmlDt):

    data={}              ## tag → (attr | # → int)
    ans={}     ## ansesters tag → tag-path  (of first oco)
    suns={}              ## tag → set(tag)
    order=[]             ## list(tag)
    pathorder=[]

    def __pcdata__(self, e):
        if e.isspace(): return ""
        self.path[-1][":pcdata"] = (self.path[-1][":pcdata"] or 0) + len(e) 
        print(f"DEBUG {e} {len(e)}")
        
#
#        if f := self.path[-1] :
#            self.data.setdefault(f.tag,{":count":0})
#            if "@pcdata" not in self.data[f.tag]:
#                self.data[f.tag]["@pcdata"] = 0
#            self.data[f.tag]["@pcdata"] += len(e)

    def __default__(self, e):
        path = [a.tag for a in self.path] + [e.tag]
#        ensurepath(self.pathorder, path)
#        if f := e.father :
#            self.suns.setdefault(f.tag,{})[e.tag] = 1
        if e.tag not in self.data:
#            self.data[e.tag] = {":count": 0}
            p = self.ans[e.tag]=[a.tag for a in self.path]
            for tag in p+[e.tag]:
                if tag in self.order: continue 
                self.order.append(tag)
            self.data[e.tag] = {":count": 0}
        self.data[e.tag][":count"] += 1
        for key in e.attrs.keys():
            if key not in self.data[e.tag]:
                self.data[e.tag][key] = 0
            if key == ":pcdata":
                self.data[e.tag][key] += e[":pcdata"]  ## len of text
            else:
                self.data[e.tag][key] += 1


class Skel (XmlDt):

    data = {}

    def __default__(self, element):
        if element.tag not in self.data:
            self.data[element.tag] = {":count": 0}
        self.data[element.tag][":count"] += 1
        for key in element.attrs.keys():
            if key not in self.data[element.tag]:
                self.data[element.tag][key] = 0
            self.data[element.tag][key] += 1

    def __end__(self, _):
        return self.data


def main():
    arg_parser = argparse.ArgumentParser()
    skel = arg_parser.add_argument_group()
    skel.add_argument("-s", "--skel", help="Creates basic skeleton file", action="store_true")
    skel.add_argument("filename", type=str, nargs='+', help="the XML file to use as model")
    args = arg_parser.parse_args()

    if args.skel:
        print(build_skel(args.filename[0]))
    else:
        build_skel_jj(args.filename)
