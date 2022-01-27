import numpy as np
from .abstract_ranker import AbstractRanker
from math import log
from collections import defaultdict

#  Upper Confidence Bound (UCB) strategy, using KL-UCB bounds [Garivier and Cappe, 2011] tailored for Bernoulli rewards
class KLUCB(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):
        super(KLUCB, self).__init__(config, dataObj)
        # self.user_segment = user_segment
        # n_segments = len(np.unique(self.user_segment))
        self.ranking_display = np.zeros((dataObj.n_users, dataObj.n_items))
        self.ranking_success = np.zeros((dataObj.n_users, dataObj.n_items))
        self.ranking_score = np.ones((dataObj.n_users, dataObj.n_items))
        self.t = 0
        # self.cascade_model = cascade_model
        self.precision = float(parameters["precision"]["value"])
        self.eps = float(parameters["eps"]["value"])

    def get_ranking(self, batch_users, round=None):
        # user_segment = np.take(self.user_segment, batch_users)
        user_score = np.take(self.ranking_score, batch_users, axis = 0)
        # Break ties
        user_random_score = np.random.random(user_score.shape)
        user_choice = np.lexsort((user_random_score, -user_score))[:, :self.config.list_size]
        # Shuffle l_init first slots
        # np.random.shuffle(user_choice[0:l_init])
        return user_choice

    def kl(self, x, y):
        x = min(max(x, self.eps), 1 - self.eps)
        y = min(max(y, self.eps), 1 - self.eps)
        return x * log(x / y) + (1 - x) * log((1 - x) / (1 - y))

    def scoring_function(self, n_success, n, t):
        if n == 0:
            return 1.0
        p = n_success / n
        value = p
        u = 1
        threshold = log(t) / n
        _count_iteration = 0
        while _count_iteration < 50 and u - value > self.precision:
            _count_iteration += 1
            m = (value + u) * 0.5
            if self.kl(p, m) > threshold:
                u = m
            else:
                value = m
        return (value + u) * 0.5

    def update(self, batch_users, rankings, clicks, round=None):
        batch_size = len(batch_users)
        modified_data = defaultdict(set)
        for i in range(batch_size):
            # user_segment = self.user_segment[user_ids[i]]
            # total_stream = len(rewards[i].nonzero())
            nb_display = 0
            for r, c in zip(rankings[i], clicks[i]):
                nb_display +=1
                modified_data[batch_users[i]].add(r)
                self.ranking_success[batch_users[i]][r]+=c
                self.ranking_display[batch_users[i]][r]+=1
                # if self.cascade_model and ((total_stream == 0 and nb_display == l_init) or (r == 1)):
                #     break
        self.t = self.ranking_display.sum()
        for seg,pls in modified_data.items():
            for pl in pls:
                self.ranking_score[seg][pl] = self.scoring_function(self.ranking_success[seg][pl], self.ranking_display[seg][pl], self.t)
        return