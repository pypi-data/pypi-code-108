import dagsim.base as ds 
import numpy as np 
from scipy.special import expit as sigmoid


def func_x2(x0, x1):
	x2 = np.random.binomial(1, sigmoid(2 * x0 + 3 * x1)) * 1.0
	return x2


def func_x3(x0, x2):
	x3 = np.random.binomial(1, sigmoid(1 * x0 + 1 * x2)) * 1.0
	return x3


Node_x0 = ds.Node(name='x0', function=np.random.normal, kwargs={'loc': 0, 'scale': 1})
Node_x1 = ds.Node(name='x1', function=np.random.normal, kwargs={'loc': 0, 'scale': 1})
Node_x2 = ds.Node(name='x2', function=func_x2, kwargs={'x0': Node_x0, 'x1': Node_x1})
Node_x3 = ds.Node(name='x3', function=func_x3, kwargs={'x0': Node_x0, 'x2': Node_x2})

listNodes = [Node_x0, Node_x1, Node_x2, Node_x3]
graph = ds.Graph('myGraph', listNodes) 
data = graph.simulate(4)