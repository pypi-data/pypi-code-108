#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
def file2df(name):
    if name.endswith(".arff"):
        from arff2pandas import a2p

        relation = None
        with open(name) as f:
            for line in f:
                if line[:9].upper() == "@RELATION":
                    relation = line[9:-1]
                    break
        with open(name) as f:
            df = a2p.load(f)
        return df, relation or name
    elif name.endswith(".csv"):
        from pandas import read_csv

        return read_csv(name), name
    else:  # pragma: no cover
        raise Exception(f"Unknown extension {name.split('.')[-1]}.")
