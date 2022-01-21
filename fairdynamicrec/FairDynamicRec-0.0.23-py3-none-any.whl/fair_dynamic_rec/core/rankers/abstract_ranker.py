import numpy as np

"""
The base class of all rankers. 
"""
class AbstractRanker():
    def __init__(self, config, dataObj):
        self.config= config
        self.dataObj = dataObj
        self.rankers = config.get_ranker_params()



    @staticmethod
    def get_features_for_optimal_ranker(config, dataObj):
        if config.full_feature:
            return np.concatenate((dataObj.feature_data['test_user_latent_features'], dataObj.feature_data['test_user_topical_features']), axis=1), np.concatenate((dataObj.feature_data['test_item_latent_features'], dataObj.feature_data['test_item_topical_features']), axis=1)
        elif config.optimal_ranker == 'naive_relevance' or config.optimal_ranker == 'sigmoid_relevance':
            return dataObj.feature_data['test_user_latent_features'], dataObj.feature_data['train_item_latent_features']
        elif config.optimal_ranker == 'topical_coverage':
            return dataObj.feature_data['test_user_topical_features'], dataObj.feature_data['test_item_topical_features']
        elif config.optimal_ranker == 'hybrid':
            item_full_feature = np.zeros((dataObj.feature_data['train_item_latent_features'].shape[0], dataObj.feature_data['train_item_latent_features'].shape[1] + dataObj.feature_data['train_item_topical_features'].shape[1]))
            item_full_feature[:, :dataObj.feature_data['train_item_topical_features'].shape[1]] = dataObj.feature_data['train_item_topical_features']
            item_full_feature[:, dataObj.feature_data['train_item_topical_features'].shape[1]:] = dataObj.feature_data['train_item_latent_features']
            user_full_feature = np.zeros((dataObj.feature_data['test_user_latent_features'].shape[0], dataObj.feature_data['test_user_latent_features'].shape[1] + dataObj.feature_data['test_user_topical_features'].shape[1]))
            for i in range(user_full_feature.shape[0]):
                user_full_feature[i,:] = np.concatenate(((1 - float(config.lmbda)) * dataObj.feature_data['test_user_topical_features'][i,:], float(config.lmbda) * dataObj.feature_data['test_user_latent_features'][i,:]))
            return user_full_feature, item_full_feature

    @staticmethod
    def ranking_coverage(s):
        """
        Return the coverage of an list s for topics. Eq 2 of Nips-11
        :param s: ranked list s in (0, 1), n by d numpy ndarray
        :return:
        """
        s = np.asarray(s) if type(s) is list else s
        return 1 - np.prod(1 - s, axis=0)

    @staticmethod
    def conditional_coverage(x, coverage):
        """
        Return the coverage of an item given the current ranking
        Based on Eq. 2 and Eq. 3 of NIPS11
        :param x: coverage of this item
        :param coverage: topic covergate of previous items
        :return: conditional coverage of x given ranking
        """
        x = np.asarray(x)
        coverage = np.asarray(coverage)
        return 1 - np.multiply(1 - x, 1 - coverage) - coverage