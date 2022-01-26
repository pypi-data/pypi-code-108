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

import numpy

from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
from autoai_ts_libs.deps.tspy.data_structures import utils


def prepare_predictions(data_time_series, left_delta, right_delta, label_range, feature_range=None,
                        label_time_series=None, anchor=None, flatten_vector=False):
    tsc = data_time_series._tsc
    if isinstance(data_time_series, TimeSeries):
        data_time_series = tsc.multi_time_series.dict({'data_structures': data_time_series})

    if isinstance(label_time_series, TimeSeries):
        label_time_series = tsc.multi_time_series.dict({'data_structures': data_time_series})

    if hasattr(anchor, '__call__'):
        anchor = utils.FilterFunction(tsc, anchor)
    elif anchor is not None:
        anchor = tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(anchor)

    j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.preparePredictions(
        data_time_series._j_mts,
        None if label_time_series is None else label_time_series._j_mts,
        anchor,
        left_delta,
        right_delta,
        label_range[0],
        label_range[1],
        feature_range[0],
        feature_range[1]
    )

    import json
    py_dict = json.loads(j_str)

    py_list = []
    for o in py_dict['key_and_vector']:

        py_fv = numpy.asarray([x for x in o['feature']])
        if flatten_vector:
            py_fv = py_fv.flatten()
        py_label = numpy.asarray([x for x in o['label']])
        if flatten_vector:
            py_label = py_label.flatten()
        py_list.append((o['key'], py_label, py_fv))
    return py_list

def prepare(data_time_series, label_time_series, anchor, left_delta, right_delta, pos_perc=1.0, neg_perc=.05,
            label_range=None, feature_range=None, with_replacement=False, flatten_vector=False, label_reducer=None,
            feature_reducer=None):
    """
        Prepare feature vectors for training using traditional shallow models or deep learning models

        Parameters
        ----------
        data_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            multi-time-series containing the data vectors
        label_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            multi-time-series containing the labels
        anchor : func or time-series boolean expression
            function or expression to denote a negative from positive label
        left_delta : int
            left delta time ticks to the left of the anchor point
        right_delta : int
            right delta time ticks to the right of the anchor point
        pos_perc : float, optional
            positive float between 0 and 1 representing the percentage of positive segments to take (default is 1.0)
        neg_perc : float, optional
            positive float between 0 and 1 representing the percentage of positive segments to take (default is 1.0)
        label_range : tuple, optional
            a tuple of the (offset_to_start, offset_to_end) for label. The offset will start from start of the segment
            (default is simple binary label)
        feature_range : tuple, optional
            a tuple of the (offset_to_start, offset_to_end) for feature. The offset will start from start of the segment
            (default is entire segment of vectors)
        with_replacement : bool, optional
            if true, will allow for segments to overlap (default is false)
        flatten_vector : bool, optional
            if true, will flatten each feature vector and label (if label is a vector) each to a single vector (default
            is false)

        Returns
        -------
        list
            a list of tuples, where each tuple contains the time-series key (str) - the key to the time-series for
            which the feature was found, label (int or nparray) binary value if no label-range given, otherwise an
            nparray representing the label vector, feature (nparray) an array representing the feature vector
        """
    tsc = data_time_series._tsc

    from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
    if isinstance(data_time_series, TimeSeries):
        data_time_series = tsc.multi_time_series.dict({'data_structures': data_time_series})

    if isinstance(label_time_series, TimeSeries):
        label_time_series = tsc.multi_time_series.dict({'data_structures': label_time_series})

    if hasattr(anchor, '__call__'):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        anchor = utils.FilterFunction(tsc, anchor)
    else:
        anchor = tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(anchor)

    if label_range is None and feature_range is None:

        # simple label, simple feature
        if feature_reducer is None:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareSimpleLabel(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                pos_perc,
                neg_perc,
                with_replacement
            )
            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:

                py_fv = numpy.asarray([x for x in o['feature']])
                if flatten_vector:
                    py_fv = py_fv.flatten()
                py_label = 1 if o['label'] else 0
                py_list.append((o['key'], py_label, py_fv))
            return py_list
        # simple label, simple feature reduced
        else:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareSimpleLabelWithReduce(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                pos_perc,
                neg_perc,
                with_replacement,
                feature_reducer
            )
            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:
                py_label = 1 if o['label'] else 0
                py_list.append((o['key'], py_label, o['feature']))
            return py_list

    elif feature_range is not None and label_range is None:

        # simple label, complex feature
        if feature_reducer is None:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareSimpleLabel(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                feature_range[0],
                feature_range[1],
                pos_perc,
                neg_perc,
                with_replacement
            )

            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:

                py_fv = numpy.asarray([x for x in o['feature']])
                if flatten_vector:
                    py_fv = py_fv.flatten()
                py_label = 1 if o['label'] else 0
                py_list.append((o['key'], py_label, py_fv))
            return py_list
        # simple label, complex feature reduced
        else:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareSimpleLabelWithReduce(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                feature_range[0],
                feature_range[1],
                pos_perc,
                neg_perc,
                with_replacement,
                feature_reducer
            )
            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:
                py_label = 1 if o['label'] else 0
                py_list.append((o['key'], py_label, o['feature']))
            return py_list
    else:
        # complex label, complex feature
        if feature_reducer is None and label_reducer is None:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareComplexLabel(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                label_range[0],
                label_range[1],
                feature_range[0],
                feature_range[1],
                pos_perc,
                neg_perc,
                with_replacement
            )

            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:

                py_fv = numpy.asarray([x for x in o['feature']])
                if flatten_vector:
                    py_fv = py_fv.flatten()
                py_label = numpy.asarray([x for x in o['label']])
                if flatten_vector:
                    py_label = py_label.flatten()
                py_list.append((o['key'], py_label, py_fv))
            return py_list
        # complex label, complex feature reduced
        elif label_reducer is None and feature_reducer is not None:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareComplexLabelWithReduce(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                label_range[0],
                label_range[1],
                feature_range[0],
                feature_range[1],
                pos_perc,
                neg_perc,
                with_replacement,
                feature_reducer
            )
            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:
                py_label = numpy.asarray([x for x in o['label']])
                if flatten_vector:
                    py_label = py_label.flatten()
                py_list.append((o['key'], py_label, o['feature']))
            return py_list
        # complex label reduced, complex feature
        elif label_reducer is not None and feature_reducer is None:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareComplexLabelWithReduceLabelOnly(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                label_range[0],
                label_range[1],
                feature_range[0],
                feature_range[1],
                pos_perc,
                neg_perc,
                with_replacement,
                label_reducer
            )
            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:
                py_fv = numpy.asarray([x for x in o['feature']])
                if flatten_vector:
                    py_fv = py_fv.flatten()
                py_list.append((o['key'], o['label'], py_fv))
            return py_list
        # complex label reduced, complex feature reduced
        else:
            j_str = tsc._jvm.com.ibm.research.time_series.ml.data_curation.PythonConnector.prepareComplexLabelWithReduce(
                data_time_series._j_mts,
                label_time_series._j_mts,
                anchor,
                left_delta,
                right_delta,
                label_range[0],
                label_range[1],
                feature_range[0],
                feature_range[1],
                pos_perc,
                neg_perc,
                with_replacement,
                label_reducer,
                feature_reducer
            )
            import json
            py_dict = json.loads(j_str)

            py_list = []
            for o in py_dict['key_and_vector']:
                py_list.append((o['key'], o['label'], o['feature']))
            return py_list
