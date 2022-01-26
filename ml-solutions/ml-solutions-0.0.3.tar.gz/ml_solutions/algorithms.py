'''
All the custom ML Algorithms of this package are written here
'''
import numpy as np

class ModelNotTrained(Exception):
    '''
    This exception will be raised if you are prediction without training the model
    '''
    def __init__(self, *args: object):
        super(ModelNotTrained, self).__init__(*args)

class HLRegression():
    '''
    Similar to Linear Regression
    '''
    def __init__(self, learning_rate=0.001, epochs=1000):
        self.lr = learning_rate
        self.n_iters = epochs
        self.weights = None
        self.bias = None
        self.X = None
        self.Y = None
        self.model_trained = False

    def train_model(self, X, Y):
        x, y = np.array(X), np.array(Y)
        try:
            n_samples, n_features = x.shape
        except:
            n_samples = x.shape
            n_features = 1

        self.weights = np.zeros(n_features)
        self.bias = 0

        for _ in range(self.n_iters):
            y_predicted = np.dot(X, self.weights) + self.bias

            if n_samples < 7:
                dw = (1/n_samples) * np.dot(X.T, (y_predicted - y))
                db = (1/n_samples) * np.sum(y_predicted - y)
            else:
                dw = (7/n_samples) * np.dot(X.T, (y_predicted - y))
                db = (1/n_samples) * np.sum(y_predicted - y)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db
        
        self.X = x
        self.Y = y
        self.model_trained = True

    def predict(self, X):
        if self.model_trained == False:
            raise ModelNotTrained('You can not predict without training the model!')
        else:
            y_predicted = np.dot(X, self.weights) + self.bias
            return y_predicted

    def mean_squared_error(self, y_true, y_predicted):
        return np.mean((y_true - y_predicted) ** 2)

    def mean_absolute_error(self, y_true, y_predicted):
        return np.mean((y_true - y_predicted))