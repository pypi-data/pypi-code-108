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

class LabeledPoint:

    def __init__(self, label, feature_vector):
        self._label = label
        self._feature_vector = feature_vector

    @property
    def label(self):
        return self._label

    @property
    def feature_vector(self):
        return self._feature_vector

    def __str__(self):
        return "LabeledPoint(label=" + str(self._label) + ", feature_vector=" + str(self._feature_vector) + ")"
