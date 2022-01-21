import torch as tr

def bce(y, t):
	L = -t * tr.log(y) - (1 - t) * tr.log(1 - y)
	L[~tr.isfinite(L)] = 100
	return L

def sigmoid_bce(y, t):
	y = tr.sigmoid(y)
	return bce(y, t)
