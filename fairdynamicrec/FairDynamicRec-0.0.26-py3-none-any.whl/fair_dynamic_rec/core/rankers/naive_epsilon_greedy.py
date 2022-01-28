import numpy as np
from .abstract_ranker import AbstractRanker

# Segment-based Epsilon-Greedy strategy: recommends playlists randomly with probability epsilon,
# otherwise recommends the top n_recos with highest mean observed rewards.
class NaiveEpsilonGreedy(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):
        super(NaiveEpsilonGreedy, self).__init__(config, dataObj)
        # self.user_segment = user_segment
        # n_segments = len(np.unique(self.user_segment))
        self.ranking_display = np.zeros((dataObj.n_users, dataObj.n_items))
        self.ranking_success = np.zeros((dataObj.n_users, dataObj.n_items))
        self.ranking_score = np.ones((dataObj.n_users, dataObj.n_items))
        self.epsilon = float(parameters["epsilon"]["value"])
        # self.cascade_model = cascade_model

    def get_ranking(self, batch_users, round=None):
        # user_segment = np.take(self.user_segment, batch_users)
        user_scores = np.take(self.ranking_score, batch_users, axis = 0)
        user_random_score = np.random.random(user_scores.shape)
        n_users = len(batch_users)
        user_greedy = np.random.binomial(1, [1- self.epsilon for i in range(n_users)])
        new_scores = user_scores * user_greedy[:,np.newaxis]
        user_choice = np.lexsort((user_random_score, -new_scores))[:, :self.config.list_size]
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
                nb_display +=1
                self.ranking_success[batch_users[i]][r] += c
                self.ranking_display[batch_users[i]][r] += 1
                self.ranking_score[batch_users[i]][r] = self.ranking_success[batch_users[i]][r] / self.ranking_display[batch_users[i]][r]
                # if self.cascade_model and ((total_stream == 0 and nb_display == l_init) or (r == 1)):
                #     break
        return