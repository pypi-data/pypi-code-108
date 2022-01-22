import numpy as np
from .abstract_ranker import AbstractRanker

class LSB1(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):
        super(LSB1, self).__init__(config, dataObj)
        self.n_samples = np.zeros(dataObj.n_users)
        self.n_clicks = np.zeros(dataObj.n_users)
        self.dim = self.dataObj.feature_data['train_item_topical_features'].shape[1]
        self.prng = np.random.RandomState(seed=config.seed)
        self.alpha = float(parameters["alpha"]["value"])

        self.sigma = float(parameters["sigma"]["value"])
        # self.t = 1
        # self.seed = seed
        # parameters
        self.ill_matrix_counter = 0
        self.theta = np.ones((self.dataObj.n_users, self.dim))  # d-dimensional
        self.b = np.zeros(self.dim)  # d
        self.M = np.eye(self.dim)  # d by d
        self.MInv = np.eye(self.dim)  # for fast matrix inverse computation, d by d
        # for ill inverse
        self.b_tmp = np.zeros(self.dim)
        self.MInv_tmp = np.zeros((self.dim, self.dim))
        self.batch_features = None

    def get_ranking(self, batch_users):
        """
        :param x: features
        :param k: number of positions
        :return: ranking: the ranked item id.
        delta: the conditional topic coverage of each item. Eq. (3) of NIPS 11 paper.
        """
        # assert x.shape[0] >= k
        rankings = np.zeros((len(batch_users), self.config.list_size), dtype=int)
        self.batch_features = np.zeros((len(batch_users), self.config.list_size, self.dim))
        tie_breaker = self.prng.rand(len(self.dataObj.feature_data['train_item_topical_features']))
        for i in range(len(batch_users)):
            coverage = np.zeros(self.dim)
            ranking = []
            for j in range(self.config.list_size):
                # Line 8 - 11 of Nips 11
                gain_in_topic_coverage = self.conditional_coverage(x=self.dataObj.feature_data['train_item_topical_features'], coverage=coverage)
                cb = self.alpha * np.sqrt(np.multiply(np.dot(gain_in_topic_coverage, self.MInv), gain_in_topic_coverage).sum(axis=1))
                score = np.dot(gain_in_topic_coverage, self.theta[batch_users[i]])
                ucb = score + cb + 1e-6 * tie_breaker

                winner = np.argmax(ucb)
                while winner in ranking:
                    ucb[winner] = -np.inf
                    winner = np.argmax(ucb)

                ranking.append(winner)
                self.batch_features[i][j] = gain_in_topic_coverage[winner]

                coverage = self.ranking_coverage(self.dataObj.feature_data['train_item_topical_features'][ranking])
            rankings[i] = np.asarray(ranking)
        return rankings

    def update(self, batch_users, rankings, clicks):
        for i in range(len(batch_users)):
            _clicks, _batch_features = self.__collect_feedback(clicks, i)

            """
            This is for computing self.theta (Line 3-5 of Alogirthm 1 of NIPS 11)
            For fast matrix inverse, we use Woodbury matrix identity (https://en.wikipedia.org/wiki/Woodbury_matrix_identity)

            Return: self.theta is updated.
            """
            # for the inverse of M, feature matrix
            # x * m^-1 * x^T
            xmx = np.dot(_batch_features, np.dot(self.MInv, _batch_features.T))
            # (1/sigma I + xmx)^-1
            try:
                tmp_inv = np.linalg.inv(1 / self.sigma * np.eye(len(_batch_features)) + xmx)
            except np.linalg.LinAlgError:
                # for the ill matrix. if the matrix is not invertible, we ignore this update
                self.ill_matrix_counter += 1
                return
            # m^-1*x^T
            MInv_xT = self.MInv.dot(_batch_features.T)
            # MInv_xT*tmp_inv*MInv_xT^T
            self.MInv_tmp = np.dot(np.dot(MInv_xT, tmp_inv), MInv_xT.T)
            # MInv - the new part
            self.MInv -= self.MInv_tmp

            self.M += self.sigma * _batch_features.T.dot(_batch_features)

            # for b: feedback
            self.b_tmp = np.dot(_clicks, _batch_features)
            self.b += self.b_tmp

            # for parameter theta
            self.theta[batch_users[i]] = np.dot(self.MInv, self.b)
            # self.theta[self.theta < 0] = 0

            self.n_samples[batch_users[i]] += len(_clicks)
            self.n_clicks[batch_users[i]] += sum(_clicks)

    def __collect_feedback(self, clicks, batch_user_id):
        """
        :param y:
        :return: the last observed position.
        """
        # With  Cascade assumption, only the first click counts.
        if self.config.feedback_model == 'cascade':
            if np.sum(clicks[batch_user_id]) == 0:
                return clicks[batch_user_id], self.batch_features[batch_user_id]
            first_click = np.where(clicks[batch_user_id])[0][0]
            return clicks[batch_user_id][:first_click + 1], self.batch_features[batch_user_id][:first_click + 1]
        elif self.config.feedback_model == 'dcm':
            if np.sum(clicks[batch_user_id]) == 0:
                return clicks[batch_user_id], self.batch_features[batch_user_id]
            last_click = np.where(clicks[batch_user_id])[0][-1]
            return clicks[batch_user_id][:last_click + 1], self.batch_features[batch_user_id][:last_click + 1]
        # all items are observed
        else:
            return clicks[batch_user_id], self.batch_features[batch_user_id]