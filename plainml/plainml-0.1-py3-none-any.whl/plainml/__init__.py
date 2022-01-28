import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.datasets import *
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

class Model:
    def __init__(self, data=None, target=None,features=[],model=None):
        if model != None:
            self.model = model
        else:
            raise Exception('Model cannot be None')
        
        self.data = data
        self.target = target
        self.features = features

    def fit(self):
        self.model.fit(self.data, self.target)
    
    def predict(self, data):
        return self.model.predict(data)
    
    def score(self, data, target):
        return self.model.score(data, target)
    
    def save(self,file_name='model.pkl'):
        joblib.dump(self, file_name)

class LinearModel(Model):
    def __init__(self, data, target):
        super().__init__(data, target, model=LinearRegression())

    def plot(self):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.show()

    def plot_score(self):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.show()
        print('Score: ', self.score())

    def plot_score_with_test_data(self, test_data, test_target):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.scatter(test_data, test_target)
        plt.plot(test_data, self.model.predict(test_data), color='green')
        plt.show()
        print('Score: ', self.score())

class LogisticModel(Model):
    def __init__(self, data, target):
        super().__init__(data, target, model=LogisticRegression())

    def plot(self):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.show()

    def plot_score(self):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.show()
        print('Score: ', self.score())

    def plot_score_with_test_data(self, test_data, test_target):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.scatter(test_data, test_target)
        plt.plot(test_data, self.model.predict(test_data), color='green')
        plt.show()
        print('Score: ', self.score())

class KnnModel(Model):
    def __init__(self, data, target, k=3):
        super().__init__(data, target, model=KNeighborsClassifier(n_neighbors=k))

    def plot(self):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.show()

    def plot_score(self):
        plt.scatter(self.data, self.target)
        plt.plot(self.data, self.model.predict(self.data), color='red')
        plt.show()
        print('Score: ', self.score())

    def plot_score_with_test_data(self, test_data, test_target):
        plt.scatter(test_data, test_target)
        plt.plot(test_data, self.model.predict(test_data), color='green')
        plt.show()
        print('Score: ', self.score())

def load_model(file_name='model.pkl'):
    return joblib.load(file_name)
