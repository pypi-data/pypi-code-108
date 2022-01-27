# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""Parser for ASAM ATF using ply"""

from ply import yacc
from . lexer import (tokens, COMMA, SEMICOLON)
from . lexer import lexer as atflex


def p_atffile(p):
    'atffile : ATF_FILE VERSION SEMICOLON texp ATF_END SEMICOLON'
    p[0] = ((p[1], p[2]), p[4])


# 'DT_BLOB'
def p_datatype_blob(p):
    """
    datatype : DT_BLOB
             | DT_BOOLEAN
             | DT_BYTE
             | DT_BYTESTR
             | DT_COMPLEX
             | DT_DATE
             | DT_DCOMPLEX
             | DT_DOUBLE
             | DT_ENUM
             | DT_EXTERNALREFERENCE
             | DT_LONG
             | DT_LONGLONG
             | DT_FLOAT
             | DT_SHORT
             | DT_STRING
             | DT_UNKNOWN
             | DS_STRING
    """
    p[0] = p[1]


def p_dexp_datatype(p):
    'dexp : DATATYPE datatype'
    p[0] = p[2]


# 'FILES'
def p_files(p):
    'files : FILES filedefs ENDFILES'
    p[0] = {'files': dict(p[2])}


def p_filedef(p):
    'filedefs : COMPONENT IDENTIFIER ASSIGN STRING SEMICOLON'
    p[0] = [(p[2], p[4])]


def p_filedefs_combine(p):
    'filedefs : filedefs filedefs'
    p[0] = p[1] + p[2]


def p_include(p):
    """
    include : INCLUDE IDENTIFIER
            | include COMMA IDENTIFIER
    """
    if p[2] == COMMA:
        p[1].append(p[3])
    else:
        p[0] = [p[2]]


# 'APPLELEM'
def p_applelem(p):
    'applelem : APPLELEM IDENTIFIER COMMA BASETYPE IDENTIFIER applattr ENDAPPLELEM'
    p[0] = {'applelem': {p[2]: (p[2], p[5], p[6])}}


def p_cardinality(p):
    """
    cardinality : INTEGER COMMA INTEGER
                | INTEGER COMMA MANY
    """
    p[0] = [p[1], p[3]]


def p_idattr(p):
    """
    idattr : BASETYPE
           | BASEATTR
           | REF_TO
           | REF_TYPE
    """
    p[0] = p[1]


def p_attr(p):
    """
    attr : CARDINALITY cardinality
         | DATATYPE datatype
         | idattr IDENTIFIER
    """
    p[0] = {p[1]: p[2]}


def p_attrs(p):
    """
    attrs : attr
          | attrs COMMA attr
    """
    if len(p) > 2:
        p[1].update(p[3])
    p[0] = p[1]


# 'APPLATTR'
def p_applattr_base(p):
    'applattr : APPLATTR IDENTIFIER COMMA attrs'
    p[4][p[1]] = p[2]
    p[0] = {p[2]: p[4]}


# 'APPLATTR'
def p_applattr_combine(p):
    """
    applattr : applattr applattr
             | applattr SEMICOLON
    """
    if p[2] == SEMICOLON:
        p[0] = p[1]
    else:
        p[0] = dict(p[1], **p[2])


# 'INSTELEM'
def p_instelem(p):
    'instelem : INSTELEM IDENTIFIER attribute_values ENDINSTELEM'
    attribute_dict = dict(p[3])
    p[0] = {'instelem': {p[2]: {attribute_dict['Id']: attribute_dict}}}


def p_attribute_values_single(p):
    'attribute_values : IDENTIFIER ASSIGN data_attribute_values'
    p[0] = [(p[1], p[3])]


def p_attribute_values_combine(p):
    'attribute_values : attribute_values attribute_values'
    p[1].extend(p[2])
    p[0] = p[1]


def p_data_attribute_values_dexp(p):
    'data_attribute_values : dexp COMMA dval'
    p[0] = (p[1], p[3])


def p_data_attribute_values(p):
    'data_attribute_values : dval'
    p[0] = p[1]


def p_dval_prims(p):
    """
    dval : prim SEMICOLON
         | prims SEMICOLON
    """
    p[0] = p[1]


def p_val_comp_num_type(p):
    """
    comp_num_type : DT_BOOLEAN
                  | DT_BYTE
                  | DT_SHORT
                  | DT_LONG
                  | DT_LONGLONG
                  | DT_FLOAT
                  | IEEEFLOAT4
                  | IEEEFLOAT8
    """
    p[0] = p[1]


def p_val_comp_str_type(p):
    """
    comp_str_type : DT_STRING
                  | DT_BYTESTR
    """
    p[0] = p[1]


def p_val_comp_blob(p):
    'comp_blob : DT_BLOB INTEGER COMMA DESCRIPTION STRING'
    p[0] = {'TYPE': p[1], 'LENGTH': p[2], p[4]: p[5]}


def p_val_comp_num(p):
    'comp_num : comp_num_type INTEGER COMMA \
                INIOFFSET INTEGER COMMA \
                BLOCKSIZE INTEGER COMMA \
                VALPERBLOCK INTEGER COMMA \
                VALOFFSETS ints'
    p[0] = {
        'TYPE': p[1],
        'LENGTH': p[2],
        p[4]: p[5],
        p[7]: p[8],
        p[10]: p[11],
        p[13]: p[14]}


def p_val_comp_str(p):
    'comp_str : comp_str_type INTEGER COMMA INIOFFSET INTEGER'
    p[0] = {'TYPE': p[1], 'LENGTH': p[2], p[4]: p[5]}


def p_val_comp(p):
    """
    comp : comp_blob
         | comp_num
         | comp_str
    """
    p[0] = p[1]


def p_dval_component(p):
    'dval : COMPONENT IDENTIFIER COMMA comp ENDCOMPONENT SEMICOLON'
    p[4][p[1]] = p[2]
    p[0] = p[4]


def p_dval_undefined(p):
    'dval : UNDEFINED SEMICOLON'
    p[0] = None


def p_ints(p):
    """
    ints : INTEGER
         | ints COMMA INTEGER
    """
    if len(p) > 2:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]


def p_prim(p):
    """
    prim : BOOL
         | FLOAT
         | INTEGER
         | STRING
    """
    p[0] = p[1]


def p_prims1(p):
    'prims : prim COMMA prim'
    p[0] = [p[1], p[3]]


def p_prims2(p):
    'prims : prims COMMA prim'
    p[1].append(p[3])
    p[0] = p[1]


def dictadd(dicta, dictb):
    """
    Add two dictionaries,
    assuming that the second dictionary contains only only one element.
    """
    for key in dictb:
        if key in dicta:
            nextlevel = dicta[key]
            if isinstance(nextlevel, dict):
                dictadd(nextlevel, dictb[key])
        else:
            dicta.update(dictb)


def p_texp_combine(p):
    'texp : texp tsexp SEMICOLON'
    dictadd(p[1], p[2])
    p[0] = p[1]


def p_texp_tsexp(p):
    'texp : tsexp SEMICOLON'
    p[0] = p[1]


def p_tsexp_files(p):
    """
    tsexp : files
          | include
          | applelem
          | instelem
    """
    p[0] = p[1]


def p_error(p):
    """Error rule for syntax errors"""
    print('Syntax error at input! {0}'.format(str(p)))


_stringparser = yacc.yacc(
    debug=0, optimize=1, write_tables=0)


def fileparser(filename):
    with open(filename) as f:
        return stringparser(f.read())


def stringparser(string):
    return _stringparser.parse(string, lexer=atflex)
