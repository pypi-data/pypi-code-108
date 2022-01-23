import sys
from pandas import DataFrame as DF
import pandas as pd
from  pathlib import PurePath
import argparse as ap
extensions=["pkl","ftr","json","xlsx","csv","md","latex","parquet"]
extensions_save_function = ""


parser=ap.ArgumentParser(description=
"""Convert a Pandas dataframe in Pickle format to another format.  Mainly useful if you want to use the dataframe in another environment, like R or Julia""")
parser.add_argument('-i',help="pickle file containing a pandas dataframe.  defaults to standard in if not specified",nargs=1,dest="infile")
parser.add_argument(
    '-o',
    help=f"""pickle file containing a pandas dataframe.  defaults to standard out if not specified.  File extension 
    determined the output type.  choose an extension  of {extensions}.  Seperate multiple files with spaces."""
    ,nargs='*',dest="ofiles",default=[])
parser.add_argument('-x',help=f"write to standard output.  Specify the type, one of {extensions}",dest="x")

def eprint(*stuff,**kwstuff):
    print(file=sys.stderr,*stuff,**kwstuff)

def main():
    eprint("hi")
    a=parser.parse_args()
    eprint(a)

    to_read = a.infile[0] if a.infile else sys.stdin

    df=pd.read_pickle(to_read)

    #create a map from file extension desired to a function to produce it
    writing_functions = [df.to_pickle,df.to_feather,df.to_json,df.to_excel,df.to_csv,df.to_markdown,df.to_latex,df.to_parquet]

    f_map=dict(zip(extensions,writing_functions))
    k=f_map.keys()
    eprint(f"\nKeys {k}")
    #eprint(f"f_map {f_map}\n")
    for ofile in a.ofiles:
        suffix=(PurePath(ofile).suffix)[1:]  #remove the period from the suffix
        f_map[suffix](ofile)     #select the function and write to the file.  traceback if user specifies invalid extension

    if a.x:
        f_map[a.x](sys.stdout)              #select the file type for standard out.  traceback if invalid or not supplied


main()