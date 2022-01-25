import pandas as pd
import string
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from streng.codes.greek.eak2000.raw.ch2.seismic_action import spectra
import openpyxl # import load_workbook
from tabulate import tabulate
from ....phd.building_models.model2d_older.slab_loads import *


# D:\MyBooks\Keimeno\Κεφάλαιο3\Υλικό\FrameAnalyzer\ExcelFiles001\Frames_initial

@dataclass
class Model2d:
    """
    Reads building data from an excel workbook

    ..
        .. http://mdp.tylingsoft.com/#class-diagram
        .. https://media.readthedocs.org/pdf/brandons-sphinx-tutorial/latest/brandons-sphinx-tutorial.pdf
        .. mermaid::

            classDiagram
            Class01 <|-- AveryLongClass : Cool
            Class03 *-- Class04
            Class05 o-- Class06
            Class01 : input_excel_filename (str)
            Class01 : input_data (dict)
            Class01 : input_info (dict)


    Args:
        input_excel_filename (str): Path and filename of the excel input file
        input_data (dict): A dictionary of pandas dataframes with data read from excel worksheets
        input_info (dict): A dictionary with additional input data given in a worksheet named `info`

        stories_total (int): Number of stories (read from joint_coordinates)
        stories_levels (list): A list with storey levels e.g. [4.5, 7.5, 10.5, ...] (read from joint_coordinates)
        stories_heights (list): A list with storey heights e.g. [4.5, 3.0, 3.0, ...] (read from stories_levels)
        x_levels (list): A list with x coordinates of the building (read from joint_coordinates)


    """
    input_excel_filename: str
    input_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    input_info: Dict = field(default_factory=dict)

    stories_total: int = None
    stories_levels: List[float] = field(default_factory=list)
    stories_heights: List[float] = field(default_factory=list)
    x_levels: List[float] = field(default_factory=list)


    def __post_init__(self):
        """
        Calls the functions that reads the excel file and process model properties
        """
        self.read_excel()
        self.process_joint_coordinates()
        self.process_node_slab_connectivity()
        self.process_beam_slab_connectivity()
        self.process_storey_masses()


    def read_excel(self):
        # info worksheet
        wb = openpyxl.load_workbook(filename=self.input_excel_filename, read_only=True)
        i = 1
        while wb['info'][f'B{i}'].value != None:
            self.input_info[ wb['info'][f'A{i}'].value] = wb['info'][f'B{i}'].value
            i+=1

        self.input_data['joint_coordinates'] = pd.read_excel(io=self.input_excel_filename,
                                                             sheet_name='dtNodes',
                                                             index_col='NodeID')

        self.input_data['materials_concrete'] = pd.read_excel(io=self.input_excel_filename,
                                                              sheet_name='dtConcrete')
        self.input_data['materials_steel'] = pd.read_excel(io=self.input_excel_filename,
                                                           sheet_name='dtSteel')

        self.input_data['sections'] = pd.read_excel(io=self.input_excel_filename,
                                                  sheet_name='dtSections',
                                                  index_col = 'SectionName')

        self.input_data['elements'] = pd.read_excel(io=self.input_excel_filename,
                                                  sheet_name='dtElements',
                                                  index_col = 'ElementID')

        self.input_data['node_slab_connectivity'] = pd.read_excel(io=self.input_excel_filename,sheet_name='dtNodeSlabConn',
                                                                  index_col = 'NodeID').query('Storey>=1').fillna('')

        self.input_data['beam_slab_connectivity'] = pd.read_excel(io=self.input_excel_filename,sheet_name='dtBeamSlabConn',
                                                               index_col = 'ElementID').fillna('')



    def process_joint_coordinates(self):
        self.stories_total = max(self.input_data['joint_coordinates']['Storey'].unique())
        self.stories_levels = self.input_data['joint_coordinates']['Z'].unique().tolist()
        self.x_levels = self.input_data['joint_coordinates']['X'].unique().tolist()

        st_h = []
        for i in range(0,self.stories_total):
            st_h.append(self.stories_levels[i+1] - self.stories_levels[i])
        self.stories_heights = st_h


    def process_node_slab_connectivity(self):

        _df_input = self.input_data['node_slab_connectivity']

        _df = pd.DataFrame(columns=['NodeID'])

        # import general info
        _building_type = self.input_info['building_type']
        _γσκυρ = self.input_info['γσκυρ']
        _gπλ = self.input_info['gπλ']
        _qπλ = self.input_info['qπλ']
        _qπλ = self.input_info['qπλ']
        _hf = self.input_info['hf']
        _gτοιχ_in = self.input_info['gτοιχ_in']
        _gτοιχ_out = self.input_info['gτοιχ_out']
        _hτοιχ = self.input_info['hτοιχ']
        _b_beam_y = self.input_info['b_beam_y']
        _h_beam_y = self.input_info['h_beam_y']
        _L_beam_y = self.input_info['L_beam_y']
        _h_storey = self.input_info['h_storey']


        for index, row in _df_input.iterrows():
            # import from excel table
            _NodeID = index
            _storey = row['Storey']
            _pointEtabs = row['Point_Etabs']
            _frame_trans_loc = row['Frame_Trans_Loc']
            _slabConnΔ1 = row['SlabConΔ1']
            _slabConnΔ2 = row['SlabConΔ2']

            # Ίδιο βάρος στύλου
            if _storey != self.stories_total:
                i = self.input_data['elements'].query(
                    '(NodeI==@_NodeID) & (ElementType!="BEAM")').first_valid_index()
                _col_geom_name = self.input_data['elements']['GeometryName'][i]
                _b_col, _h_col = self.get_element_b_h(_col_geom_name)
            else:
                _col_geom_name = ''
                _b_col, _h_col = 0., 0.

            # Ίδιο βάρος τοιχοπληρώσεων
            if _frame_trans_loc == 'IN':
                _gτοιχ = _gτοιχ_in
            else:
                _gτοιχ = _gτοιχ_out

            # Φορτία δοκών
            if _slabConnΔ1 != '':
                _gΔ1πλ = phd_beam_loads_from_slabs(_building_type, _slabConnΔ1, _gπλ)
                _qΔ1 = phd_beam_loads_from_slabs(_building_type, _slabConnΔ1, _qπλ)
                _gΔ1ΙΒ = _γσκυρ * _b_beam_y * (_h_beam_y - _hf)
                if _storey != self.stories_total:
                    _gΔ1τοιχ = _gτοιχ * _hτοιχ
                else:
                    _gΔ1τοιχ = 0.0
                _gΔ1ολ = _gΔ1πλ + _gΔ1ΙΒ + _gΔ1τοιχ
            else:
                _gΔ1πλ = 0.
                _qΔ1 = 0.
                _gΔ1ΙΒ = 0.
                _gΔ1τοιχ = 0.
                _gΔ1ολ = 0.

            if _slabConnΔ2 != '':
                _gΔ2πλ = phd_beam_loads_from_slabs(_building_type, _slabConnΔ2, _gπλ)
                _qΔ2 = phd_beam_loads_from_slabs(_building_type, _slabConnΔ2, _qπλ)
                _gΔ2ΙΒ = _γσκυρ * _b_beam_y * (_h_beam_y - _hf)
                if _storey != self.stories_total:
                    _gΔ2τοιχ = _gτοιχ * _hτοιχ
                else:
                    _gΔ2τοιχ = 0.0
                _gΔ2ολ = _gΔ2πλ + _gΔ2ΙΒ + _gΔ2τοιχ
            else:
                _gΔ2πλ = 0.
                _qΔ2 = 0.
                _gΔ2ΙΒ = 0.
                _gΔ2τοιχ = 0.
                _gΔ2ολ = 0.

            _G = (_gΔ1ολ + _gΔ2ολ) * _L_beam_y / 2.0 + _γσκυρ * _b_col * _h_col * _h_storey
            _Q = (_qΔ1 + _qΔ2) * _L_beam_y / 2.0


            _df = _df.append({'NodeID': _NodeID,
                              'Storey': _storey,
                              'Point_Etabs': _pointEtabs,
                              'ColGeom': _col_geom_name,
                              'gπλ': _gπλ,
                              'qπλ': _qπλ,
                              'hf': _hf,
                              'gτοιχ': _gτοιχ,
                              'hτοιχ': _hτοιχ,
                              'b_col': _b_col,
                              'h_col': _h_col,
                              'b_beam_y': _b_beam_y,
                              'h_beam_y': _h_beam_y,
                              'gΔ1πλ': _gΔ1πλ,
                              'qΔ1': _qΔ1,
                              'gΔ2πλ': _gΔ2πλ,
                              'qΔ2': _qΔ2,
                              'gΔ1ΙΒ': _gΔ1ΙΒ,
                              'gΔ1τοιχ': _gΔ1τοιχ,
                              'gΔ1': _gΔ1ολ,
                              'gΔ2ΙΒ': _gΔ2ΙΒ,
                              'gΔ2τοιχ': _gΔ2τοιχ,
                              'gΔ2': _gΔ2ολ,
                              'G': _G,
                              'Q': _Q,
                              },
                              ignore_index=True)

        self.input_data['node_loads'] = _df


    def process_beam_slab_connectivity(self):
        _df_input = self.input_data['beam_slab_connectivity']

        _df = pd.DataFrame(columns=['ElementID',
                                    'GeometryName'])

        # import general info
        _building_type = self.input_info['building_type']
        _γσκυρ = self.input_info['γσκυρ']
        _gπλ = self.input_info['gπλ']
        _qπλ = self.input_info['qπλ']
        _qπλ = self.input_info['qπλ']
        _hf = self.input_info['hf']
        _gτοιχ_in = self.input_info['gτοιχ_in']
        _gτοιχ_out = self.input_info['gτοιχ_out']
        _hτοιχ = self.input_info['hτοιχ']

        for index, row in _df_input.iterrows():
            # import from excel table
            _elementID = index
            _geom_name = row['GeometryName']
            _storey = row['Storey']
            _lineEtabs = row['Line_Etabs']
            _slabConn = row['SlabConnectivity']
            _frameLoc = row['Frame_Loc']

            if _frameLoc == 'IN':
                _gτοιχ = _gτοιχ_in
            else:
                _gτοιχ = _gτοιχ_out

            _b, _h = self.get_element_b_h(_geom_name)

            _gΔΙΒ = _γσκυρ * _b * (_h - _hf)

            if _storey != self.stories_total:
                _gΔτοιχ = _gτοιχ * _hτοιχ
            else:
                _gΔτοιχ = 0.0

            _gΔπλ = phd_beam_loads_from_slabs(_building_type, _slabConn, _gπλ)
            _qΔ = phd_beam_loads_from_slabs(_building_type, _slabConn, _qπλ)

            _gΔολ = _gΔπλ + _gΔΙΒ + _gΔτοιχ


            _df = _df.append({'ElementID': _elementID,
                              'GeometryName': _geom_name,
                              'Storey': _storey,
                              'Line_Etabs': _lineEtabs,
                              'SlabConnectivity': _slabConn,
                              'gπλ': _gπλ,
                              'qπλ': _qπλ,
                              'hf': _hf,
                              'gτοιχ': _gτοιχ,
                              'hτοιχ': _hτοιχ,
                              'b': _b,
                              'h': _h,
                              'gΔΙΒ': _gΔΙΒ,
                              'gΔτοιχ': _gΔτοιχ,
                              'gΔπλ': _gΔπλ,
                              'gΔ': _gΔολ,
                              'qΔ': _qΔ},
                              ignore_index=True)

        self.input_data['beam_loads'] = _df


    def process_storey_masses(self):

        m_nodes = []
        _df_input_nodal = self.input_data['node_loads']

        for i in range(0, self.stories_total):
          _g =  _df_input_nodal.query(f'Storey=={i+1}')['G'].sum()
          _q =  _df_input_nodal.query(f'Storey=={i+1}')['Q'].sum()
          m_nodes.append((_g + 0.3 * _q)/9.81)

        m_beams = []
        _df_input_nodal = self.input_data['beam_loads']
        for i in range(0, self.stories_total):
            _load = 0.
            beams_in_storey = _df_input_nodal.query(f'Storey=={i+1}')
            for index, row in beams_in_storey.iterrows():
                _element_id = row['ElementID']
                _gbeam = row['gΔ']
                _qbeam = row['qΔ']
                _element_length = self.get_element_length_by_ID(_element_id)
                _load += (_gbeam + 0.3 * _qbeam) * _element_length

            m_beams.append(_load / 9.81)

        m_tot = [sum(x) for x in zip(m_nodes, m_beams)]

        _data = {'Storey':[i for i in range(1, self.stories_total+1)], 'mass_nodes': m_nodes, 'mass_beams': m_beams, 'mass': m_tot}
        self.input_data['masses'] = pd.DataFrame(data=_data)

    def get_element_length_by_ID(self, elementID):
        _nodeI = self.input_data['elements']['NodeI'][elementID]
        _nodeJ = self.input_data['elements']['NodeJ'][elementID]

        _nodeI_X = self.input_data['joint_coordinates']['X'][_nodeI]
        _nodeI_Y = self.input_data['joint_coordinates']['Y'][_nodeI]
        _nodeI_Z = self.input_data['joint_coordinates']['Z'][_nodeI]

        _nodeJ_X = self.input_data['joint_coordinates']['X'][_nodeJ]
        _nodeJ_Y = self.input_data['joint_coordinates']['Y'][_nodeJ]
        _nodeJ_Z = self.input_data['joint_coordinates']['Z'][_nodeJ]

        return self.get_element_length(_nodeI_X, _nodeI_Y, _nodeI_Z, _nodeJ_X, _nodeJ_Y, _nodeJ_Z)


    @staticmethod
    def get_element_length(x_start, y_start, z_start, x_end, y_end, z_end):
        return ((x_end - x_start)**2 + (y_end - y_start)**2 + (z_end - z_start)**2)**0.5


    def get_element_b_h(self, section_name):
        _b = self.input_data['sections']['b'][section_name]
        _h = self.input_data['sections']['h'][section_name]
        return _b, _h


    def show_tabulate_input(self, input_table_name):
        return tabulate(self.input_data[input_table_name], headers="keys")