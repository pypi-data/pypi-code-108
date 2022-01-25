#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  shiftcrypt.py
#
#  Copyright 2018  <@gmail.com>
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

# TEMPORARY HACK REMOVE
import sys
sys.path.append("/Users/wim/bio2byte/b2bTools/python/")
#

from b2bTools.general.Io import B2bIo
from b2bTools.singleSeq.EFoldMine.Predictor import EFoldMine
import warnings
warnings.filterwarnings("ignore")
import argparse
from b2bTools.singleSeq.Agmata.sources.agmata_source import agmata

def getAgmataPredictions(seqs, efm = None):

	# Best cutoff for aggregating, or not
	threshold = 0.015563146

	model=agmata(verbose=-1)

	try:
		model.load()
	except:
		raise
		print('Error loading the model. Please double check you installed all the dependencies. If everything is correct, please report the bug to wim.vranken@vub.be')
		return

	if not efm:
		print('Running EFoldMine')
		efm = EFoldMine()
		efm.predictSeqs(seqs)

	try:
		results = model.predict(seqList=seqs,dmPredictions=efm.allPredictions)

		for (proteinId, sequence) in seqs:
			# Loop over sequence, set category
			efm.allPredictions[proteinId]['agmata'] = []
			for i in range(len(results[proteinId])):
				aggrclass = 0
				if results[proteinId][i] > threshold:
					aggrclass = 1

				results[proteinId][i] = (sequence[i],results[proteinId][i],aggrclass)
				efm.allPredictions[proteinId]['agmata'].append(results[proteinId][i])

	except:
		raise
		print('Error in the prediction. Please double check you installed all the dependencies. If everything is correct, please report the bug to wim.vranken@vub.be')
		return

	return results

def run_agmata(args):
	args=args[1:]
	pa = argparse.ArgumentParser()

	pa.add_argument('-i', '--infile',
						help='the input FASTA file',
						)
	pa.add_argument('-o', '--outfile',
						help='output file',
						default=None)

	parseArgs = pa.parse_args(args)

	b2bio = B2bIo()

	try:
 	  seqs = b2bio.readFasta(parseArgs.infile)
	except:
		print('Error in FASTA file parsing. Please double check the format and input file name. If everything is correct, please report the bug to wim.vranken@vub.be')
		return

	results = getAgmataPredictions(seqs)

	textOutput = ""

	textOutput+= '#AA AgmataScore BinaryPrediction\n'
	for proteinId in results.keys():
		textOutput+= '# {}\n'.format(proteinId)
		for (aaCode,prediction,predClass) in results[proteinId]:
			textOutput+="{} {:7.2e} {}\n".format(aaCode,prediction,predClass)

	if parseArgs.outfile!=None:
		f = open(parseArgs.outfile, 'w')
		f.write(textOutput)
		f.close()

	else:
		print(textOutput)

	print('\nDONE')

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(run_agmata(sys.argv))
