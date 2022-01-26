#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  phase_transition_hmm.py
#
#  Copyright 2018 scimmia <scimmia@scimmia-ThinkPad-L540>
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
from sklearn.metrics import roc_auc_score
from scipy.stats import ranksums
import matplotlib.pyplot as plt
from b2bTools.singleSeq.PSPer.hmmer_research.hmmsearch_otf import hmmer_wrapper
from b2bTools.singleSeq.PSPer.source.utils import seqs_features,leggifasta
import numpy as np
import pickle, string, random
from pomegranate import *
from scipy.optimize import minimize
import json
import os, pathlib
from b2bTools.singleSeq.DynaMine.Predictor import DynaMine
from b2bTools.singleSeq.EFoldMine.Predictor import EFoldMine
from b2bTools.singleSeq.DisoMine.Predictor import DisoMine

def load_pickle(pickle_file):
    try:
        with open(pickle_file, 'rb') as f:
            pickle_data = pickle.load(f)
    except UnicodeDecodeError as e:
        with open(pickle_file, 'rb') as f:
            pickle_data = pickle.load(f, encoding='latin1')
    except Exception as e:
        print('Unable to load data ', pickle_file, ':', e)
        raise
    return pickle_data

class phase_hmm:

	def __init__(self):
		self.emiss_diverse=None
		self.emiss_bg=None
		self.scaler=None

		self.scriptDir = str(pathlib.Path(__file__).parent.absolute())

	def fit(self):

		if 'emissions.m' in os.listdir(os.path.join(self.scriptDir,'marshalled')):
			print ('loading emissions')
			self.emiss_diverse,self.emiss_bg=load_pickle(os.path.join(self.scriptDir,'marshalled/emissions.m'))
		else:
			print ('calculating emissions')
			self.emiss_diverse,self.emiss_bg=self.learn_distro()
			pickle.dump((self.emiss_diverse,self.emiss_bg),open(os.path.join(self.scriptDir,'marshalled/emissions.m','w')))

		self.build_hmm()

		if 'scaler.m' in os.listdir(os.path.join(self.scriptDir,'marshalled')):
			print ('loading scaler')
			self.scaler=load_pickle(os.path.join(self.scriptDir,'marshalled/scaler.m'))
		else:
			print ('calculating scaler')
			self.scaler=self.learn_scaling()
			pickle.dump(self.scaler,open(os.path.join(self.scriptDir,'marshalled/scaler.m','w')))
		print (self.scaler)

	def build_hmm(self,param=None,optim_params=False,PLOT_DISTROS=False):
		if self.emiss_diverse==None or self.emiss_bg==None:
			raise ValueError('YOU FIRST NEED TO FIT EMISSIONS! RUN .fit()')
		diverso=self.emiss_diverse
		costante=self.emiss_bg
		if not optim_params:
			len_pld=80
			len_rna=50
			len_altro=20
			len_grigio=15

			### param transizioni ###
			TRANS_ALTRO=0.001

			## somma a 1 ###
			TRANS_ESTENDI_STATO=0.6

			################

		else:
			len_pld=int(param[1])
			len_rna=int(param[2])
			len_altro=int(param[3])
			len_grigio=int(param[4])
		diz_rna={}
		diz_NON_rna={}

		for i in range(11):
			if i==10:
				diz_rna['a']=0.05+i*0.1*0.9/5.5
			else:

				diz_rna[str(i)]=0.05+i*0.1*0.9
		for i in range(10,-1,-1):
			if i!=10:
				diz_NON_rna[str(i)]=0.05+(10-i)*0.1*0.9
			else:

				diz_NON_rna['a']=0.05+(10-i)*0.1*0.9
		norm=sum(diz_rna.values())
		for i in diz_rna.keys():
			diz_rna[i]=diz_rna[i]/norm
		norm=sum(diz_NON_rna.values())
		for i in diz_NON_rna.keys():
			diz_NON_rna[i]=diz_NON_rna[i]/norm
		rna_alto=DiscreteDistribution(diz_rna)
		rna_basso=DiscreteDistribution(diz_NON_rna)
		#rna_alto=DiscreteDistribution(diverso[3])
		#rna_basso=DiscreteDistribution(costante[4])
		#print diz_NON_rna
		#ad
		if PLOT_DISTROS:
			features=['complexity','G-R_enrichment','Y_enrichment','RNA','Disorder']
			for i in range(len(features)):
				data_c = costante[i]
				data_d =diverso[i]
				cos=[]
				div=[]
				for k in sorted(data_c.keys()):
					cos+=[data_c[k]]
					div+=[data_d[k]]
				if features[i]!='complexity':
					plt.plot(range(len(cos)),cos,'r',label='background distr.')
					plt.plot(range(len(cos)),div,'b',label='inferred PSP distr.')
				else:
					plt.plot(range(len(cos)),div,'b',label='inferred PSP distr.')
					plt.plot(range(len(cos)),cos,'r',label='background distr.')
				plt.xlabel(features[i])
				plt.ylabel('Emission probability')
				plt.legend()
				#left_of_first_bin = 0
				#right_of_last_bin = len(data_k.keys())#data.max() + float(d)/2
				#plt.hist(data, np.arange(left_of_first_bin, right_of_last_bin + d, d))
				plt.title(features[i])
				plt.savefig('plot_distros/'+features[i]+'.png')
				plt.clf()



		distrib_altro =IndependentComponentsDistribution([DiscreteDistribution(costante[0]),DiscreteDistribution(costante[1]),DiscreteDistribution(costante[2]),rna_basso,DiscreteDistribution(costante[4])])
		distrib_grigia=IndependentComponentsDistribution([DiscreteDistribution(costante[0]),DiscreteDistribution(diverso[1]),DiscreteDistribution(costante[2]),rna_basso,DiscreteDistribution(diverso[4])])
		distrib_rna   =IndependentComponentsDistribution([DiscreteDistribution(costante[0]),DiscreteDistribution(costante[1]),DiscreteDistribution(costante[2]),rna_alto,DiscreteDistribution(costante[4])])
		distrib_pdl   =IndependentComponentsDistribution([DiscreteDistribution(diverso[0]),DiscreteDistribution(costante[1]),DiscreteDistribution(diverso[2]),rna_basso,DiscreteDistribution(diverso[4])])
		PLD1=[]
		PLD2=[]
		altroB=[]
		altroF=[]

		altroRNA=[]
		altroPLD=[]
		grigioB=[]
		grigioF=[]
		grigio_intra1=[]
		grigio_intra2=[]
		grigioRNA=[]
		grigioPLD=[]
		RNA1=[]
		RNA2=[]

		for i in range(len_pld):
			PLD1+=[State(distrib_pdl,name='PLD_1'+str(i))]
			PLD2+=[State(distrib_pdl,name='PLD_2'+str(i))]
		for i in range(len_rna):
			RNA1+=[State(distrib_rna,name='RRM_1'+str(i))]
			RNA2+=[State(distrib_rna,name='RRM_2'+str(i))]
		for i in range(len_altro):
			altroB+=[State(distrib_altro,name='OTHER_B_'+str(i))]
			altroPLD+=[State(distrib_altro,name='OTHER_PLD_'+str(i))]
			altroRNA=[State(distrib_altro,name='OTHER_RNA_'+str(i))]
			altroF+=[State(distrib_altro,name='OTHER_F_'+str(i))]
		for i in range(len_grigio):
			grigioB+=[State(distrib_grigia,name='SPACER_B_'+str(i))]
			grigioF+=[State(distrib_grigia,name='SPACER_F_'+str(i))]
			grigioPLD+=[State(distrib_grigia,name='SPACER_PLD_'+str(i))]
			grigioRNA+=[State(distrib_grigia,name='SPACER_RNA_'+str(i))]
			grigio_intra1+=[State(distrib_grigia,name='SPACER_intra2_'+str(i))]
			grigio_intra2+=[State(distrib_grigia,name='SPACER_intra1_'+str(i))]
		model = HiddenMarkovModel()
		background= HiddenMarkovModel()
		bg=State(distrib_altro,name='background')
		background.add_states(bg)
		background.add_transition(bg ,bg ,0.7)
		background.add_transition(bg ,background.end ,0.3)
		background.add_transition(background.start,bg,1)
		background.bake()
		self.background=background
		# grigio
		for i in range(len(grigioB)):
			model.add_states(grigioB[i])
		for i in range(len(grigioF)):
			model.add_states(grigioF[i])
		for i in range(len(grigioRNA)):
			model.add_states(grigioRNA[i])
		for i in range(len(grigioPLD)):
			model.add_states(grigioPLD[i])
		for i in range(len(grigio_intra1)):
			model.add_states(grigio_intra1[i])
		for i in range(len(grigio_intra2)):
			model.add_states(grigio_intra2[i])
		# altro
		for i in range(len(altroB)):
			model.add_states(altroB[i])
		for i in range(len(altroF)):
			model.add_states(altroF[i])
		for i in range(len(altroPLD)):
			model.add_states(altroPLD[i])
		for i in range(len(altroRNA)):
			model.add_states(altroRNA[i])
		#######################################
		#PLD
		for i in range(len(PLD1)):
			model.add_states(PLD1[i])
		for i in range(len(PLD2)):
			model.add_states(PLD2[i])
		#RNA
		for i in range(len(RNA1)):
			model.add_states(RNA1[i])
		for i in range(len(RNA2)):
			model.add_states(RNA2[i])
		#######################################
		#              GRIGIO
		for i in range(len(grigioB)-1):
			model.add_transition(grigioB[i],grigioB[i+1] , 1)
		model.add_transition(grigioB[-1],grigioB[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(grigioF)-1):
			model.add_transition(grigioF[i],grigioF[i+1] , 1)
		model.add_transition(grigioF[-1],grigioF[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(grigioPLD)-1):
			model.add_transition(grigioPLD[i],grigioPLD[i+1] , 1)
		model.add_transition(grigioPLD[-1],grigioPLD[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(grigioRNA)-1):
			model.add_transition(grigioRNA[i],grigioRNA[i+1] , 1)
		model.add_transition(grigioRNA[-1],grigioRNA[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(grigio_intra1)-1):
			model.add_transition(grigio_intra1[i],grigio_intra1[i+1] , 1)
		model.add_transition(grigio_intra1[-1],grigio_intra1[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(grigio_intra2)-1):
			model.add_transition(grigio_intra2[i],grigio_intra2[i+1] , 1)
		model.add_transition(grigio_intra2[-1],grigio_intra2[-1] , TRANS_ESTENDI_STATO)

		################################################
		#                 altro
		for i in range(len(altroB)-1):
			model.add_transition(altroB[i],altroB[i+1] , 1)
		model.add_transition(altroB[-1],altroB[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(altroPLD)-1):
			model.add_transition(altroPLD[i],altroPLD[i+1] , 1)
		model.add_transition(altroPLD[-1],altroPLD[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(altroF)-1):
			model.add_transition(altroF[i],altroF[i+1] , 1)
		model.add_transition(altroF[-1],altroF[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(altroRNA)-1):
			model.add_transition(altroRNA[i],altroRNA[i+1] , 1)
		model.add_transition(altroRNA[-1],altroRNA[-1] , TRANS_ESTENDI_STATO)

		################################################
		#                  rna
		for i in range(len(RNA1)-1):
			model.add_transition(RNA1[i],RNA1[i+1] , 1)
		model.add_transition(RNA1[-1],RNA1[-1] , TRANS_ESTENDI_STATO)
		for i in range(len(RNA2)-1):
			model.add_transition(RNA2[i],RNA2[i+1] , 1)
		model.add_transition(RNA2[-1],RNA2[-1] , TRANS_ESTENDI_STATO)

		################################################
		#                 pld
		for i in range(len(PLD1)-1):
			model.add_transition(PLD1[i],PLD1[i+1] , 1)
		model.add_transition(PLD1[-1],PLD1[-1] , TRANS_ESTENDI_STATO)

		for i in range(len(PLD2)-1):
			model.add_transition(PLD2[i],PLD2[i+1] , 1)
		model.add_transition(PLD2[-1],PLD2[-1] , TRANS_ESTENDI_STATO)

		##################### MODULO 1 #######################
		#  somma a 0.05 per avere estensione di 20 al blocco #
		# la P disponibile e' 1-P(self-transizione interna al blocco) --> ora a 0.95 --> estensione media 20
		######################################################


		######################################################à
		#                    BEGIN                            #
		#######################################################

		model.add_transition(model.start,PLD1[0] , 0.5)
		model.add_transition(model.start,grigioB[0] , 0.3)
		model.add_transition(model.start,altroB[0] , TRANS_ALTRO)
		model.add_transition(model.start,RNA1[0] , 0.1)
		######################################################à
		#                    altrob                           #
		#######################################################
		model.add_transition(altroB[-1],PLD1[0] , 0.1*(1-TRANS_ESTENDI_STATO))
		model.add_transition(altroB[-1],grigioB[0] , 0.8*(1-TRANS_ESTENDI_STATO))
		model.add_transition(altroB[-1],RNA1[0] , 0.1*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    grigioB                            #
		#######################################################
		model.add_transition(grigioB[-1],PLD1[0] , 0.45*(1-TRANS_ESTENDI_STATO))
		model.add_transition(grigioB[-1],altroB[0] , TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))
		model.add_transition(grigioB[-1],RNA1[0] , 0.45*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    RNA1                            #
		#######################################################
		model.add_transition(RNA1[-1],PLD2[0] , 0.1*(1-TRANS_ESTENDI_STATO))
		model.add_transition(RNA1[-1],grigio_intra1[0] , 0.6*(1-TRANS_ESTENDI_STATO))
		model.add_transition(RNA1[-1],grigioRNA[0] , 0.4*(1-TRANS_ESTENDI_STATO))
		model.add_transition(RNA1[-1],altroRNA[0] , TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))

		model.add_transition(grigio_intra1[-1],RNA1[0] , 1*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    grigioRNA                        #
		#######################################################
		model.add_transition(grigioRNA[-1],PLD2[0] , 0.8*(1-TRANS_ESTENDI_STATO))
		model.add_transition(grigioRNA[-1],altroRNA[0] , TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))


		######################################################à
		#                    altroRNA                        #
		#######################################################
		model.add_transition(altroRNA[-1],PLD2[0] , 0.1*(1-TRANS_ESTENDI_STATO))
		model.add_transition(altroRNA[-1],grigioRNA[0] , 0.9*(1-TRANS_ESTENDI_STATO))


		######################################################à
		#                   PLD2                             #
		#######################################################
		model.add_transition(PLD2[-1],altroF[0] ,TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))
		model.add_transition(PLD2[-1],grigioF[0] , 0.1*(1-TRANS_ESTENDI_STATO))
		model.add_transition(PLD2[-1],model.end ,0.8*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    altroF                      #
		#######################################################
		model.add_transition(altroF[-1],model.end , 0.2*(1-TRANS_ESTENDI_STATO))
		model.add_transition(altroF[-1],grigioF[0] , 0.8*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    grigioF                      #
		#######################################################
		model.add_transition(grigioF[-1],model.end , 0.2*(1-TRANS_ESTENDI_STATO))
		model.add_transition(grigioF[-1],altroF[0] , 0.8*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                   PLD1                             #
		#######################################################
		model.add_transition(PLD1[-1],altroPLD[0] , TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))
		model.add_transition(PLD1[-1],grigioPLD[0] , 0.8*(1-TRANS_ESTENDI_STATO))
		model.add_transition(PLD1[-1],RNA2[0] ,0.1*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    grigioPLD                        #
		#######################################################
		model.add_transition(grigioPLD[-1],RNA2[0] , 0.8*(1-TRANS_ESTENDI_STATO))
		model.add_transition(grigioPLD[-1],altroPLD[0] , TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))


		######################################################à
		#                    altroPLD                       #
		#######################################################
		model.add_transition(altroPLD[-1],RNA2[0] , 0.2*(1-TRANS_ESTENDI_STATO))
		model.add_transition(altroPLD[-1],grigioPLD[0] , 0.8*(1-TRANS_ESTENDI_STATO))

		######################################################à
		#                    RNA2                            #
		#######################################################
		model.add_transition(RNA2[-1],grigio_intra2[0] , 0.4*(1-TRANS_ESTENDI_STATO))
		model.add_transition(RNA2[-1],grigioF[0] , 0.4*(1-TRANS_ESTENDI_STATO))
		model.add_transition(RNA2[-1],altroF[0] , TRANS_ALTRO*(1-TRANS_ESTENDI_STATO))
		model.add_transition(RNA2[-1],model.end , 0.2*(1-TRANS_ESTENDI_STATO))
		model.add_transition(grigio_intra2[-1],RNA2[0] , 1*(1-TRANS_ESTENDI_STATO))
		######

		model.bake()

		self.model=model
		#import json
		#a=self.model.to_json()
		#open('params.json','w').write(a)
	def build_vector(self,seqs):
		SEQS = []
		for key, value in seqs.items():
			temp = (key,value)
			SEQS.append(temp)


		# TODO - could still improve this by providing the predictions if already run prior to PSPer request! Will speed things up...
		dm = DynaMine(predictionTypes=['backbone', 'sidechain'])
		dm.predictSeqs(SEQS)
		efm = EFoldMine()
		efm.allPredictions = dm.allPredictions
		efm.predictSeqs(SEQS)
		de = DisoMine()
		de.allPredictions = efm.allPredictions
		disomine=de.predictSeqs(SEQS)
		entry={}
		for protID in range(len(seqs)):
			entry[json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['proteinID']] = np.array(json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['disoMine'])

		disomine = entry
		hmmer_class=hmmer_wrapper(root=os.path.join(self.scriptDir,'hmmer_research/'))
		hmmer=hmmer_class.predict(seqs)

		fea=seqs_features(seqs)
		diz={}

		for i in hmmer.keys():
			diz[i]=discretizza([fea[i][0],fea[i][1],fea[i][2],hmmer[i],disomine[i]])

		return diz

	def predict_proba(self,seq,scale=True):

		if type(seq)==str:
			seq={'input_seq':seq}
			vets=self.build_vector(seq)
		elif type(seq)==dict and type(seq[list(seq.keys())[0]])==str:
			vets=self.build_vector(seq)
		elif type(seq)==dict and type(seq[list(seq.keys())[0]])==list:
			vets = seq
		else:
			raise TypeError('predict takes a protein sequnce (str) or a dict of sequences or a dict of feature vectors (list)')
		res={}
		for i in vets.keys():
			true=self.model.log_probability(vets[i])
			rand=self.background.log_probability(vets[i])
			score=true-rand

			if scale==True:
				cattivo=False

				if score<-10000:
					score=-10000
					cattivo=True
				score=self.scaler.transform([[score]])[0][0]
				if cattivo:
					score=0

				if score<0:
					score=0.0
				elif score>1:
					score=1.0
			res[i]=float(score)
		return res

	def viterbi(self,seq,scale=False):
		if type(seq)==str:
			seq={'input_seq':seq}
			vet=self.build_vector(seq)
		elif type(seq)==dict and type(seq[list(seq.keys())[0]])==str:
			vet=self.build_vector(seq)
		elif type(seq)==dict and type(seq[list(seq.keys())[0]])==list:
			vet = seq
		else:
			raise TypeError('predict takes a protein sequnce (str) or a dict of sequences or a dict of feature vectors (list)')
		r={}
		for i in seq.keys():
			p=[]
			path= ", ".join(state.name for i, state in self.model.viterbi(vet[i])[1])
			for k in path.split(',')[1:-1]:
				p+=[k.split('_')[0]]
			assert len(p)==len(seq[i])
			r[i]=p
		return r

	def learn_scaling(self):
		from sklearn.preprocessing import MinMaxScaler

		if FAST and 'backgroundDataset.fasta.cPickle' in os.listdir('marshalled'):
			vets_bg=load_pickle('marshalled/backgroundDataset.fasta.cPickle')

		else:
			print ('no vect marshal for background, this will take ages')
			seqs_bg=leggifasta('validationDatasets/background/backgroundDataset.fasta')
			s={}

			for i in seqs_bg.keys()[:]:
				if len(seqs_bg[i])>=MAX_SEQ_SIZE or len(seqs_bg[i])<MIN_SEQ_SIZE:
					continue
				s[i]=seqs_bg[i]
			seqs_bg=s
			vets_bg=self.build_vector(seqs_bg)
			pickle.dump((vets_bg,seqs_bg),open('marshalled/backgroundDataset.fasta.cPickle','w'))

		if "phaseSepVects.cPickle" in os.listdir('marshalled'):
			vets=load_pickle('marshalled/phaseSepVects.cPickle')
		else:
			seqs=leggifasta('validationDatasets/phaseSepProts/phase_separation_proteins.fasta')
			print ('no vect marshal for phase_separation, marshalling.',len(seqs),'proteins to do')
			s={}
			for i in seqs.keys()[:]:

				if len(seqs[i])>=MAX_SEQ_SIZE:
					continue
				s[i]=seqs[i]
			seqs=s
			vets=self.build_vector(seqs)
			pickle.dump(vets,open('marshalled/phaseSepVects.cPickle','w'))


		if "RNABPdatasetFinal.fasta.cPickle" in os.listdir('marshalled'):
			vetsbp=load_pickle('marshalled/RNABPdatasetFinal.fasta.cPickle')
			#del vetsbp['Q9UQ35']
			#pickle.dump(vetsbp,open('marshalled/RNABPdatasetFinal.fasta.cPickle','w'))
		else:
			seqsbp=leggifasta('validationDatasets/RNAbp/RNABPdatasetFinal.fasta')
			print ('no vect marshal for phase_separation, marshalling.',len(seqsbp),'proteins to do')
			s={}
			for i in seqsbp.keys()[:]:

				if len(seqsbp[i])>=MAX_SEQ_SIZE:
					continue
				s[i]=seqsbp[i]
			seqsbp=s
			vetsbp=self.build_vector(seqsbp)


			pickle.dump(vetsbp,open('marshalled/RNABPdatasetFinal.fasta.cPickle','w'))
		#vets.update(vets_bg)
		#print vetsbp[0]
		#print vets
		vetsbp.update(vets_bg)
		if vetsbp.has_key('Q25434'):
			del vetsbp['Q25434']
		r=self.predict_proba(vetsbp,scale=False)
		scaler=MinMaxScaler() #QuantileTransformer()
		scaler.fit(np.array(r.values()).reshape(-1, 1))
		a=[]
		pickle.dump(scaler, open('marshalled/scaler.m', 'w'))
		return scaler

	def learn_distro(self,bg_file='validationDatasets/background/backgroundDataset.fasta',bins=[12,12,12,10,10],reverse=[False,True,True,True,True],minemiss=0.05,plot_histograms=True): # si e' grezza,ma in bin_range_per_fea devi mettere, per ogni feature il numero di bins e il range di ogni feature. questo perche' alcuni valori non vengono visti mai
		seqs=leggifasta(bg_file)
		s={}
		for i in seqs.keys()[:500]:

			if len(seqs[i])>MAX_SEQ_SIZE or len(seqs[i])<MIN_SEQ_SIZE:
				continue
			s[i]=seqs[i]
		seqs=s

		if FAST and 'seqs_vec_background.m' in os.listdir('marshalled'):
			vets,seqs=load_pickle('marshalled/seqs_vec_background.m')
		else:
			vets=self.build_vector(seqs)
		printable=string.printable

		cont=0
		g=[]
		for i in vets.keys():
			dig=vets[i]
			for j in dig:
				l=[]
				for k in j:
					l+=[printable.index(k)]
				g+=[l]
		diz_prob=[]
		diz_cost=[]
		g=np.array(g)
		h=[]
		for i in range(g.shape[1]):
			hist, bin_edges=np.histogram(g[:,i], bins=bins[i], range=(0,bins[i]), density=True,normed=True)
			h+=[hist]
			costante=list(np.cumsum(hist))

			for k in range(len(costante)):

				costante[k]=max(costante[k],minemiss)
				#print costante[i],max(costante[i],minemiss)
				#raw_input()
			#print min(costante),'qe'
			assert min(costante)>=minemiss
			d=[]
			if reverse[i]:
				prev=1.0
				pc=1.0
				c=[1]
				for k in range(1,len(hist[1:])+1):
					c+=[max(c[-1]-hist[k-1],minemiss)]
					assert min(c)>=0.05
				for k in range(len(hist)-1,-1,-1):
					prev-=hist[k]
					prev=max(prev,minemiss)
					d=[prev]+d
				diz_cost+=[c]
				diz_prob+=[d]
			else:
				prev=1.0
				diz_cost+=[costante]

				for k in range(len(hist)):
					prev-=hist[k]
					prev=max(prev,minemiss)
					d+=[prev]
				diz_prob+=[d]

		distro=[]
		for i in diz_prob:
			diz={}
			for k in range(len(i)):
				diz[printable[k]]=i[k]
			distro+=[diz]

		distro_cost=[]
		cont=0
		for i in diz_cost:

			di={}
			for k in range(len(i)):
				#print i[k]
				assert i[k]>=0.05
				di[printable[k]]=i[k]
			distro_cost+=[di]
			cont+=1
		if plot_histograms:
			fea_names=['Sequence complexity','Arg enrichment','Tyr enrichment','RNA-binding','Disorder']
			for i in range(g.shape[1]):
				data = g[:,i]
				fig, ax1 = plt.subplots()
				d = np.diff(np.unique(data)).min()
				left_of_first_bin = data.min() - float(d)/2
				right_of_last_bin = data.max() + float(d)/2
				ax1.hist(data, np.arange(left_of_first_bin, right_of_last_bin + d, d),normed=True,label='feature distribution')

				#ax1.hist(scores, bins=15,alpha=0.3, color="b")
				#ax1.set_xlabel('HMM scores')
				# Make the y-axis label, ticks and tick labels match the line color.
				#ax1.set_ylabel('Occurrence', color='b')
				ax1.tick_params('y', colors='b')

				ax2 = ax1.twinx()
				ax2.tick_params('y', colors='r')
				#values, base = np.histogram(scores, bins=100,normed=False)

				y=[]
				cont=0.0
				x=[]
				for j in sorted(distro_cost[i].keys()):
					if distro_cost[i][j]==0.05:
						y+=[0.0]
					elif distro_cost[i][j]==0.95:
						y+=[1]
					else:
						y+=[distro_cost[i][j]]
					x+=[cont]
					cont+=1

				if i!=0:
					yc=[]
					for k in y:
						yc+=[1-k]
						y=yc

				ax2.plot(x, y, c='r',label='Cumulative')
				if i==1:
					plt.legend()

				#plt.plot(x,y,label='feature cumulative distribution', alpha=0.4)
				plt.legend()

				plt.ylabel('Probability')
				plt.xlabel('Feature value')

				plt.title(fea_names[i])
				plt.savefig(fea_names[i]+'.png',dpi=400)
				plt.clf()
		for i in range(len(distro_cost)):
			v=distro_cost[i].values()
			for k in distro_cost[i].keys():
				distro_cost[i][k]=distro_cost[i][k]/sum(v)
		for i in range(len(distro)):
			v=distro[i].values()
			for k in distro[i].keys():
				distro[i][k]=distro[i][k]/sum(v)
		pickle.dump((distro,distro_cost), open('marshalled/emissions.m', 'w'))
		pickle.dump((distro,distro_cost), open('marshalled/emissions.m', 'w'))
		return distro,distro_cost

class scoring_function:
	def __init__(self):
		self.distro,self.distro_cost=load_pickle('marshalled/emissions.m')
		seqs_rna=leggifasta('rna_bp.fasta')
		s={}
		for i in seqs_rna.keys()[:]:
			s[i]=seqs_rna[i]
		seqs_rna=s
		seqs=leggifasta('phase_separation_proteins.fasta')

		s={}
		for i in seqs.keys()[:]:
			s[i]=seqs[i]
		seqs=s
		self.vets=build_vector(seqs)
		self.vets_rna=build_vector(seqs_rna)

	def score(self,c):
		model=phase_hmm(self.distro,self.distro_cost,param=c,optim_params=True)
		a= model.predict(self.vets)
		b= model.predict(self.vets_rna)
		return np.median(b)-np.median(a)

def parameter_opt():
	score_obj=scoring_function()
	c=minimize(score_obj.score, [0,70,80,50,30])
	print (c)

def discretizza(feas,continue_val=[False,False,False,False,True],n_bins=10): ## metti numero bins per ogni feature
	printable=string.printable
	bins = numpy.linspace(0, 1, n_bins)
	dig=[]
	for i in range(len(continue_val)):
		if continue_val[i]:
			dig+=[numpy.digitize(feas[i], bins)]
			#print numpy.digitize(feas[i], bins)

		else:

			dig+=[feas[i]]
	v=[]
	for i in range(len(dig[0])):
		s=''
		for j in range(len(dig)):
			#print len(feas[j]),len(feas),len(threshold),i,j
			s+=printable[dig[j][i]]
		v+=[s]
	return v

####  cose da fare : cumulativa background direttamente da hist, le distro fatte  bene--> diverso[i], costante[i] per fare background o non background
PSP = 'validationDatasets/phaseSepProts/phase_separation_proteins.fasta'
FAST = True
#TARGET = "validationDatasets/mip6.fasta"
#TARGET = "proteomes/ecoli.UP000000625.fasta"
#TARGET = "proteomes/saccharomycesUP000002311.fasta"
#TARGET= "validationDatasets/144granuleCoreProts/144granuleCoreProts.fasta"
#TARGET = "validationDatasets/granuleForming/granuleForming.fasta"
#TARGET = "validationDatasets/RNAbp/RNABPdatasetFinal.fasta"
#TARGET = "disordered.fasta"
#TARGET = "validationDatasets/prionLikeFromCellPaper/prionLike.fasta"
#TARGET = "validationDatasets/prions/prionDataset.fasta"
TARGET = "validationDatasets/background/backgroundDataset.fasta"
#TARGET= "validationDatasets/disordered_proteins.fasta" #
#TARGET='newPSP.fasta'
ERASE = False
MIN_SEQ_SIZE=150
MAX_SEQ_SIZE=3000

def test(TARGET):
	model=phase_hmm()
	model.fit()


	seqs = leggifasta(PSP)
	targetSeqs = leggifasta(TARGET)
	print ("Found %d proteins in %s" % (len(seqs), PSP))
	print ("Reading PSP...")
	if FAST and os.path.exists("marshalled/phaseSepVects.cPickle") and not ERASE:
		vets = load_pickle("marshalled/phaseSepVects.cPickle")
	else:
		s={}
		for i in seqs.keys()[:]:
			if len(seqs[i])>MAX_SEQ_SIZE :
				continue
			s[i]=seqs[i]
		seqs=s
		vets = model.build_vector(seqs)
		pickle.dump(vets, open("marshalled/phaseSepVects.cPickle","w"))
	phaseSepPreds = model.predict_proba(vets).values()
	####################################################################

	if  "background" in TARGET:
		targets = targetSeqs.keys()[15000:]

		random.shuffle(targets)
		targets = targets[:2000]

	else:
		targets = targetSeqs.keys()[:]

	print ("Found %d proteins in %s" % (len(targets), TARGET))

	if FAST and os.path.exists("marshalled/"+TARGET.split("/")[-1]+".cPickle") and not ERASE:
		vets = load_pickle("marshalled/"+TARGET.split("/")[-1]+".cPickle")


	else:
		s={}
		for i in targets:
			if len(targetSeqs[i])>MAX_SEQ_SIZE or len(targetSeqs[i])<MIN_SEQ_SIZE:
				continue
			s[i]=targetSeqs[i]
		targets=s

		targets = removeKnownPSP(targets, seqs.keys())  #this removes known PSP

		vets = model.build_vector(targets)
		pickle.dump(vets, open("marshalled/"+TARGET.split("/")[-1]+".cPickle","w"))

	print ('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
	preds = model.predict_proba(vets)
	prediction_diz=preds
	for i in sorted(preds.items(), key=lambda x:x[1], reverse=True)[0:50]:
		print (i[0],i[1],'\\\\')

	targetPreds = preds.values()
	print (targetPreds)
	print ("Using %d proteins" % len(vets))

	####random.shuffle(preds)
	labels = [1]*len(phaseSepPreds)+[0]*len(targetPreds)
	print ('auc',roc_auc_score(labels, preds))
	print ('pvalue',ranksums(phaseSepPreds, targetPreds))
	print (np.median(phaseSepPreds))

	plt.figure(figsize=(5,4))
	plt.title("Ranksums p-value = %.3e\nAUC = %.3f" % (ranksums(phaseSepPreds,targetPreds)[1], roc_auc_score(labels, preds)))
	plt.grid()
	plt.ylabel("HMM scores")
	#plt.violinplot([a,b])
	plt.boxplot([phaseSepPreds, targetPreds], notch=True)

	plt.xticks([1,2],["Phase Separation", "IDPs"])
	plt.tight_layout()
	#plt.savefig(TARGET+".png", dpi=400)
	#plt.show()

	print ('ok')

	return prediction_diz

def removeKnownPSP(t, s):
	#print type(t), type(s)
	r = {}
	c = 0
	for i in t.items():
		if i[0] in s:
			c += 1
			continue
		r[i[0]] = i[1]
	print ("Removed %d prots from targets" % c)
	return r

if __name__ == '__main__':
	test(TARGET)
