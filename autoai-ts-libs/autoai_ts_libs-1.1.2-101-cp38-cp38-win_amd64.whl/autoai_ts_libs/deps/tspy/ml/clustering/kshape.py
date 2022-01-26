#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

from autoai_ts_libs.deps.tspy.data_structures.ml.clustering.KShapeModel import KShapeModel

def fit(multi_time_series, k_clusters, num_runs, use_eigen=True, init_strategy="plusplus"):
    """
    create a time-series-clustering model using the kshape clustering implementation.

    Parameters
    ----------
    multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
        the input multi-time-series
    k_clusters : int or list
        if a single int is given, will create a clustering model with the given number of cluster. If a list is given,
        k-shape will be performed for each k-cluster value between the first number given and the second number given,
        the output will be the best model based on the min sum of square distances for all centroids
    num_runs : int
        number of runs for clustering
    use_eigen : bool, optional
        if True, uses Eigen-Decomposition for shape extraction, otherwise uses simple averaging (default is True)
    init_strategy : str, optional
        the initialization strategy for the seed centroids in the model. Can be one of "random", "zero", "plusplus"
        (default is "plusplus")

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.ml.clustering.TimeSeriesClusteringModel.TimeSeriesClusteringModel`
        a new time-series-clustering-model
    """
    jvm = multi_time_series._tsc._jvm
    multi_time_series.cache() # todo we might want to collect and re-create a mts here
    if isinstance(k_clusters, int):

        if init_strategy == "random":
            model = KShapeModel(
                multi_time_series._tsc,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.run(
                    multi_time_series._j_mts,
                    k_clusters,
                    num_runs,
                    use_eigen,
                    jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.Random
                )
            )
        elif init_strategy == "zero":
            model = KShapeModel(
                multi_time_series._tsc,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.run(
                    multi_time_series._j_mts,
                    k_clusters,
                    num_runs,
                    use_eigen,
                    jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.Zero
                )
            )
        else:
            model = KShapeModel(
                multi_time_series._tsc,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.run(
                    multi_time_series._j_mts,
                    k_clusters,
                    num_runs,
                    use_eigen,
                    jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.PlusPlus
                )
            )

        return model
    else:
        if init_strategy == "random":
            return KShapeModel(
                multi_time_series._tsc,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.explore(
                    multi_time_series._j_mts,
                    num_runs,
                    k_clusters[1],
                    k_clusters[0],
                    use_eigen,
                    jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.Random
                )
            )
        elif init_strategy == "zero":
            return KShapeModel(
                multi_time_series._tsc,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.explore(
                    multi_time_series._j_mts,
                    num_runs,
                    k_clusters[1],
                    k_clusters[0],
                    use_eigen,
                    jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.Zero
                )
            )
        else:
            return KShapeModel(
                multi_time_series._tsc,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.explore(
                    multi_time_series._j_mts,
                    num_runs,
                    k_clusters[1],
                    k_clusters[0],
                    use_eigen,
                    jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.PlusPlus
                )
            )
