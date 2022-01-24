import numpy as np 
import pickle 


class SARSA:
	def __init__(self,policy,env,state_size,action_size,alpha=0.85,gamma=0.95,epsilon=0.9):
		self.env =env 
		self.state_size = state_size
		self.action_size = action_size
		self.gamma = gamma
		self.alpha = alpha
		self.Q_table = np.zeros((self.state_size,self.action_size))
		self.epsilon = epsilon
		self.loaded_model =None
		self.policy = policy

	def learn(self,max_episodes=1000,avg=False):

		rewards = []

		for i in range(max_episodes):
			state = self.env.reset()
			done = False

			while not done:

				action = self.policy(self.env,state,self.epsilon,self.Q_table)

				next_state,reward,done,info = self.env.step(action)


				action_ = self.policy(self.env,state,self.epsilon,self.Q_table)

				self.Q_table[state,action] += self.alpha * (reward + self.gamma * (self.Q_table[next_state,action_] - self.Q_table[state,action]))

				state = next_state 
				action = action_

				rewards.append(reward )

				if done:
					print('Episode :  {} Reward : {}'.format(i,reward))
					break 

		if avg == True:
			print('Average Reward Score :', np.mean(rewards))

	def get_Q(self):
		return self.Q_table


	def save_model(self,filename):
		with open(filename+'.pkl','wb') as f:
			pickle.dump(self.Q_table,f)
		print('Model saved ')

	def load_model(self,filename):
		model =  pickle.load(open(filename,'rb'))
		self.loaded_model = model 
		return model 
	def predict(self,state):
		actions = self.action_size
		values = np.argmax(self.loaded_model[state,:] )
		return values 








