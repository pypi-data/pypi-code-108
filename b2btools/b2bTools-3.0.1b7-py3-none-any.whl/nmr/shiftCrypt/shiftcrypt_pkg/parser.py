#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  parser.py
#
#  Copyright 2017  <@gmail.com>
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
from b2bTools.general.Io import B2bIo

aa3To1Code={'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K', 'ASN': 'N', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ALA': 'A', 'HIS': 'H', 'GLY': 'G', 'ILE': 'I', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}

ss_3class={'H':'H','G':'H','I':'H','E':'E','B':'E','S':'C','T':'C','C':'C','-':'-','b':'-','R':'-','D':'-','_':'-','A':'-','L':'-'}


class protein_class():
	def __init__(self,chainCode):
		self.chainCode = chainCode
		self.seq=''
		self.resi=[]
		self.ss=''
		self.rci=[]
		self.resnum=[]

class residue_class():
	def __init__(self):
		self.resname=None
		self.atom={}
		self.ss=None
		self.rci=None

def parse_official(fileName,is_star=False,original_numbering=True):

	b2bIo = B2bIo()

	proteins = []

	if type(is_star) == type(""):
		is_star = eval(is_star)

	if is_star:
		allSeqInfo = b2bIo.readNmrStarSequenceShifts(fileName,original_numbering=original_numbering)
	else:
		allSeqInfo = b2bIo.readNefFileSequenceShifts(fileName)

	chainCodes = allSeqInfo.keys()

	for chainCode in chainCodes:

		prot=protein_class(chainCode)

		seqInfo = allSeqInfo[chainCode]

		for (seqElement,shiftInfo) in seqInfo:

			if seqElement['residue_name'] in aa3To1Code:
				resitype=aa3To1Code[seqElement['residue_name']]
			else:
				resitype='X'

			prot.seq += resitype

			resi = residue_class()
			resi.resname = resitype
			prot.resnum += [int(seqElement['sequence_code'])]
			prot.resi += [resi]

			for shiftValue in shiftInfo:
				atom_name=shiftValue['atom_name']
				shift=shiftValue['value']

				resi.atom[atom_name]=shift

		proteins.append(prot)

	return proteins

if __name__ == '__main__':
	a=parse_official('../../test/input/NEF_example.nef')
	print(a)

