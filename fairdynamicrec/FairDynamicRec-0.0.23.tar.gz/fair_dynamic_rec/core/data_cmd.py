import numpy as np
import pickle as pk
from datetime import datetime
import pandas as pd
from fair_dynamic_rec.core.util.utils import get_dict_key_from_value

class DataCmd:
    """
    Load the data files
    """

    def __init__(self, config, log_filename=None):
        # key: originalid, value: mappedid
        self.userid_mapped_data = {}
        self.itemid_mapped_data = {}
        self.supplierid_mapped_data = {}

        self.user_attribute_mapped_data = {}
        self.item_topic_mapped_data = {}

        # key: category (e.g. genre), value: integer index
        self.topic_mapped_data = {}

        self.rating_file_path = config.get_rating_file_path()
        self.train_file_path = config.get_train_file_path()
        self.test_file_path = config.get_test_file_path()
        self.user_file_path = config.get_user_file_path()
        self.item_file_path = config.get_item_file_path()
        self.supplier_file_path = config.get_supplier_file_path()

        self.load_data_from_text_file(config)

        self.n_users = self.ratings.shape[0] if self.ratings is not None else self.train_data.shape[0]
        self.n_items = self.ratings.shape[1] if self.ratings is not None else self.train_data.shape[1]

        self.feature_data = self.load_features(config)
        self.save_item_features(config)

    # def read_rating_as_pandas_dataframe(self, file_path, separator):
    #     return pd.read_csv(file_path, sep=separator, names=['userid', 'itemid', 'rating'], header=None)

    def read_rating_text_file(self, file_path, delimiter):
        data = np.array(np.zeros((1, 1)))
        user_index, item_index = 0, 0
        with open(file_path) as f:
            for instance in f:
                instance_separated = instance.strip().split(delimiter)
                userid = instance_separated[0]
                itemid = instance_separated[1]
                rating = instance_separated[2]

                # map userid and itemid, and update the dictionary
                if userid not in self.userid_mapped_data.keys():
                    self.userid_mapped_data[userid] = user_index
                    user_index += 1
                if itemid not in self.itemid_mapped_data.keys():
                    self.itemid_mapped_data[itemid] = item_index
                    item_index += 1

                # update the data by appending the new data instance to the data matrix
                if (data.shape[0] - 1) < self.userid_mapped_data[userid]:
                    data = np.append(data, np.zeros((1, data.shape[1])), axis=0)
                if (data.shape[1] - 1) < self.itemid_mapped_data[itemid]:
                    data = np.append(data, np.zeros((1, data.shape[0])).transpose(), axis=1)

                data[self.userid_mapped_data[userid], self.itemid_mapped_data[itemid]] = rating

        return data
    def read_train_test_text_file(self, train_path, test_path, train_delimiter, test_delimiter):
        train_df = pd.read_csv(train_path, names=['userid', 'itemid', 'rating'], sep='\t')
        test_df = pd.read_csv(test_path, names=['userid', 'itemid', 'rating'], sep='\t')

        n_users = len(set(list(train_df.userid.unique()) + list(test_df.userid.unique())))
        # n_items = len(set(train_df.itemid.unique()) & set(test_df.itemid.unique()))
        n_items = len(set(list(train_df.itemid.unique()) + list(test_df.itemid.unique())))

        train_data = np.zeros((n_users, n_items))
        with open(train_path) as f:
            for instance in f:
                instance_separated = instance.strip().split(train_delimiter)
                userid = instance_separated[0]
                itemid = instance_separated[1]
                rating = instance_separated[2]

                if userid not in self.userid_mapped_data.keys():
                    self.userid_mapped_data[userid] = len(self.userid_mapped_data)
                if itemid not in self.itemid_mapped_data.keys():
                    self.itemid_mapped_data[itemid] = len(self.itemid_mapped_data)

                train_data[self.userid_mapped_data[userid], self.itemid_mapped_data[itemid]] = rating

        test_data = np.zeros((n_users, n_items))
        with open(test_path) as f:
            for instance in f:
                instance_separated = instance.strip().split(test_delimiter)
                userid = instance_separated[0]
                itemid = instance_separated[1]
                rating = instance_separated[2]

                if userid not in self.userid_mapped_data.keys():
                    self.userid_mapped_data[userid] = len(self.userid_mapped_data)
                if itemid not in self.itemid_mapped_data.keys():
                    self.itemid_mapped_data[itemid] = len(self.itemid_mapped_data)

                test_data[self.userid_mapped_data[userid], self.itemid_mapped_data[itemid]] = rating
        return train_data, test_data
    # def read_test_text_file(self, file_path, delimiter):
    #     data = np.zeros((self.train_data.shape))
    #     user_index, item_index = 0, 0
    #     with open(file_path) as f:
    #         for instance in f:
    #             instance_separated = instance.strip().split(delimiter)
    #             userid = instance_separated[0]
    #             itemid = instance_separated[1]
    #             rating = instance_separated[2]
    #
    #             # map userid and itemid, and update the dictionary
    #             # if userid not in self.userid_mapped_data.keys():
    #             #     self.userid_mapped_data[userid] = user_index
    #             #     user_index += 1
    #             # if itemid not in self.itemid_mapped_data.keys():
    #             #     self.itemid_mapped_data[itemid] = item_index
    #             #     item_index += 1
    #
    #             # update the data by appending the new data instance to the data matrix
    #             # if (data.shape[0] - 1) < self.userid_mapped_data[userid]:
    #             #     data = np.append(data, np.zeros((1, data.shape[1])), axis=0)
    #             # if (data.shape[1] - 1) < self.itemid_mapped_data[itemid]:
    #             #     data = np.append(data, np.zeros((1, data.shape[0])).transpose(), axis=1)
    #
    #             if itemid not in self.itemid_mapped_data.keys():
    #                 self.itemid_mapped_data[itemid] = len(self.itemid_mapped_data)
    #             data[self.userid_mapped_data[userid], self.itemid_mapped_data[itemid]] = rating
    #
    #     return data
    def read_user_text_file(self, file_path, delimiter):
        data = np.array(np.zeros((len(self.userid_mapped_data.keys()), 1)))
        feature_index = 0
        with open(file_path) as f:
            for instance in f:
                instance_separated = instance.strip().split(delimiter)
                userid = instance_separated[0]
                feature = instance_separated[1]

                # map user feature, and update the dictionary
                if feature not in self.user_attribute_mapped_data.keys():
                    self.user_attribute_mapped_data[feature] = feature_index
                    feature_index += 1

                # update the data by appending the new data instance to the data matrix
                if (data.shape[1] - 1) < self.user_attribute_mapped_data[feature]:
                    data = np.append(data, np.zeros((1, data.shape[0])).transpose(), axis=1)

                data[self.userid_mapped_data[userid], self.user_attribute_mapped_data[feature]] = 1

        return data
    def read_item_text_file(self, file_path, delimiter, category_column, category_delimiter):
        # file format: itemid, categories
        data = np.array(np.zeros((len(self.itemid_mapped_data.keys()), 1)))
        category_index = 0
        with open(file_path) as f:
            for instance in f:
                instance_separated = instance.strip().split(delimiter)
                itemid = instance_separated[0]
                categories = instance_separated[category_column].split(category_delimiter)

                for category in categories:
                    # map categories, and update the dictionary
                    if category not in self.item_topic_mapped_data.keys():
                        self.item_topic_mapped_data[category] = category_index
                        category_index += 1

                    # update the data by appending the new data instance to the data matrix
                    if (data.shape[1] - 1) < self.item_topic_mapped_data[category]:
                        data = np.append(data, np.zeros((1, data.shape[0])).transpose(), axis=1)
                    if itemid in self.itemid_mapped_data.keys():
                        data[self.itemid_mapped_data[itemid], self.item_topic_mapped_data[category]] = 1

        # Adding category "unknown" to the dictionary to be assigned to the items with no category
        col_sum = data.sum(axis=1)
        if data[col_sum == 0].size != 0:
            self.item_topic_mapped_data['unknown'] = category_index
            data = np.append(data, np.zeros((1, data.shape[0])).transpose(), axis=1)
            data[col_sum == 0, category_index] = 1 # equivalent to data[col_sum == 0, -1] = 1

        return data
    def read_supplier_text_file(self, file_path, delimiter):
        # file format: supplierid, itemid
        data = np.array(np.zeros((len(self.itemid_mapped_data.keys()), 1)))
        supplier_index = 0
        with open(file_path) as f:
            for instance in f:
                instance_separated = instance.strip().split(delimiter)
                itemid = instance_separated[1]
                supplierid = instance_separated[0]

                # map categories, and update the dictionary
                if supplierid not in self.supplierid_mapped_data.keys():
                    self.supplierid_mapped_data[supplierid] = supplier_index
                    supplier_index += 1

                # update the data by appending the new data instance to the data matrix
                if (data.shape[1] - 1) < self.supplierid_mapped_data[supplierid]:
                    data = np.append(data, np.zeros((1, data.shape[0])).transpose(), axis=1)

                if itemid in self.itemid_mapped_data.keys():
                    data[self.itemid_mapped_data[itemid], self.supplierid_mapped_data[supplierid]] = 1

        return data[:, np.where(sum(data) > 0)[0]]

    def load_data_from_text_file(self, config):
        self.ratings, self.train_data, self.test_data, self.user_data, self.item_data, self.supplier_data = None, None, None, None, None, None
        if self.rating_file_path is not None:
            self.ratings = self.read_rating_text_file(self.rating_file_path, config.get_rating_data_delimiter())
        if config.get_splitter_model() == 'giventraintest':
            # self.train_data = self.read_rating_text_file(self.train_file_path, config.get_train_data_delimiter())
            # self.test_data = self.read_test_text_file(self.test_file_path, config.get_test_data_delimiter())
            self.train_data, self.test_data = self.read_train_test_text_file(self.train_file_path, self.test_file_path, config.get_train_data_delimiter(), config.get_test_data_delimiter())

        if self.user_file_path is not None:
            self.user_data = self.read_user_text_file(self.user_file_path, config.get_user_data_delimiter())
        if self.item_file_path is not None:
            self.item_data = self.read_item_text_file(self.item_file_path, config.get_item_data_delimiter(), config.get_item_data_category_column(), config.get_item_data_category_delimiter())
        if self.supplier_file_path is not None:
            self.supplier_data = self.read_supplier_text_file(self.supplier_file_path, config.get_supplier_data_delimiter())

        self.sample_rating_by_active_user_item(config)
        self.binarize_rating_data(config)
        if config.get_splitter_model() == 'splittraintest':
            self.train_data, self.test_data = self.split_rating_data(self.ratings, config.get_splitter_model_traintest_ratio(), config.seed)

        self.save_data_as_txt_file(config)

        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ": Data loaded.")

    def sample_rating_by_active_user_item(self, config):
        # Get the most active users and most popular items
        if config.get_sampling_model() == 'active_user_item':
            F_idx = np.argsort(np.count_nonzero(self.ratings, axis=0))[-config.max_item:]
            self.ratings = self.ratings[:, F_idx]
            if hasattr(self, 'item_data'):
                if self.item_data is not None:
                    self.item_data = self.item_data[F_idx, :]
            if hasattr(self, 'supplier_data'):
                if self.supplier_data is not None:
                    self.supplier_data = self.supplier_data[F_idx, :]
                    self.supplier_data = self.supplier_data[:, np.where(sum(self.supplier_data) > 0)[0]]
            u_idx = np.argsort(np.count_nonzero(self.ratings, axis=1))[-config.max_user:]
            self.ratings = self.ratings[u_idx, :]
            if hasattr(self, 'user_data'):
                if self.user_data is not None:
                    self.user_data = self.user_data[u_idx, :]
        elif config.get_sampling_model() == 'active_user':
            u_idx = np.argsort(np.count_nonzero(self.ratings, axis=1))[-config.max_user:]
            self.ratings = self.ratings[u_idx, :]
            if hasattr(self, 'user_data'):
                if self.user_data is not None:
                    self.user_data = self.user_data[u_idx, :]
    def binarize_rating_data(self, config):
        binarize, threshold = config.get_data_binarization()
        if binarize:
            for u in range(self.ratings.shape[0]):
                for i in range(self.ratings.shape[1]):
                    self.ratings[u, i] = int(self.ratings[u, i]) > threshold
    def split_rating_data(self, rating_data, ratio, seed):
        train_data = np.zeros(rating_data.shape)
        test_data = np.zeros(rating_data.shape)
        np.random.seed(seed=seed)
        for u in range(rating_data.shape[0]):
            u_vec = rating_data[u]
            index_ones = np.asarray(np.where(u_vec != 0))[0]
            np.random.shuffle(index_ones)
            train_size = int(len(index_ones) * ratio)
            test_data[u][index_ones[:train_size]] = rating_data[u][index_ones[:train_size]]
            train_data[u][index_ones[train_size:]] = rating_data[u][index_ones[train_size:]]
        return train_data, test_data
    def save_data_as_txt_file(self, config):
        save_data, train_file_name, test_file_name = config.get_save_txt_data_info()
        if save_data:
            f = open(config.get_data_path() / train_file_name, "w")
            for u in range(self.train_data.shape[0]):
                # items = np.asarray(np.where(self.train_data[u] == 1))[0]
                items = np.asarray(np.where(self.train_data[u] > 0))[0]
                for j in range(len(items)):
                    f.write(str(list(self.userid_mapped_data.keys())[list(self.userid_mapped_data.values()).index(u)]) + "\t" + str(list(self.itemid_mapped_data.keys())[list(self.itemid_mapped_data.values()).index(items[j])]) + "\t" + str(self.train_data[u, items[j]]) + "\n")
            f.close()

            f = open(config.get_data_path() / test_file_name, "w")
            for u in range(self.test_data.shape[0]):
                items = np.asarray(np.where(self.test_data[u] > 0))[0]
                # items = np.asarray(np.where(self.test_data[u] == 1))[0]
                for j in range(len(items)):
                    f.write(str(list(self.userid_mapped_data.keys())[list(self.userid_mapped_data.values()).index(u)]) + "\t" + str(list(self.itemid_mapped_data.keys())[list(self.itemid_mapped_data.values()).index(items[j])]) + "\t" + str(self.test_data[u, items[j]]) + "\n")
            f.close()
    def save_data_as_pkl_file(self, config):
        save_data, file_name = config.get_save_pkl_data_info()
        if save_data:
            save_obj = {'R': self.ratings, 'U': self.user_data, 'I': self.item_data, 'S': self.supplier_data}
            with open(config.get_data_path() / file_name, 'wb') as f:
                pk.dump(save_obj, f)
#
#
#
#
#     config = ConfigCmd(config_file, target, log_filename)
#     print(target)
#     if config.is_valid():
#         # config.load_libraries()
#         config.process_config()
#     # else:
#     #     raise InvalidConfiguration("Configuration file load error", "There was an error loading the configuration file.")
#     return config

    def get_topical_features(self):
        def __w(F, G):
            w = np.zeros(G.shape)
            FG = np.dot(F, G)
            # total number of clicks received by an item
            FG[FG > 1] = 1
            w_den = np.sum(FG, axis=0)
            # total number of clicks received by a topic
            w_num = np.sum(F, axis=0)

            for i in range(G.shape[0]):
                j = np.where(G[i])[0]
                try:
                    w[i, j] = w_num[i] / w_den[j]
                except RuntimeWarning:
                    w[i, j] = 0
            # Now compute theta
            FG = np.dot(F, G)
            theta = np.zeros((F.shape[0], G.shape[1]))
            # numerator is actually FG
            for i in range(theta.shape[0]):
                theta[i] = FG[i] / (np.sum(FG[i]) + 1e-10)
            return w, theta

        train_item_topical_features, train_user_topical_features = __w(self.train_data, self.item_data)
        # train_item_topical_features = train_item_topical_features / np.linalg.norm(train_item_topical_features, axis=1)[:, np.newaxis]
        # train_user_topical_features = train_user_topical_features / np.linalg.norm(train_user_topical_features, axis=1)[:, np.newaxis]
        test_item_topical_features, test_user_topical_features = __w(self.test_data, self.item_data)
        # test_item_topical_features = test_item_topical_features / np.linalg.norm(test_item_topical_features, axis=1)[:, np.newaxis]
        # test_user_topical_features = test_user_topical_features / np.linalg.norm(test_user_topical_features, axis=1)[:, np.newaxis]

        return {"train_item_topical_features": train_item_topical_features, "train_user_topical_features": train_user_topical_features, "test_item_topical_features": test_item_topical_features, "test_user_topical_features": test_user_topical_features}
    def get_latent_features_by_SVD(self, latent_feature_dim, latent_feature_normalize):
        """
        Get the feature and mu from MovieLense based on SVD.
        F = USV, features: SV from training, mu U from testing
        :param f_name: file name
        :param train_percentage:
        :param max_user:
        :param max_item:
        :param d: number of eigenvalue
        :param seed:
        :return:
        """

        u, s, v = np.linalg.svd(self.train_data)
        train_item_features = v[:latent_feature_dim, :].T * s[:latent_feature_dim]
        if latent_feature_normalize:
            train_item_features = train_item_features / (np.linalg.norm(train_item_features, axis=1)[:, np.newaxis] + 1e-10)
            train_item_features = train_item_features / np.sqrt(2)
        train_user_features = u[:, :latent_feature_dim]

        u, s, v = np.linalg.svd(self.test_data)
        test_item_features = v[:latent_feature_dim, :].T * s[:latent_feature_dim]
        if latent_feature_normalize:
            test_item_features = test_item_features / (np.linalg.norm(test_item_features, axis=1)[:, np.newaxis] + 1e-10)
            test_item_features = test_item_features / np.sqrt(2)
        test_user_features = u[:, :latent_feature_dim]

        return {"train_item_latent_features": train_item_features, "train_user_latent_features": train_user_features,
                "test_item_latent_features": test_item_features, "test_user_latent_features": test_user_features}
    def get_latent_features_by_SVD_LeastSquare(self, latent_feature_dim, latent_feature_normalize):
        """
        Get the feature and mu from MovieLense based on SVD.
        F = USV, features: SV from training, mu U from testing
        :param f_name: file name
        :param train_percentage:
        :param max_user:
        :param max_item:
        :param d: number of eigenvalue
        :param seed:
        :return:
        """

        u, s, v = np.linalg.svd(self.train_data)
        # u, s, v = np.linalg.svd(self.train_data, full_matrices=False)
        # u, s, v = svds(self.train_data, k=10)
        train_item_features = v[:latent_feature_dim, :].T * s[:latent_feature_dim]
        if latent_feature_normalize:
            train_item_features = train_item_features / (np.linalg.norm(train_item_features, axis=1)[:, np.newaxis] + 1e-10)
            train_item_features = train_item_features / np.sqrt(2)
        # Y = F_test
        #### Y = F_test.sum(axis=0) / F_test.shape[0]

        """
        attraction_prob = item_feature.T * user_feature
        user_feature = item_covariance_matrix_inverse * (item_feature * attraction_prob)
        attraction_prob: test_data 
        """
        item_covariance_matrix_inverse = np.linalg.inv(train_item_features.T.dot(train_item_features))
        B = train_item_features.T.dot(self.test_data.T)
        test_user_features = np.dot(item_covariance_matrix_inverse, B)

        return {"train_item_latent_features": train_item_features, "test_user_latent_features": test_user_features.T}

    def load_features(self, config):
        data_features = {}
        if self.train_data is not None and self.test_data is not None:
            data_features = self.get_latent_features_by_SVD_LeastSquare(config.get_latent_feature_dim(), config.normalize_latent_feature())
        if hasattr(self, 'item_data'):
            if self.item_data is not None:
                topical_features = self.get_topical_features()
                data_features = dict(list(topical_features.items()) + list(data_features.items()))
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ": Feature data created.")
        return data_features
        # data_features = {}
        # derivation_type = config.get_features_derivation_type()
        # if 'latent' in derivation_type:
        #     data_features = self.get_latent_features_by_SVD(config.get_latent_feature_dim())
        # if 'topical' in derivation_type:
        #     topical_features = self.get_topical_features()
        #     data_features = dict(list(topical_features.items()) + list(data_features.items()))
        #
        # return data_features
    def save_item_features(self, config):
        if config.save_item_features():
            with open(config.get_data_path() / 'train_item_latent_features.txt', 'w') as f:
                for i in range(self.feature_data['train_item_latent_features'].shape[0]):
                    f.write(str(get_dict_key_from_value(self.itemid_mapped_data, i)) + "\t" + ",".join(map(str, self.feature_data['train_item_latent_features'][i,:])) + "\n")
            if 'train_item_latent_features' in self.feature_data:
                with open(config.get_data_path() / 'train_item_topical_features.txt', 'w') as f:
                    for i in range(self.feature_data['train_item_topical_features'].shape[0]):
                        f.write(str(get_dict_key_from_value(self.itemid_mapped_data, i)) + "\t" + ",".join(map(str, self.feature_data['train_item_topical_features'][i, :])) + "\n")