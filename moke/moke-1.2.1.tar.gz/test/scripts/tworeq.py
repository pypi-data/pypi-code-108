#!/usr/bin/env python2.7
from moke import * #@UnusedWildImport

@task
def sayhello(a,bc,d=1):
    """
     - a(``path``) a is legit 
     - bc(``path+``) bc is legit
     - d(``int``) some option
    """

if __name__ == "__main__":
    task("asa")
