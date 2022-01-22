#!/usr/bin/env python
import getpass
import zipfile
from pathlib import Path

import codefast as cf


class Configurations(type):
    @property
    def accounts(cls) -> dict:
        """ init configureation file on installing library."""
        _config_path = str(Path.home()) + "/.config/"
        _cf = _config_path + 'dofast.json'
        if not cf.io.exists(_cf):
            zip_json = f"{cf.io.dirname()}/dofast.json.zip"
            with zipfile.ZipFile(zip_json, 'r') as zip_ref:
                zip_ref.extractall(
                    path=_config_path,
                    pwd=bytes(
                        getpass.getpass("type here your config password: "),
                        'utf-8'))
        cls._accounts = cf.js(_cf)
        return cls._accounts


class InitConfig(metaclass=Configurations):
    pass
