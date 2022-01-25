#from hartools import vobs
from hartools import vobs as vobs
from pytest import mark
from pytest import fixture
import os
import sys
import subprocess
import shutil

@fixture
def prepare_data():
    """
    Extract data and return path
    """
    tarball = "vobs_sample.tgz"
    wrkdir = "/tmp/vobs"
    if not os.path.isdir(wrkdir): os.makedirs(wrkdir)
    cwd = os.getcwd()
    shutil.copy(os.path.join(cwd,tarball),wrkdir)
    os.chdir(wrkdir)
    cmd = f"tar -zxvf {tarball} --strip-components 6"
    try:
        out=subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as err:
        print(f"Error in subprocess {err}")
    datapath = wrkdir
    return datapath

@fixture
def set_input(data_path):
    period = '20220115-20220115'
    datadir = data_path
    return [period, datadir]
    
    
def Testvobs(set_input):  
    period = set_input[0]
    datadir = set_input[1]
    #period='20220115-20220115'
    #datadir='/scratch/ms/dk/nhd/tmp/vobs/'
    vobs_data = vobs(period=period, datadir=datadir)
    print(vobs_data.data_synop)
    assert vobs_data.data_synop.shape[0] == 24

