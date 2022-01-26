#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  chemical_shifts_custom_model.py
#  
#  Copyright 2019  
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
letters={'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K', 'ASN': 'N', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ALA': 'A', 'HIS': 'H', 'GLY': 'G', 'ILE': 'I', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}


shifts={ 'A': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'C': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'E': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'D': ['HA', 'CA', 'CB', 'C', 'HB2', 'N', 'H'],
		 'G': ['HA3', 'HA2', 'CA', 'C', 'N', 'H'],
		 'F': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'I': ['HA', 'CA', 'CB', 'C', 'HD11', 'HB', 'N', 'H'],
		 'H': ['HA', 'CA', 'CB', 'C', 'N', 'H', 'HB2', 'HD2'],
		 'K': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'M': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'L': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N', 'HD11', 'HD21'],
		 'N': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'Q': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'P': ['HA', 'CA', 'CB', 'C', 'HG2', 'HB2', 'CD', 'HD2'],
		 'S': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'R': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'T': ['HA', 'CA', 'CB', 'C', 'HG21', 'HB', 'N', 'H'],
		 'W': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N'],
		 'V': ['HA', 'CA', 'CB', 'C', 'HG11', 'HG22', 'N', 'H'],
		 'Y': ['HA', 'CA', 'CB', 'C', 'HB2', 'H', 'N']
 }

