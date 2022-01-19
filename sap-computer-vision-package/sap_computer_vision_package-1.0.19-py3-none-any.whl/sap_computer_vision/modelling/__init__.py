"""This submodule contains new backbones and meta architectures."""
from .image_classifier import ImageClassifier
from .distance_metric_learner import (TripletDistanceLearner,
                                      SelectContrastiveTripletMarginLoss,
                                      SelectiveContrastiveTripletNCALoss,
                                      CircleLoss)
#from .spice import SpiceSelf
__all__ = ['TripletDistanceLearner',
           'ImageClassifier',
           'TripletDistanceLearner',
           'SelectContrastiveTripletMarginLoss',
           'SelectiveContrastiveTripletNCALoss',
           'CircleLoss']
