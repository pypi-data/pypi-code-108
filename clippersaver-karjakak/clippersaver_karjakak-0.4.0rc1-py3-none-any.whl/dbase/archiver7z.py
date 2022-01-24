# -*- coding: utf-8 -*-
# Copyright (c) 2020, KarjaKAK
# All rights reserved.

from py7zr import SevenZipFile as szf
import os


class Ziper:
    """
    Archiving folders and files.
    """

    def __init__(self, filen: str):
        self.filen = filen

    def ziper7z(self, name: str, pssd: str):
        # Archiving folders and files to .7z.

        if os.path.isfile(self.filen):
            try:
                with szf(f"{name}.7z", mode="w", password=pssd) as tf:
                    if os.path.isfile(self.filen):
                        tf.write(self.filen)
                    else:
                        raise Exception("File is not exist!")
            except Exception as e:
                raise e
        else:
            raise Exception("Nothing to archive!")

    def extfile(self, name: str, pssd: str):
        # Extract file.

        if os.path.isfile(f"{name}.7z"):
            try:
                with szf(f"{name}.7z", mode="r", password=pssd) as tf:
                    tf.extract(targets=self.filen)
            except Exception as e:
                raise e
        else:
            raise Exception("Archive not exist yet!")
