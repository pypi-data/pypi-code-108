import imp


import numpy as np

class DeterministicAugmentation:
    def __init__(self, seed: int, num_precomputted: int=100):
        assert isinstance(seed, int)
        self.seed = seed
        np.random.seed(seed)
        self.next_seeds = np.random.randint(0, 1000, size=(num_precomputted, ))
        self.index = 0

    def __call__(self):
        next_seed = self.next_seeds[self.index % len(self.next_seeds)]
        np.random.seed(next_seed)
        self.index += 1
