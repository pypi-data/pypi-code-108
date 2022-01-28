#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  autoenc.py
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
import torch
import torch.autograd as autograd
import torch.nn as nn

import numpy as np
torch.manual_seed(1)
EPOCH=10
class nn_class_autoenc(nn.Module):
		def __init__(self, n_features,hidden_dim=10,cuda=False):
			super(nn_class_autoenc, self).__init__()

			self.encoder = nn.Sequential(
				nn.Linear(n_features, hidden_dim),
				nn.ReLU(),
				nn.Linear(hidden_dim, hidden_dim),
				nn.ReLU(),
				#nn.Linear(hidden_dim, hidden_dim//2),
				#nn.Tanh(),
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
			print(epoch,loss.data.numpy()[0]) 
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
def main(args):
	x=np.random.rand(100,3)
	a=autoencoder()
	a.fit(x)
	v= a.encode(x)
	print(a.decode(v.reshape(len(v),1)))

if __name__ == '__main__':
		import sys
		sys.exit(main(sys.argv))
