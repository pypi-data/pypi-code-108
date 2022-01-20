from ._environment import BaseEnvironment

from copy import deepcopy
import numpy as np
import torch
import torch.nn as nn
from torch.distributions.multinomial import Multinomial

class NaiveEnv(BaseEnvironment):
    r"""
    Args:
        actions:
        grid:

    Examples:
        >>> from ailever.machine.RL import NaiveEnv
        >>> from ailever.machine.RL import NaiveAgent
        >>> ...
        >>> actions = {'a':0, 'b':1, 'c':2, 'd':3}
	>>> observation = {}
	>>> observation['grid'] = (3, 3)
        >>> ...
	>>> env = NaiveEnv(actions, observation['grid'])
        >>> #env.set_env(P=None, R=None, termination_states=None)
        >>> ...
        >>> agent = NaiveAgent(env)
        >>> #agent.set_agent(V=None, Q=None, policy=None, epsilon=None, gamma=None)
        >>> agent.macro_update_Q()
        >>> ...
        >>> for epi_cnt in range(1):
        >>>     env.reset(); step = 0
        >>>     while True:
        >>>         action = agent.judge(env.s)
        >>>         next_state, reward, done, info = env.step(action); step += 1
        >>>         env.render(step)
        >>>         if step == 1:
        >>>             observables = {'reward':reward, 'done':done}
        >>>             env.observe(step, epi_cnt, observables)
        >>>         if done : break
        >>> env.memory
        >>> agent.policy
        
    Attributes:
        set_env: (*method*) **return**
        Process: (*method*) **return**
        termination_query: (*method*) **return**
        reward: (*method*) **return**
        reset: (*method*) **return**
        step: (*method*) **return** 
        render: (*method*) **return** 
        observe: (*method*) **return** 
        gymP: (*variable*) Transition Probability

    Examples:
        >>> from ailever.machine.RL import NaiveEnv
        >>> ...
	>>> env = NaiveEnv({'a':0, 'b':1, 'c':2, 'd':3}, (3,3))
        >>> env.P
        >>> env.R
        >>> env.nS
        >>> env.nA
        >>> env.ids
        >>> env.S
        >>> env.A
        >>> env.memory
        >>> env.s

    Attributes:
        P: (*variable*) Transition Probability
        R: (*variable*) Reward
        nS: (*variable*) Number of States
        nA: (*variable*) Number of Actions
        ids: (*variable*) Initial state distribution
        S: (*variable*) State Function Space
        A: (*variable*) Action Function Space
        memory: (*variable*) Observation Results
        s: (*variable*) Current State
    """

    def __init__(self, actions, grid):
        self.grid = grid
        self.nA = torch.tensor(len(actions))
        self.nS = torch.prod(torch.tensor(grid))

        isd_func = nn.Softmax(dim=-1)
        self.isd = torch.ones(self.nS).type(torch.FloatTensor)                
        self.isd = isd_func(self.isd)                   # Initial state distribution is uniform

        self.s = None ; self.reset()                    # self.s : current state
        self.termination_states = [0,self.nS-1]         # self.termination_states : termination states
        self.memory = dict()
        self.A = torch.arange(self.nA)                  # self.A : Action Function Space
        self.S = torch.arange(self.nS)                  # self.S : State Function Space
        self.P = torch.zeros(self.nA, self.nS, self.nS) # self.P : Transition Probability
        self.R = torch.zeros(self.nS, self.nA)          # self.R : Reward
        self._update_PR()
        self._update_gymP()

        self.render_info = dict()
        self.render_info['current_state'] = self.s
        self.render_info['next_state'] = None
        self.render_info['reward'] = self.R[self.s]
        self.render_info['action'] = None

    def _update_PR(self):
        # self.P
        for action in self.A:
            for state in self.S:
                self.P[action,state,:] = self.isd

        # self.R
        self.R = torch.ones(self.nS, self.nA).mul(-1)
        for termination_state in self.termination_states:
            self.R[termination_state, :] = 0

    def _update_gymP(self):
        # P[state][action] = (prob, next_state, reward, is_done)
        P = {}
        grid_array = np.empty(self.grid)
        it = np.nditer(grid_array, flags=['multi_index'])
        while not it.finished:
            state = it.iterindex
            P[state] = {} 
            for action in self.A:
                for new_state in self.S:
                    prob = float(self.P[action, state, new_state])
                    reward = float(self.R[state, action])
                    P[state][action] = [(prob, new_state, reward, self.termination_query(new_state))]
            it.iternext()
        self._gymP = P
        
        """
        for state in P.keys():
            for action in P[state].keys():
                for next_step in P[state][action]:
                    prob, new_state, reward, done = next_step
                    self.P[action, state, new_state] = prob
                    self.R[state, action] = reward
        """
    
    def set_env(self, P=None, R=None, termination_states=None):
        if P is None:
            P = self.P
        if R is None:
            R = self.R
        if termination_states is None:
            termination_states = self.termination_states

        assert P.size() == self.P.size(), 'P shape is not right. Correct the P shape.'
        assert R.size() == self.R.size(), 'R shape is not right. Correct the R shape.'
        assert isinstance(termination_states, list), 'terminations_states must be type of list.'

        self.P = P
        self.R = R
        self.termination_states = termination_states
        self._update_gymP()

        self.render_info = dict()
        self.render_info['current_state'] = self.s
        self.render_info['next_state'] = None
        self.render_info['reward'] = self.R[self.s]
        self.render_info['action'] = None

    @property
    def gymP(self):
        return self._gymP

    def _ProcessCore(self, state, action=False):
        self.render_info['current_state'] = state
        transition = self.P[int(action), state]
        samples = self.sampler(probs=transition)

        self.s = samples.argmax()
        new_state = self.s
        self.render_info['next_state'] = new_state
        return new_state, transition[new_state]
    
    #property
    def Process(self, state, action=False):
        transition = self.P[int(action), state]
        samples = self.sampler(probs=transition)
        new_state = samples.argmax()
        return new_state, transition[new_state]

    def termination_query(self, state):
        if state in self.termination_states:
            return True
        else:
            return False

    def reward(self, state, action=False):
        self.render_info['reward'] = self.R[state]
        self.render_info['action'] = action
        return self.R[state, action]

    def sampler(self, probs=[0.1, 0.9], size=1):
        total_count = 1
        size = torch.Size([size])
        probs = torch.tensor(probs)
        samples = Multinomial(total_count=total_count, probs=probs).sample(sample_shape=size).squeeze()
        return samples

    def reset(self):
        self.s = torch.randint(0, self.nS, (1,)).squeeze()   

    def step(self, action):
        cur_state = self.s
        next_state, prob = self._ProcessCore(cur_state, action)
        reward = self.reward(cur_state, action)
        done = self.termination_query(next_state)
        return (next_state, reward, done, {"prob": prob})

    def render(self, step_cnt, mode=None, verbose=False):
        if verbose : return

        print(f'\n[ STEP : {step_cnt} ]')
        print(f"- Current State({self.render_info['current_state']}) > Next State({self.render_info['next_state']})")
        print(f"- Reward of each actions on the state: {self.render_info['reward']}")
        print(f"  - Choiced Action : {self.render_info['action']}")

    def observe(self, step_cnt, episode_cnt, observables=dict()):
        assert isinstance(observables, dict), 'Your observables must be dict type.'

        observations = {}
        observations['Current State'] = deepcopy(self.s)
        
        for key, observable in observables.items():
            observations[key] = deepcopy(observable)

        self.memory[f'{episode_cnt},{step_cnt}'] = observations


