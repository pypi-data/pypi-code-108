import pandas as pd
import string
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from streng.codes.greek.eak2000.raw.ch2.seismic_action import spectra
import openpyxl # import load_workbook
from tabulate import tabulate
from streng.phd.building_models.model2d_older.slab_loads import *
from streng.phd.building_models.model2d_older.model_input import Model2d


# D:\MyBooks\Keimeno\Κεφάλαιο3\Υλικό\FrameAnalyzer\ExcelFiles001\Frames_initial

@dataclass
class EtabsModel2d(Model2d):
    etabs_filename: str = ''
    etabs_file_text: List[str] = field(default_factory=list)


    def etabs_write_file(self):
        self._etabs_write_info()
        self._etabs_write_stories()
        self._etabs_write_diaphragm_names()
        self._etabs_write_grids()
        self._etabs_write_point_coordinates()
        self._etabs_write_line_connectivities()
        self._etabs_write_point_assigns()
        self._etabs_write_material_properties()
        self._etabs_write_frame_sections()
        self._etabs_write_line_assigns()
        self._etabs_write_static_load_cases()
        self._etabs_write_element_loads()
        self._etabs_write_point_loads()
        self._etabs_write_spectrum_function()
        self._etabs_write_spectrum_cases()
        self._etabs_write_analysis_options()

        self.etabs_file_text.append('  END')
        self.etabs_file_text.append('$ END OF MODEL FILE')

        file = open(self.etabs_filename, 'w')
        file.write('\n'.join(self.etabs_file_text))
        file.close()

    def _etabs_write_info(self):
        self.etabs_file_text.append('$ PROGRAM INFORMATION')
        self.etabs_file_text.append('  PROGRAM  "ETABS"  VERSION "9.7.2"')
        self.etabs_file_text.append('')
        self.etabs_file_text.append('$ CONTROLS')
        self.etabs_file_text.append('  UNITS  "KN"  "M"  ')
        self.etabs_file_text.append('  TITLE1  "university"  ')
        self.etabs_file_text.append('  PREFERENCE  MERGETOL 0.001')
        self.etabs_file_text.append('  RLLF  METHOD "TRIBAREAUBC97"  USEDEFAULTMIN "YES"  ')
        self.etabs_file_text.append('')


    def _etabs_write_analysis_options(self):
        self.etabs_file_text.append('$ ANALYSIS OPTIONS')
        self.etabs_file_text.append('  ACTIVEDOF "UX UZ RY"  ')
        self.etabs_file_text.append(f'  DYNAMICS  MODES {3*self.stories_total}  MODETYPE "EIGEN"  TOL 1E-09')
        self.etabs_file_text.append('  MASSOPTIONS  GRAVITY 9.81  SOURCE "LOADS"  LATERALONLY "YES"    STORYLEVELONLY "YES"  ')
        self.etabs_file_text.append('  MASSOPTIONS  LOAD "G"  FACTOR 1')
        self.etabs_file_text.append('  MASSOPTIONS  LOAD "Q"  FACTOR 0.3')
        self.etabs_file_text.append('')


    def _etabs_write_stories(self):
        self.etabs_file_text.append('$ STORIES - IN SEQUENCE FROM TOP')
        self.etabs_file_text.append(f'  STORY "STORY{self.stories_total}"  HEIGHT {self.stories_heights[self.stories_total-1]}  MASTERSTORY "Yes"')
        for i in range(self.stories_total-1, 0, -1):
            self.etabs_file_text.append(f'  STORY "STORY{i}"  HEIGHT {self.stories_heights[i-1]}  SIMILARTO "STORY{self.stories_total}"')
        self.etabs_file_text.append('  STORY "BASE"  ELEV 0')
        self.etabs_file_text.append('')

    def _etabs_write_diaphragm_names(self):
        self.etabs_file_text.append('$ DIAPHRAGM NAMES')
        for i in range(1, self.stories_total+1):
            self.etabs_file_text.append(f'  DIAPHRAGM "DIAPH{i}"    TYPE RIGID')
        self.etabs_file_text.append('')

    def _etabs_write_grids(self):
        alphabet = list(string.ascii_uppercase)
        self.etabs_file_text.append('$ GRIDS')
        self.etabs_file_text.append('  COORDSYSTEM "GLOBAL"  TYPE "CARTESIAN"  BUBBLESIZE 1.25')
        for i, val in enumerate(self.x_levels):
            self.etabs_file_text.append(f'  GRID "GLOBAL"  LABEL "{alphabet[i]}"  DIR "X"  COORD {val:.2f}  GRIDTYPE  "PRIMARY"    BUBBLELOC "DEFAULT"  GRIDHIDE "NO"')
        self.etabs_file_text.append('  GRID "GLOBAL"  LABEL "1"  DIR "Y"  COORD 0  GRIDTYPE  "PRIMARY"    BUBBLELOC "SWITCHED"  GRIDHIDE "NO" ')
        self.etabs_file_text.append('')

    def _etabs_write_point_coordinates(self):
        self.etabs_file_text.append('$ POINT COORDINATES')
        for i, val in enumerate(self.x_levels):
            self.etabs_file_text.append(f'  POINT "{i+1}"  {val:.2f} 0 ')
        self.etabs_file_text.append('')

    def _etabs_write_line_connectivities(self):
        self.etabs_file_text.append('$ LINE CONNECTIVITIES')
        for i in range(1, len(self.x_levels) +1):
            self.etabs_file_text.append(f'  LINE  "C{i}"  COLUMN  "{i}"  "{i}"  1')
        for i in range(1, len(self.x_levels)):
            self.etabs_file_text.append(f'  LINE  "B{i}"  BEAM  "{i}"  "{i+1}"  0')
        self.etabs_file_text.append('')

    def _etabs_write_point_assigns(self):
        self.etabs_file_text.append('$ POINT ASSIGNS')
        for i in range(1, len(self.x_levels) +1):
            self.etabs_file_text.append(f'  POINTASSIGN  "{i}"  "BASE"  RESTRAINT "UX UY UZ RX RY RZ" ')
            for j in range(1, self.stories_total + 1):
                self.etabs_file_text.append(f'  POINTASSIGN  "{i}"  "STORY{j}"  DIAPH "DIAPH{j}"  ')
        self.etabs_file_text.append('')

    def _etabs_write_material_properties(self):
        self.etabs_file_text.append('$ MATERIAL PROPERTIES')
        ds = self.input_data['materials_concrete']
        for i in range(len(ds)):
            _concID = ds.at[i, 'ConcID']
            _fc = ds.at[i, 'fc']
            _E= ds.at[i, 'E']
            _U= ds.at[i, 'U']
            _A= ds.at[i, 'A']
            _fy= ds.at[i, 'fy']
            _fys= ds.at[i, 'fys']
            self.etabs_file_text.append(f'  MATERIAL  "{_concID}"  M 0  W 0  TYPE "ISOTROPIC"  E {_E}  U {_U}  A {_A}')
            self.etabs_file_text.append(f'  MATERIAL  "{_concID}"  DESIGNTYPE "CONCRETE"  FY {_fy}  FC {_fc}  FYS {_fys}')
        self.etabs_file_text.append('')

    def _etabs_write_frame_sections(self):
        self.etabs_file_text.append('$ FRAME SECTIONS')
        ds = self.input_data['sections']
        for index, row in ds.iterrows():
            _section_name = index
            _element_type = row['ElementType']
            _b = row['b']
            _h = row['h']
            _hf = self.input_info['hf']
            _frame_loc = row['Frame_Loc']
            if _frame_loc == 'IN':
                _beff = _b + 8 * _hf
            else:
                _beff = _b + 3 * _hf
            _frame = row['Frame']
            if _element_type == 'BEAM':
                self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  MATERIAL "C20"  SHAPE "Tee"  D {_h}  B {_beff}  TF {_hf}  TW {_b}')
                self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  JMOD 0.1  I2MOD 0.5  I3MOD 0.5  MMOD 0  WMOD 0')
            elif _element_type == 'COLUMN':
                self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  MATERIAL "C20"  SHAPE "Rectangular"  D {_h}  B {_b}')
                self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  JMOD 0.1  MMOD 0  WMOD 0')
        self.etabs_file_text.append('')

    def _etabs_write_line_assigns(self):
        self.etabs_file_text.append('$ LINE ASSIGNS')
        _dict = self.input_data['elements'].to_dict('index')
        for row in _dict:
            _line = _dict[row]['Line_Etabs']
            _element_type = _dict[row]['ElementType']
            _storey = _dict[row]['Storey']
            _geometry_name = _dict[row]['GeometryName']
            if _element_type == 'BEAM':
                self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  SECTION "{_geometry_name}"  ANG  0  MAXSTASPC 0.5  LENGTHOFFI 0  LENGTHOFFJ 0  RIGIDZONE 1  CARDINALPT 8    MESH "POINTSANDLINES"')
            elif 'COLUMN' in _element_type:
                self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  SECTION "{_geometry_name}"  ANG  0  MINNUMSTA 3  LENGTHOFFI 0  LENGTHOFFJ 0  RIGIDZONE 1  MESH "POINTSANDLINES"')
        self.etabs_file_text.append('')

    def _etabs_write_static_load_cases(self):
        self.etabs_file_text.append('$ STATIC LOADS')
        self.etabs_file_text.append('  LOADCASE "G"  TYPE  "DEAD"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "Q"  TYPE  "LIVE"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "EXSTAT"  TYPE  "QUAKE"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "EYSTAT"  TYPE  "QUAKE"  SELFWEIGHT  0')
        self.etabs_file_text.append('')


    def _etabs_write_element_loads(self):
        self.etabs_file_text.append('$ LINE OBJECT LOADS')
        ds = self.input_data['beam_loads']
        for index, row in ds.iterrows():
            _line_etabs = row['Line_Etabs']
            _storey = row['Storey']
            _g = row['gΔ']
            _q = row['qΔ']
            self.etabs_file_text.append(f'  LINELOAD  "{_line_etabs}"  "STORY{_storey:.0f}"  TYPE "UNIFF"  DIR "GRAV"  LC "G"  FVAL {_g:.2f}')
            self.etabs_file_text.append(f'  LINELOAD  "{_line_etabs}"  "STORY{_storey:.0f}"  TYPE "UNIFF"  DIR "GRAV"  LC "Q"  FVAL {_q:.2f}')
        self.etabs_file_text.append('')

    def _etabs_write_point_loads(self):
        self.etabs_file_text.append('$ POINT OBJECT LOADS')
        ds = self.input_data['node_loads'] # .query('Storey>=1' )
        for index, row in ds.iterrows():
            _storey = row['Storey']
            _point_etabs = row['Point_Etabs']
            _G = row['G']
            _Q = row['Q']
            self.etabs_file_text.append(f'  POINTLOAD  "{_point_etabs:.0f}"  "STORY{_storey:.0f}"  TYPE "FORCE"  LC "G"    FZ -{_G:.2f}')
            self.etabs_file_text.append(f'  POINTLOAD  "{_point_etabs:.0f}"  "STORY{_storey:.0f}"  TYPE "FORCE"  LC "Q"    FZ -{_Q:.2f}')
        self.etabs_file_text.append('')

    def _etabs_write_spectrum_function(self):
        self.etabs_file_text.append('  FUNCTION "EAKSPEC"  FUNCTYPE "SPECTRUM"  DAMPRATIO 0.05  SPECTYPE "USER"  ')
        _eak_ground = self.input_info['EAK_ground']
        _eak_α = self.input_info['EAK_α']
        x = np.linspace(1e-10, 2, 201)
        y = spectra.Φd(T=x,
                       α=_eak_α*9.81,
                       γI=1.0,
                       T1=spectra.T1(_eak_ground),
                       T2=spectra.T2(_eak_ground),
                       q=3.5,
                       η=1.0,
                       θ=1.0,
                       β0=2.5)
        for i in range(0, len(x)):
            self.etabs_file_text.append(f'  FUNCTION "EAKSPEC"  TIMEVAL "{x[i]:.3f}  {y[i]:.3f}"')
        self.etabs_file_text.append('')

    def _etabs_write_spectrum_cases(self):
        self.etabs_file_text.append('  RSCASE "EX"  DAMP 0.05  DIRCOMBO "SRSS"  ANG 0')
        self.etabs_file_text.append('  RSCASE "EX"  FUNC1 "EAKSPEC"  SF1 1')
        self.etabs_file_text.append('  RSCASE "EX"  MODECOMBO "CQC"')

        self.etabs_file_text.append('')




