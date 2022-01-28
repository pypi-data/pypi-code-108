import tensorflow as tf
import tensorflow_datasets as tfds
import hcai_datasets.hcai_nova_dynamic.utils.nova_types as nt
import numpy as np
import pandas as pd
from numba import njit
from abc import ABC, abstractmethod
from hcai_datasets.hcai_nova_dynamic.utils.nova_utils import merge_role_key


@njit
def _get_overlap(a, start, end):
    """
    Calculating all overlapping intervals between the given array of time intervals and the interval [start, end]
    Args:
        a (): numpy array of shape (1,2), where each entry contains an interval [from, to]
        start (): start of the interval to check
        end (): end of the interval to check

    Returns:
    Numpy array with boolean values. The array is true where the interval specified in a overlaps [start, end]
    """
    annos_for_sample = (
        # annotation is bigger than frame
        ((a[:, 0] <= start) & (a[:, 1] >= end))
        # end of annotation is in frame
        | ((a[:, 1] >= start) & (a[:, 1] <= end))
        # start of annotation is in frame
        | ((a[:, 0] >= start) & (a[:, 0] <= end))
    )
    return annos_for_sample


@njit
def _get_anno_majority(a, overlap_idxs, start, end):
    """
    Returns the index of the annotation with the largest overlap with the current frame
    Args:
        a (): numpy array of shape (1,2), where each entry contains an interval [from, to]
        overlap_idxs (): aray of boolean values where a is overlapping the intervall [start, end] (as returned by get _get_overlap())
        start (): start of the interval to check
        end (): end of the interval to check

    Returns:

    """
    majority_index = np.argmax(
        np.minimum(a[overlap_idxs][:, 1], end)
        - np.maximum(a[overlap_idxs][:, 0], start)
    )
    return majority_index


class Annotation(ABC):
    def __init__(self, role: str = "", scheme: str = "", is_valid: bool = True):
        self.role = role
        self.scheme = scheme
        self.is_valid = is_valid

        # Gets set when load_annotation is called
        self.data = None

    @abstractmethod
    def get_tf_info(self):
        """
        Returns the labels for this annotation to create the DatasetInfo for tensorflow
        """
        raise NotImplementedError

    @abstractmethod
    def set_annotation_from_mongo_doc(self, session, time_to_ms=False):
        """
        Returns the labels for this annotation to create the DatasetInfo for tensorflow
        """
        raise NotImplementedError

    @abstractmethod
    def get_label_for_frame(self, start, end):
        """
        Returns the label for this frame
        """
        raise NotImplementedError


class DiscreteAnnotation(Annotation):

    REST = "REST"

    def __init__(self, labels={}, add_rest_class=False, **kwargs):
        super().__init__(**kwargs)
        self.type = nt.AnnoTypes.DISCRETE
        self.labels = {
            x["id"]: x["name"] if x["isValid"] else ""
            for x in sorted(labels, key=lambda k: k["id"])
        }
        self.add_rest_class = add_rest_class
        if self.add_rest_class:
            self.labels[max(self.labels.keys()) + 1] = DiscreteAnnotation.REST

    def get_tf_info(self):
        return (
            merge_role_key(self.role, self.scheme),
            tfds.features.ClassLabel(names=list(self.labels.values())),
        )

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        self.data = mongo_doc
        if time_to_ms:
            for d in self.data:
                d["from"] = int(d["from"] * 1000)
                d["to"] = int(d["to"] * 1000)

        # Creating Pandas Dataframe version of annotations
        self.dataframe = pd.DataFrame(self.data)

        # Creating numpy array of annotations for fast access
        # Splitting the annotations into interval and data array
        self.data_interval = self.dataframe[["from", "to"]].values.astype(np.int)
        self.data_values = self.dataframe[["id", "conf"]].values

    def get_label_for_frame_legacy(self, start, end):

        # If we don't have any data we return the garbage label
        if self.data == -1:
            return -1

        else:
            # Finding all annos that overlap with the frame
            def is_overlapping(af, at, ff, ft):

                # anno is larger than frame
                altf = af <= ff and at >= ft

                # anno overlaps frame start
                aofs = at >= ff and at <= ft

                # anno overlaps frame end
                aofe = af >= ff and af <= ft

                return altf or aofs or aofe

            annos_for_sample = list(
                filter(
                    lambda x: is_overlapping(x["from"], x["to"], start, end), self.data
                )
            )

            # No label matches
            if not annos_for_sample:
                if self.add_rest_class:
                    return len(self.labels.values()) - 1
                else:
                    return -1

            majority_sample_idx = np.argmax(
                list(
                    map(
                        lambda x: min(end, x["to"]) - max(start, x["from"]),
                        annos_for_sample,
                    )
                )
            )

            return annos_for_sample[majority_sample_idx]["id"]

    def get_label_for_frame_np(self, start, end):

        # If we don't have any data we return the garbage label
        if self.data == -1:
            return -1

        else:
            overlap_idxs = _get_overlap(self.data_interval, start, end)

            # No label matches
            if not overlap_idxs.any():
                if self.add_rest_class:
                    return len(self.labels.values()) - 1
                else:
                    return -1

            majority_idx = _get_anno_majority(
                self.data_interval, overlap_idxs, start, end
            )

            return self.data_values[majority_idx, 0]

    def get_label_for_frame(self, start, end):
        return self.get_label_for_frame_np(start, end)


class FreeAnnotation(Annotation):
    """
    The FREE annotation scheme is used for any form of free text.
    """

    def __init__(self, **kwargs):
        self.type = nt.AnnoTypes.FREE
        super().__init__(**kwargs)

    def get_tf_info(self):
        return (
            merge_role_key(self.role, self.scheme),
            tfds.features.Sequence(tfds.features.Text()),
        )

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        self.data = mongo_doc
        if time_to_ms:
            for d in self.data:
                d["from"] = int(d["from"] * 1000)
                d["to"] = int(d["to"] * 1000)

        # Creating Pandas Dataframe version of annotations
        self.dataframe = pd.DataFrame(self.data)

        # Creating numpy array of annotations for fast access
        # Splitting the annotations into interval and data array
        self.data_interval = self.dataframe[["from", "to"]].values.astype(np.int)
        self.data_values = self.dataframe[["name", "conf"]].values

    def get_label_for_frame_legacy(self, start, end):

        # If we don't have any data we return the garbage label
        if self.data == -1:
            return -1

        else:
            # Finding all annos that overlap with the frame
            def is_overlapping(af, at, ff, ft):

                # anno is larger than frame
                altf = af <= ff and at >= ft

                # anno overlaps frame start
                aofs = at >= ff and at <= ft

                # anno overlaps frame end
                aofe = af >= ff and af <= ft

                return altf or aofs or aofe

            annos_for_sample = list(
                filter(
                    lambda x: is_overlapping(x["from"], x["to"], start, end), self.data
                )
            )

            # No label matches
            if not annos_for_sample:
                return [""]

            return [a["name"] for a in annos_for_sample]

    def get_label_for_frame_np(self, start, end):

        # If we don't have any data we return the garbage label
        if self.data == -1:
            return -1

        else:
            annos_for_sample = _get_overlap(self.data_interval, start, end)

            # No label matches
            if not annos_for_sample.any():
                return [""]

            return self.data_values[annos_for_sample, 0]

    def get_label_for_frame(self, start, end):
        return self.get_label_for_frame_np(start, end)


class ContinousAnnotation(Annotation):
    def __init__(self, sr=0, min=0, max=0, **kwargs):
        super().__init__(**kwargs)
        self.type = nt.AnnoTypes.CONTINOUS
        self.sr = sr
        self.min = min
        self.max = max


class DiscretePolygonAnnotation(Annotation):
    def __init__(self, labels={}, sr=0, **kwargs):
        super().__init__(**kwargs)
        self.type = nt.AnnoTypes.DISCRETE_POLYGON
        self.labels = {
            str(x["id"]): x["name"] if x["isValid"] else ""
            for x in sorted(labels, key=lambda k: k["id"])
        }
        self.sr = sr
        self.dummy_label = np.full((10, 2), -1, dtype=np.float64)

    def get_tf_info(self):
        """
                Example:
                   <role>.<scheme>, {
                        'label_id_1' : [ (x1,y1), (x2,y2), ...  (xn, yn)],
                        'label_id_2' : ...
                        ...
        ,           }
        """
        tf_features = tfds.features.FeaturesDict(
            {
                str(l): tfds.features.Sequence(
                    tfds.features.Tensor(shape=(2,), dtype=tf.float64)
                )
                for l in self.labels.keys()
            }
        )
        return (merge_role_key(self.role, self.scheme), tf_features)

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        self.data = mongo_doc

    def get_label_for_frame(self, start, end):
        # Use the start of the frame to determine the label
        frame_nr = int(self.sr * start)

        # Prefill array with dummy -1 labels
        label = {str(l): self.dummy_label for l in self.labels.keys()}

        # If we have any label data fill the label
        if not self.data == -1 and len(self.data) > frame_nr:
            for l in self.data[frame_nr]["polygons"]:
                if str(l["label"]) in label.keys():
                    label[str(l["label"])] = np.array(
                        [(p["x"], p["y"]) for p in l["points"]]
                    )
                else:
                    print(
                        "Warning! Label ID {} found in annotation but not in scheme.".format(
                            l["label"]
                        )
                    )
        return label
