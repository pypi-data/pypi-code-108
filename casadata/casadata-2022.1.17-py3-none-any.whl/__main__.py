import sys
import casadata
import subprocess

for flag in sys.argv:
    if flag == '--datapath':
        print(casadata.datapath)
    if flag == '--update':
        #_tmp = subprocess.run(['rsync','-qavz','rsync://casa-rsync.nrao.edu/casa-data',casadata.datapath])
        sys.exit("incremental update of data is no longer supported\nplease use pip to update the runtime data, for example:\n\ncasa-6.1.1-36/bin/pip3 install --upgrade  --extra-index-url https://go.nrao.edu/pypi casadata\n\nfor more information see:\nhttps://casadocs.readthedocs.io/en/latest/notebooks/external-data.html")
    if flag == '--help':
        print("--datapath\t\tprint path to data repository")
