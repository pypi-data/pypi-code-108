# Author: Robert Guthrie

#typ='dyna_back,psipred,ef,dyna_side'
#ws=3
#400 epoche 0.816002568073
import torch
import sys
from torch.nn import  BCELoss
from torch.nn import MaxPool1d
import numpy as np

import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim


torch.manual_seed(1)

def to_scalar(var):
    # returns a python float
    return var.view(-1).data.tolist()[0]


def argmax(vec):
    # return the argmax as a python int
    _, idx = torch.max(vec, 1)
    return to_scalar(idx)


def prepare_sequence(seq, to_ix):  #### faivet
    idxs = [to_ix[w] for w in seq]
    tensor = torch.LongTensor(idxs)
    return autograd.Variable(tensor)


# Compute log sum exp in a numerically stable way for the forward algorithm
def log_sum_exp(vec):
	max_score = vec[0, argmax(vec)]
	max_score_broadcast = max_score.view(1, -1).expand(1, vec.size()[1])
	return max_score + \
		torch.log(torch.sum(torch.exp(vec - max_score_broadcast)))
class BiLSTM_CRF(nn.Module):
	def __init__(self, hidden_dim,n_features,n_classes=2,cuda=True):
		self.classes_=[0,1]
		super(BiLSTM_CRF, self).__init__()
		self.hidden_dim = hidden_dim
		self.criterion = CrossEntropyLoss()#(torch.Tensor([1,0.35]))
		#self.vocab_size = vocab_size
		#self.tag_to_ix = tag_to_ix
		self.tagset_size = n_classes+2 ## begin e end
		self.STOP_TAG=3
		self.START_TAG=2
		self.tag_to_ix={}
		self.tag_to_ix[self.START_TAG]=2
		self.tag_to_ix[self.STOP_TAG]=3
		tag_to_ix=self.tag_to_ix
		self.cuda=cuda
		# self.word_embeds = nn.Embedding(vocab_size, embedding_dim)
		if self.cuda:
			self.lstm = nn.LSTM(n_features, hidden_dim // 2,num_layers=1, bidirectional=True).cuda() 
			self.hidden2tag = nn.Linear(hidden_dim, self.tagset_size).cuda() 
			self.transitions = nn.Parameter(torch.randn(self.tagset_size, self.tagset_size).cuda() )
		else:
			self.lstm = nn.LSTM(n_features, hidden_dim // 2,num_layers=1, bidirectional=True)
			self.hidden2tag = nn.Linear(hidden_dim, self.tagset_size)
			self.transitions = nn.Parameter(torch.randn(self.tagset_size, self.tagset_size))
		# Maps the output of the LSTM into tag space.

		# These two statements enforce the constraint that we never transfer
		# to the start tag and we never transfer from the stop tag
		self.transitions.data[tag_to_ix[self.START_TAG], :] = -10000
		self.transitions.data[:, tag_to_ix[self.STOP_TAG]] = -10000

		self.hidden = self.init_hidden()

	def init_hidden(self):
		if self.cuda:
			return (autograd.Variable(torch.randn(2, 1, self.hidden_dim // 2)).cuda(),autograd.Variable(torch.randn(2, 1, self.hidden_dim // 2)).cuda() )
		else:
			return (autograd.Variable(torch.randn(2, 1, self.hidden_dim // 2)),autograd.Variable(torch.randn(2, 1, self.hidden_dim // 2)) )

	def _forward_alg(self, feats):
		# Do the forward algorithm to compute the partition function
		if self.cuda:
			init_alphas = torch.Tensor(1, self.tagset_size).fill_(-10000.).cuda()
		else:
			init_alphas = torch.Tensor(1, self.tagset_size).fill_(-10000.)
		# START_TAG has all of the score.
		init_alphas[0][self.tag_to_ix[self.START_TAG]] = 0.

		# Wrap in a variable so that we will get automatic backprop
		forward_var = autograd.Variable(init_alphas)

		# Iterate through the sentence
		for feat in feats:
			alphas_t = []  # The forward variables at this timestep
			for next_tag in range(self.tagset_size):
				# broadcast the emission score: it is the same regardless of
				# the previous tag
				emit_score = feat[next_tag].view(
					1, -1).expand(1, self.tagset_size)
				# the ith entry of trans_score is the score of transitioning to
				# next_tag from i
				trans_score = self.transitions[next_tag].view(1, -1)
				# The ith entry of next_tag_var is the value for the
				# edge (i -> next_tag) before we do log-sum-exp
				next_tag_var = forward_var + trans_score + emit_score
				# The forward variable for this tag is log-sum-exp of all the
				# scores.
				alphas_t.append(log_sum_exp(next_tag_var))
			forward_var = torch.cat(alphas_t).view(1, -1)
		terminal_var = forward_var + self.transitions[self.tag_to_ix[self.STOP_TAG]]
		alpha = log_sum_exp(terminal_var)
		return alpha
	def get_params(self,deep=True):
		return {}
	def _get_lstm_features(self, sentence):
		
		self.hidden = self.init_hidden()
		sentence=sentence.view(len(sentence), 1, -1)
		#embeds = self.word_embeds(sentence).view(len(sentence), 1, -1)
		lstm_out, self.hidden = self.lstm(sentence, self.hidden)

		lstm_out = lstm_out.view(len(sentence), self.hidden_dim)
		lstm_feats = self.hidden2tag(lstm_out)
		return lstm_feats

	def _score_sentence(self, feats, tags):
		# Gives the score of a provided tag sequence
		if self.cuda:
			score = autograd.Variable(torch.Tensor([0]).cuda())
			tags = torch.cat([torch.LongTensor([self.tag_to_ix[self.START_TAG]]).cuda(), tags])
		else:
			score = autograd.Variable(torch.Tensor([0]))
			tags = torch.cat([torch.LongTensor([self.tag_to_ix[self.START_TAG]]), tags])
		#print torch.cat([torch.LongTensor([self.tag_to_ix[self.START_TAG]]).cuda(), tags])
		#raw_input()

		for i, feat in enumerate(feats):
			score = score + \
				self.transitions[tags[i + 1], tags[i]] + feat[tags[i + 1]]
		score = score + self.transitions[self.tag_to_ix[self.STOP_TAG], tags[-1]]
		return score

	def _viterbi_decode(self, feats):
		backpointers = []

		# Initialize the viterbi variables in log space
		init_vvars = torch.Tensor(1, self.tagset_size).fill_(-10000.)
		init_vvars[0][self.tag_to_ix[self.START_TAG]] = 0

		# forward_var at step i holds the viterbi variables for step i-1
		if  self.cuda:
			forward_var = autograd.Variable(init_vvars).cuda()
		else:
			forward_var = autograd.Variable(init_vvars)
		for feat in feats:
			bptrs_t = []  # holds the backpointers for this step
			viterbivars_t = []  # holds the viterbi variables for this step

			for next_tag in range(self.tagset_size):
				# next_tag_var[i] holds the viterbi variable for tag i at the
				# previous step, plus the score of transitioning
				# from tag i to next_tag.
				# We don't include the emission scores here because the max
				# does not depend on them (we add them in below)
				next_tag_var = forward_var + self.transitions[next_tag]
				best_tag_id = argmax(next_tag_var)
				bptrs_t.append(best_tag_id)
				viterbivars_t.append(next_tag_var[0][best_tag_id])
			# Now add in the emission scores, and assign forward_var to the set
			# of viterbi variables we just computed
			forward_var = (torch.cat(viterbivars_t) + feat).view(1, -1)
			backpointers.append(bptrs_t)

		# Transition to STOP_TAG
		terminal_var = forward_var + self.transitions[self.tag_to_ix[self.STOP_TAG]]
		best_tag_id = argmax(terminal_var)
		path_score = terminal_var[0][best_tag_id]

		# Follow the back pointers to decode the best path.
		best_path = [best_tag_id]
		for bptrs_t in reversed(backpointers):
			best_tag_id = bptrs_t[best_tag_id]
			best_path.append(best_tag_id)
		# Pop off the start tag (we dont want to return that to the caller)
		start = best_path.pop()
		assert start == self.tag_to_ix[self.START_TAG]  # Sanity check
		best_path.reverse()
		return path_score, best_path

	def neg_log_likelihood(self, sentence, tags):
		feats = self._get_lstm_features(sentence)
		forward_score = self._forward_alg(feats)
		gold_score = self._score_sentence(feats, tags)
		return forward_score - gold_score

	def forward(self, sentence):  # dont confuse this with _forward_alg above.
		# Get the emission scores from the BiLSTM
		lstm_feats = self._get_lstm_features(sentence)

		# Find the best path, given the features.
		score, tag_seq = self._viterbi_decode(lstm_feats)
		return score, tag_seq
class lstmCRF_pytorch():
	def __init__(self,HIDDEN_DIM = 10,epoche=10,lr=0.1, weight_decay=1e-4,cuda=True):
		self.START_TAG = -1
		self.STOP_TAG = -2
		self.HIDDEN_DIM = 4
		self.epoche=epoche
		self.lr=lr
		self.weight_decay=weight_decay
		self.cuda=cuda
	def fit(self,x,y,verbose=2,batch=None):
		if batch==None:
			self.batch=len(x) ### una volta sola
		else:
			self.batch=batch
		#x=[[[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0]],[[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0]]]
		#y=[[1,1,0,0,1,1,0,0,1,1],[0,0,1,1,0,0,1,1,0,0,1,1,0,0]]
		#training_data=[(x[0],y[0]),(x[1],y[1])]

		model = BiLSTM_CRF( self.HIDDEN_DIM,n_features=len(x[0][0]),cuda=self.cuda)
		#optimizer = optim.SGD(model.parameters(), lr=self.lr, weight_decay=self.weight_decay)
		optimizer = optim.Adam(model.parameters(), lr = 0.01)
		for epoch in range(self.epoche):
			if verbose>=2:
				print('starting epoch',epoch)
			cont=0
			for i in range(len(x)):
				if verbose>=3:
					print('\tstarting protein',i,'/',len(x))
				sentence, tags=(x[i],y[i])
				# Step 1. Remember that Pytorch accumulates gradients.
				# We need to clear them out before each instance

				# Step 2. Get our inputs ready for the network, that is,
				# turn them into Variables of word indices.
				if self.cuda:
					sentence_in = autograd.Variable(torch.Tensor(sentence)).cuda() #prepare_sequence(sentence, word_to_ix)
					targets = torch.LongTensor(tags).cuda() 
				else:
					sentence_in = autograd.Variable(torch.Tensor(sentence)) #prepare_sequence(sentence, word_to_ix)
					targets = torch.LongTensor(tags) 
				#print targets
				# Step 3. Run our forward pass.
				neg_log_likelihood = model.neg_log_likelihood(sentence_in, targets)

				#s+=float(neg_log_likelihood)
				# Step 4. Compute the loss, gradients, and update the parameters by
				# calling optimizer.step()
				neg_log_likelihood.backward()
				if self.batch==cont or cont==len(x)-2: #batch di 1==cont0
					#neg_log_likelihood.backward()
					optimizer.step()
					model.zero_grad()
					print('\t',neg_log_likelihood)
				cont+=1
				#print 
		# Check predictions after training
		self.model=model
		#precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
	def decision_function(self,x):
		y_pred=[]
		for i in x:
			if self.cuda:
				y_pred+=[list(self.model(autograd.Variable(torch.Tensor(i).cuda()))[1])]
			else:
				y_pred+=[list(self.model(autograd.Variable(torch.Tensor(i)))[1])]
		assert len(y_pred)==len(x)
		for i in range(len(y_pred)):
			assert len(y_pred[i])==len(x[i])
		return y_pred
		# We got it!



class LSTMTagger(nn.Module):

	def __init__(self, n_features,hidden_dim,cuda=False):
		super(LSTMTagger, self).__init__()
		self.hidden_dim = hidden_dim
		self.cuda=cuda
		# The LSTM takes word embeddings as inputs, and outputs hidden states
		# with dimensionality hidden_dim.
		if self.cuda:
			self.lstm = nn.LSTM(n_features, hidden_dim).cuda()
			self.lstm1 = nn.LSTM(hidden_dim, hidden_dim).cuda()
			self.lstm2 = nn.LSTM(hidden_dim, hidden_dim).cuda()
			self.lstm3 = nn.LSTM(hidden_dim, hidden_dim).cuda()
			self.sig=nn.Sigmoid()
			self.pooling=MaxPool1d(hidden_dim).cuda()
		else:
			self.lstm = nn.LSTM(n_features, hidden_dim)
			self.lstm1 = nn.LSTM(hidden_dim, hidden_dim)
			self.sig=nn.Sigmoid()
			self.pooling=MaxPool1d(hidden_dim)
			# The linear layer that maps from hidden state space to tag space
		self.hidden = self.init_hidden()
		self.hidden1 = self.init_hidden()
		self.hidden2 = self.init_hidden()
		self.hidden3 = self.init_hidden()
	def init_hidden(self):
		# Before we've done anything, we dont have any hidden state.
		# Refer to the Pytorch documentation to see exactly
		# why they have this dimensionality.
		# The axes semantics are (num_layers, minibatch_size, hidden_dim)
		if self.cuda:
			return (autograd.Variable(torch.zeros(1, 1, self.hidden_dim).cuda()),autograd.Variable(torch.zeros(1, 1, self.hidden_dim).cuda()))
		else:
			return (autograd.Variable(torch.zeros(1, 1, self.hidden_dim)),autograd.Variable(torch.zeros(1, 1, self.hidden_dim)))


	def forward(self, sentence):

		lstm_out, self.hidden = self.lstm(sentence.view(len(sentence), 1, -1), self.hidden)
		lstm_out, self.hidden=self.lstm1(lstm_out, self.hidden1)
		#lstm_out, self.hidden=self.lstm2(lstm_out, self.hidden2)
		#lstm_out, self.hidden=self.lstm3(lstm_out, self.hidden3)
		lstm_out=self.sig(lstm_out)

		tag_space=self.pooling(lstm_out)
		#tag_scores = F.log_softmax(tag_space)
		#print tag_space.view(len(sentence), 1)
		#raw_input()
		return tag_space.view(len(sentence),1)
class nn1(nn.Module):

	def __init__(self, n_features,hidden_dim=10,cuda=False):
		super(nn1, self).__init__()
		self.cuda=cuda
		if self.cuda:
			self.net = nn.Sequential(
								nn.Linear(n_features, hidden_dim),
								nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								#nn.Linear(hidden_dim, hidden_dim),
								#nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								#nn.Linear(hidden_dim, hidden_dim),
								#nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim,1),
								nn.Sigmoid()
								).cuda()
		else:
			self.net = nn.Sequential(nn.Linear(n_features, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim,1).
								nn.Sigmoid()
								)
	def forward(self, sentence):
		#print sentence
		
		#print sentence.view(len(sentence),-1)

		out=self.net(sentence.view(len(sentence), -1))

		return out
class gru1(nn.Module):

	def __init__(self, n_features,hidden_dim=10,cuda=False):
		super(gru1, self).__init__()
		self.cuda=cuda
		self.hidden_dim=hidden_dim
		if self.cuda:
			self.net = nn.Sequential(
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								#nn.Linear(hidden_dim, hidden_dim),
								#nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								#nn.Linear(hidden_dim, hidden_dim),
								#nn.ReLU(),
								#nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim,1),
								nn.Sigmoid()
								).cuda()
								
			
			
		else:
			self.net = nn.Sequential(nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim, hidden_dim),
								nn.ReLU(),
								nn.BatchNorm1d(hidden_dim),
								nn.Linear(hidden_dim,1).
								nn.Sigmoid()
								)
		self.hidden = self.init_hidden()
		self.gru=nn.GRU(n_features,hidden_dim,bidirectional=True).cuda()
		self.pooling=nn.MaxPool1d(2)
	def init_hidden(self):
		if self.cuda:
			return autograd.Variable(torch.randn(2, 1, self.hidden_dim)).cuda().float()
		else:
			return (autograd.Variable(torch.randn(2, 1, self.hidden_dim )),autograd.Variable(torch.randn(2, 1, self.hidden_dim // 2)) )

	def forward(self, sentence):
		#print sentence
		out=[]
		#print sentence.view(len(sentence),-1)
		for sen in sentence:
			a= sen.view(len(sen), 1, -1).float()
			#print a
			#print self.hidden
			gru_out,hidden=self.gru(a, self.hidden)
			#print gru_out
			gru_out=self.pooling(gru_out)
			#print gru_out
			#raw_input()
			gru_out.view(len(gru_out), -1)
			out+=[self.net(gru_out.view(len(gru_out), -1))]
		return out
class lstm_pytorch():
	def __init__(self,HIDDEN_DIM = 10,epoche=10,lr=0.1, weight_decay=1e-4,cuda=False):
		self.epoche=epoche
		self.lr=lr
		self.weight_decay=weight_decay
		self.cuda=cuda
		self.HIDDEN_DIM = 4
	def fit(self,x,y,verbose=2,batch=None):
		if batch==None:
			self.batch=len(x) ### una volta sola
		else:
			self.batch=batch
		model = LSTMTagger(n_features=len(x[0][0]), hidden_dim=self.HIDDEN_DIM,cuda=self.cuda)
		#optimizer = optim.SGD(model.parameters(), lr=self.lr, weight_decay=self.weight_decay)
		optimizer = optim.Adam(model.parameters(), lr = 0.5)
		loss_function = BCELoss()
	
		p=[]
		for i in  model.parameters():
			p+= list(i.data.cpu().numpy().flat)
		print('number of parameters=',len(p))
		
		for epoch in range(self.epoche):
			if verbose>=2:
				sys.stdout.write('starting epoch'+str(epoch)+' ')
				
			loss_tot=[]
			cont=0
			model.zero_grad()
			for i in range(len(x)):
				if verbose>=3:
					print('\tstarting protein',i,'/',len(x))
				sentence, tags=(x[i],y[i])
				if self.cuda:
					sentence_in = autograd.Variable(torch.Tensor(sentence)).cuda() #prepare_sequence(sentence, word_to_ix)
					targets = autograd.Variable(torch.FloatTensor(tags)) .cuda() 
				else:
					sentence_in = autograd.Variable(torch.Tensor(sentence)) #prepare_sequence(sentence, word_to_ix)
					targets =  autograd.Variable(torch.FloatTensor(tags)) 
				tag_scores = model(sentence_in)
				
				model.hidden = model.init_hidden()

				targets=targets.view(len(targets),1)

				loss = loss_function(tag_scores, targets.view(len(targets),-1))
				loss.backward()
				loss_tot+=[float(loss.cpu().data.numpy().flat[0])]
				
				#print loss
			
			optimizer.step()
			model.zero_grad()
			sys.stdout.write( ' '+str(np.mean(loss_tot))+'\n')

		self.model=model
		#precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
	def decision_function(self,x):
		y_pred=[]
		for i in x:
			if self.cuda:
				a=list(self.model(autograd.Variable(torch.Tensor(i).cuda())).data.cpu().numpy().flat)

				y_pred+=[a]
			else:
				a=list(self.model(autograd.Variable(torch.Tensor(i))).data.numpy().flat)

				y_pred+=[a]
		assert len(y_pred)==len(x)
		
		for i in range(len(y_pred)):

			assert len(y_pred[i])==len(x[i])
		return y_pred
		# We got it!
class nn_pytorch():
	def __init__(self,HIDDEN_DIM = 30,epoche=100,lr=0.001, weight_decay=1e-4,batch=5,cuda=True,name=None):
		self.epoche=epoche
		self.lr=lr
		self.weight_decay=weight_decay
		self.cuda=cuda
		self.HIDDEN_DIM=HIDDEN_DIM
		self.batch=batch
		self.name=name
	def fit(self,x,y,verbose=2,batch=None):
		if batch==None:
			self.batch=len(x) ### una volta sola
		else:
			self.batch=batch
		model = gru1(n_features=len(x[0][0]), hidden_dim=self.HIDDEN_DIM,cuda=self.cuda)
		#optimizer = optim.SGD(model.parameters(), lr=self.lr, weight_decay=self.weight_decay)
		optimizer = optim.Adam(model.parameters())
		loss_function = BCELoss()
	
		p=[]
		for i in  model.parameters():
			p+= list(i.data.cpu().numpy().flat)
		print('number of parameters=',len(p))
		cont=1
		verbose=2
		for epoch in range(self.epoche):
			model.zero_grad()
			sentence_in=[]
			if verbose>=2:
				sys.stdout.write('starting epoch'+str(epoch)+' ')
				
			loss_tot=[]
			
			model.zero_grad()
			
			if verbose>=3:
				print('\tstarting protein',i,'/',len(x))
			sentence, tags=(x,y)
			targets=[]
			if self.cuda:
				for i in sentence:
					sentence_in += [autograd.Variable(torch.Tensor(i)).cuda()] #prepare_sequence(sentence, word_to_ix)
				for i in tags:
					targets += [autograd.Variable(torch.FloatTensor(i)).cuda()]
			else:
				sentence_in = autograd.Variable(torch.Tensor(sentence)) #prepare_sequence(sentence, word_to_ix)
				targets =  autograd.Variable(torch.FloatTensor(tags)) 
			tag_scores = model(sentence_in)
			a=[]
			for i in range(len(tag_scores)):
				true=targets[i].view(len(targets[i]),1)
				a+=[loss_function(tag_scores[i], true)]
			
			loss =torch.mean(torch.stack(a))
			
			loss_tot+=[float(loss.cpu().data.numpy().flat[0])]
			cont+=1
			
			loss.backward()
			optimizer.step()
			sys.stdout.write( ' '+str(np.mean(loss_tot))+'\n')
			if epoch%20==0 and epoch !=0:
				if self.name!= None:
					torch.save(model,'/home/scimmiacasa/Dropbox/modelli_disordine/'+self.name+'_gru80_'+str(epoch)+'_epochs.mtorch')
				else:
					torch.save(model,'/home/scimmiacasa/Dropbox/modelli_disordine/gru80_'+str(epoch)+'_epochs.mtorch')
		self.model=model
		#precheck_sent = prepare_sequence(training_data[0][0], word_to_ix)
		torch.save(model.cpu(),'gru80_final.mtorch')
	def load_model(self,fil):
		self.model=torch.load(fil,map_location={'cuda:0': 'cpu'})
	def decision_function(self,x):
		y_pred=[]
		#self.model=torch.load('gru80_final.mtorch',map_location={'cuda:0': 'cpu'})
		for i in x:
			a=list(self.model([autograd.Variable(torch.Tensor(i).float())])[0].data.cpu().numpy().flat)
			y_pred+=[a]
		assert len(y_pred)==len(x)
		
		for i in range(len(y_pred)):

			assert len(y_pred[i])==len(x[i])
		return y_pred
if __name__ == '__main__':
		x=[[[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0]],[[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0]]]
		y=[[1,1,0,0,1,1,0,0,1,1],[0,0,1,1,0,0,1,1,0,0,1,1,0,0]]
		a=nn_pytorch(epoche=30,cuda=True)
		#a.fit(x,y,batch=1)
		print(a.decision_function([[[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0],[1,1,1],[0,0,0],[1,0,1],[1,0,0]]]))
