#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
"""Pyxel examples downloader."""

import shutil
from os import listdir, remove, rmdir
from os.path import isdir, join
from zipfile import ZipFile

import requests
from tqdm import tqdm


def download_examples(foldername: str = "pyxel-examples", force: bool = False) -> None:
    """Download and save examples from Pyxel Data Gitlab repository in the working directory.

    Parameters
    ----------
    foldername: str
    force: bool
    """

    if isdir(foldername) and not force:
        raise OSError(
            f"Folder {foldername} already exists. Either delete it, "
            f"use a different name, or use the '--force' argument."
        )
    elif isdir(foldername) and force:
        shutil.rmtree(foldername)

    url = "https://gitlab.com/esa/pyxel-data/-/archive/master/pyxel-data-master.zip"
    response = requests.get(url, stream=True)

    total = int(response.headers.get("content-length", 0))
    with open("examples_tmp.zip", "wb") as tmp, tqdm(
        desc="Downloading examples",
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = tmp.write(data)
            bar.update(size)

    with ZipFile("examples_tmp.zip", "r") as zipobj:
        zipobj.extractall(foldername)

    root = foldername
    for filename in listdir(join(root, "pyxel-data-master")):
        shutil.move(join(root, "pyxel-data-master", filename), join(root, filename))
    rmdir(join(root, "pyxel-data-master"))

    remove("examples_tmp.zip")

    print("Done.")
