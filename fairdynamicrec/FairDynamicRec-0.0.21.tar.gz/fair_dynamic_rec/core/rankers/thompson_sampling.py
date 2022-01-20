import numpy as np
from .abstract_ranker import AbstractRanker


# Segment-based Thompson Sampling strategy, with Beta(alpha_zero,beta_zero) priors
class ThompsonSampling(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):
        super(ThompsonSampling, self).__init__(config, dataObj)
        # self.user_segment = user_segment
        # n_segments = len(np.unique(self.user_segment))
        self.ranking_display = np.zeros((dataObj.n_users, dataObj.n_items))
        self.ranking_success = np.zeros((dataObj.n_users, dataObj.n_items))
        self.alpha = float(parameters["alpha"]["value"])
        self.beta = float(parameters["beta"]["value"])
        # self.t = 0
        # self.cascade_model = cascade_model

    def get_ranking(self, batch_users, round=None):
        # user_segment = np.take(self.user_segment, batch_users)
        user_displays = np.take(self.ranking_display, batch_users, axis = 0).astype(float)
        user_success = np.take(self.ranking_success, batch_users, axis = 0)
        user_score = np.random.beta(self.alpha + user_success, self.beta + user_displays - user_success)
        user_choice = np.argsort(-user_score)[:, :self.config.list_size]
        # Shuffle l_init first slots
        # np.random.shuffle(user_choice[0:l_init])
        return user_choice

    def update(self, batch_users, rankings, clicks, round=None):
        batch_size = len(batch_users)
        for i in range(batch_size):
            # user_segment = self.user_segment[user_ids[i]]
            # total_stream = len(rewards[i].nonzero())
            nb_display = 0
            for r, c in zip(rankings[i], clicks[i]):
                nb_display += 1
                self.ranking_success[batch_users[i]][r] += c
                self.ranking_display[batch_users[i]][r] += 1
                # if self.cascade_model and ((total_stream == 0 and nb_display == l_init) or (r == 1)):
                #     break
        return