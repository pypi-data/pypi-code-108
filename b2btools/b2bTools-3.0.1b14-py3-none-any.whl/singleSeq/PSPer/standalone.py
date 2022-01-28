# -*- coding: utf-8 -*-
import sysconfig, os
from b2bTools.singleSeq.PSPer.phase_transition_hmm import phase_hmm
import string
import numpy as np


def leggifasta(database):
		f=open(database)
		uniprot=f.readlines()
		f.close()
		dizio={}
		for i in uniprot:
			if i[0]=='>':
					uniprotid=i.strip('>\n')
					dizio[uniprotid]=''
			else:
				dizio[uniprotid]=dizio[uniprotid]+i.strip('\n').upper()
		return dizio
def standalone(input_obj):
	features='dyna_back,psipred,ef,dyna_side'
	window=4
	verbose=0
	def check_sequences(seqs):
		for i in list(seqs.keys()):
			if i=='extra_predictions':
				continue
			if seqs[i].strip()=='SEMBRI QUEL FESSO DI MIO ZIO VITO':
				return {'error':'tua zia troverebbe il paragone alquanto ardito'}
			if i=='extra_predictions':  # questa cosa è un pochino grezza, ma noi siamo grezzi nell'anima
				continue
			if not seqs[i].isalpha():
				return {'error':'invalid char in sequence '+i}
			if len(seqs[i])>3000:
				#print len(seqs[i])
				return {'error':'sequence '+i+' too long, maximum lenght is 3000 amino acids'}
			if len(seqs[i])<20:
				#print len(seqs[i])
				return {'error':'sequence '+i+' short, minimum lenght is 20 amino acids'}
		return True
	def clean_psipred_tmp():
		scriptDir = sysconfig.get_paths()["purelib"]+'/b2bTools/singleSeq/DisoMine'
		print('Running Cleaner')
		TEMPDIR = scriptDir+'/vector_builder/psipred/tmp/'
		for filename in os.listdir(TEMPDIR):
		    file_path = os.path.join(TEMPDIR, filename)
		    try:
		        if os.path.isfile(file_path) or os.path.islink(file_path):
		            os.unlink(file_path)
		        elif os.path.isdir(file_path):
		            shutil.rmtree(file_path)
		    except Exception as e:
		        print('Failed to delete %s. Reason: %s' % (file_path, e))

	def load_model():
		mod=phase_hmm()
		mod.fit()
		scaler=None
		return mod,scaler


	def format_output(disorder,viterbi,seqs,features):
		out=[]

		for i in range(len(disorder.keys())):
			assert len(features[list(disorder.keys())[i]][:,i])==len(features[list(disorder.keys())[i]][:,0])
			entry={}
			features[list(disorder.keys())[i]]=np.array(features[list(disorder.keys())[i]])
			entry['proteinID']=list(disorder.keys())[i]
			entry['sequence']=seqs[list(disorder.keys())[i]]
			entry['protein_score']=disorder[list(disorder.keys())[i]]
			entry['viterbi']=viterbi[list(disorder.keys())[i]]
			entry['complexity']=list(features[list(disorder.keys())[i]][:,0])
			entry['arg']=list(features[list(disorder.keys())[i]][:,1])
			entry['tyr']=list(features[list(disorder.keys())[i]][:,2])
			entry['RRM']=list(features[list(disorder.keys())[i]][:,3])
			entry['disorder']=list(features[list(disorder.keys())[i]][:,4])
			out+=[entry]
		return {'results':out}



	def predict_fasta(fil,crunch=100):
		if type(fil)==str:
			try:
				a=leggifasta(fil)
			except:
				return {'error':"problems in the fasta file"}
		elif type(fil)==dict:
			a=fil
		else:
			return {'error':'internal error, wrong object passed to the standalone, it must be a dict or a string'}
		check=check_sequences(a)
		if check!=True:
			return check
		targets=list(a.keys())[:]
		results_dict={}
		cont=0
		dyna={}
		side={}
		ef={}
		v=model.build_vector(a)
		results_dict=model.predict_proba(v)
		viterbi=model.viterbi(v)
		fea={}
		printable=string.printable
		for id in v.keys():
			vet=[]
			for i in v[id]:
				t=[]
				cont=0
				for j in i:
					if cont==1:
						l=printable.index(j)
						t+=[float(l)]
					elif cont==2:
						l=printable.index(j)
						t+=[float(l)]
					else:
						l=printable.index(j)
						t+=[float(l)]
						cont+=1
				vet+=[t]
			fea[id]=np.array(vet)

		results=format_output(results_dict,viterbi,a,fea)
		return results
	# This should not be necessary with new disomine setup, commented out
	#clean_psipred_tmp()
	model,scaler=load_model()
	results=predict_fasta(input_obj)
	return results

def main(args):
	#print standalone("example.fasta")
	a=leggifasta('input_files_examples/example_toy.fasta')
	a['extra_predictions']=False
	print(standalone(a))
	#from memory_profiler import memory_usage
	#mem_usage = memory_usage(standalone,interval=0.01)
	#print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
	#print('Maximum memory usage: %s' % max(mem_usage))
	#cProfile.run('standalone("example.fasta")')

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
