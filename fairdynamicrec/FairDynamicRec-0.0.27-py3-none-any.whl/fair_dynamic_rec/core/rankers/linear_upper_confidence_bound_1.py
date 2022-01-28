import numpy as np
from .linear_submodular_bandit import LSB

class LinUCB1(LSB):
    def __init__(self, config, dataObj, parameters=None):
        super(LinUCB1, self).__init__(config, dataObj, parameters)
        self.dim = self.dataObj.feature_data['train_item_latent_features'].shape[1]

        # parameters
        self.ill_matrix_counter = 0
        self.theta = np.ones((self.dataObj.n_users, self.dim))  # d-dimensional
        self.b = np.zeros(self.dim)  # d
        self.M = np.eye(self.dim)  # d by d
        self.MInv = np.eye(self.dim)  # for fast matrix inverse computation, d by d
        # for ill inverse
        self.b_tmp = np.zeros(self.dim)
        self.MInv_tmp = np.zeros((self.dim, self.dim))

    def get_ranking(self, batch_users):
        """
        :param x: features
        :param k: number of positions
        :return: ranking: the ranked item id.
        """
        # assert x.shape[0] >= k
        rankings = np.zeros((len(batch_users), self.config.list_size), dtype=int)
        self.batch_features = np.zeros((len(batch_users), self.config.list_size, self.dim))
        tie_breaker = self.prng.rand(len(self.dataObj.feature_data['train_item_latent_features']))
        for i in range(len(batch_users)):
            cb = self.alpha * np.sqrt(np.multiply(np.dot(self.dataObj.feature_data['train_item_latent_features'], self.MInv), self.dataObj.feature_data['train_item_latent_features']).sum(axis=1))
            score = np.dot(self.dataObj.feature_data['train_item_latent_features'], self.theta[batch_users[i]])
            ucb = score + cb
            rankings[i] = np.lexsort((tie_breaker, -ucb))[:self.config.list_size]
            self.batch_features[i] = self.dataObj.feature_data['train_item_latent_features'][rankings[i]]
        return rankings