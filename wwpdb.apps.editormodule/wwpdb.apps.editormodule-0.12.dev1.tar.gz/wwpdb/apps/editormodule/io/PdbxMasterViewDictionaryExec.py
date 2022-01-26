#!/usr/bin/env python

# Simple front end to dump views to files....

import argparse

from wwpdb.apps.editormodule.io.PdbxMasterViewDictionary import PdbxMasterViewDictionary
from mmcif.io.PdbxWriter import PdbxWriter


def main():
    parser = argparse.ArgumentParser(description="Front end commands for editor config file")
    parser.add_argument("--file", help="Master view configuration file", required=True, dest="filename")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--export", help="Export methods to files", action="store_true")
    group.add_argument("--list-methods", help="List methods supported", action="store_true")

    parser.add_argument("--methods", help="Internal comma separated method names to work with")

    parseargs = parser.parse_args()

    print(parseargs)

    # filename is mandatory
    dV = PdbxMasterViewDictionary(verbose=False)
    dV.read(parseargs.filename)

    if parseargs.list_methods:
        print("Methods: %s" % dV.getMethods())

    if parseargs.export:
        if parseargs.methods:
            methodList = parseargs.methods.split(",")
        else:
            methodList = dV.getMethods()

        for m in methodList:
            print("Exporting %s" % m)
            catObj = dV.generateMethodsView(m)
            if catObj:
                ofh = open(m + ".cif", "w")
                pdbxW = PdbxWriter(ofh)
                pdbxW.setAlignmentFlag(flag=True)
                pdbxW.write([catObj])
                ofh.close()
            else:
                print("Method %s invalid" % m)


if __name__ == "__main__":
    main()
