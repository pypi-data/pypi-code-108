# -*- coding: utf-8 -*-
"""
This subpackage contains functions to help
preprocess raw datasets in the Mental Health Services
Data Set (MHSDS) format in preparation for machine
learning model training and selection or machine learning
prediction on unseen data once a model has been trained. 
It contains tools to load a dataset (or use provided dummy 
data), clean the data, and calculate new variables which
can be used to train the classification models.
"""

from MHDataLearn.preprocessing import load, clean, calculate, process
from MHDataLearn.preprocessing.load import load_data
from MHDataLearn.preprocessing.process import wrangle_data