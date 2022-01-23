"""
SatNOGS Decoder subpackage initialization
"""
from __future__ import absolute_import, division, print_function

import functools
import re

from .aausat4 import Aausat4
from .acrux1 import Acrux1
from .alsat1n import Alsat1n
from .amicalsat import Amicalsat
from .armadillo import Armadillo
from .ascii85test import Ascii85test
from .asuphoenix import Asuphoenix
from .ax25frames import Ax25frames
from .ax25monitor import Ax25monitor
from .bisonsat import Bisonsat
from .bobcat1 import Bobcat1
from .bugsat1 import Bugsat1
from .cape1 import Cape1
from .cas4 import Cas4
from .cas9 import Cas9
from .chomptt import Chomptt
from .csim import Csim
from .cubebel1 import Cubebel1
from .cubesatsim import Cubesatsim
from .cute import Cute
from .delfin3xt import Delfin3xt
from .delfipq import Delfipq
from .dhabisat import Dhabisat
from .diy1 import Diy1
from .duchifat3 import Duchifat3
from .elfin import Elfin
from .entrysat import Entrysat
from .equisat import Equisat
from .eshail2 import Eshail2
from .fox import Fox
from .grbalpha import Grbalpha
from .grizu263a import Grizu263a
from .irazu import Irazu
from .irvine import Irvine
from .iss import Iss
from .ksu import Ksu
from .ledsat import Ledsat
from .lightsail2 import Lightsail2
from .meznsat import Meznsat
from .minxss import Minxss
from .mirsat1 import Mirsat1
from .mitee1 import Mitee1
from .mxl import Mxl
from .mysat import Mysat
from .netsat import Netsat
from .neutron1 import Neutron1
from .opssat1 import Opssat1
from .origamisat1 import Origamisat1
from .painani import Painani
from .polyitan1 import Polyitan1
from .pwsat2 import Pwsat2
from .qarman import Qarman
from .qbee import Qbee
from .qubik import Qubik
from .quetzal1 import Quetzal1
from .ramsat import Ramsat
from .salsat import Salsat
from .siriussat import Siriussat
from .skcube import Skcube
from .spoc import Spoc
from .strand import Strand
from .us6 import Us6
from .uwe4 import Uwe4
from .vzlusat2 import Vzlusat2

__all__ = [
    'Aausat4',
    'Acrux1',
    'Alsat1n',
    'Amicalsat',
    'Armadillo',
    'Ascii85test',
    'Asuphoenix',
    'Ax25frames',
    'Ax25monitor',
    'Bisonsat',
    'Bobcat1',
    'Bugsat1',
    'Cape1',
    'Cas4',
    'Cas9',
    'Chomptt',
    'Cubebel1',
    'Cubesatsim',
    'Cute',
    'Csim',
    'Delfin3xt',
    'Delfipq',
    'Dhabisat',
    'Diy1',
    'Duchifat3',
    'Elfin',
    'Entrysat',
    'Eshail2',
    'Equisat',
    'Fox',
    'Grbalpha',
    'Grizu263a',
    'Irazu',
    'Irvine',
    'Iss',
    'Ksu',
    'Ledsat',
    'Lightsail2',
    'Meznsat',
    'Minxss',
    'Mitee1',
    'Mirsat1',
    'Mxl',
    'Mysat',
    'Netsat',
    'Neutron1',
    'Opssat1',
    'Origamisat1',
    'Painani',
    'Polyitan1',
    'Pwsat2',
    'Qarman',
    'Qbee',
    'Qubik',
    'Quetzal1',
    'Ramsat',
    'Salsat',
    'Siriussat',
    'Skcube',
    'Spoc',
    'Strand',
    'Us6',
    'Uwe4',
    'Vzlusat2',
]

FIELD_REGEX = re.compile(
    r':field (?P<field>[\*\w]+): (?P<attribute>.*?)'
    r'(?:(?=:field)|\Z|\n)', re.S)


def get_fields(struct, empty=False):
    """
    Get fields defined in docstring
    """
    fields = {}

    try:
        doc_fields = FIELD_REGEX.findall(struct.__doc__)
    except TypeError:
        return fields

    for key, value in doc_fields:
        try:
            fields[key] = functools.reduce(getattr, value.split('.'), struct)
        except AttributeError:
            if empty:
                fields[key] = None

    return fields
