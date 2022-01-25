import pandas as pd
import string

alphabet = string.ascii_uppercase


# Κόμβοι
def sap2d_nodes(_df_nodes):
    _str = 'TABLE:  "JOINT COORDINATES"\n'
    for row in _df_nodes.itertuples():
        _str += f'Joint={row.Node}   CoordSys=GLOBAL   CoordType=Cartesian   ' \
                f'XorR={row.X:.3f}   Y=0   Z={row.Z:.3f}   SpecialJt=No\n'
    return _str + '\n'


# Gridlines
def sap2d_gridlines(_df_nodes):
    xs = _df_nodes.X.unique()
    zs = _df_nodes.Z.unique()

    _str = 'TABLE:  "GRID LINES"\n'

    i = 0
    for x in xs:
        _str += f'   CoordSys=GLOBAL   AxisDir=X   GridID={alphabet[i]}   XRYZCoord={x}   LineType=Primary   ' \
                f'LineColor=Gray8Dark   Visible=Yes\n'
        i += 1

    _str += '   CoordSys=GLOBAL   AxisDir=Y   GridID=1   XRYZCoord=0   LineType=Primary   LineColor=Gray8Dark   ' \
            'Visible=Yes\n'

    i = 0
    for z in zs:
        _str += f'   CoordSys=GLOBAL   AxisDir=Z   GridID=Z{i}   XRYZCoord={z}   LineType=Primary   ' \
                f'LineColor=Gray8Dark   Visible=Yes\n'
        i += 1

    return _str + '\n'


# Στηρίξεις
def sap2d_node_restraints(_df_node_restraints):
    _str = 'TABLE:  "JOINT RESTRAINT ASSIGNMENTS"\n'
    for row in _df_node_restraints.itertuples():
        _str += f'   Joint={row.Node}   ' + \
                f'U1={row.U1}   U2={row.U2}   U3={row.U3}   ' \
                f'R1={row.R1}   R2={row.R2}   R3={row.R3}\n'.replace('=1', '=Yes').replace('=0', '=No')
    return _str + '\n'


# Διαφράγματα
def sap2d_diaphragms(_df_node_constraints):
    _str = 'TABLE:  "CONSTRAINT DEFINITIONS - DIAPHRAGM"\n'
    for row in _df_node_constraints.itertuples():
        _str += f'   Name=DIAPH{row.ID}   CoordSys=GLOBAL   Axis=Z   MultiLevel=No\n'
    return _str + '\n'


def sap2d_diaphragms_assignments(_df_node_constraints_assignments):
    _str = 'TABLE:  "JOINT CONSTRAINT ASSIGNMENTS"\n'
    for row in _df_node_constraints_assignments.itertuples():
        nodes = row.NODES.split(',')
        for node in nodes:
            _str += f'   Joint={node}   Constraint=DIAPH{row.ID}\n'
    return _str + '\n'


# Connectivity - Frame
def sap2d_frame_connectivity(_df_frame_connectivity):
    _str = 'TABLE:  "CONNECTIVITY - FRAME"\n'
    for row in _df_frame_connectivity.itertuples():
        _str += f'   Frame={row.FRAME}   JointI={row.NODEI}   JointJ={row.NODEJ}   IsCurved=No\n'
    return _str + '\n'


# Materials - General
def sap2d_materials_general(_df_materials_general):
    _str = 'TABLE:  "MATERIAL PROPERTIES 01 - GENERAL"\n'
    for row in _df_materials_general.itertuples():
        _str += f'   Material={row.MATERIAL_ID}   Type={row.TYPE}   SymType=Isotropic   TempDepend=No\n'
    return _str + '\n'


# Materials - Basic Mechanical Properties
def sap2d_materials_basic_mechanical(_df_materials_general):
    _str = 'TABLE:  "MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES"\n'
    for row in _df_materials_general.itertuples():
        _str += f'   Material={row.MATERIAL_ID}   UnitWeight=0   UnitMass=0   E1={row.E}   U12={row.POISSON}   A1=0\n'
    return _str + '\n'


def get_section_name(sect_geom, sect_id, _df_section_rect_elastic):
    if sect_geom == 'RECT':
        df = _df_section_rect_elastic.set_index("RECT_SECTION_ID")
        rect_name = df.at[sect_id, 'SECTION_NAME']
        return rect_name


# FRAME SECTION ASSIGNMENTS
def sap2d_frame_section_assignments(_df_frame_connectivity, _df_section_rect_elastic):
    _str = 'TABLE:  "FRAME SECTION ASSIGNMENTS"\n'
    for row in _df_frame_connectivity.itertuples():
        sect_id = get_section_name(row.SECT_GEOM, row.SECTION_ID, _df_section_rect_elastic)
        _str += f'   Frame={row.FRAME}   AutoSelect=N.A.   AnalSect={sect_id}   MatProp=Default\n'
    return _str + '\n'


# "FRAME SECTION PROPERTIES 01 - GENERAL"
def sap2d_frame_section_properties_general(_df_section_rect_elastic):
    _str = 'TABLE:  "FRAME SECTION PROPERTIES 01 - GENERAL"\n'
    for row in _df_section_rect_elastic.itertuples():
        _str += f'   SectionName={row.SECTION_NAME}   Material={row.MATERIAL}   Shape=Rectangular   ' \
                f't3={row.h:.3f}   t2={row.b:.3f}   ' \
                f'AMod={row.modArea:.3f}   A2Mod={row.modShear:.3f}   A3Mod={row.modShear:.3f}   ' \
                f'JMod={row.modTorsional:.3f}   I2Mod={row.modMoment:.3f}   I3Mod={row.modMoment:.3f}   ' \
                f'MMod=0   WMod=0\n'
    return _str + '\n'


# Load Patterns
def sap2d_load_patterns(_df_load_patterns):
    _str = 'TABLE:  "LOAD PATTERN DEFINITIONS"\n'
    for row in _df_load_patterns.itertuples():
        _str += f'   LoadPat={row.NAME}   DesignType={row.DesignType}   SelfWtMult=0\n'
    return _str + '\n'


# Load Cases
def sap2d_load_cases(_df_load_patterns):
    _str = 'TABLE:  "LOAD CASE DEFINITIONS"\n'
    _str += '   Case=MODAL   Type=LinModal   InitialCond=Zero   DesTypeOpt="Prog Det"   DesignType=OTHER   ' \
            'AutoType=None   RunCase=Yes\n'
    for row in _df_load_patterns.itertuples():
        _str += f'   Case={row.NAME}   Type=LinStatic   InitialCond=Zero   DesTypeOpt="Prog Det"   ' \
                f'DesignType={row.DesignType}   AutoType=None   RunCase=Yes\n'
    return _str + '\n'


# Load Cases - Static - Assignments
def sap2d_load_cases_static_assignments(_df_load_patterns):
    _str = 'TABLE:  "CASE - STATIC 1 - LOAD ASSIGNMENTS"\n'
    for row in _df_load_patterns.itertuples():
        _str += f'   Case={row.NAME}   LoadType="Load pattern"   LoadName={row.NAME}   LoadSF=1\n'
    return _str + '\n'


# Masses
def sap2d_masses():
    _str = 'TABLE:  "MASSES 1 - MASS SOURCE"\n'
    _str += '   MassFrom=Elements\n'
    return _str + '\n'


def sap2d_masses_nodal(_df_masses_nodal):
    _str = 'TABLE:  "JOINT ADDED MASS ASSIGNMENTS"\n'
    for row in _df_masses_nodal.itertuples():
        _str += f'   Joint={row.NODE}   CoordSys=Global   ' \
                f'Mass1={row.UX:.3f}   Mass2={row.UY:.3f}   Mass3={row.UZ:.3f}   ' \
                f'MMI1={row.RX:.3f}   MMI2={row.RY:.3f}   MMI3={row.RZ:.3f}\n'
    return _str + '\n'


# Loads - Nodal
def sap2d_loads_nodal(_df_loads_nodal):
    _str = 'TABLE:  "JOINT LOADS - FORCE"\n'
    for row in _df_loads_nodal.itertuples():
        _str += f'   Joint={row.NODE}   LoadPat={row.LOAD_PATTERN}   CoordSys=Global   ' \
                f'F1={row.FX:.3f}   F2={row.FY:.3f}   F3={row.FZ:.3f}   ' \
                f'M1={row.MX:.3f}   M2={row.MY:.3f}   M3={row.MZ:.3f}\n'
    return _str + '\n'


# Loads - Distributed
def sap2d_loads_dist(_df_loads_dist_gravity):
    _str = 'TABLE:  "FRAME LOADS - DISTRIBUTED"\n'
    for row in _df_loads_dist_gravity.itertuples():
        _str += f'   Frame={row.FRAME}   LoadPat={row.LOAD_PATTERN}   CoordSys=GLOBAL   Type=Force   Dir=Gravity   ' \
                f'DistType=RelDist      RelDistA=0   RelDistB=1   ' \
                f'FOverLA={row.VALUE:.3f}   FOverLB={row.VALUE:.3f} \n'
    return _str + '\n'
