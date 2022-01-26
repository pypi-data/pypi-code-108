#packages environment
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gym
from gym import error, spaces, utils
import pandas.testing as tm
import math
from sklearn.linear_model import LogisticRegression
from scipy.stats import truncnorm

#Gym environment - continuous

class UpdateEnv(gym.Env):
  def __init__(self):
    self.size = 2000     

    #set range for action space
    self.high_th = np.array([2, 2, 2])
   
    #set ACTION SPACE
    self.action_space = spaces.Box(
            low = np.float32(-self.high_th),
            high = np.float32(self.high_th))
    
    #set range for obs space    
    self.min_Xas=np.array([0, 0])
    self.max_Xas=np.array([math.inf, math.inf])
    
    #set OBSERVATION SPACE
    #it is made of values for Xa, Xs for each observation
    self.observation_space = spaces.Box(low=np.float32(self.min_Xas),
                                        high=np.float32(self.max_Xas))
        
    #set an initial state
    self.state=None 

    #introduce some length
    self.horizon=200

  def seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return [seed]    

#take an action with the environment
  def step(self, action):
    #MODEL FITTING CYCLE      
    
    #e=0, t=0
    #see patients (from reset function) (Xa(0), Xs(0)), no intervention
    list1 = np.zeros((self.size,self.horizon+1))
    rho_mean=[]
    rho_meanl=[]
    theta_list=[]
    theta_list_l=[]

    #e=0, t=1    
    #see same patients (Xa(1), Xs(1))=(Xa(0), Xs(0)) because no intervention occurred but this only at e=0
    #see Y (not necessary I guess)   
    theta0, theta1, theta2 = action  


    #compute rho
    patients1= np.hstack([np.ones((self.size, 1)), self.patients]) #shape (50, 3), 1st column of 1's, 2nd columns Xs, 3rd column Xa
    rho1 = (1/(1+np.exp(-(np.matmul(patients1, action[:, None])))))  #prob of Y=1  # (sizex3) x (3x1) = (size, 1)
    rho1 = rho1.squeeze() # shape: size, individual risk
    rho1_mean =  np.mean(rho1)

    list1[:,0]=rho1
    rho_mean.append(rho1_mean)
    theta_list.append(action)
    
    for i in range(self.horizon):
      #e=1, t=0
      #see new patients (Xa(0), Xs(0))
      patients2 = truncnorm.rvs(a=0, b= math.inf,size=(self.size,2)) #shape (size, 2), 1st columns is Xs, second is Xa
      Xa = patients2[:, 1] # shape: size
      #apply intervention and use rho from previous episode. g(rho_{e-1}, Xa(0))
      g2 = ((Xa) + 0.5*((Xa)+np.sqrt(1+(Xa)**2)))*(1-list1[:,i]**2) + ((Xa) - 0.5*((Xa)+np.sqrt(1+(Xa)**2)))*(list1[:,i]**2)
    
      #e=1, t=1
      #update Xa(0) to Xa(1) with intervention. Xa(1)=g(rho_{e-1}, Xa(0))
      Xa = g2 # size
      Y = np.random.binomial(1, 0.2, (self.size, 1))
      patients3 = np.hstack([Y, np.reshape(patients2[:, 0], (self.size,1)), np.reshape(Xa, (self.size,1))]) #Y, Xs, Xa
      model2 = LogisticRegression().fit(patients3[:, 1:3], np.ravel(patients3[:, 0].astype(int)))
      #compute rho by fitting model
      thetas2 = np.array([model2.intercept_[0], model2.coef_[0,0] , model2.coef_[0,1]]) #thetas2[0]: intercept; thetas2[1]: coef for Xs, thetas2[2] coef for Xa
      patients4 = np.hstack([np.ones((self.size, 1)), patients3[:, 1:3]]) #1, Xs, Xa
      rho3 = (1/(1+np.exp(-(np.matmul(patients4, thetas2[:, None])))))  #prob of Y=1 # (sizex3) x (3x1) = (size, 1)
      rho3=rho3.squeeze() 
      rho3_mean =  np.mean(rho3)
  
      list1[:, i+1]=rho3
      rho_mean.append(rho3_mean)  
      theta_list.append(thetas2)
      #HERE. should repeat only dynamics of episode 1    
      
    #check if horizon is over, otherwise keep on going
    if rho_mean[-1] >= 0.2:
      done = True
    else:
      done = False
    #set the reward equal to the mean hospitalization rate
    reward = np.mean(rho_mean)
        
    self.state = self.patients[self.random_indices, :].reshape(2,) #not sure if with or without reshape
    
    #set placeholder for infos
    info ={}    
    return self.state, reward, theta_list[0], theta_list[-1], rho_mean[-1], done, {}

#reset state and horizon    
  def reset(self):
    self.horizon = 200
    
    #define dataset of patients with non-actionable covariate Xs and actionable covariate Xa
    self.patients = truncnorm.rvs(a=0, b= math.inf,size=(self.size,2)) #shape (size, 2), 1st columns is Xs, second is Xa
    
       
    self.random_indices = np.random.choice(self.size, size=1, replace=False)
    self.state = self.patients[self.random_indices, :].reshape(2,) 

    
    
    return self.state
