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

def explore(multi_time_series, num_runs, max_k, min_k, use_eigen=True, init_strategy="plusplus"):
    jvm = multi_time_series._tsc._jvm

    if init_strategy == "random":
        return KShapeModel(
            multi_time_series._tsc,
            jvm.com.ibm.research.time_series.ml.clustering.k_shape.KShape.explore(
                multi_time_series._j_mts,
                num_runs,
                max_k,
                min_k,
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
                max_k,
                min_k,
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
                max_k,
                min_k,
                use_eigen,
                jvm.com.ibm.research.time_series.ml.clustering.k_shape.containers.InitializationStrategies.PlusPlus
            )
        )


def run(multi_time_series, k_clusters, num_runs=2, use_eigen=True, init_strategy="plusplus"):
    multi_time_series.cache()
    jvm = multi_time_series._tsc._jvm

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
