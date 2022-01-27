#!python3

#from rdflib import Graph, URIRef
from os import listdir, getcwd
# from os.path import isfile, join
# from datetime import datetime
# import pandas as pd
import sys

from functions import get_files, uniqid, nt2ttl

mypath = getcwd()+ "/data"

argv = sys.argv[1:]
if argv[0] == "uniqid":

    all_files = get_files(mypath,"csv")
    for a in all_files:
        afile = mypath + "/" + a
        print(afile)
        uniqid(afile)

elif argv[0] == "2ttl":

    all_files = get_files(argv[0],"nt")
    for a in all_files:
        afile = argv[0] + "/" + a
        nt2ttl(afile)

else:
    print("You must provide an argument depending on your choosen functionality, like 'uniqid' or '2ttl'")