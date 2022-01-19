# fmt: off
# This file is automatically generated, DO NOT EDIT

from os.path import abspath, join, dirname
_root = abspath(dirname(__file__))

libinit_import = "ctre._init_ctre"
depends = ['wpiutil', 'wpiHal', 'wpilibc', 'wpilib_core', 'ctre_simCANCoder', 'ctre_simPigeonIMU', 'ctre_simVictorSPX', 'ctre_simTalonFX', 'ctre_simTalonSRX', 'ctre_cci_sim', 'ctre_api_sim', 'ctre_wpiapi_sim']
pypi_package = 'robotpy-ctre'

def get_include_dirs():
    return [join(_root, "include"), join(_root, "rpy-include")]

def get_library_dirs():
    return []

def get_library_dirs_rel():
    return []

def get_library_names():
    return []

def get_library_full_names():
    return []