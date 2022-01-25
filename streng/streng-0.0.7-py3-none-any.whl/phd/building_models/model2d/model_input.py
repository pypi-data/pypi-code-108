# import pandas as pd
# import numpy as np
# import math
from dataclasses import dataclass, field
from typing import List, Dict
from tabulate import tabulate
from ....phd.building_models.model2d.slab_loads import *
from ....codes.greek.eak2000.raw.ch2.seismic_action import spectra
from ....ppp.sections.concrete.typical_sections.rectangular_rc import SectionMaterials
from ....ppp.sections.concrete.typical_sections.rectangular_rc import RectangularConcreteSection
from ....codes.greek.kanepe.assessment.section_properties.rectangular import RectangularKanepe as RectKanepe
from ....ppp.sections.concrete.reinforcement.rectangular_reinforcement import RectangularSectionReinforcement
from ....ppp.sections.concrete.reinforcement.combos import LongReinforcementLayer, TransReinforcementLayer
from ....common.io.output import OutputExtended, OutputString
import pickle
import gzip



@dataclass
class Model2d:
    input_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    misc: Dict[str, object] = field(default_factory=dict)

    stories_total: int = 0
    storey_levels: List[float] = field(init=False, repr=False, default_factory=list)
    storey_heights: List[float] = field(init=False, repr=False, default_factory=list)
    x_levels: List[float] = field(init=False, repr=False, default_factory=list)
    master_nodes: List[int] = field(init=False, repr=False, default_factory=list)
    base_level_nodes: List[int] = field(init=False, repr=False, default_factory=list)

    storey_masses: List[float] = field(init=False, repr=False, default_factory=list)
    fist_mode: List[float] = field(init=False, repr=False, default_factory=list)
    periods: List[float] = field(init=False, repr=False, default_factory=list)
    seismic_static_forces: Dict[str, list] = field(init=False, repr=False, default_factory=dict)
    elastic_gravity_element_forces: Dict[int, list] = field(init=False, repr=False, default_factory=dict)

    reinforcement_beams: Dict[str, dict] = field(init=False, repr=False, default_factory=dict)
    reinforcement_beams_kanepe: Dict[str, RectKanepe] = field(init=False, repr=False, default_factory=dict)
    reinforcement_columns_kanepe: Dict[str, RectKanepe] = field(init=False, repr=False, default_factory=dict)

    logs: OutputExtended = field(init=False, repr=False, default_factory=OutputExtended)

    def get_eigen(self):
        from .os_input import OpenSeesModel2d
        os = OpenSeesModel2d(self, inelastic_analysis=False)
        os.tcl_make = True
        os.tcl_filename = ''
        os.os_run_elastic()
        self.periods = os.results.elastic_periods
        self.fist_mode = os.results.elastic_eigenvectors[0]
        self.elastic_gravity_element_forces = os.results.elastic_gravity_element_forces

        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Periods - Eigenvectors  ------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        _log.append('  Mode       Period (sec)')
        for i in range(0, self.stories_total):
            _log.append(f'{i+1:>5} {self.periods[i]:14.4f}')

        _log.append('')
        _log.append('Mode 1 - Horizontal displacements')
        _log.append('  Storey       si')
        for i in range(0, self.stories_total):
            _log.append(f'{i+1:>5} {self.fist_mode[i]:14.4f}')

        _log.append('')
        _log.append('')
        self.logs.outputStrings['eigen'] = OutputString(data=_log)

    def get_seismic_static_forces(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Seismic Static Forces  -------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        T0 = self.periods[0]
        V0_push = 1000.
        storeys = range(1, self.stories_total+1)
        m = np.array(self.storey_masses)
        s = np.array(self.fist_mode)
        ms = m * s

        forces_push_modal = V0_push*ms / sum(ms)
        forces_push_uni = V0_push*m / sum(m)
        forces_eak = np.zeros(len(m))

        if self.misc['EAK_α'] > 0:
            _eak_ground = self.misc['EAK_ground']
            _eak_α = self.misc['EAK_α']
            _eak_Φd = spectra.Φd(T=T0,
                           α=_eak_α*9.81,
                           γI=1.0,
                           T1=spectra.T1(_eak_ground),
                           T2=spectra.T2(_eak_ground),
                           q=3.5,
                           η=1.0,
                           θ=1.0,
                           β0=2.5)

            V0_eak = sum(m) * _eak_Φd

            if T0>1.0:
                VH_eak = min(0.07*T0*V0_eak, 0.25*V0_eak)
            else:
                VH_eak = 0.0

            forces_eak = (V0_eak-VH_eak) * ms / sum(ms)

            _log.append(f'T0 = {T0:.4f}sec')
            _log.append(f'Φd = {_eak_Φd:.3f}m/sec2')
            _log.append(f'V0_eak = {V0_eak:.2f}kN')
            _log.append(f'VH_eak = {VH_eak:.2f}kN')

            _log.append('')

            self.seismic_static_forces['EPUSHmod'] = forces_push_modal.tolist()
            self.seismic_static_forces['EPUSHuni'] = forces_push_uni.tolist()
            self.seismic_static_forces['EXSTAT'] = forces_eak.tolist()



        _df = pd.DataFrame(data = {'storey': storeys, 'm': m, 's': s, 'm*s':ms,
                                   'E_push_modal': forces_push_modal, 'E_push_uni': forces_push_uni,
                                   'E_eak': forces_eak})




        _log.append(tabulate(_df,
                             headers='keys',
                             tablefmt='pipe',
                             floatfmt=".4f"))

        _log.append('')
        _log.append('')
        self.logs.outputStrings['seismic_static_forces'] = OutputString(data=_log)


    def load_excel_single(self, input_excel_filename):
        # Read the excel file
        xls = pd.ExcelFile(input_excel_filename)
        # Get worksheet names
        for sheet_name in xls.sheet_names:
            self.input_data[sheet_name] = xls.parse(sheet_name).set_index(self.excel_index_column[sheet_name])

    def load_excel_collection(self, input_excel_filename, building_props):
        # Read the excel file
        xls = pd.ExcelFile(input_excel_filename)
        # Get worksheet names
        for sheet_name in xls.sheet_names:
            self.input_data[sheet_name] = \
                xls.parse(sheet_name)[xls.parse(sheet_name).Building ==
                                      building_props[sheet_name]].set_index(self.excel_index_column[sheet_name])

    def __post_init__(self):
        self.excel_index_column = dict()
        self.excel_index_column['Misc'] = 'Building'
        self.excel_index_column['Nodes'] = 'NodeID'
        self.excel_index_column['Slabs'] = 'SlabID'
        self.excel_index_column['NodeSlabConn'] = 'NodeID'
        self.excel_index_column['BeamSlabConn'] = 'ElementID'
        self.excel_index_column['Sections'] = 'SectionName'
        self.excel_index_column['Elements'] = 'ElementID'
        self.excel_index_column['Concrete'] = 'ConcID'
        self.excel_index_column['BeamReinforcement'] = 'ReinforcementID'
        self.excel_index_column['ColumnReinforcement'] = 'ReinforcementID'
        self.excel_index_column['ModFactors'] = 'ElementType'

    def prepare(self, get_eigen_from_opensees = False):
        self.process_misc()
        self.process_joint_coordinates()
        self.process_sections()
        self.log_table_elements()
        self.log_table_slabs()
        self.log_node_slab_connectivity()
        self.process_node_slab_connectivity()
        self.log_beam_slab_connectivity()
        self.process_beam_slab_connectivity()
        self.process_storey_masses()

        if get_eigen_from_opensees == True:
            self.get_eigen()
            self.get_seismic_static_forces()


    def prepare_Mtheta(self):
        self.process_beam_reinforcement()
        self.process_column_reinforcement()

    def process_misc(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Process Misc  ----------------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        self.misc = self.input_data['Misc'].iloc[0].to_dict()

        for key, value in self.misc.items():
            _log.append(f'{key} = {value}')
        _log.append('')
        _log.append('')
        self.logs.outputStrings['misc'] = OutputString(data=_log)

    def process_joint_coordinates(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Process Joint Coordinates  ---------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        self.stories_total = max(self.input_data['Nodes']['Storey'])
        self.storey_levels = self.input_data['Nodes']['Z'].unique().tolist()
        self.x_levels = sorted(self.input_data['Nodes']['X'].unique().tolist(), key=float)
        st_h = [self.storey_levels[i + 1] - self.storey_levels[i] for i in range(0, self.stories_total)]
        self.storey_heights = st_h
        self.master_nodes = [int(self.input_data['Nodes'].query(f'Z=={sl}').first_valid_index())
                             for sl in self.storey_levels][1:]
        self.base_level_nodes = self.input_data['Nodes'].query(f'Z==0').index.tolist()

        _log.append(f'stories total = {self.stories_total}')
        _log.append(f'storey levels: {self.storey_levels}')
        _log.append(f'x levels: {self.x_levels}')
        _log.append(f'storey heights: {self.storey_heights}')
        _log.append(f'master nodes: {self.master_nodes}')
        _log.append(f'base level nodes: {self.base_level_nodes}')
        _log.append('')
        _log.append('--------  Coordinates  --------------------------')
        _log.append('   Node         X      Y (Z)      Storey    Point_Etabs')
        for key, value in self.input_data['Nodes'].to_dict('index').items():
            _log.append(f'{key:>7} {value["X"]:9.2f} {value["Z"]:9.2f} {value["Storey"]:>9} {value["Point_Etabs"]:>12}')
        _log.append('')
        _log.append('')
        self.logs.outputStrings['joints'] = OutputString(data=_log)

    def process_sections(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Process Sections  ------------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        # *********** Προσθήκη στήλης με συνεργαζόμενα πλάτη *************************
        beffs = []
        for index, row in self.input_data['Sections'].iterrows():
            if row['ElementType'] == 'BEAM':
                bw = row['b']
                hf = self.misc['hf']
                if row['Frame_Loc'] == 'IN':
                    factor = 8.
                else:
                    factor = 3.
                beffs.append(bw + factor * hf)
            else:
                beffs.append(None)
        self.input_data['Sections']['beff'] = beffs

        _log.append(tabulate(self.input_data['Sections'],
                             headers='keys',
                             tablefmt='pipe',
                             floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['sections'] = OutputString(data=_log)

    def log_table_elements(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Elements Table  --------------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '',
                tabulate(self.input_data['Elements'],
                         headers='keys',
                         tablefmt='pipe',
                         floatfmt=".2f"), '', '']
        self.logs.outputStrings['elements'] = OutputString(data=_log)

    def log_table_slabs(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Slabs Table  -----------------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '',
                tabulate(self.input_data['Slabs'],
                         headers='keys',
                         tablefmt='pipe',
                         floatfmt=".2f"), '', '']
        self.logs.outputStrings['slabs'] = OutputString(data=_log)

    def log_node_slab_connectivity(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Node-Slab Connectivity Table  ------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '',
                tabulate(self.input_data['NodeSlabConn'],
                         headers='keys',
                         tablefmt='pipe',
                         floatfmt=".2f"), '', '']
        self.logs.outputStrings['NodeSlabConnTable'] = OutputString(data=_log)

    def process_node_slab_connectivity(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Process node-slab connectivity  ----------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        _df_input = self.input_data['NodeSlabConn'][self.input_data['NodeSlabConn'].Frame_Trans_Loc.notnull()]
        _df_input = _df_input.fillna(value={'SlabConΔ1': '', 'SlabConΔ2': ''})
        _df_input_nodes_dict = self.input_data['Nodes'].to_dict('index')
        _df = pd.DataFrame(columns=['NodeID'])
        _slabs_dict = self.input_data['Slabs'].to_dict('index')

        # import misc info
        _building_type = self.misc['building_type']
        _γσκυρ = self.misc['γσκυρ']
        _gπλ = self.misc['gπλ']
        _qπλ = self.misc['qπλ']
        _hf = self.misc['hf']
        _gτοιχ_in = self.misc['gτοιχ_in']
        _gτοιχ_out = self.misc['gτοιχ_out']
        _hτοιχ = self.misc['hτοιχ']
        _b_beam_y = self.misc['b_beam_y']
        _h_beam_y = self.misc['h_beam_y']
        _L_beam_y = self.misc['L_beam_y']
        _h_storey = self.misc['h_storey']

        _row_data = dict
        # *****************************************************************
        # **** Φορτία στους κόμβους που συνδέονται με εγκάρσιες δοκούς ****
        # *****************************************************************
        for index, row in _df_input.iterrows():
            row_in_nodes_table = _df_input_nodes_dict[index]
            # import from excel table
            _NodeID = index
            _storey = row_in_nodes_table['Storey']
            _pointEtabs = row_in_nodes_table['Point_Etabs']
            _frame_trans_loc = row['Frame_Trans_Loc']
            _slabConnΔ1 = row['SlabConΔ1']
            _slabConnΔ2 = row['SlabConΔ2']

            _col_geom_name = ''
             # ********* Ίδιο βάρος στύλου ***********************
            if _storey != self.stories_total:
                i = self.input_data['Elements'].query(
                    '(NodeI==@_NodeID) & '
                    '((ElementType=="COLUMN_EX") | (ElementType=="COLUMN_IN")'
                    ' | (ElementType=="WALL"))').first_valid_index()
                if i is not None:
                    _col_geom_name = self.input_data['Elements']['SectionName'][i]
                    _b_col, _h_col = self.get_element_b_h(_col_geom_name)
            else:
                _col_geom_name = ''
                _b_col, _h_col = 0., 0.

            # ********* Ίδιο βάρος τοιχοπληρώσεων ****************
            if _frame_trans_loc == 'IN':
                _gτοιχ = _gτοιχ_in
            else:
                _gτοιχ = _gτοιχ_out

            # ********* Φορτία εγκάρσιων δοκών *******************
            if _slabConnΔ1 != '':
                _gΔ1πλ = phd_beam_loads_from_slabs(_slabs_dict, _slabConnΔ1, _gπλ)
                _qΔ1 = phd_beam_loads_from_slabs(_slabs_dict, _slabConnΔ1, _qπλ)
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
                _gΔ2πλ = phd_beam_loads_from_slabs(_slabs_dict, _slabConnΔ2, _gπλ)
                _qΔ2 = phd_beam_loads_from_slabs(_slabs_dict, _slabConnΔ2, _qπλ)
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

            _G_col = _γσκυρ * _b_col * _h_col * _h_storey

            _G = (_gΔ1ολ + _gΔ2ολ) * _L_beam_y / 2.0 + _G_col
            _Q = (_qΔ1 + _qΔ2) * _L_beam_y / 2.0

            _row_data = {'NodeID': _NodeID,
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
                          'G_col': _G_col,
                          'G': _G,
                          'Q': _Q,
                          }
            _df = _df.append(_row_data, ignore_index=True)

        # *********************************************************************************
        # **** Φορτία στους κόμβους που συνδέονται με τοιχώματα. Ίδιο βάρος τουχωμάτων ****
        # **** Το κάνω ξεχωριστά γιατί δε συνδέονται με εγκάρσιες δοκούς όπως παραπάνω ****
        # *********************************************************************************
        _df_wall_part = self.input_data['Elements'].query('ElementType=="WALL"')
        for index, row in _df_wall_part.iterrows():
            _storey = row['Storey']
            # Ίδιο βάρος τοιχώματος
            if  _storey!= self.stories_total:
                _wall_geom_name = row['SectionName']
                _node_start = row['NodeI']
                _pointEtabs = _df_input_nodes_dict[_node_start]['Point_Etabs']
                _b_wall, _h_wall = self.get_element_b_h(_wall_geom_name)
            else:
                _wall_geom_name = ''
                _b_wall, _h_wall = 0., 0.

            _G_wall = _γσκυρ * _b_wall * _h_wall * _h_storey

            _row_data = {'NodeID': _node_start,
                         'Storey': _storey,
                         'Point_Etabs': _pointEtabs,
                         'ColGeom': _wall_geom_name,
                         'gπλ': 0.0,
                         'qπλ': 0.0,
                         'hf': 0.0,
                         'gτοιχ': 0.0,
                         'hτοιχ': 0.0,
                         'b_col': _b_wall,
                         'h_col': _h_wall,
                         'b_beam_y': 0.0,
                         'h_beam_y': 0.0,
                         'gΔ1πλ': 0.0,
                         'qΔ1': 0.0,
                         'gΔ2πλ': 0.0,
                         'qΔ2': 0.0,
                         'gΔ1ΙΒ': 0.0,
                         'gΔ1τοιχ': 0.0,
                         'gΔ1': 0.0,
                         'gΔ2ΙΒ': 0.0,
                         'gΔ2τοιχ': 0.0,
                         'gΔ2': 0.0,
                         'G_col': _G_wall,
                         'G': _G_wall,
                         'Q': 0.0,
                          }

            _df = _df.append(_row_data, ignore_index=True)

        self.input_data['node_loads'] = _df[_row_data.keys()]

        # *********  Write log  ***********************
        _log.append(tabulate(self.input_data['node_loads'], headers='keys',
                 tablefmt='pipe',
                 floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['node-slab'] = OutputString(data = _log)

    def log_beam_slab_connectivity(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Beam-Slab Connectivity Table  ------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']
        _log.append(tabulate(self.input_data['BeamSlabConn'], headers='keys',
                 tablefmt='pipe',
                 floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['BeamSlabConnTable'] = OutputString(data=_log)

    def process_beam_slab_connectivity(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Process beam-slab connectivity  ----------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        _df_input = self.input_data['BeamSlabConn']
        _df = pd.DataFrame(columns=['ElementID', 'SectionName'])

        # import misc info
        _building_type = self.misc['building_type']
        _γσκυρ = self.misc['γσκυρ']
        _gπλ = self.misc['gπλ']
        _qπλ = self.misc['qπλ']
        _qπλ = self.misc['qπλ']
        _hf = self.misc['hf']
        _gτοιχ_in = self.misc['gτοιχ_in']
        _gτοιχ_out = self.misc['gτοιχ_out']
        _hτοιχ = self.misc['hτοιχ']

        _row_data = dict()

        for index, row in _df_input.iterrows():
            _elementID = index
            _geom_name = row['SectionName']
            _storey = row['Storey']
            _lineEtabs = row['Line_Etabs']
            _slabConn = row['SlabConnectivity']
            _frameLoc = row['Frame_Loc']

            # Φορτίο από ίδιο βάρος
            _b, _h = self.get_element_b_h(_geom_name)
            _gΔΙΒ = _γσκυρ * _b * (_h - _hf)

            # Φορτίο από τοιχοπληρώσεις
            if _frameLoc == 'IN':
                _gτοιχ = _gτοιχ_in
            else:
                _gτοιχ = _gτοιχ_out

            if _storey != self.stories_total:
                _gΔτοιχ = _gτοιχ * _hτοιχ
            else:
                _gΔτοιχ = 0.0

            # Φορτία από πλάκες
            _slabs_dict = self.input_data['Slabs'].to_dict('index')
            _gΔπλ = phd_beam_loads_from_slabs(_slabs_dict, _slabConn, _gπλ)
            _qΔ = phd_beam_loads_from_slabs(_slabs_dict, _slabConn, _qπλ)

            # Συνολικό φορτίο
            _gΔολ = _gΔπλ + _gΔΙΒ + _gΔτοιχ

            if row['SectionName'] != 'RIGID':
                _row_data ={'ElementID': _elementID,
                                  'SectionName': _geom_name,
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
                                  'qΔ': _qΔ}
            else:
                _row_data ={'ElementID': _elementID,
                                  'SectionName': _geom_name,
                                  'Storey': _storey,
                                  'Line_Etabs': _lineEtabs,
                                  'SlabConnectivity': _slabConn,
                                  'gπλ': _gπλ,
                                  'qπλ': _qπλ,
                                  'hf': None,
                                  'gτοιχ': None,
                                  'hτοιχ': None,
                                  'b': None,
                                  'h': None,
                                  'gΔΙΒ': None,
                                  'gΔτοιχ': None,
                                  'gΔπλ': _gΔπλ,
                                  'gΔ': _gΔπλ,
                                  'qΔ': _qΔ}


            _df = _df.append(_row_data, ignore_index=True)
        self.input_data['beam_loads'] = _df[_row_data.keys()]

        # *********  Write log  ***********************
        _log.append(tabulate(self.input_data['beam_loads'], headers='keys',
                             tablefmt='pipe',
                             floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['beam-slab'] = OutputString(data=_log)


    def process_storey_masses(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  Process beam-slab connectivity  ----------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        # ***********  Masses from nodes  **************************
        m_nodes = []
        _df_input_nodal = self.input_data['node_loads']

        for i in range(0, self.stories_total):
          _g =  _df_input_nodal.query(f'Storey=={i+1}')['G'].sum()
          _q =  _df_input_nodal.query(f'Storey=={i+1}')['Q'].sum()
          m_nodes.append((_g + 0.3 * _q)/9.81)

        # ***********  Masses from beams  **************************
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

        # ***********  Total torey masses  *************************
        m_tot = [sum(x) for x in zip(m_nodes, m_beams)]
        self.storey_masses = m_tot
        _data = {'Storey':[i for i in range(1, self.stories_total+1)], 'mass_nodes': m_nodes, 'mass_beams': m_beams, 'mass': m_tot}
        self.input_data['masses'] = pd.DataFrame(data=_data).set_index('Storey')


        # *********  Write log  ***********************
        _log.append(tabulate(self.input_data['masses'], headers='keys',
                             tablefmt='pipe',
                             floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['masses'] = OutputString(data=_log)

    def process_column_reinforcement(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  ColumnReinforcement Table ----------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']
        _dict = self.input_data['ColumnReinforcement'].fillna({'LongSide': '0Φ0', 'SideHoopLegs':0}).to_dict('index')
        _dict_sections = self.input_data['Sections'].to_dict('index')
        _dict_concrete = self.input_data['Concrete'].to_dict('index')
        for key, value in _dict.items():
            _reinforcementID = key
            _sectionID = key
            _b = _dict_sections[_sectionID]['b']
            _h = _dict_sections[_sectionID]['h']
            _cnom = float(self.misc['cnom'])

            _fc = _dict_concrete['CONC']['fc']
            _Ec = _dict_concrete['CONC']['E']
            _fy = _dict_concrete['CONC']['fy']
            _fyw = _dict_concrete['CONC']['fyw']
            _Es = 200.e6

            _element_id = (self.input_data['Elements'].query(f'ReinforcementID=="{_reinforcementID}"')).index.tolist()[0]
            _element_length = self.get_element_length_by_ID(_element_id)

            _longMain = value["LongMain"]
            _longSide = value["LongSide"]
            _trans = value["Trans"]
            _sideHoopLegs = value["SideHoopLegs"]

            _sectionMaterials = SectionMaterials(fc=_fc, Ec=_Ec, fy=_fy, Es=_Es, fyw=_fyw)

            self.reinforcement_columns_kanepe[f'{_reinforcementID}'] = \
                self.__get_kanepe_Mtheta (b=_b, h=_h, cnom=_cnom, length=_element_length, materials=_sectionMaterials,
                                          long1str=_longMain, long2str=_longMain, transstr=_trans,
                                          longVstr=_longSide, disdiastr='0Φ0', N=0., side_legs=_sideHoopLegs)


        # *********  Write log  ***********************
        _log.append(tabulate(self.input_data['ColumnReinforcement'], headers='keys',
                             tablefmt='pipe',
                             floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['column_reinforcement'] = OutputString(data=_log)


    def process_beam_reinforcement(self):
        _log = ['---------------------------------------------------------------------------------------------',
                '-------------  BeamReinforcement Table ------------------------------------------------------',
                '---------------------------------------------------------------------------------------------',
                '']

        _dict = self.input_data['BeamReinforcement'].to_dict('index')
        _dict_sections = self.input_data['Sections'].to_dict('index')
        _dict_concrete = self.input_data['Concrete'].to_dict('index')
        for key, value in _dict.items():
            _reinforcementID = key
            _sectionID = str(_reinforcementID[:_reinforcementID.rfind('.')])
            _b = _dict_sections[_sectionID]['b']
            _h = _dict_sections[_sectionID]['h']
            _cnom = float(self.misc['cnom'])

            _fc = _dict_concrete['CONC']['fc']
            _Ec = _dict_concrete['CONC']['E']
            _fy = _dict_concrete['CONC']['fy']
            _fyw = _dict_concrete['CONC']['fyw']
            _Es = 200.e6

            _element_id = (self.input_data['Elements'].query(f'ReinforcementID=="{_reinforcementID}"')).index.tolist()[0]
            _element_length = self.get_element_length_by_ID(_element_id)

            _longTopLeft = value["LongTopLeft"]
            _longBotLeft = value["LongBotLeft"]
            _transLeft = value["TransLeft"]
            _longTopRight = value["LongTopRight"]
            _longBotRight = value["LongBotRight"]
            _transRight = value["TransRight"]

            _sectionMaterials = SectionMaterials(fc=_fc, Ec=_Ec, fy=_fy, Es=_Es, fyw=_fyw)

            self.reinforcement_beams_kanepe[f'{_reinforcementID}.L.neg'] = \
                self.__get_kanepe_Mtheta (b=_b, h=_h, cnom=_cnom, length=_element_length, materials=_sectionMaterials,
                                        long1str=_longTopLeft, long2str=_longBotLeft, transstr=_transLeft)

            self.reinforcement_beams_kanepe[f'{_reinforcementID}.L.pos'] = \
                self.__get_kanepe_Mtheta (b=_b, h=_h, cnom=_cnom, length=_element_length, materials=_sectionMaterials,
                                        long1str=_longBotLeft, long2str=_longTopLeft, transstr=_transLeft)

            self.reinforcement_beams_kanepe[f'{_reinforcementID}.R.neg'] = \
                self.__get_kanepe_Mtheta (b=_b, h=_h, cnom=_cnom, length=_element_length, materials=_sectionMaterials,
                                        long1str=_longTopRight, long2str=_longBotRight, transstr=_transRight)

            self.reinforcement_beams_kanepe[f'{_reinforcementID}.R.pos'] = \
                self.__get_kanepe_Mtheta (b=_b, h=_h, cnom=_cnom, length=_element_length, materials=_sectionMaterials,
                                        long1str=_longBotRight, long2str=_longTopRight, transstr=_transRight)

        # *********  Write log  ***********************
        _log.append(tabulate(self.input_data['BeamReinforcement'], headers='keys',
                             tablefmt='pipe',
                             floatfmt=".2f"))
        _log.append('')
        _log.append('')
        self.logs.outputStrings['beam_reinforcement'] = OutputString(data=_log)

    def __get_kanepe_Mtheta(self, b, h, cnom, length, materials, long1str, long2str, transstr, longVstr='0Φ0', disdiastr='0Φ0', N=0., side_legs=0):

        _reinf = RectangularSectionReinforcement(
            long1=LongReinforcementLayer.from_string(reinf_string=long1str, units_input='mm', units_output='m'),
            long2=LongReinforcementLayer.from_string(reinf_string=long2str, units_input='mm', units_output='m'),
            longV=LongReinforcementLayer.from_string(reinf_string=longVstr, units_input='mm', units_output='m'),
            disdia=LongReinforcementLayer.from_string(reinf_string=disdiastr, units_input='mm', units_output='m'),
            trans=TransReinforcementLayer.from_string(reinf_string=transstr, units_input='mm', units_output='m'),
            cnom=cnom,
            side_hoop_legs= side_legs)

        return RectKanepe(
                    rcs = RectangularConcreteSection(b=b,
                                                     h=h,
                                                     materials = materials,
                                                     reinforcement = _reinf),
                    Ls = length / 2.0,
                    N = N,
                    calc_on_init = False
                )



    def get_element_length_by_ID(self, elementID):
        _nodeI, _nodeJ = self.get_element_endpoints(elementID)

        _nodeI_X = self.input_data['Nodes']['X'][_nodeI]
        _nodeI_Y = self.input_data['Nodes']['Y'][_nodeI]
        _nodeI_Z = self.input_data['Nodes']['Z'][_nodeI]

        _nodeJ_X = self.input_data['Nodes']['X'][_nodeJ]
        _nodeJ_Y = self.input_data['Nodes']['Y'][_nodeJ]
        _nodeJ_Z = self.input_data['Nodes']['Z'][_nodeJ]

        return self.get_element_length(_nodeI_X, _nodeI_Y, _nodeI_Z, _nodeJ_X, _nodeJ_Y, _nodeJ_Z)

    def get_element_endpoints(self, elementID):
        _nodeI = int(self.input_data['Elements']['NodeI'][elementID])
        _nodeJ = int(self.input_data['Elements']['NodeJ'][elementID])
        return _nodeI, _nodeJ


    @staticmethod
    def get_element_length(x_start, y_start, z_start, x_end, y_end, z_end):
        return ((x_end - x_start)**2 + (y_end - y_start)**2 + (z_end - z_start)**2)**0.5


    def get_element_b_h(self, section_name):
        _b = self.input_data['Sections']['b'][section_name]
        _h = self.input_data['Sections']['h'][section_name]
        return _b, _h


    def save_model(self, pathfilename):
        f = gzip.open(pathfilename + '.model', 'wb', compresslevel=9)
        pickle.dump(self, f)
        f.close()