#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  shiftcrypt.py
#
#  Copyright 2019  <orlando.gabriele89@gmail.com>
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
import warnings
warnings.filterwarnings("ignore")
import torch
import argparse, subprocess, os, errno
from b2bTools.singleSeq.PSPer.source.utils import leggifasta
from b2bTools.singleSeq.PSPer.phase_transition_hmm import phase_hmm

def run_psper():

	pa = argparse.ArgumentParser()

	pa.add_argument('-i', '--infile',
						help='the input fasta file',
						required=True,
						)
	pa.add_argument('-viterbi', '--viterbi',
						action='store_true',
						help='provides the viterbi output',)
	pa.add_argument('-o', '--outfile',
						help='output file',
						default=None)
	args = pa.parse_args()
	if args.infile:
		prot=leggifasta(args.infile)
		try:
			prot=leggifasta(args.infile)
		except:
			print ('error in the parsing of the file. Please double check the fasta format. If everyhting is correct, please report the bug to orlando.gabriele89@gmail.com')
			return

		model=phase_hmm()
		model.fit()
		try:
			print ('running prediction')
			out=model.predict_proba(prot)
			if args.viterbi:
				print ('STARTING VITERBI')
				vit=model.viterbi(prot)
		except:
			raise
			print ('Error in the prediction phase. Please double check you installed all the dependencies. If everyhting is correct, please report the bug to orlando.gabriele89@gmail.com')
			return

		if args.outfile!=None:
			f=open(args.outfile,'w')
			for i in prot.keys():
				f.write(i+' '+str(out[i])+'\n')
				if args.viterbi:
					for k in range(len(prot[i])):
						f.write('\t'+prot[i][k]+' '+str(vit[i][k].split('_')[0])+'\n')
			f.close()
			#print out
		else:
			for i in prot.keys():
				print(i+' '+str(out[i])+'\n')
				if args.viterbi:
					for k in range(len(prot[i])):
						print('\t'+prot[i][k]+' '+str(vit[i][k].split('_')[0]))
			#print out
		print ('\nDone')
	else:
		print('infile argument not found')

def main(args):
		return 0

if __name__ == '__main__':
    run_psper()
