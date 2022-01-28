#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import urllib
import zipfile
from os.path import join, isdir, isfile, exists
import tempfile
from sys import argv, version_info
if version_info[0] == 3:
    import urllib.request
from os import listdir

ARCH_NAME = "faust_data-3.5.2.zip"
BASE_URL = "https://gitlab.inria.fr/faustgrp/gforge_files/-/raw/master/"

def download_uncompress(uncompress_dir=None, base_url=BASE_URL,
                        arch_name=ARCH_NAME, data_name="FAuST data",
                        already_downloaded_msg=False,
                        extra_file_to_check_dl=None):
    ARCH_URL = "/".join([base_url, arch_name])

    TMP_DIR = tempfile.gettempdir()
    DEST_FILE = join(TMP_DIR, arch_name)

    def reporthook(x,y,z):
        print("\rDownloading", data_name, ":", int((x*y)*100.0/z),'%', end='')

    if(uncompress_dir):
        if(not isdir(uncompress_dir)):
            raise Exception(uncompress_dir+" is not an existing "
                            "directory/folder.")
        loc_files = [f for f in listdir(uncompress_dir) if isfile(join(uncompress_dir, f))]
        if(len(loc_files) > 0 and (extra_file_to_check_dl == None or
                                   exists(join(uncompress_dir,
                                               extra_file_to_check_dl)))):
            if(already_downloaded_msg):
                print("It seems ", data_name, "is already available locally. To renew"
                      " the download please empty the directory:", uncompress_dir)
            return

    if version_info[0] == 2:
        urllib.urlretrieve (ARCH_URL, DEST_FILE, reporthook=reporthook)
    else:
        urllib.request.urlretrieve (ARCH_URL, DEST_FILE, reporthook=reporthook)

    print()

    print("====== data downloaded:", DEST_FILE)

    if uncompress_dir and isdir(uncompress_dir):
        print("Uncompressing zip archive to", uncompress_dir)
        zip_ref = zipfile.ZipFile(DEST_FILE, 'r')
        zip_ref.extractall(uncompress_dir)
        zip_ref.close()


if __name__ == '__main__':
    uncompress_dir=None
    if len(argv) > 1 and isdir(argv[1]):
        uncompress_dir=argv[1]
    download_uncompress(uncompress_dir)
