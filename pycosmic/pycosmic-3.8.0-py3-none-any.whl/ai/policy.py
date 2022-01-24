import numpy as np 

def greedyPolicy(env_,state_,epsilon,Q_table):
	if np.random.uniform(0,1) < epsilon:
		return env_.action_space.sample()
	else:
		return np.argmax(Q_table[state_,:])