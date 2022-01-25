#
# this is the pyinstaller hook which describes how to collect data to freeze the
# 'globus_sdk' correctly
#
# pyinstaller hooks are modules which define a number of known variables, which
# pyinstaller then loads and uses
#
#
# This module is based on the PyInstaller Hook Sample
# see:  https://github.com/pyinstaller/hooksample
#

from PyInstaller.utils.hooks import collect_data_files

# "datas" is a list of files which need to be included as data files
# collect_data_files will crawl the source tree and grab up *all* non-python files
# exclude any files in the pyinstaller dir
datas = collect_data_files("globus_sdk", excludes=["_pyinstaller"])
