#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  agmata.py
#
#  Copyright 2018 Gabriele Orlando <orlando.gabriele89@gmail.com>
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

import numpy as np
import sys, pathlib
import os,gc,tempfile,shutil
from b2bTools.singleSeq.DisoMine.vector_builder.vettore_gen import build_vector

import pickle

class agmata():

	def __init__(self,features='dyna_back,dyna_coil,dyna_sheet,dyna_helix,dyna_side',sw=1,verbose=2):
		self.features=features
		self.sw=sw
		self.LEARNING='log_reg'
		self.verbose=verbose
		self.params=[self.LEARNING,self.features,self.sw]
		self.scriptDir = str(pathlib.Path(__file__).parent.absolute())
		#self.tmpDir = os.path.join(self.scriptDir,'..','tmp')
		self.tmpDir = tempfile.mkdtemp()
		self.binDir = os.path.dirname(self.scriptDir)

	def load(self,force=False):

		with open(os.path.join(self.scriptDir,'..','marshalled','model_parameters.m'), 'rb') as f:
			u = pickle._Unpickler(f)
			u.encoding = 'latin1'
			p = u.load()
			if self.params!=p:
				if force==False:
					print('PARAMETERS CHANGED! NEW FITTING')
					self.fit()
				else:

					print('PARAMETERS CHANGED! but force==True,keeping old params(',p,')')
					# Dp,Da,Dn=self.strands=pickle.load(open('marshalled/discriminative.m','rb'))
					Dp,Da,Dn=self.strands=pickle.load(open('marshalled/agmata_discriminative_converted.m','rb'))
					self.Dp=Dp
					self.Da=Da
					self.Dn=Dn
					self.params=p
					self.LEARNING=p[0]
					self.features=p[1]
					self.sw=p[2]
			else:
				# with open(os.path.join(self.scriptDir,'..','marshalled','discriminative.m'),'rb') as f:
				with open(os.path.join(self.scriptDir,'..','marshalled','agmata_discriminative_converted.m'),'rb') as f:
					u = pickle._Unpickler(f)
					u.encoding = 'latin1'
					p = u.load()
					Dp,Da,Dn=p
					self.Dp=Dp
					self.Da=Da
					self.Dn=Dn

	def compare(self,v1,v2,COMP='vicini'):
		vf=[]
		#print v1,v2
		if COMP=='diff':

			if '-' in v1:
				vf=[]
				for i in v2:
					if type(i)!=str:
						vf+=[i]
				return vf
			elif '-' in v2:
				vf=[]
				for i in v1:
					if type(i)!=str:
						vf+=[i]
				return vf
			else:

				for i in range(len(v1)):

					if type(v1[i])!=str:
						vf+=[abs(v1[i]-v2[i])]

					else:
						if (v1[i].upper(),v2[i].upper()) in blosum:

							vf+=[blosum[(v1[i].upper(),v2[i].upper())]]
						else:

							vf+=[blosum[(v2[i].upper(),v1[i].upper())]]
		if COMP=='vicini':
			if '-' in v1:
				vf=[]
				for i in v2:
					if type(i)!=str:
						vf+=[i]
				return vf
			elif '-' in v2:
				vf=[]
				for i in v1:
					if type(i)!=str:
						vf+=[i]
				return vf
			else:

				for i in range(len(v1)):

					if type(v1[i])!=str:
						vf+=[v1[i],v2[i]]

					else:
						if (v1[i].upper(),v2[i].upper()) in blosum:

							vf+=[blosum[(v1[i].upper(),v2[i].upper())]]
						else:

							vf+=[blosum[(v2[i].upper(),v1[i].upper())]]
		return vf
	def predict(self,seqList,dmPredictions):
		features=self.features
		window= self.sw
		verbose=self.verbose

		currentPlatform = sys.platform
		if currentPlatform.startswith("linux"):
			agmata_suffix = "linux"
		elif currentPlatform == 'darwin':
			agmata_suffix = 'mac'
		else:
			raise RuntimeError("Executable not available for this OS - please contact wim.vranken@vub.be to add it.")


		results = {}

		for i in range(len(seqList)):
			(proteinId,sequence) = seqList[i]
			if verbose>=2:
				print('\tStarting target:',proteinId)
			vet=np.array(build_vector(sequence,dmPredictions[proteinId],TYPE=features,sw=window))

			x=[]
			for i in range(len(vet)):
				for j in range(i,len(vet)):
					x+=[self.compare(vet[i],vet[j])]

			if self.verbose>=1:
				print('\tnumero coefficienti:',2*len(x))

			if self.LEARNING=='kde':
				par=self.Dp.score_samples(x)
				ant=self.Da.score_samples(x)
				non=self.Dn.score_samples(x)
				cont=0
				f=open(os.path.join(self.tmpDir,'coef.tmp'),'w')
				for i in range(len(vet)):
					for j in range(i+1,len(vet)):
						pa=-(par[cont]-non[cont])
						an=-(ant[cont]-non[cont])
						f.write(str(i+1)+' '+str(j+1)+' '+str(pa)+' '+str(an)+' 0.00000 0.00000 \n')
						cont+=1
				f.close()
			elif self.LEARNING=='log_reg' or self.LEARNING=='SVM':
				ant=self.Da.predict_log_proba(x)
				par=self.Dp.predict_log_proba(x)
				cont=0
				f=open(os.path.join(self.tmpDir,'coef.tmp'),'w')
				for i in range(len(vet)):
					for j in range(i,len(vet)):
						pa=-(par[cont][1]-par[cont][0])
						an=-(ant[cont][1]-ant[cont][0])
						f.write(str(i+1)+' '+str(j+1)+' '+str(pa)+' '+str(an)+' 0.00000 0.00000 \n')
						cont+=1
				f.close()

			else:
				raise('unknown discriminative method')

			f=open(os.path.join(self.tmpDir,'seq.tmp'),'w')
			f.write(sequence+'\n')
			f.close()

			#os.system("cd {}; ../bin/agmata_c_final_{} seq.tmp 600 0".format(self.tmpDir,agmata_suffix))
			os.chdir(self.tmpDir)
			os.system("{}/bin/agmata_c_final_{} seq.tmp 600 0".format(self.binDir,agmata_suffix))
			f=open(os.path.join(self.tmpDir,'aggr_profile.dat'),'r')
			output=[]
			for i in f.readlines():
				output+=[float(i)]
			gc.collect()
			f.close()

			os.system('cd {}; rm aggr_profile.dat nseq pairing_mat.dat best_pairings_list.dat coef.tmp seq.tmp'.format(self.tmpDir))

			results[proteinId] = output
		shutil.rmtree(self.tmpDir)

		return results

