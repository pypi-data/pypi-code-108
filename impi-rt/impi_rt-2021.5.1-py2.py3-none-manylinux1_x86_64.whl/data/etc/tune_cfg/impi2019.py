#!/usr/bin/env python
#
# Copyright Intel Corporation.
# 
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you (License). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this
# software or the related documents without Intel's prior written permission.
# 
# This software and the related documents are provided as is, with no express
# or implied warranties, other than those that are expressly stated in the
# License.
#

""" The optimization tree custom converter in json format
    for IMPI 2019
"""

import json
import sys
from collections import OrderedDict


def main(m_doc):
    def rework(obj):
        adjust_prefix, m_key = "I_MPI_ADJUST_", None
        for k, v in list(obj.items()):
            if not isinstance(v, dict):
                m_key = k.replace(adjust_prefix, "") + "=" + v
                del obj[k]
        return {m_key :{}}

    def print_tree(obj, params):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if isinstance(v, dict):
                    # rename keys, if it's needed
                    for elem in params:
                        k_new = k.replace(elem, "")
                        if k_new != k:
                            del obj[k]
                            obj.update({k_new: v})
                            break
                else:
                    # rework last dict
                    obj.update(rework(obj))
                    break
                print_tree(v, params)
        return obj
    data = json.loads(m_doc, object_pairs_hook=OrderedDict)
    # do not nessesary to remove "func=" now, but leave it for compatibility with IMPI 2019 Beta
    json.dump(print_tree(data, ["func="]), sys.stdout, indent=2)


if __name__ == "__main__":
    # print("Usage: ./impi2019_comp.py < BCAST.cfg > BCAST.json")
    doc = " ".join([line.rstrip() for line in sys.stdin])
    main(doc)
