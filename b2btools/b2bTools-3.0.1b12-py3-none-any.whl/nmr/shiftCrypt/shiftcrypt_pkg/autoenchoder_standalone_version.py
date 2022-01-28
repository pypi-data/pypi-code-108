#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  autoenchoder_V0.0.py
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
import operator
from .autoenc_solo4 import autoencoder
from scipy.stats import pearsonr
import parser

letters={'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K', 'ASN': 'N', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ALA': 'A', 'HIS': 'H', 'GLY': 'G', 'ILE': 'I', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
from .parser import protein_class, residue_class
import torch
import torch.autograd as autograd
import torch.nn as nn

torch.manual_seed(1)
EPOCH=10
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler,StandardScaler

def run_rsa(folder='datasets/rereferenced_nmr/',outdir='rsa_vals/'):
	rsabin='./pdbasa'
	#for i in os.listdir(folder):
	#	os.system(rsabin+' '+folder+i+' '+outdir+i)
	## parse ##
	diz={}
	v=[]
	seqs={}
	for i in os.listdir(outdir):
		nome=i.split('.')[0]
		diz[nome]=[]
		resold=1
		tmp=[]
		cont=0
		seq=''
		for j in open(outdir+i,'r').readlines():

			if j.strip()=='':
				continue
			if not 'ATOM' == j[0:4]:
				continue
			res=j[22:26]
			rsa=j[60:66]
			try:
				aa=letters[j[17:20]]
			except:
				continue
			v+=[float(rsa)]
			if res!=resold and cont!=0:

				diz[nome]+=[np.mean(tmp)]
				seq+=aa
				tmp=[]
			tmp+=[-float(rsa)]
			resold=res
			cont+=1

		diz[nome]+=[np.mean(tmp)]
		seq+=aa
		assert len(seq)==len(diz[nome])
		seqs[nome]=seq
	v=np.array(v).reshape((-1,1))
	scaler=MinMaxScaler()
	scaler.fit(v)

	#print diz[i]
	for i in list(diz.keys()):
		try:
			diz[i]=scaler.transform(np.array(diz[i]).reshape((-1,1))).reshape((-1))
		except:
			diz[i]=[-10]*len(seqs[i])
	return diz,seqs
def leggifasta(database): #legge un file fasta e lo converte in un dizionario
	f=open(database)
	uniprot=f.readlines()
	f.close()
	dizio={}
	for i in uniprot:

		if i[0]=='>':
				if '|' in i:

					uniprotid=i.strip('>\n').split('|')[1]
				else:
					uniprotid=i.strip('>\n')
				dizio[uniprotid]=''
		else:
			dizio[uniprotid]=dizio[uniprotid]+i.strip('\n')
	return dizio
def parse_uniprot_annotations(fil='dataset/all_seqs_dnabinding_uniprot.annotations'):
	diz={}
	salta=0
	for i in open(fil).readlines():
		a=i.split()
		try:
			bind_start=int(a[3])-1
			bind_end=int(a[4])
		except:
			salta+=1
			continue
		seq=a[1]
		p1=[0]*bind_start
		p2=[1]*(bind_end-bind_start)
		p3=[0]*(len(seq)-bind_end)
		p=p1+p2+p3
		assert len(p)==len(seq)
		diz[a[0]]=(seq,p)
	#print 'got ',len(diz),'predictions. Saltate',salta
	return diz
def getScoresSVR(pred, real, threshold,FULL_SCORES=True):
	import math
	import numpy as np
	if len(pred) != len(real):
		raise Exception("ERROR: input vectors have differente len!")
	i = 0
	confusionMatrix = {}
	confusionMatrix["TP"] = confusionMatrix.get("TP", 0)
	confusionMatrix["FP"] = confusionMatrix.get("FP", 0)
	confusionMatrix["FN"] = confusionMatrix.get("FN", 0)
	confusionMatrix["TN"] = confusionMatrix.get("TN", 0)
	while i < len(real):
		if float(pred[i])<=threshold and (int(real[i])==0):
			confusionMatrix["TN"] = confusionMatrix.get("TN", 0) + 1
		if float(pred[i])<=threshold and int(real[i])==1:
			confusionMatrix["FN"] = confusionMatrix.get("FN", 0) + 1
		if float(pred[i])>=threshold and int(real[i])==1:
			confusionMatrix["TP"] = confusionMatrix.get("TP", 0) + 1
		if float(pred[i])>=threshold and int(real[i])==0:
			confusionMatrix["FP"] = confusionMatrix.get("FP", 0) + 1
		i += 1
	#print confusionMatrix
	if FULL_SCORES:

		#print "--------------------------------------------"
		#print confusionMatrix["TN"],confusionMatrix["FN"],confusionMatrix["TP"],confusionMatrix["FP"]
		#print "          | SSBOND            | FREE             |"
		#print "predBond  | TP: %d (%2.2f%%)  | FP: %d (%2.2f%%) |" % (confusionMatrix["TP"], (confusionMatrix["TP"]/float(confusionMatrix["TP"]+confusionMatrix["FN"]))*100, confusionMatrix["FP"], (confusionMatrix["FP"]/float(confusionMatrix["FP"]+confusionMatrix["TN"]))*100 )
		#print "predFree  | FN: %d (%2.2f%%)  | TN: %d (%2.2f%%) |" % (confusionMatrix["FN"],(confusionMatrix["FN"]/float(confusionMatrix["TP"]+confusionMatrix["FN"]))*100, confusionMatrix["TN"], (confusionMatrix["TN"]/float(confusionMatrix["FP"]+confusionMatrix["TN"]))*100)
		sen = (confusionMatrix["TP"]/float((confusionMatrix["TP"] + confusionMatrix["FN"])))
		spe = (confusionMatrix["TN"]/float((confusionMatrix["TN"] + confusionMatrix["FP"])))
		acc =  (confusionMatrix["TP"] + confusionMatrix["TN"])/float((sum(confusionMatrix.values())))
		bac = (0.5*((confusionMatrix["TP"]/float((confusionMatrix["TP"] + confusionMatrix["FN"])))+(confusionMatrix["TN"]/float((confusionMatrix["TN"] + confusionMatrix["FP"])))))
		inf =((confusionMatrix["TP"]/float((confusionMatrix["TP"] + confusionMatrix["FN"])))+(confusionMatrix["TN"]/float((confusionMatrix["TN"] + confusionMatrix["FN"])))-1.0)
		pre =(confusionMatrix["TP"]/float((confusionMatrix["TP"] + confusionMatrix["FP"])))
		mcc =	( ((confusionMatrix["TP"] * confusionMatrix["TN"])-(confusionMatrix["FN"] * confusionMatrix["FP"])) / math.sqrt((confusionMatrix["TP"]+confusionMatrix["FP"])*(confusionMatrix["TP"]+confusionMatrix["FN"])*(confusionMatrix["TN"]+confusionMatrix["FP"])*(confusionMatrix["TN"]+confusionMatrix["FN"])) )

	#print real
	#print pred
	from sklearn.metrics import roc_auc_score
	aucScore = roc_auc_score(real, pred)

	#print "AUC = %3.3f" % aucScore
	#print "--------------------------------------------"
	if FULL_SCORES:
		return sen,spe,acc,pre,mcc,aucScore
	else:
		return aucScore
def run_ring(pdb_folder='pdb_interacting/'):
	############ you need to export VICTOR_ROOT=/home/gabriele/HD1/dna_binding_prediction/ring/ ####
	def parse_ring(fil,tmp_fold='tmp_ringfiles/'):
		fil=tmp_fold+fil
		diz={}
		for i in open(fil).readlines():
			a=i.split()
			if ':_:DA' in a[0] or ':_:DT' in a[0] or ':_:DC' in a[0] or ':_:DG' in a[0]:
				first_dna=True
			else:
				first_dna=False
			if ':_:DA' in a[2] or ':_:DT' in a[2] or ':_:DC' in a[2] or ':_:DG' in a[2]:
				second_dna=True
			else:
				second_dna=False
			if first_dna and not second_dna:
				resi=a[2].split(':')
				if resi[3] not in letters:
					print('MISSING AMINOACID')
					rname='X'
				else:
					rname=letters[resi[3]]
				if resi[0] not in diz:
					diz[resi[0]]={}
				diz[resi[0]][(int(resi[1]),rname)]=1
			if not first_dna and second_dna:
				resi=a[0].split(':')
				if resi[3] not in letters:
					print('MISSING AMINOACID')
					rname='X'
				else:
					rname=letters[resi[3]]
				if resi[0] not in diz:
					diz[resi[0]]={}
				diz[resi[0]][(int(resi[1]),rname)]=1
		return diz
	def parse_pdb(fil,tmp_fold='pdb_interacting/'):
		fil=tmp_fold+fil
		diz={}
		seq={}
		for i in open(fil).readlines():
			if i.strip()=='':
				continue
			a=i.split()
			if not a[0]=='ATOM':
				continue
			if 'DA' in a[3] or 'DT' in a[3] or 'DC' in a[3] or 'DG' in a[3]: #dna
				continue
			chain=i[21]#a[4]
			resnum=int(i[22:26])
			if chain not in seq:
				seq[chain]={}
			'''
			try:
				int(a[5])
			except:
				return 'error'
			'''

			if a[3] not in letters:
				print('MISSING AMINOACID')
				rname='X'
			else:
				rname=letters[a[3]]
			if (int(resnum),rname) not in seq[chain]:
						seq[chain][(int(resnum),rname)]=0
			#except:
			#	return 'error'
			'''
			except:
				i=i[:22]+' '+i[22:] ### ma porcodio...se i residui vanno sopra 999 il pdb si dimentica di aggiungere una colonna
				a=i.split()
				if not a[0]=='ATOM':
					continue
				if 'DA' in a[3] or 'DT' in a[3] or 'DC' in a[3] or 'DG' in a[3]: #dna
					continue
				chain=a[4]
				if not seq.has_key(chain):
					seq[chain]={}

				if not seq[chain].has_key((int(a[5]),letters[a[3]])):
					seq[chain][(int(a[5]),letters[a[3]])]=0
				#raw_input()
			'''
		return seq
	ring_bin='ring/bin/Ring'
	db={}
	cont=0
	for pdb in os.listdir(pdb_folder)[:]:
		if not '.pdb' in pdb:
			continue
		#if pdb.replace('.pdb','.edges') in os.listdir('tmp_ringfiles'):
		#	continue
		print('starting ',pdb)
		os.system(ring_bin+' -i '+pdb_folder+pdb+' -t 3 --all -E tmp_ringfiles/'+pdb.replace('.pdb','.edges')+' > /dev/null')

		diz=parse_ring(pdb.replace('.pdb','.edges'))
		pdb_diz=parse_pdb(pdb)
		if pdb_diz=='error':
			print('salto')
			continue
		### chain selection policy i take the one with the greatest number of interactions ###
		bestchain=0
		for i in list(diz.keys()):
			if len(diz[i])>bestchain:
				chain=i
				bestchain=len(diz[i])
		if bestchain==0:
			print('NO DNA INTERACTIONS IN',pdb.replace('.pdb',''))
			continue
		if chain not in pdb_diz:
			print('salto')
			continue
		for i in list(diz[chain].keys()):
			pdb_diz[chain][i]=1

		seq=''
		vals=[]
		for i in sorted(pdb_diz[chain].keys()):
			seq+=i[1]
			vals+=[pdb_diz[chain][i]]
		db[pdb.replace('.pdb','')]=(seq,vals)


	return db

def aucNth(yp, y, N=50):
	assert len(y) == len(yp)
	assert len(y) > 1
	from sklearn.metrics import roc_curve, auc
	fpr, tpr, thresholds = roc_curve(y, yp)
	negatives = y.count(0)
	assert N < negatives
	perc = N / float(negatives)
	#print perc
	fpr1k = []
	tpr1k = []
	i = 0
	while i < len(fpr):
		if fpr[i] > perc:
			break
		fpr1k.append(fpr[i])
		tpr1k.append(tpr[i])
		i+=1
	assert len(fpr1k) > 1
	#print fpr1k, tpr1k
	aucScore = auc(fpr1k, tpr1k) / perc
	#print ">>AUC%d: %3.3f" %(N,aucScore)
	return aucScore

class nn_class_autoenc(nn.Module):
		def __init__(self, n_features,hidden_dim=10,cuda=False):
			super(nn_class_autoenc, self).__init__()

			self.encoder = nn.Sequential(
				nn.Linear(n_features, hidden_dim),
				nn.ReLU(),
				nn.Linear(hidden_dim, hidden_dim),
				nn.ReLU(),
				nn.Linear( hidden_dim, 1),
				nn.Sigmoid()
				)
			self.decoder = nn.Sequential(
				nn.Linear( 1,hidden_dim),
				nn.ReLU(),
				nn.Linear(hidden_dim, hidden_dim),
				nn.ReLU(),
				nn.Linear(hidden_dim,n_features),
				nn.Sigmoid()
			)

		def forward(self, x):
				encoded = self.encoder(x)
				decoded = self.decoder(encoded)
				return encoded, decoded
		def encode_x(self,x):
			return self.encoder(x)
		def decode_x(self,x):
			return self.decoder(x)

class autoencoder():
	def __init__(self, hidden_dim=100,cuda=False):
		self.hidden_dim=hidden_dim
		self.cuda=cuda
	def fit(self,x,batch=100,EPOCH=10,LR=0.01):
		nn_auto=nn_class_autoenc(len(x[0]),hidden_dim=self.hidden_dim)
		optimizer = torch.optim.Adam(nn_auto.parameters())
		loss_func = nn.MSELoss()
		#plt.ion()
		#fig, ax = plt.subplots(nrows=1, ncols=1)
		for epoch in range(EPOCH):
			decoded_all=[]
			x_all=[]
			for i in range(0,len(x),batch):
				if i+batch>len(x):
					end=len(x)
				else:
					end=len(x)+i
				if self.cuda:
					b_x = autograd.Variable(torch.Tensor(x[i:end])).cuda()
					b_y = autograd.Variable(torch.Tensor(x[i:end])).cuda()
				else:
					b_x = autograd.Variable(torch.Tensor(x[i:end]))
					b_y = autograd.Variable(torch.Tensor(x[i:end]))

				encoded, decoded = nn_auto(b_x)
				decoded_all+=list(decoded.data.numpy())
				x_all+=list(x[i:end])
				loss = loss_func(decoded[:,:4], b_y[:,:4])
				optimizer.zero_grad()
				loss.backward()



				#ax.plot([np.array(x_all)[:,0],np.array(x_all)[:,1]],'ro')


				optimizer.step()
			#print epoch,loss.data.numpy()[0]
			'''
			ax.clear()
			a=np.array(decoded_all)[0:100,0]
			b=np.array(decoded_all)[0:100,1]

			#assert len(a)==len(b)

			ax.scatter(a,b,alpha=1)
			ax.scatter(np.array(x_all)[:,0],np.array(x_all)[:,1],color='r',alpha=0.01)
			plt.draw(); plt.pause(0.05)
			print loss.data

			ax.clear()
			ax.plot([np.array(decoded_all)[0:100,0],np.array(decoded_all)[0:100,1]],'bo')
			ax.plot([np.array(x_all)[:,0],np.array(x_all)[:,1]],'ro')
			plt.draw(); plt.pause(0.05)
			'''
		self.model=  nn_auto
	def encode(self,x):

		if self.cuda:
			b_x = autograd.Variable(torch.Tensor(x)).cuda()
			b_y = autograd.Variable(torch.Tensor(x)).cuda()
		else:
			b_x = autograd.Variable(torch.Tensor(x))
			b_y = autograd.Variable(torch.Tensor(x))
		y_b=self.model.encode_x(b_x)
		#print len(y_b)
		return y_b.data.numpy().flatten()
	def decode(self,x):

		if self.cuda:
			b_x = autograd.Variable(torch.Tensor(x)).cuda()
			b_y = autograd.Variable(torch.Tensor(x)).cuda()
		else:
			b_x = autograd.Variable(torch.Tensor(x))
			b_y = autograd.Variable(torch.Tensor(x))
		y_b=self.model.decode_x(b_x)

		return y_b.data.numpy()

class autoencoder_transformation():
	def __init__(self,chemical_shifts_diz):
		self.scalers={}
		self.autoen={}
		self.shifts={}
		self.second_scaler={}
		self.third_scaler={}
		self.inverse={}
		self.sec_struct_scaler={}
		#################################
		#### change here the scalers ####
		#################################
		# remember the first one MUST mantain the shape --> don't use standard scaler or you will get random fitting
		self.first_scaler_class=MinMaxScaler
		self.second_scaler_class=StandardScaler
		self.third_scaler_class=MinMaxScaler
		self.sec_struct_scaler_class=None#secondary_structure_scaler
		self.boundaries={}
		self.shifts=chemical_shifts_diz
		#################################
	def fit(self,training_folder,remove_outlayers=True): #training _folder contains the nef files for training
		diz_base={}

		diz_base=parser.parse_train(training_folder)
		predictor={}
		scalers={}
		diz={}
		for prot in list(diz_base.keys()):
			for resi in diz_base[prot].resi:
				if resi.resname not in diz:
					diz[resi.resname]=[]

				diz[resi.resname]+=[resi]
		count_available_chemical_shft=False
		if count_available_chemical_shft:
			for i in list(diz.keys()):
				conteggio={}
				print(i)
				#if i=='G' or i=='P':
				#	continue
				for r in diz[i]:
					for k in list(r.atom.keys()):
						if k not in conteggio:
							conteggio[k]=0

						conteggio[k]+=1
				for k in sorted(list(conteggio.items()), key=operator.itemgetter(1)):
					print('\t',k[0],k[1])
		self.average={}
		#print sorted(diz.keys())
		pearson_resu={}
		for aa in sorted(diz.keys())[:]:
			print('starting',aa)
			ss=[]
			X=[]
			if aa not in self.average:
				self.average[aa]={}
			for entry in diz[aa][:]:
				xt=[]
				buona=True

				for i in self.shifts[aa]:

					if i not in entry.atom:
						buona=False

						break
				if buona:

					for i in self.shifts[aa]:
						xt+=[entry.atom[i]]
						if i not in self.average[aa]:
							self.average[aa][i]=[]
						self.average[aa][i]+=[entry.atom[i]]
					X+=[xt]
					ss+=[entry.ss]
			for i in list(self.average[aa].keys()):
				self.average[aa][i]=np.mean(self.average[aa][i])
			scaler=self.first_scaler_class()
			if X==[]:
				print('## ERROR NOT ENOUGH DATA TO TRAIN THE DEFINED MODEL ##')
				print('try to reduce the number/type of atom taken into consideration for amino acid',aa)
				print('Another possibility is that you mispelled an atom code. They need to be the same of the ones in the training files(sources/datasets/rereferenced_nmr/)')
				assert False
			X=np.array(X)
			if remove_outlayers==True:
				perc=[]
				Xnew=[]
				ssnew=[]
				goodpos=[]
				fin=np.ones(len(X),dtype=bool)

				for i in range(len(self.shifts[aa])):

					up=np.percentile(X[:,i],99)
					down=np.percentile(X[:,i],1)
					low_values_flags = X[:,i] > down
					high_values_flags = X[:,i] < up
					fin=np.logical_and(np.logical_and(low_values_flags,high_values_flags),fin)

				for i in range(len(X)):
					if fin[i]==True:
						Xnew+=[X[i]]
						ssnew+=[ss[i]]
					else:
						pass
				print('removed',len(X)-len(Xnew),'outlaiers starting from',len(X),'points')
				X=np.array(Xnew)
				#print X.shape

				ss=ssnew

			X=scaler.fit_transform(X)
			self.scalers[aa]=scaler
			self.autoen[aa]=autoencoder(hidden_dim=50)
			self.autoen[aa].fit(X,batch=100,EPOCH=10,LR=0.01)
			yp=self.autoen[aa].encode(X)
			back_to_x=self.autoen[aa].decode(yp.reshape(-1,1))
			pear=True

			if pear:
				f=open('pear','a')
				for sh in range(len(self.shifts[aa])-1,-1,-1):
					if self.shifts[aa][sh] not in pearson_resu:
						pearson_resu[self.shifts[aa][sh]]=[]
						pearson_resu[self.shifts[aa][sh]]+=[pearsonr(X[:,sh],back_to_x[:,sh])[0]]
					f.write(aa+'\t'+self.shifts[aa][sh]+'\t'+str(np.round(pearsonr(X[:,sh],back_to_x[:,sh])[0],2))+'\n')
					print('\tpearosn for arom:',self.shifts[aa][sh], pearsonr(X[:,sh],back_to_x[:,sh])[0])
					#plt.scatter(X[:,sh],back_to_x[:,sh])
					#plt.show()
			colors={'H':'g','E':'r','C':'b','-':'k'}


			yp_original=yp[:]
			vals=np.percentile(yp,10)
			sec=[]
			for i in range(len(yp)):
				if yp[i]<vals:
					sec+=ss[i]
			print('\tH/E rate:',float(sec.count('H'))/(float(sec.count('E')+1)))
			if sec.count('H')>sec.count('E'):
				self.inverse[aa]=False
			else:
				self.inverse[aa]=True

			if self.inverse[aa]==True:
				yp= np.array([ -x for x in yp])

			if self.second_scaler_class!=None:
				self.second_scaler[aa]=self.second_scaler_class()
				yp=self.second_scaler[aa].fit_transform(yp.reshape(-1,1)).reshape(-1)
			if self.third_scaler_class!=None:
				self.third_scaler[aa]=self.third_scaler_class()
				yp=self.third_scaler[aa].fit_transform(yp.reshape(-1,1)).reshape(-1,1)
			'''
			n, bins, patches = plt.hist(yp, 50, histtype='stepfilled')
			plt.setp(patches, 'facecolor', 'blue', 'alpha', 0.3)
			#plt.setp(patches, 'facecolor', 'alpha', 0.3)
			plt.show()
			'''
			####inverse:
			'''
			if self.third_scaler_class!=None:
				yp=self.third_scaler[aa].inverse_transform(yp.reshape(-1,1)).reshape(-1,1)
			if self.second_scaler_class!=None:
				yp=self.second_scaler[aa].inverse_transform(yp.reshape(-1,1)).reshape(-1,1)
			if self.inverse[aa]==True:
				yp= np.array([ -x for x in yp])
			'''
			if self.sec_struct_scaler_class!=None:
				self.sec_struct_scaler[aa]=self.sec_struct_scaler_class()
				self.sec_struct_scaler[aa].fit(yp,ss)
				if self.sec_struct_scaler[aa]!=None:
					yp=self.sec_struct_scaler[aa].transform(np.array(yp).reshape(-1,1)).reshape(-1)
				#xs = np.linspace(0,1,200)
				#yxs=self.sec_struct_scaler[aa].transform(xs.reshape(-1,1)).reshape(-1)
				#plt.plot(xs,yxs)
			plot_single_atom=False
			if plot_single_atom:
				raw_cs=X
				raw_cs=np.array(raw_cs)
				for i in range(len(self.shifts[aa])):
					plt.title('aa '+aa+' atom: '+self.shifts[aa][i])
					plt.xlabel('Original CS (scaled from 0 to 1)')
					plt.ylabel('NN-Transformed CS')
					plt.xlim(0,1)
					plt.ylim(0,1)
					for j in range(len(raw_cs)):
						plt.plot([raw_cs[j][i]],[yp[j]],color=colors[ss[j]],marker=',',alpha=0.5)

					plt.clf()
					#plt.show()

	def transform(self,protein): ##takes a protein instance
		res=[]
		for i in protein.resi:
			xt=[]
			buona=True
			aa=i.resname
			if aa=='X':
				res+=[-10]
				continue
			for atom in self.shifts[aa]:
				if atom not in i.atom:
					#i.atom[atom]=self.average[aa][atom]
					buona=False
					break
			if buona:
				for atom in self.shifts[aa]:
					xt+=[i.atom[atom]]
				xt=self.scalers[aa].transform([xt])
				yp=self.autoen[aa].encode(xt)
				if self.inverse[aa]==True:
					yp= np.array([ -x for x in yp])
				if self.second_scaler_class!=None:
					yp=self.second_scaler[aa].transform([yp])
				if self.third_scaler_class!=None:
					yp=self.third_scaler[aa].transform(yp)
				if self.sec_struct_scaler_class!=None:
					yp=self.sec_struct_scaler[aa].transform(yp)
				res+=list(yp[0]) ###	BUG QUI, VIENE DIVERSO SE USI SCALERS OPPURE NO, TIPO UNA LISTA IN PIU
			else:

				res+=[-10]
		#print res
		return np.array(res)
	def inverse_transform(self,yp,seq): ##takes a protein instance
		yp=np.array(yp)
		fin=[]
		prot=protein_class()
		for ind in range(len(seq)):
			resi=residue_class()
			aa=seq[ind]
			val=[[yp[ind]]]
			if self.sec_struct_scaler_class!=None and self.sec_struct_scaler[aa]!=None:
				val=self.sec_struct_scaler[aa].inverse_transform(val)
			if self.third_scaler_class!=None:
				val=self.third_scaler[aa].inverse_transform(val)
			if self.second_scaler_class!=None:

				val=self.second_scaler[aa].inverse_transform(val)
			if self.inverse[aa]==True:
				val= [[-val[0][0]]]
			xt=self.autoen[aa].decode(val)[0]  ###ANCHE QUI, VEDI SOPRA
			xt=self.scalers[aa].inverse_transform([xt])[0]
			atoms={}
			assert len(xt)==len(self.shifts[aa])
			for i in range(len(self.shifts[aa])):
				atoms[self.shifts[aa][i]]=float(xt[i])
			resi.resname=aa
			resi.atom=atoms
			prot.resi+=[resi]
			prot.seq=seq

			#xt=list(xt)

			#fin+=[xt]

		return prot

def main(args):
	a=autoencoder_transformation()
	a.fit(training_folder='datasets/rereferenced_nmr')
	torch.save(a,'../marshalled/custom_model_10epocs.mtorch')
	#a.transform('../training_dataset_example/bmr4031_1.nef')

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
