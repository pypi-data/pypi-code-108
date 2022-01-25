#!/usr/bin/env python
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
import warnings
import torch
import argparse, sysconfig
import pathlib
import sys
import os

PATH = str(pathlib.Path(__file__).parent.absolute())
sys.path.append(os.path.abspath(os.path.join(PATH, "../../..")))

from b2bTools.nmr.shiftCrypt.shiftcrypt_pkg import parser

class Standalone():

	PATH = PATH

	def run_shiftcrypt(self):

		warnings.filterwarnings("ignore")

		pa = argparse.ArgumentParser()

		pa.add_argument('-i', '--infile',
							help='the input Nmr Exchange Format (NEF) file',
							)
		pa.add_argument('-fit','--fit',
							help='Custom_model_Name. re-runs the training and saves the model as marshalled/Custom_model_Name. For custom model',

							default=None
							)
		pa.add_argument('-o', '--outfile',
							help='output file. Residues with a shiftcrypt value of -10 highlight residues with too many missing values',
							default=None)

		pa.add_argument('-m', '--model',
							help='model to use:\n\t1 --> full model\n\n\t2 --> model that uses just the most common atoms (default) \n\n\t3 --> the method with only N, H  and CA CS. Used for dimers. if you want to load a custom model,use -m NameOfTheModel. Please remember the model is required to be in ./marshalled/ and can be generated with python shiftcrypt.py --fit MOdelName ',
							default='2')
		args = pa.parse_args()

		if args.fit:

			#
			# This part generates new models based on a new dataset
			#

			from .src.chemical_shifts_custom_model import shifts
			from .src.autoencoder_standalone_version import autoencoder_transformation

			a=autoencoder_transformation(shifts)
			a.fit(training_folder='src/datasets/rereferenced_nmr/')
			torch.save(a,'marshalled/'+args.fit)
			print ('############################################')
			print ('TRAIN SUCCESSFUL! the model has been saved')
			print ('in the "marshalled" folder. To use it run')
			print ('python2 shiftcrypt.py -m ModelName -i input')
			print ('############################################')
			print ('The monkeys are listening')
			return

		if args.infile:
			try:
				allProteinShifts = parser.parse_official(fil=args.infile)
			except:
				print('error in the parsing of the file. Please double check the format. If everyhting is correct, please report the bug to @gmail.com')
				return

			self.loadModel(args.model, args)
			encryptedValues = self.encryptProteinShifts(allProteinShifts)

			(void,inputFile) = os.path.split(args.infile)

			output = self.organiseData(encryptedValues,allProteinShifts,inputFile=inputFile)

			# Dump to custom file or print
			if args.outfile!=None:
				f=open(args.outfile,'w')

				for entry in output:
					chainCode = entry['chainCode']
					sequence = entry['sequence']
					shiftCryptValues = entry['shiftCrypt']
					seqCodes = entry['seqCodes']

					for i in range(len(sequence)):
						f.write("{} {:5d} {:s} {:7.3f}\n".format(chainCode,seqCodes[i],sequence[i],shiftCryptValues[i]))
				f.close()

			else:
				print (output)
		else:
			print('-i or --infile argument is obligatory, please retry')

	def api_shiftcrypt(self, fileName, modelClass, is_star, original_numbering):

		"""
    :param proteinShifts: Shift information for a protein
    """

		proteinShifts = parser.parse_official(fileName,is_star=is_star,original_numbering=original_numbering)

		self.loadModel(modelClass, None)

		encryptedValues = self.encryptProteinShifts(proteinShifts)
		shiftCryptResults = self.organiseData(encryptedValues, proteinShifts,inputFile=os.path.split(fileName)[1])

		if not shiftCryptResults:
			print("ShiftCrypt failed....")

		return {'results': shiftCryptResults}

	def encryptProteinShifts(self,allProteinShifts):

		outputs = []

		try:
			print('Running transformation')
			print(allProteinShifts)
			for proteinShifts in allProteinShifts:
				outputs.append(self.auto.transform(proteinShifts))
		except:
			print('Error transforming the CS data. Please double-check you installed all the dependencies. If everyhting is correct, please report the bug to wim.vranken@vub.be')

		return outputs

	def loadModel(self, modelType, args):

		# Hacks to ensure the model is loaded, was saved within specific directory architecture
		sys.path.append(os.path.abspath(self.PATH))

		if modelType == '1':
			self.auto = torch.load(self.PATH + '/models/new_full.mtorch',
														 encoding='latin1')  # the method with the full set of Cs. this may retur a lot of -10 (missing values) because of the scarcity of cs data for some residues
		elif modelType == '2':
			self.auto = torch.load(self.PATH + '/models/new_commons.mtorch',
														 encoding='latin1')  # the method with just the most common Cs values
		elif modelType == '3':
			self.auto = torch.load(self.PATH + '/models/new_NH.mtorch',
														 encoding='latin1')  # the method with only N and H CS. Used for dimers
		else:
			try:
				self.auto = torch.load(self.PATH + '/models/' + args.new_model, encoding='latin1')
			except:
				print("custom model not found")
				self.auto = None

	def organiseData(self, encryptedValues, allProteinShifts,inputFile=None):

		# Now organise output into a decent dictionary structure
		output = []

		for protIndex in range(len(encryptedValues)):
			encryptedValue = encryptedValues[protIndex]
			protInfo = allProteinShifts[protIndex]

			sequence = []
			shiftcrypt = []
			seqCodes = []

			for i in range(len(protInfo.seq)):
				sequence.append(protInfo.seq[i])
				shiftcrypt.append(str(encryptedValue[i]))
				seqCodes.append(protInfo.resnum[i])

			entry = {}

			entry['ID_file'] = inputFile
			entry['sequence'] = sequence
			entry['seqCodes'] = seqCodes
			entry['shiftCrypt'] = shiftcrypt
			entry['chainCode'] = protInfo.chainCode

			output.append(entry)

		return output

if __name__ == '__main__':

	sa = Standalone()
	sa.run_shiftcrypt()
