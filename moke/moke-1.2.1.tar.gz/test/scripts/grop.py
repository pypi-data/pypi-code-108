#!/usr/bin/env python2.7
from moke import *
import re

@task
def main(pattern, i=stdin, o=stdout, only_matching=False):
    """grop is not grep.
    """
    sre = re.compile(pattern)
    with i as i, o as o:
        for line in i:
            match = sre.match(line)
            if match:
                if only_matching:
                    o.write("%s\n" % match.groups()[0])
                else:
                    o.write(line)
    
if __name__ == "__main__":
    task()
