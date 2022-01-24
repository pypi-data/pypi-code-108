import unittest

import numpy as np
from sklearn.cluster import KMeans


class TestCluster(unittest.TestCase):
    def test_kmeans(self):
        n_query = 3
        test_x = np.array([[1, 2], [1, 4], [1, 0], [2, 2], [4, 2], [5, 7], [6, 4], [10, 2], [10, 4], [10, 0]])
        kmeans = KMeans(n_clusters=n_query).fit(test_x)
        cluster_id_list = kmeans.predict(test_x)
        centers = kmeans.cluster_centers_[cluster_id_list]
        distance = (test_x - centers) ** 2
        distance = distance.sum(axis=1)
        query_ids = np.array(
            [np.arange(test_x.shape[0])[cluster_id_list == i][distance[cluster_id_list == i].argmax()] for i in
             range(n_query)])


if __name__ == '__main__':
    unittest.main()
