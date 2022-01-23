#!/usr/bin/env python2.7
from moke import *
import sys

@task
def fromdef_int(i=1):
    assert type(i) == int

@task
def fromdef_float(i=1.):
    assert type(i) == float

@task
def fromdef_path_r(i=stdin):
    assert type(i) == file
    assert i.mode == "rb"

@task
def fromdef_path_w(i=stdout):
    assert type(i) == file
    assert i.mode == "wb"

@task
def fromdoc_none_int(i=None):
    """
    -i(int) gets parsed!
    """
    assert type(i) == int
    
@task
def fromdoc_none_float(i=None):
    """
    -i(float) gets parsed!
    """
    assert type(i) == float  


@task
def fromdoc_pos_int(k):
    """General docs.
    -k(int) gets parsed!
    More general docs.
    """
    assert type(k) == int

@task
def fromdoc_pos_2(j, k):
    """General docs.
    -k(int) gets parsed!
    More general docs.
    """
    assert type(k) == int
    assert type(j) == str
    

@task
def none():
    pass

@task
def null():
    log("null called")

@task
def nulldoc():
    """
    """

@task
def justdoc():
    """ethio-jazz rules!
    for ever!
    """

@task
def nonedoc(j = None):
    """
    """

@task
def unktype(j = 1, zzz=17, a="Strrr"):
    """
    -j(sasalambada)
    """
    assert type(j) == int
    assert type(a) == str
    
@task
def iptopt(ipt=stdin, opt=stdout):
    #print ipt
    with ipt as ipt, opt as opt:
        for line in ipt:
            cols = line.strip().split("\t")
            opt.write("\t".join(cols[::-1]) + "\n")

@task
def filew(opt=stdout):
    """
    opt(file_w) A file to write
    """
    print repr(opt)


@task
def postype(a):
    """
    -a(int)
    """
    assert type(a) == int

@task
def deftype(a=7):
    """
    """
    assert type(a) == int


@task
def greet(who, shout=False, times=1):
    """
    Sends greetings from moke.
    
    -who(str2) two persons to greet
    -shout(switch) triggers CAPS
    
    """
    greetings = ("Hello %s and %s!\n" % (who[0], who[1])) * times
    if shout:
        greetings = greetings.upper()
    print greetings
    
if __name__ == "__main__":
    task()