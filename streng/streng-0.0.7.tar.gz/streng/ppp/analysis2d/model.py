import pandas as pd
from . import s2k_from_pandas as sap_from_pd
from . import tcl_from_pandas as tcl_from_pd


class Input:

    def __init__(self, input_filetype, filename):
        self.__s2k_file = ''
        self.__tcl_file = ''

        if input_filetype == 'excel':
            self.df_nodes = pd.read_excel(filename, sheet_name='nodes')
            self.df_node_restraints = pd.read_excel(filename, sheet_name='node_restraints')
            self.df_node_constraints = pd.read_excel(filename, sheet_name='node_constraints')
            self.df_materials_general = pd.read_excel(filename, sheet_name='materials_general')
            self.df_frame_connectivity = pd.read_excel(filename, sheet_name='frame_connectivity')
            self.df_section_rect_elastic = pd.read_excel(filename, sheet_name='section_rect_elastic')
            self.df_load_patterns = pd.read_excel(filename, sheet_name='load_patterns')
            self.df_masses_nodal = pd.read_excel(filename, sheet_name='masses_nodal')
            self.df_loads_nodal = pd.read_excel(filename, sheet_name='loads_nodal')
            self.df_loads_dist_gravity = pd.read_excel(filename, sheet_name='loads_dist_gravity')

    @staticmethod
    def __save_file(filename, text):
        file = open(filename, 'w')
        file.write(text)
        file.close()

    def make_sap2d_s2k_file(self):
        _str = 'TABLE:  "PROGRAM CONTROL"\n'
        _str += '   ProgramName=SAP2000   Version=14.2.4   CurrUnits="KN, m, C"   RegenHinge=Yes"\n'
        _str += '\n'
        _str += sap_from_pd.sap2d_nodes(self.df_nodes) 
        _str += sap_from_pd.sap2d_gridlines(self.df_nodes) 
        _str += sap_from_pd.sap2d_diaphragms(self.df_node_constraints) 
        _str += sap_from_pd.sap2d_diaphragms_assignments(self.df_node_constraints) 
        _str += sap_from_pd.sap2d_node_restraints(self.df_node_restraints) 
        _str += sap_from_pd.sap2d_frame_connectivity(self.df_frame_connectivity) 
        _str += sap_from_pd.sap2d_materials_general(self.df_materials_general) 
        _str += sap_from_pd.sap2d_materials_basic_mechanical(self.df_materials_general) 
        _str += sap_from_pd.sap2d_frame_section_assignments(self.df_frame_connectivity, self.df_section_rect_elastic)
        _str += sap_from_pd.sap2d_frame_section_properties_general(self.df_section_rect_elastic) 
        _str += sap_from_pd.sap2d_load_patterns(self.df_load_patterns) 
        _str += sap_from_pd.sap2d_load_cases(self.df_load_patterns) 
        _str += sap_from_pd.sap2d_load_cases_static_assignments(self.df_load_patterns) 
        _str += sap_from_pd.sap2d_masses() 
        _str += sap_from_pd.sap2d_masses_nodal(self.df_masses_nodal) 
        _str += sap_from_pd.sap2d_loads_nodal(self.df_loads_nodal) 
        _str += sap_from_pd.sap2d_loads_dist(self.df_loads_dist_gravity)
        self.__s2k_file = _str

    @property
    def s2k_file(self):
        if self.__s2k_file == '':
            return 'You should call "make_sap2d_s2k_file" first'
        else:
            return self.__s2k_file

    def save_s2k_file(self, filename):
        self.__save_file(filename, self.__s2k_file)

    def make_os2d_tcl_file(self):
        _str = ''
        _str += tcl_from_pd.os2d_general()
        _str += tcl_from_pd.os2d_nodes(self.df_nodes)
        _str += tcl_from_pd.os2d_node_restraints(self.df_node_restraints)
        _str += tcl_from_pd.os2d_diaphragms(self.df_node_constraints)
        _str += tcl_from_pd.os2d_masses_nodal(self.df_masses_nodal)
        _str += tcl_from_pd.os2d_frame_connectivity(self.df_frame_connectivity,
                                                    self.df_section_rect_elastic,
                                                    self.df_materials_general)
        self.__tcl_file = _str

    @property
    def tcl_file(self):
        if self.__tcl_file == '':
            return 'You should call "make_os2d_tcl_file" first'
        else:
            return self.__tcl_file

    def save_tcl_file(self, filename):
        self.__save_file(filename, self.__tcl_file)