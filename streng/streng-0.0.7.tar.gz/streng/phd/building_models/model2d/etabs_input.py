import pandas as pd
import string
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from streng.codes.greek.eak2000.raw.ch2.seismic_action import spectra
from streng.phd.building_models.model2d.slab_loads import *
from streng.phd.building_models.model2d.model_input import Model2d

# from streng.codes.greek.kanepe.assessment.section_properties.rectangular import RectangularKanepe
# from streng.ppp.sections.concrete.typical_sections.rectangular_rc import RectangularConcreteSection
# from streng.ppp.sections.concrete.typical_sections.rectangular_rc import SectionMaterials
# from streng.ppp.sections.concrete.reinforcement.rectangular_reinforcement import RectangularSectionReinforcement
# from streng.ppp.sections.concrete.reinforcement.combos import LongReinforcementLayer, TransReinforcementLayer

# D:\MyBooks\Keimeno\Κεφάλαιο3\Υλικό\FrameAnalyzer\ExcelFiles001\Frames_initial

@dataclass
class EtabsModel2d:
    model: Model2d
    etabs_filename: str = ''
    etabs_file_text: List[str] = field(default_factory=list)

    inelastic_analysis: bool = False

    def etabs_write_file(self):
        self._etabs_write_info()
        self._etabs_write_stories()
        self._etabs_write_diaphragm_names()
        self._etabs_write_grids()
        self._etabs_write_piers()
        self._etabs_write_point_coordinates()
        self._etabs_write_line_connectivities()
        self._etabs_write_point_assigns()
        self._etabs_write_material_properties()
        self._etabs_write_frame_sections()
        if self.inelastic_analysis==True:
            self._etabs_write_hinge_properties()
        self._etabs_write_line_assigns()
        self._etabs_write_static_load_cases()
        self._etabs_write_element_loads()
        self._etabs_write_point_loads()
        self._etabs_write_spectrum_function()
        self._etabs_write_spectrum_cases()
        self._etabs_write_analysis_options()
        if self.inelastic_analysis==True:
            self._etabs_write_pushover_cases()

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
        self.etabs_file_text.append(f'  DYNAMICS  MODES {3*self.model.stories_total}  MODETYPE "EIGEN"  TOL 1E-09')
        # self.etabs_file_text.append('  MASSOPTIONS  GRAVITY 9.81  SOURCE "LOADS"  LATERALONLY "YES"    STORYLEVELONLY "YES"  ')
        # self.etabs_file_text.append('  MASSOPTIONS  LOAD "G"  FACTOR 1')
        # self.etabs_file_text.append('  MASSOPTIONS  LOAD "Q"  FACTOR 0.3')
        self.etabs_file_text.append('  MASSOPTIONS  GRAVITY 9.81  SOURCE "MASS"  LATERALONLY "YES"    STORYLEVELONLY "YES"  ')
        self.etabs_file_text.append('')

    def _etabs_write_stories(self):
        self.etabs_file_text.append('$ STORIES - IN SEQUENCE FROM TOP')
        self.etabs_file_text.append(f'  STORY "STORY{self.model.stories_total}"  HEIGHT {self.model.storey_heights[self.model.stories_total - 1]}  MASTERSTORY "Yes"')
        for i in range(self.model.stories_total-1, 0, -1):
            self.etabs_file_text.append(f'  STORY "STORY{i}"  HEIGHT {self.model.storey_heights[i - 1]}  SIMILARTO "STORY{self.model.stories_total}"')
        self.etabs_file_text.append('  STORY "BASE"  ELEV 0')
        self.etabs_file_text.append('')

    def _etabs_write_diaphragm_names(self):
        self.etabs_file_text.append('$ DIAPHRAGM NAMES')
        for i in range(1, self.model.stories_total+1):
            self.etabs_file_text.append(f'  DIAPHRAGM "DIAPH{i}"    TYPE RIGID')
        self.etabs_file_text.append('')

    def _etabs_write_piers(self):
        self.etabs_file_text.append('$ PIER/SPANDREL NAMES')
        self.etabs_file_text.append('  PIERNAME  "P1"')

    def _etabs_write_grids(self):
        alphabet = list(string.ascii_uppercase)
        self.etabs_file_text.append('$ GRIDS')
        self.etabs_file_text.append('  COORDSYSTEM "GLOBAL"  TYPE "CARTESIAN"  BUBBLESIZE 1.25')
        for i, val in enumerate(self.model.x_levels):
            self.etabs_file_text.append(f'  GRID "GLOBAL"  LABEL "{alphabet[i]}"  DIR "X"  COORD {val:.2f}  GRIDTYPE  "PRIMARY"    BUBBLELOC "DEFAULT"  GRIDHIDE "NO"')
        self.etabs_file_text.append('  GRID "GLOBAL"  LABEL "1"  DIR "Y"  COORD 0  GRIDTYPE  "PRIMARY"    BUBBLELOC "SWITCHED"  GRIDHIDE "NO" ')
        self.etabs_file_text.append('')

    def _etabs_write_point_coordinates(self):
        self.etabs_file_text.append('$ POINT COORDINATES')
        for i, val in enumerate(self.model.x_levels):
            self.etabs_file_text.append(f'  POINT "{i+1}"  {val:.2f} 0 ')
        self.etabs_file_text.append('')

    def _etabs_write_line_connectivities(self):
        self.etabs_file_text.append('$ LINE CONNECTIVITIES')


        if self.model.misc['building_type'] == 'frames':
            for i in range(1, len(self.model.x_levels) + 1):
                self.etabs_file_text.append(f'  LINE  "C{i}"  COLUMN  "{i}"  "{i}"  1')
            for i in range(1, len(self.model.x_levels)):
                self.etabs_file_text.append(f'  LINE  "B{i}"  BEAM  "{i}"  "{i+1}"  0')
        else:
            self.etabs_file_text.append(f'  LINE  "C1"  COLUMN  "1"  "1"  1')
            self.etabs_file_text.append(f'  LINE  "C2"  COLUMN  "2"  "2"  1')
            self.etabs_file_text.append(f'  LINE  "C3"  COLUMN  "3"  "3"  1')
            self.etabs_file_text.append(f'  LINE  "C4"  COLUMN  "4"  "4"  1')
            self.etabs_file_text.append(f'  LINE  "C5"  COLUMN  "5"  "5"  1')
            self.etabs_file_text.append(f'  LINE  "C6"  COLUMN  "6"  "6"  1')
            self.etabs_file_text.append(f'  LINE  "C7"  COLUMN  "7"  "7"  1')
            self.etabs_file_text.append(f'  LINE  "C8"  COLUMN  "8"  "8"  1')
            self.etabs_file_text.append(f'  LINE  "C9"  COLUMN  "9"  "9"  1')
            self.etabs_file_text.append(f'  LINE  "C11"  COLUMN  "11"  "11"  1')
            self.etabs_file_text.append(f'  LINE  "C13"  COLUMN  "13"  "13"  1')
            self.etabs_file_text.append(f'  LINE  "B1"  BEAM  "1"  "2"  0')
            self.etabs_file_text.append(f'  LINE  "B2"  BEAM  "2"  "3"  0')
            self.etabs_file_text.append(f'  LINE  "B3"  BEAM  "3"  "4"  0')
            self.etabs_file_text.append(f'  LINE  "B4"  BEAM  "5"  "6"  0')
            self.etabs_file_text.append(f'  LINE  "B5"  BEAM  "6"  "7"  0')
            self.etabs_file_text.append(f'  LINE  "B6"  BEAM  "7"  "8"  0')
            self.etabs_file_text.append(f'  LINE  "B7"  BEAM  "9"  "10"  0')
            self.etabs_file_text.append(f'  LINE  "B8"  BEAM  "10"  "11"  0')
            self.etabs_file_text.append(f'  LINE  "B9"  BEAM  "11"  "12"  0')
            self.etabs_file_text.append(f'  LINE  "B10"  BEAM  "12"  "13"  0')


        self.etabs_file_text.append('')




    def _etabs_write_point_assigns(self):
        self.etabs_file_text.append('$ POINT ASSIGNS')

        masses_dict = self.model.input_data['masses'].to_dict('index')

        # Restraints and diaphragms
        for i in range(1, len(self.model.x_levels) +1):
            self.etabs_file_text.append(f'  POINTASSIGN  "{i}"  "BASE"  RESTRAINT "UX UY UZ RX RY RZ" ')
            for j in range(1, self.model.stories_total + 1):
                self.etabs_file_text.append(f'  POINTASSIGN  "{i}"  "STORY{j}"  DIAPH "DIAPH{j}"  ')

        # Masses
        for i in range(1, self.model.stories_total + 1):
            massX = masses_dict[i]['mass']
            self.etabs_file_text.append(f'  POINTASSIGN  "1"  "STORY{i}"  MASSUXUY {massX:.3f}  ')


        self.etabs_file_text.append('')


    def _etabs_write_material_properties(self):
        self.etabs_file_text.append('$ MATERIAL PROPERTIES')
        # self.etabs_file_text.append('  MATERIAL  "FAKE"  M 0  W 0  TYPE "ISOTROPIC"  E 29000000  U 0.2  A 0')
        # self.etabs_file_text.append('  MATERIAL  "FAKE"  DESIGNTYPE "CONCRETE"  FY 400000  FC 20000  FYS 400000')

        ds = self.model.input_data['Concrete'].to_dict('index')
        for key, value in ds.items():
            _concID = key
            _fc = value['fc']
            _E= value['E']
            _U= value['U']
            _A= value['A']
            _fy= value['fy']
            _fyw= value['fyw']
            self.etabs_file_text.append(f'  MATERIAL  "{_concID}"  M 0  W 0  TYPE "ISOTROPIC"  E {_E}  U {_U}  A {_A}')
            self.etabs_file_text.append(f'  MATERIAL  "{_concID}"  DESIGNTYPE "CONCRETE"  FY {_fy}  FC {_fc}  FYS {_fyw}')
        self.etabs_file_text.append('')

    def _etabs_write_frame_sections(self):
        self.etabs_file_text.append('$ FRAME SECTIONS')
        ds = self.model.input_data['Sections']
        _dict_modFactors = self.model.input_data['ModFactors'].to_dict('index')

        for index, row in ds.iterrows():
            _section_name = index
            _element_type = row['ElementType']
            _b = row['b']
            _h = row['h']
            _hf = self.model.misc['hf']
            _beff = row['beff']
            _frame_loc = row['Frame_Loc']
            _frame = row['Frame']

            mf_area = _dict_modFactors[_element_type]['Area']
            mf_mom = _dict_modFactors[_element_type]['Moment']
            mf_shear = _dict_modFactors[_element_type]['Shear']
            mf_tor = _dict_modFactors[_element_type]['Torsional']

            if _element_type == 'BEAM':
                self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  MATERIAL "CONC"  SHAPE "Tee"  D {_h}  B {_beff}  TF {_hf}  TW {_b}')
            elif 'COLUMN' in _element_type or _element_type == 'WALL' or _element_type == 'RIGID':
                self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  MATERIAL "CONC"  SHAPE "Rectangular"  D {_h}  B {_b}')

            self.etabs_file_text.append(f'  FRAMESECTION  "{_section_name}"  AMOD {mf_area:.2f}  A2MOD {mf_shear:.2f}  A3MOD {mf_shear:.2f}  JMOD {mf_tor:.2f}  I2MOD {mf_mom:.2f}  I3MOD {mf_mom:.2f}  MMOD 0  WMOD 0')

        self.etabs_file_text.append('')

    def _etabs_write_line_assigns(self):
        self.etabs_file_text.append('$ LINE ASSIGNS')
        _dict = self.model.input_data['Elements'].to_dict('index')
        for row in _dict:
            _line = _dict[row]['Line_Etabs']
            _element_type = _dict[row]['ElementType']
            _storey = _dict[row]['Storey']
            _geometry_name = _dict[row]['SectionName']
            if _element_type == 'BEAM':
                self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  SECTION "{_geometry_name}"  ANG  0  MAXSTASPC 0.5  LENGTHOFFI 0  LENGTHOFFJ 0  RIGIDZONE 1  CARDINALPT 8    MESH "POINTSANDLINES"')
                if self.inelastic_analysis==True:
                    self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  HINGE "{_geometry_name}.{_line}.L"  RDISTANCE 0')
                    self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  HINGE "{_geometry_name}.{_line}.R"  RDISTANCE 1')
            elif 'COLUMN' in _element_type:
                self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  SECTION "{_geometry_name}"  ANG  0  MINNUMSTA 3  LENGTHOFFI 0  LENGTHOFFJ 0  RIGIDZONE 1  MESH "POINTSANDLINES"')
                if self.inelastic_analysis==True:
                    self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  HINGE "{_geometry_name}"  RDISTANCE 0')
                    self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  HINGE "{_geometry_name}"  RDISTANCE 1')
            elif _element_type == 'WALL':
                self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  SECTION "{_geometry_name}"  ANG  0  MINNUMSTA 3  LENGTHOFFI 0  LENGTHOFFJ 0  RIGIDZONE 1  MESH "POINTSANDLINES"    PIER "P1"')
            elif _element_type == 'RIGID':
                self.etabs_file_text.append(f'  LINEASSIGN  "{_line}"  "STORY{_storey}"  SECTION "{_geometry_name}"  ANG  0  MAXSTASPC 0.5  LENGTHOFFI 0  LENGTHOFFJ 0  RIGIDZONE 1  CARDINALPT 8    MESH "POINTSANDLINES"')
        self.etabs_file_text.append('')

    def _etabs_write_static_load_cases(self):
        self.etabs_file_text.append('$ STATIC LOADS')
        self.etabs_file_text.append('  LOADCASE "G"  TYPE  "DEAD"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "Q"  TYPE  "LIVE"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "EXSTAT"  TYPE  "QUAKE"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "EYSTAT"  TYPE  "QUAKE"  SELFWEIGHT  0')
        self.etabs_file_text.append('  LOADCASE "EPUSH"  TYPE  "QUAKE"  SELFWEIGHT  0')
        self.etabs_file_text.append('')

    def _etabs_write_element_loads(self):
        self.etabs_file_text.append('$ LINE OBJECT LOADS')
        ds = self.model.input_data['beam_loads']
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
        ds = self.model.input_data['node_loads'] # .query('Storey>=1' )
        for index, row in ds.iterrows():
            _storey = row['Storey']
            _point_etabs = row['Point_Etabs']
            _G = row['G']
            _Q = row['Q']
            self.etabs_file_text.append(f'  POINTLOAD  "{_point_etabs:.0f}"  "STORY{_storey:.0f}"  TYPE "FORCE"  LC "G"    FZ -{_G:.2f}')
            self.etabs_file_text.append(f'  POINTLOAD  "{_point_etabs:.0f}"  "STORY{_storey:.0f}"  TYPE "FORCE"  LC "Q"    FZ -{_Q:.2f}')

        for i in range(self.model.stories_total):
            self.etabs_file_text.append(f'  POINTLOAD  "1"  "STORY{i+1}"  TYPE "FORCE"  LC "EPUSH"  FX {self.model.seismic_static_forces["EPUSHmod"][i]:.3f}')
            self.etabs_file_text.append(f'  POINTLOAD  "1"  "STORY{i+1}"  TYPE "FORCE"  LC "EXSTAT"  FX {self.model.seismic_static_forces["EXSTAT"][i]:.3f}')

        self.etabs_file_text.append('')

    def _etabs_write_spectrum_function(self):
        self.etabs_file_text.append('$ FUNCTIONS')
        self.etabs_file_text.append('  FUNCTION "EAKSPEC"  FUNCTYPE "SPECTRUM"  DAMPRATIO 0.05  SPECTYPE "USER"  ')
        _eak_ground = self.model.misc['EAK_ground']
        _eak_α = self.model.misc['EAK_α']
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

    def _etabs_write_hinge_properties(self):
        self.etabs_file_text.append('$ FRAME HINGE PROPERTIES')
        _dict_beams = self.model.input_data['BeamReinforcement'].to_dict('index')
        for key, value in _dict_beams.items():
            _reinforcementID = key
            self.etabs_file_text.append(self._make_hinge_text_beams(f'{_reinforcementID}'))
        self.etabs_file_text.append('')

        _dict_columns = self.model.input_data['ColumnReinforcement'].to_dict('index')
        for key, value in _dict_columns.items():
            _reinforcementID = key
            self.etabs_file_text.append(self._make_hinge_text_columns(f'{_reinforcementID}'))
        self.etabs_file_text.append('')


    def _make_hinge_text_beams(self, hingeID):
        txt = []

        self.model.reinforcement_beams_kanepe[f'{hingeID}.L.neg'].calculate()
        self.model.reinforcement_beams_kanepe[f'{hingeID}.L.pos'].calculate()
        self.model.reinforcement_beams_kanepe[f'{hingeID}.R.neg'].calculate()
        self.model.reinforcement_beams_kanepe[f'{hingeID}.R.pos'].calculate()


        txt.append(f'  HINGE "{hingeID}.L"  {self.model.reinforcement_beams_kanepe[f"{hingeID}.L.neg"].get_etabs9_7_2_M3(negative=True)}')
        txt.append(f'  HINGE "{hingeID}.L"  {self.model.reinforcement_beams_kanepe[f"{hingeID}.L.pos"].get_etabs9_7_2_M3(negative=False)}')
        txt.append(f'  HINGE "{hingeID}.L"  TYPE "M3"  MOMENTSFP 1  ROTATIONSFP 1')
        txt.append(f'  HINGE "{hingeID}.L"  TYPE "M3"  MOMENTSFN 1  ROTATIONSFN 1')
        txt.append(f'  HINGE "{hingeID}.L"  TYPE "M3"  -IO -2  -LS -4  -CP -6')
        txt.append(f'  HINGE "{hingeID}.L"  TYPE "M3"  IO 2  LS 4  CP 6')

        txt.append(f'  HINGE "{hingeID}.R"  {self.model.reinforcement_beams_kanepe[f"{hingeID}.R.neg"].get_etabs9_7_2_M3(negative=True)}')
        txt.append(f'  HINGE "{hingeID}.R"  {self.model.reinforcement_beams_kanepe[f"{hingeID}.R.pos"].get_etabs9_7_2_M3(negative=False)}')
        txt.append(f'  HINGE "{hingeID}.R"  TYPE "M3"  MOMENTSFP 1  ROTATIONSFP 1')
        txt.append(f'  HINGE "{hingeID}.R"  TYPE "M3"  MOMENTSFN 1  ROTATIONSFN 1')
        txt.append(f'  HINGE "{hingeID}.R"  TYPE "M3"  -IO -2  -LS -4  -CP -6')
        txt.append(f'  HINGE "{hingeID}.R"  TYPE "M3"  IO 2  LS 4  CP 6')


        return '\n'.join(txt)

    def _make_hinge_text_columns(self, hingeID):
        txt = []

        self.model.reinforcement_columns_kanepe[f'{hingeID}'].calculate()

        txt.append(f'  HINGE "{hingeID}"  {self.model.reinforcement_columns_kanepe[f"{hingeID}"].get_etabs9_7_2_M3(negative=True)}')
        txt.append(f'  HINGE "{hingeID}"  {self.model.reinforcement_columns_kanepe[f"{hingeID}"].get_etabs9_7_2_M3(negative=False)}')
        txt.append(f'  HINGE "{hingeID}"  TYPE "M3"  MOMENTSFP 1  ROTATIONSFP 1')
        txt.append(f'  HINGE "{hingeID}"  TYPE "M3"  MOMENTSFN 1  ROTATIONSFN 1')
        txt.append(f'  HINGE "{hingeID}"  TYPE "M3"  -IO -2  -LS -4  -CP -6')
        txt.append(f'  HINGE "{hingeID}"  TYPE "M3"  IO 2  LS 4  CP 6')


        return '\n'.join(txt)


    def _etabs_write_spectrum_cases(self):
        self.etabs_file_text.append('$ RESPONSE SPECTRUM CASES')
        self.etabs_file_text.append('  RSCASE "EX"  DAMP 0.05  DIRCOMBO "SRSS"  ANG 0')
        self.etabs_file_text.append('  RSCASE "EX"  FUNC1 "EAKSPEC"  SF1 1')
        self.etabs_file_text.append('  RSCASE "EX"  MODECOMBO "CQC"')

        self.etabs_file_text.append('')

    def _etabs_write_pushover_cases(self):
        self.etabs_file_text.append('$ RESPONSE SPECTRUM CASES')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  CONTROL "FORCE"  STORY "STORY4"  POINT "1"  DOF "UX"  ')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  GEONONLIN "NONE"  ')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  MINSTEPS 1  MAXNULLSTEPS 50  MAXTOTALSTEPS 200  MAXITER 10')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  ITERTOL 0.0001  EVENTTOL 0.01')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  LOADTYPE "STATIC"  LOAD "G"  SCALEFACTOR 1')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  LOADTYPE "STATIC"  LOAD "Q"  SCALEFACTOR 0.3')
        self.etabs_file_text.append('  STATICNLCASE "PUSHGRAV"  ACTIVEGROUP "ALL"  ')
        self.etabs_file_text.append('  STATICNLCASE "PUSHOVER"  CONTROL "CONJUGATEDISP"  TARGETDISP 0.54  STORY "STORY4"  POINT "1"  DOF "UX" ')
        self.etabs_file_text.append('  STATICNLCASE "PUSHOVER"  STARTFROM "PUSHGRAV"  GEONONLIN "NONE" ')
        self.etabs_file_text.append('  STATICNLCASE "PUSHOVER"  MINSTEPS 100  MAXNULLSTEPS 500  MAXTOTALSTEPS 2000  MAXITER 50')
        self.etabs_file_text.append('  STATICNLCASE "PUSHOVER"  ITERTOL 0.0001  EVENTTOL 0.001')
        self.etabs_file_text.append('  STATICNLCASE "PUSHOVER"  LOADTYPE "STATIC"  LOAD "EPUSH"  SCALEFACTOR 1')
        self.etabs_file_text.append('  STATICNLCASE "PUSHOVER"  ACTIVEGROUP "ALL"  ')



        self.etabs_file_text.append('')





