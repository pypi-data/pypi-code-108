# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


#if gettext has not been installed, install a fallback in builtins
import builtins
if '_' not in dir(builtins):
    builtins._ = lambda x: x

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def set_up_logging(level):
    # add a handler to prevent basicConfig
    root = logging.getLogger()
    null_handler = NullHandler()
    root.addHandler(null_handler)

    formatter = logging.Formatter("%(levelname)s:%(name)s: %(funcName)s() '%(message)s'")
    logger_sh = logging.StreamHandler()
    logger_sh.setFormatter(formatter)
    for lg in ['emulica.emulation', 'emulica.plot', 'emulica.controller', 'emulica.emuML']:
        logger = logging.getLogger(lg)
        logger.addHandler(logger_sh)
        logger.setLevel(level)
    

