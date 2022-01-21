import torch as tr

def l1(y, t):
	L = tr.abs(y - t)
	return L
