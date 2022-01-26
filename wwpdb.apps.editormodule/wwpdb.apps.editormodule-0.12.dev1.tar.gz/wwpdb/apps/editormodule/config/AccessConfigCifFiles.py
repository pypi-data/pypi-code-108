import os


def get_display_view_info_cif():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "pdbx_display_view_info.cif")


def get_display_view_info_master_cif():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "pdbx_display_view_info_master.cif")
