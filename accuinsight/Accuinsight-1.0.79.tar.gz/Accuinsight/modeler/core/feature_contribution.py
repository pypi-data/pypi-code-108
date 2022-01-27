import shap
import re
import numpy as np
from collections import OrderedDict
from Accuinsight.modeler.core import ModelType


def as_array(dat):
    if 'ndarray' not in str(type(dat)):
        dat = np.array(dat)

    return dat


def get_model_name(model):
    model_name = str(model)
    
    if '<' and '>'in model_name:
        model_name = re.sub('<', '', model_name)
        model_name = re.sub('>', '', model_name)
        model_name = model_name.split('.')[0]
    elif '(' and ')' in model_name:
        model_name = model_name.split('(')[0]
        
    return model_name


def shap_value(model, dat, feature_name):
    dat = as_array(dat)
        
    if feature_name is None:                               
        feature_name = ['feature_' + str(i + 1) for i in range(dat.shape[1])]
    
    model_name = get_model_name(model)
    if 'tensorflow' in str(model):
        explainer = shap.DeepExplainer(model, dat)
    elif model_name in ModelType.Tree_type_2:
        explainer = shap.TreeExplainer(model)
    elif model_name in ModelType.Tree_type_1:
        explainer = shap.TreeExplainer(model, dat)
    elif model_name in ModelType.Linear:
        explainer = shap.LinearExplainer(model, dat)
    else:
        explainer = shap.KernelExplainer(model, dat)
    
    feature_contribution = OrderedDict()
    
    shap_values = explainer.shap_values(dat)
    if type(shap_values) == list:
        shap_values = shap_values[0]
    else:
        pass
    
    if len(feature_name) == shap_values.shape[1]:
        
        for i in range(shap_values.shape[1]):
            feature_contribution[feature_name[i]] = np.mean(np.abs(shap_values[:,i])) 
    else:
        raise ValueError("The dimensions of the train data and the feature name do not match. \nPlease use 'set_feature()' function for setting feature names.")
        
    return dict(feature_contribution)

