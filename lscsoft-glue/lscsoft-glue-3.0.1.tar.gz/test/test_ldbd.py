#!/usr/bin/env python

import unittest

import pyRXPU as pyRXP
from glue import ldbd

LIGO_LW_XML = """
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE LIGO_LW SYSTEM "http://ldas-sw.ligo.caltech.edu/doc/ligolwAPI/html/ligolw_dtd.txt">
<LIGO_LW>
  <Table Name="demo:table"><Column Name="name" Type="lstring"/>
    <Column Name="value" Type="real8"/>
    <Stream Name="demo:table" Type="Local" Delimiter=",">
      "mass",0.5,"velocity",34,
      "mass",1.0,"velocity",120
    </Stream>
  </Table>
  <Table Name="demo2:table"><Column Name="name" Type="lstring"/>
    <Column Name="value" Type="real8"/>
    <Stream Name="demo:table" Type="Local" Delimiter=",">
      "mass",0.5,"velocity",34,
      "mass",1.0,"velocity",,
    </Stream>
  </Table>
</LIGO_LW>
""".strip()


class TestLdbd(unittest.TestCase):
    def test_ligolwparser(self):
        xmlparser = pyRXP.Parser()
        lwtparser = ldbd.LIGOLwParser()

        md = ldbd.LIGOMetadata(xmlparser, lwtparser)
        md.parse(LIGO_LW_XML)
        self.assertListEqual(
            md.table["demo"]["stream"],
            [
                ('mass', 0.5), ('velocity', 34.0),
                ('mass', 1.0), ('velocity', 120.0),
            ]
        )
        self.assertListEqual(
            md.table["demo2"]["stream"],
            [
                ('mass', 0.5), ('velocity', 34.0),
                ('mass', 1.0), ('velocity', None),
            ]
        )


if __name__ == "__main__":
    unittest.main()
