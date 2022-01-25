import pandas as pd
from . import RectangularBeamProperties as rect_props


def os2d_general():
    _str = '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# U N I T S\n'
    _str += '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# Length : m\n'
    _str += '# Force  : kN\n'
    _str += '# Moment : kNm\n'
    _str += '# Stress : kPa\n'
    _str += '# Mass   : ton\n'
    _str += '\n'
    _str += '# Model domain 3DOF\n'
    _str += '\n'
    _str += 'model BasicBuilder -ndm 2 -ndf 3\n'
    return _str + '\n'


def os2d_nodes(_df_nodes):
    _str = '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# N O D E S\n'
    _str += '# ---------------------------------------------------------------------------------------------------\n'
    _str += '#        nodeID            X            Y\n'
    for row in _df_nodes.itertuples():
        _str += f'node {row.Node:10} {row.X:12.3f} {row.Z:12.3f}\n'
    return _str + '\n'


# Στηρίξεις
def os2d_node_restraints(_df_node_restraints):
    _str = '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# R E S T R A I N T S\n'
    _str += '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# fix    nodeID   dxFixity   dyFixity    rzFixity\n'
    for row in _df_node_restraints.itertuples():
        _str += f'fix {row.Node:10} {row.U1:10} {row.U3:10}  {row.R2:10} \n'
    return _str + '\n'


# Διαφράγματα
def os2d_diaphragms(_df_node_constraints):
    _str = '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# C O N S T R A I N T S\n'
    _str += '# ---------------------------------------------------------------------------------------------------\n'
    _str += '#          master     slave      dof\n'
    df_diaphragms = _df_node_constraints[_df_node_constraints.TYPE == 'Diaphragm']
    # print(df_diaphragms)
    for row in df_diaphragms.itertuples():
        nodes = row.NODES.split(',')
        #     print(f'masternode for diaph {row.ID} is {nodes[0]}')
        for node in nodes:
            if node != nodes[0]:
                _str += f'equalDOF {nodes[0]:>8}  {node:>8}        1\n'
    return _str + '\n'


# Μάζες στους κόμβους
def os2d_masses_nodal(_df_masses_nodal):
    _str = '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# M A S S E S\n'
    _str += '# ---------------------------------------------------------------------------------------------------\n'
    _str += '#Mass Definition : mass $NodeTag $(ndf nodal mass values corresponding to each DOF)\n'
    for row in _df_masses_nodal.itertuples():
        _str += f'mass {row.NODE:>10} {row.UX:>10.3f} {row.UY:>10.3f}{row.RZ:>10.3f}\n'
    return _str + '\n'


# Connectivity - Frame
def os2d_frame_connectivity(_df_frame_connectivity, _df_section_rect_elastic, _df_materials_general):
    _str = '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# E L A S T I C   B E A M - C O L U M N   E L E M E N T S\n'
    _str += '# ---------------------------------------------------------------------------------------------------\n'
    _str += '# Elastic Beam Column Definition\n'
    _str += '# element elasticBeamColumn $eleTag $iNode $jNode $A $E $Iz $transfTag <-mass $MassPerUnitLength>\n'
    for row in _df_frame_connectivity.itertuples():
        _sect_geom = row.SECT_GEOM
        _sect_id = row.SECTION_ID
        _sect_props = get_section_properties(_sect_geom, _sect_id, _df_section_rect_elastic, _df_materials_general)
        _str += f'element elasticBeamColumn{row.FRAME:>7} {row.NODEI:>7} {row.NODEJ:>7}' \
                f'{_sect_props[2]:>12.6f} {_sect_props[0]:>14.1f} {_sect_props[3]:>15.10f}' \
                f'    1   -mass    0.000\n'
    return _str + '\n'


def get_section_properties(sect_geom, sect_id, _df_section_rect_elastic, _df_materials_general):
    if sect_geom == 'RECT':
        _df = _df_section_rect_elastic.set_index("RECT_SECTION_ID")
        _row = _df.loc[sect_id]
        _mat = _row.MATERIAL
        _b = _row.b
        _h = _row.h
        _mod_area = _row.modArea
        _mod_shear = _row.modShear
        _mod_moment = _row.modMoment
        _mod_torsional = _row.modTorsional
        _rect_props = rect_props.RectangularBeamProperties(_b, _h)

        _df_mat = _df_materials_general.set_index("MATERIAL_ID")
        _mat_E = _df_mat.at[_mat, 'E']
        _mat_poisson = _df_mat.at[_mat, 'POISSON']
        _mat_G = _mat_E / (2 * (1.0 + _mat_poisson))

        _tup = _mat_E, \
               _mat_G, \
               _rect_props.area() * _mod_area, \
               _rect_props.moment_of_inertia_xx() * _mod_moment, \
               _rect_props.shear_area_2() * _mod_shear
        # returns a tuple with: E, G, A, Iz, Avy
        # A, Iz, Avy are multiplied with mod factors
        return _tup
