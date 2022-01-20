import torch as tr
import torch.nn.functional as F

# @brief Negative log likelihood (or categorical cross entropy) of a multi class classifier.
def nll(y, t):
	# Negative log-likeklihood (used for softmax+NLL for classification), expecting targets are one-hot encoded
	t = t.type(tr.bool)
	L = (-tr.log(y[t] + 1e-5))
	L[~tr.isfinite(L)] = 100
	return L

# @brief NLL, but applies softmax to outputs before calling the main loss function.
def softmax_nll(y, t, dim=-1):
	y = F.softmax(y, dim=dim)
	return nll(y, t)
