#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#  
#  Copyright 2018 -ThinkPad-L540>
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
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler,StandardScaler
letters={'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K', 'ASN': 'N', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ALA': 'A', 'HIS': 'H', 'GLY': 'G', 'ILE': 'I', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
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


	for i in list(diz.keys()):
		diz[i]=scaler.transform(np.array(diz[i]).reshape((-1,1))).reshape((-1))
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
	from sklearn.metrics import roc_curve, auc, roc_auc_score 
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
def parse_official(fil='bound_free/bmr16065_bound.nef',bound=False):
	start=False
	arom_diz={  'F': ('CG','CD1','CD2','CE1','CE2','CZ'),
                'Y': ('CG','CD1','CD2','CE1','CE2','CZ'),
                'H': ('CD2','CE1','CG'),
                'W': ('CG','CD1','CD2','CE2','CE3','CH2','CZ2','CZ3')}

	oldnum=None
	chainold=None
	prot=protein_class()
	cominciato=False
	for l in open(fil).readlines():
		if not start:
			
			if '_Atom_shift_assign_ID' in l or '_nef_chemical_shift.value_uncertainty' in l:
				start=True
			else:
				prot.useless_stuf+=l
			continue

		if '_' in l:
			if not cominciato:
				prot.useless_stuf+=l+'\n'
			continue
		if 'loop_' in l:
			if not cominciato:
				prot.useless_stuf+=l+'\n'
			continue
		if 'stop_' in l:
			continue
		if 'save_' in l:
			continue	
		l=l.strip()
		if l=='':
			if not cominciato:
				prot.useless_stuf+='\n'
			continue
		
		cominciato=True
		a=l.replace('%','').split()
		chain=a[0]
		resitype=letters[a[2]]
		if resitype in arom_diz and a[3] in arom_diz[resitype]:
			atom=a[3]+'_'

		else:
			atom=a[3]

		shift=float(a[4])
		resinum=int(a[1])
		
		if oldnum==None:
			
			oldnum=resinum
			resi=residue_class()
			resi.resname=resitype
		if 	oldnum!=resinum:
			#print prot.seq,resi.resname
			prot.seq+=resi.resname
			prot.resi+=[resi]
			prot.resnumbering+=[resi.resinumbering]
			prot.chain+=[resi.chain]
			oldnum=resinum
			resi=residue_class()
		resi.atom[atom]=shift
		
		resi.resname=resitype
		resi.resname3letters=a[2]
		resi.chain=chain
		resi.resinumbering=resinum
		#def __init__(self):
		#	self.resname=None
		#	self.atom={}
		#	self.ss=None
		#	self.rci=None
		#	shift=float(a[4])
	return prot
if __name__ == '__main__':

	db=run_ring()
	print('ok')
	import pickle
	pickle.dump(db,open('marshalled/db_contacts_dna.m','w'))
	print(len(db))
	'''
	diz=leggifasta('dataset/cdhit_uniprot.fasta')
	diz1=parse_uniprot_annotations()
	buono=0
	for i in diz.keys():
		if diz1.has_key(i):
			buono+=1
	print buono
	'''
