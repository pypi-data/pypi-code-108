import numpy as np
import torch
from collections import deque
import random


class ReplayBuffer:
    # initialize the Replay buffer
    # Fix the seed for random sampling through the Replay Buffer
    # Batch size defines number of samples drawn at each learning operation
    # buffer is the actual buffer
    def __init__(
        self,
        buffer_size,
        num_state_variables,
        state_variable_sizes,
        batch_size,
        seed=0,
        device=None,
    ):
        assert (num_state_variables) == len(
            state_variable_sizes
        ), "The provided number of state variables and the provided dimensions differ"
        self.batch_size = batch_size
        self.buffer_size = buffer_size
        self.num_state_variables = num_state_variables
        self.state_variable_sizes = state_variable_sizes
        # determine the size of the state buffers

        # initialize a full buffer - store all parts apart from each other for faster sampling
        self.states = [0 for _ in range(num_state_variables)]
        self.next_states = [0 for _ in range(num_state_variables)]
        for i, variable_size in enumerate(state_variable_sizes):
            dimension = tuple([buffer_size] + list(variable_size))
            self.states[i] = np.zeros(dimension)
            self.next_states[i] = np.zeros(dimension)

        self.actions = np.zeros(buffer_size)
        self.rewards = np.zeros(buffer_size)
        self.dones = np.zeros(buffer_size)
        # buffer counter
        self.counter = 0
        self.filled = False
        # use only numpys random
        self.seed = np.random.seed(seed)

        # if no external device is give, use CPU
        if device == None:
            self.device = torch.device("cpu")
        else:
            self.device = device

    # add samples to the buffer
    # transfer the done value to an integer
    # we assume, that a state is given through several parts, so you always need to provide a list
    def add(self, state, action, reward, next_state, done):
        assert (
            len(state) == self.num_state_variables
        ), "Provided state did not contain all state variables"
        assert (
            len(next_state) == self.num_state_variables
        ), "Provided next_state did not contain all state variables"

        # transformation to integer
        if done:
            done_value = 1
        else:
            done_value = 0

        # fill buffer
        for i, (state_variable, next_state_variable) in enumerate(
            zip(state, next_state)
        ):
            self.states[i][self.counter] = state_variable
            self.next_states[i][self.counter] = next_state_variable

        self.actions[self.counter] = action
        self.rewards[self.counter] = reward
        self.dones[self.counter] = done_value

        # increase counter (and reset, if nessary)
        self.counter += 1
        if self.counter == self.buffer_size:
            self.counter = self.counter % self.buffer_size
            self.filled = True

    # sample from the database
    # the samples later need to be split into tensors of each part of the samples
    # thus, collects a sample and writes every part of the sample in the corresponding list
    # afterwards transforms this lists into tensors and returns them
    def sample(self):
        sample_ids = np.random.randint(0, self.__len__(), self.batch_size)
        states = [0 for _ in range(self.num_state_variables)]
        next_states = [0 for _ in range(self.num_state_variables)]
        for i in range(self.num_state_variables):
            tmp = self.states[i][tuple([sample_ids])]
            states[i] = torch.from_numpy(tmp).float().to(self.device)
            tmp = self.next_states[i][tuple([sample_ids])]
            next_states[i] = torch.from_numpy(tmp).float().to(self.device)

        actions = self.actions[tuple([sample_ids])]
        rewards = self.rewards[tuple([sample_ids])]
        dones = self.dones[tuple([sample_ids])]

        # next state and state have already been transformed
        actions = torch.from_numpy(actions).long().to(self.device)
        rewards = torch.from_numpy(rewards).float().to(self.device)
        dones = torch.from_numpy(dones).float().to(self.device)
        return [states, actions, rewards, next_states, dones]

    # depending on whether the buffer is completely filled or whether is still about to be filled
    def __len__(self):
        if self.filled:
            return self.buffer_size
        else:
            return self.counter
