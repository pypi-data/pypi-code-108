from py4j.java_collections import ListConverter


def stamp(ts, m, sampling=.2, num_threads=None):
    tsc = ts._tsc

    if num_threads is None:
        pair_result = tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.MatrixProfiles.stamp(ts._j_ts, m,
                                                                                                   sampling)
    else:
        pair_result = tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.MatrixProfiles.stamp(ts._j_ts, m, None,
                                                                                                   sampling,
                                                                                                   num_threads)
    return __py_result(pair_result)


def stomp(ts, m):
    tsc = ts._tsc

    pair_result = tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.MatrixProfiles.stomp(ts._j_ts, m)
    return __py_result(pair_result)


def scrimp_plus_plus(ts, m, relative_step_size=.25, runtime=-1):
    tsc = ts._tsc

    pair_result = tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.MatrixProfiles.scrimpPlusPlus(
        ts._j_ts, m, relative_step_size, runtime)
    return __py_result(pair_result)


def discords(ts, mp, exclusion_zone, k):
    j_mp = ListConverter().convert(mp, ts._tsc._gateway._gateway_client)
    j_list_obs = ts._tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.PythonConnector.discords(ts._j_ts, j_mp, exclusion_zone, k)
    return [ts._tsc.observation(j_obs.getTimeTick(), j_obs.getValue()) for j_obs in j_list_obs]


def motifs(ts, mp_and_index, max_motifs=3, radius=2.0, n_neighbors=-1, exclusion_zone=-1.0):
    j_pair = ts._tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.PythonConnector.motifs(ts._j_ts,
                                                                                                ListConverter().convert(mp_and_index[0], ts._tsc._gateway._gateway_client),
                                                                                                ListConverter().convert(mp_and_index[1], ts._tsc._gateway._gateway_client),
                                                                                                max_motifs,
                                                                                                radius,
                                                                                                n_neighbors,
                                                                                                exclusion_zone)
    return [[i for i in j_list] for j_list in j_pair.left()], [x for x in j_pair.right()]


def fluss(mp_index, m=-1):
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    j_list = tsc._jvm.com.ibm.research.time_series.ml.matrix_profile.PythonConnector.fluss(
        ListConverter().convert(mp_index, tsc._gateway._gateway_client), m)
    return [i for i in j_list]



def __py_result(j_pair):
    return [x for x in j_pair.left()], [x for x in j_pair.right()]
