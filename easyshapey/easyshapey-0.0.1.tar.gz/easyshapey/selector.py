#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 17:06:57 2017

@author: caganze
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Selector(object):
	"""
	A selecting tool for different shapes
	"""
	def __init__(self):
		self._logic=None
		self._data=None
		self._shapes=None
		self.logic=None
		
	def __repr__(self):
		return 'Selector with data len {}'.format(len(self))
	
	def __len__(self):
		if self._data is None:
			return 0
		else:
			return len(self.data)
        
	def __add__(self, other_selector):
		
		"allows the creation of a larger selector"
		if len(self)==0 or len(other_selector)==0 :
			return Selector()
		else:
			shapes=self.shapes+other_selector.shapes
			#data=functools.reduce(lambda left,right: pd.merge(left,right), [self.data,	 other_selector.data])
			data=pd.concat([self.data,	other_selector.data])
			New=Selector()
			New.data=data
			New.shapes=shapes
	
			if (self._logic is None) or	 (other_selector.logic is None):
				New.logic=None
	
			if (self._logic == 'and') and  (other_selector.logic =='and'):
				New.logic='and'
	
			if (self._logic == 'or') or	 (other_selector.logic =='or'):
				New.logic='or'
	
			ids=None
			if New.logic=='and':
				ids=set.intersection(*map(set,[list(self.data.index),	 list(other_selector.data.index)]))
		
			if New.logic=='or':
				ids=set().union(*[list(self.data.index),	 list(other_selector.data.index)])
			
			New.data=data.ix[ids]
			return New
	
	@property 
	def data(self):
		"""
		data
		"""
		return self._data
		
	@data.setter
	def data(self, new_data):
		self._data=new_data
	
	@property 
	def logic(self):
		"""
		logic
		"""
		return self._logic
		
	@logic.setter
	def logic(self, new_logic):
		self._logic=new_logic
	
	@property
	def shapes(self):
		return self._shapes
	
	@shapes.setter
	def shapes(self, new_shapes):
		self._shapes=new_shapes
		data= np.array([s.data for s in self.shapes])
		#print ('concatenating ....')
	
		if isinstance(data, list) and isinstance(data[0], pd.DataFrame):
			data=pd.concat(data).reset_index(drop=True)
			data.columns=['x', 'y']
			self._data=data

		#if the input is a nested list of numpy arrays
		if isinstance(data, (np.ndarray, np.generic)) and isinstance(data[0], (np.ndarray, np.generic)):
			#transform this into one dataframe
			#concatenate all the lists and create a numpy array
			data=np.concatenate(data).T
			x=data[:, 0]
			y=data[:, 1]
			#print ('x', x)
			data=pd.DataFrame(np.array([x, y])).transpose()
			data.columns=['x', 'y']
			self._data=data

		if isinstance(data, (np.ndarray, np.generic)) and isinstance(data[0], float):
			data=pd.DataFrame(np.array([data[0], data[1]])).transpose()
			data.columns=['x', 'y']
			self._data=data

		
	def select(self, **kwargs):
		"""
		shapes is a dictionary
		kwargs: pandas dataframe
		"""
		shapes=kwargs.get('shapes', self.shapes)
		_logic=kwargs.get('logic', self._logic)
		if not isinstance(_logic, str) or _logic not in ['and', 'or']:
			raise ValueError(""" Logic must 'and' or 'or' """)
		
		#print ('creating points ....')
		
		#points=list(data.apply(tuple, axis=1))
    
		selected=[]
		#print(data)
		#print ('selecting ....')
		
		for s in shapes:
			selected.append(list(s.select(self.data).index))

		result=None
		result_index=None
		
		#print(selected)
		#print (type(selected))

		if _logic =='and':
			result_index=set.intersection(*map(set,selected))
		if _logic=='or':
			result_index=set().union(*selected)
		
		result=self.data.ix[result_index].drop_duplicates()
		
		
		return result
		
		