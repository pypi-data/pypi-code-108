#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 21:42:35 2021

@author: hemerson
"""

""" 
environment_base - A template for environments for reinforcement learning agents

"""

import numpy as np

class environment_base:
    def __init__(self):
        """ 
        Each environment must have the following variables: 
            
        self.render - bool (is the environment visualised?)
        self.seed - int (what is the seeding for the environment?)
            
        """
        pass
        
    def reset(self):
        """ 
        Resets the parameters of the learning environment
        
        Inputs:
        --------
        None
        
        Returns:
        ----------
        state - np.float32 (the initialised state of the environment)
        """   
        raise NotImplementedError
        
    def step(self, action=None):
        """ 
        Updates the state of the environment following an action
        
        Inputs:
        --------
        action - np.int32 (the action selected by the agent)
        
        Returns:
        ----------
        state - np.float32 (the next state of the environment)
        reward - float (the reward from taking the action)
        done - bool (if this is the terminal state of the environment)
        info - dict (additional information relating to the environment)
        """   
        raise NotImplementedError
        
    def check_discrete_input(self, input_value):
        """ 
        Checks the player action is in the correct format
        
        Inputs:
        --------
        input - any type
        
        Returns:
        ----------
        None
        """  
        
        # check the input is a numpy array
        valid_numpy = type(input_value) == np.ndarray   
        assert valid_numpy, "The input must be a numpy array."     
        
        # check the input array is 1D
        valid_shape = input_value.ndim == 1
        assert valid_shape, "The input array must be 1D - input is {}D.".format(input_value.ndim) 
        
        # check the input type is correct
        valid_type = issubclass(input_value.dtype.type, np.integer) 
        assert valid_type, "The input must be an integer array."   
        
        # check the length is correct
        valid_length = input_value.shape[0] == self.action_dim
        assert valid_length, "The input must be of length {}".format(self.action_dim) 
        
        # check the values are permittable
        valid_max = np.array_equal(np.minimum(input_value, self.action_num - 1), input_value)
        valid_min = np.array_equal(np.maximum(input_value, np.zeros(self.action_dim)), input_value)
        assert (valid_max and valid_min), "The input must be within the valid range of actions"
        
        
    def sample_discrete_action(self):
        """ 
        Returns a random discrete action
        
        Inputs:
        --------
        None
        
        Returns:
        ----------
        action - np.int32 (a random action from the environment)
        """  
        raise NotImplementedError
        
    def sample_continuous_action(self):
        """ 
        Returns a random continuous action
        
        Inputs:
        --------
        None
        
        Returns:
        ----------
        action - np.float32 (a random action from the environment)
        """  
        raise NotImplementedError

if __name__ == "__main__":  
    
    
    env = environment_base()    
    
    # initialise the number of actions and options per action
    env.action_dim = 2
    env.action_num = np.array([2, 3], dtype=np.int32)
    
    # example of valid array 
    input_val = np.array([1, 2], dtype=np.int32)
    
    # raises not numpy assertion
    # input_val = [32]
    
    # raises not correct shape
    #input_val = np.array([[1.0, 2.0]], dtype=np.float32)
    
    # raises not integer assertion
    # input_val = np.array([1.0, 2.0], dtype=np.float32)
    
    # raise not valid range assertion
    # input_val = np.array([-1.0, 3.0], dtype=np.int32)
    
    # check the input
    env.check_discrete_input(input_val)
        
        
        
        