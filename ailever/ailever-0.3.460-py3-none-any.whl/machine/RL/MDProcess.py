import numpy as np
from copy import deepcopy
from gym.envs.toy_text import discrete


class MDP(discrete.DiscreteEnv):
    r"""
    Args:
        actions:
        grid:
 
    Examples:
        >>> import numpy as np
        >>> from ailever.machine.RL import MDP
        >>> ...
        >>> actions = {'a':0, 'b':1, 'c':2, 'd':3}
	>>> observation = {}
	>>> observation['grid'] = (3, 3)
        >>> ...
        >>> agent = lambda state : np.random.randint(low=0, high=4)
	>>> mdp = MDP(actions, observation['grid'])
        >>> mdp.reset()
        >>> ...
        >>> step = 0
        >>> while True:
        >>>     mdp.render(step)
        >>>     state = mdp.s
        >>>     ...
        >>>     action = agent(state)
        >>>     next_state, reward, done, info = mdp.step(action); step += 1
        >>>     ...
        >>>     if step == 10:
        >>>         observables = {'reward':reward, 'done':done}
        >>>         mdp.observe(step, observables)
        >>>     if done : break
        >>> ...
        >>> mdp.memory

    Attributes:
        reset: (*method*) **return**
        step: (*method*) **return** 
        render: (*method*) **return** 
        observe: (*method*) **return** 

    Examples:
        >>> from ailever.machine.RL import MDP
        >>> ...
	>>> mdp = MDP({'a':0, 'b':1, 'c':2, 'd':3}, (3,3))
        >>> mdp.PTensor
        >>> mdp.RTensor
        >>> mdp.nS
        >>> mdp.nA
        >>> mdp.S
        >>> mdp.A
        >>> mdp.memory
        >>> mdp.s
        >>> mdp.observation_space
        >>> mdp.action_space

    Attributes:
        PTensor: (*variable*) Transition Probability
        RTensor: (*variable*) Reward
        nS: (*variable*) Number of States
        nA: (*variable*) Number of Actions
        S: (*variable*) State Function Space
        A: (*variable*) Action Function Space
        memory: (*variable*) Observation Results
        s: (*variable*) Current State
        observation_space: (*variable*) Observation Space
        action_space: (*variable*) Action Space

    .. note::
        MDP = <S,A,P,R>
            - S : State Space
            - A : Action Space
            - P : Transition Probability
            - R : Reward

    """

    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self, actions, grid):
        nA = len(actions)
        nS = np.prod(grid)
        isd = np.ones(nS) / nS                      # Initial state distribution is uniform

        self.A = np.arange(nA)                      # self.A : Action Function Space
        self.S = np.arange(nS)                      # self.S : State Function Space
        self.PTensor = np.zeros(shape=(nA, nS, nS)) # self.PTensor : Transition Probability
        self.RTensor = np.zeros(shape=(nS, nA))     # self.RTensor : Reward
        
        # P[state][action] = [(probabilty, ProcessCore(state, action), reward(state, action), termination_query(ProcessCore(state, action)))]
        P = self.__update(actions, grid, nS)
        super(MDP, self).__init__(nS, nA, P, isd)
        self.memory = dict()


    def __update(self, actions, grid, nS):
        def ProcessCore(state, action=None):
            new_state = state + action
            if new_state < nS-1:
                return new_state
            else:
                new_state = nS-1
                return new_state

        def termination_query(state):
            return state == 0 or state == (nS - 1)

        def reward(state, action=None):
            if termination_query(state) : return 0.0 
            else : return -1.0

        # P[state][action] = (prob, next_state, reward, is_done)
        P = {}
        grid_array = np.empty(grid)
        it = np.nditer(grid_array, flags=['multi_index'])
        while not it.finished:
            state = it.iterindex
            P[state] = {} 
            for action in self.A:
                new_state = ProcessCore(state, action)
                P[state][action] = [(1.0, new_state, reward(state, action), termination_query(new_state))]
            it.iternext()

        for state in P.keys():
            for action in P[state].keys():
                prob, new_state, reward, done = P[state][action][0]
                self.PTensor[action, state, new_state] = prob
                self.RTensor[state, action] = reward

        return P

    def render(self, step, mode='human', verbose=False):
        if verbose : return
        print(f'\n[ STEP : {step} ]')
        print(f'- Current State : {self.s}')

    def observe(self, step, observables=dict()):
        assert isinstance(observables, dict), 'Your observables must be dict type.'

        observations = {}
        observations['Current State'] = deepcopy(self.s)
        
        for key, observable in observables.items():
            observations[key] = deepcopy(observable)

        self.memory[step] = observations

