#!/usr/bin/env python2.7
from moke import * #@UnusedWildImport

@task
def nodef_float(name):
    """
    - name(``float``)
    """
    print type(name)

@task
def nodef_path(name):
    """
    - name(``path``)
    """
    print type(name)

@task
def none_float(name=None):
    """
    - name(``float``)
    """
    print type(name)

@task
def none_path(name=None):
    """
    - name(``path``)
    """
    print type(name)

    

    
if __name__ == "__main__":
    task()
