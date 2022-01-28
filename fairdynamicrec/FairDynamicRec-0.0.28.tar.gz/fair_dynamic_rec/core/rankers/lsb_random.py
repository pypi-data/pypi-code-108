import numpy as np
from .linear_submodular_bandit import LSB
from .random import Random

class LSBRandom(LSB):
    def __init__(self, config, dataObj, parameters=None):
        super(LSBRandom, self).__init__(config, dataObj, parameters)
        self.initial_randomization_round = int(parameters['initial-randomization-round']['value'])
        self.random_ranker = Random(config, dataObj, None)

    def get_ranking(self, batch_users, round=None):
        if round < self.initial_randomization_round:
            return self.random_ranker.get_ranking(batch_users, round)
        else:
            return super(LSBRandom, self).get_ranking(batch_users, round) #self.get_ranking(batch_users, round)

    def update(self, batch_users, rankings, clicks, round=None):
        if round < self.initial_randomization_round:
            return self.random_ranker.update(batch_users, rankings, clicks, round)
        else:
            return super(LSBRandom, self).update(batch_users, rankings, clicks, round) #self.update(batch_users, rankings, clicks, round)