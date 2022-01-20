import numpy as np
from .abstract_ranker import AbstractRanker

# An Explore-then-Commit strategy: similar to random until each playlist has been displayed n times or more,
# then recommends the top n_reco playlists with highest mean observed rewards, for each segment
class NaiveGreedy(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):
        super(NaiveGreedy, self).__init__(config, dataObj)
        # self.user_segment = user_segment
        # n_segments = len(np.unique(self.user_segment))
        self.ranking_display = np.zeros((dataObj.n_users, dataObj.n_items))
        self.ranking_success = np.zeros((dataObj.n_users, dataObj.n_items))
        self.min_n = int(parameters["min-n"]["value"])
        # self.cascade_model = cascade_model

    def get_ranking(self, batch_users, round=None):
        # user_segment = np.take(self.user_segment, batch_users)
        user_success = np.take(self.ranking_success, batch_users, axis = 0)
        user_displays = np.take(self.ranking_display, batch_users, axis = 0).astype(float)
        user_random_score = np.random.random(user_displays.shape)
        user_score = np.divide(user_success, user_displays, out=np.zeros_like(user_displays), where=user_displays!=0)
        discounted_displays = np.maximum(np.zeros_like(user_displays), self.min_n - user_displays)
        user_choice = np.lexsort((user_random_score, - user_score, -discounted_displays))[:, :self.config.list_size]
        # Shuffle l_init first slots
        # np.random.shuffle(user_choice[0:l_init])
        return user_choice

    def update(self, batch_users, rankings, clicks, round=None):
        batch_size = len(batch_users)
        for i in range(batch_size):
            # user_segment = self.user_segment[batch_users[i]]
            # total_stream = len(rewards[i].nonzero())
            nb_display = 0
            for r, c in zip(rankings[i], clicks[i]):
                nb_display += 1
                self.ranking_success[batch_users[i]][r] += c
                self.ranking_display[batch_users[i]][r] += 1
                # if self.cascade_model and ((total_stream == 0 and nb_display == l_init) or (r == 1)):
                #     break
        return