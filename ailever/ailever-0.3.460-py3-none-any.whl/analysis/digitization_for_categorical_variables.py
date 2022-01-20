import pandas as pd

import torch
import torch.nn as nn
from torch import optim
from torch.utils.data import Dataset



class CategoricalDataset(Dataset):
    def __init__(self, X):
        self.device = 'cpu'
        X = X.value_counts(ascending=False)
        self.target = torch.from_numpy(X.values).type(torch.float)
        self.target = (self.target - self.target.mean())/self.target.std(unbiased=False)
        self.dataset = torch.arange(X.shape[0]).reshape(-1,1)
        
    def __len__(self):
        return self.dataset.size()[0]

    def __getitem__(self, idx):
        x_item = self.dataset[idx, :].to(self.device)
        y_item = self.target[idx].to(self.device)
        return x_item, y_item
    
class QuantifyingModel(nn.Module):
    def __init__(self, training_information):
        super(QuantifyingModel, self).__init__()
        self.training_information = training_information
        self.latent_feature = None
        
        self.embedding = nn.Embedding(self.training_information['NumUnique'], 100)
        self.superficial_linear1 = nn.Linear(100, self.training_information['NumFeature'])
        self.latent_linear = nn.Linear(self.training_information['NumFeature'], self.training_information['NumFeature'])
        self.superficial_linear2 = nn.Linear(self.training_information['NumFeature'], 100)
        self.pdf_layer = nn.Linear(100, 1)        
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        
        nn.init.xavier_uniform_(self.superficial_linear1.weight)
        nn.init.xavier_uniform_(self.latent_linear.weight)
        nn.init.xavier_uniform_(self.superficial_linear2.weight)
        
    def forward(self, x, generate=False):
        x = self.superficial_linear1(self.embedding(x)).reshape(1,-1)
        x = self.latent_linear(self.relu(x))
        
        if generate:
            self.feature_generator(x)

        x = self.superficial_linear2(self.relu(x))
        x = self.pdf_layer(self.relu(x)).squeeze()
        return x

    def feature_generator(self, x):
        if self.latent_feature is None:
            self.latent_feature = x.detach().clone()
        else:
            self.latent_feature = torch.cat((self.latent_feature, x.detach().clone()), dim=0)

class Criterion(nn.Module):
    def __init__(self):
        super(Criterion, self).__init__()
        self.mse = nn.MSELoss()

    def forward(self, hypothesis, target):
        return self.mse(hypothesis, target)


AdamaxOptimizer = optim.Adamax


