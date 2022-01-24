# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional, Union, Dict

from azureml.responsibleai.tools._common.base_request import BaseRequest


class CounterfactualRequest(BaseRequest):
    def __init__(self,
                 total_CFs: int,
                 method: str = 'random',
                 desired_class: Union[str, int] = 'opposite',
                 desired_range: Optional[List[float]] = None,
                 feature_importance: bool = True,
                 comment: Optional[str] = None,
                 permitted_range: Optional[Dict[str, List[float]]] = None,
                 features_to_vary: Union[List[str], str] = 'all'):
        """Initialize a request for counterfactual examples.

        :param total_CFs: Total number of counterfactuals required.
        :type total_CFs: int
        :param method: Type of dice-ml explainer. Either of "random", "genetic" or "kdtree".
        :type method: str
        :param desired_class: Desired counterfactual class. For binary
                              classification, this needs to be set as
                              "opposite".
        :type desired_class: string or int
        :param desired_range: For regression problems.
                              Contains the outcome range
                              to generate counterfactuals in.
        :type desired_range: list[float]
        :param permitted_range: Dictionary with feature names as keys and
                                permitted range in list as values.
                                Defaults to the range inferred from training
                                data.
        :type permitted_range: dict
        :param features_to_vary: Either a string "all" or a list of
                                 feature names to vary.
        :type features_to_vary: list
        :param feature_importance: Flag to compute feature importance using
                                   dice-ml.
        :type feature_importance: bool
        :param comment: Comment to identify the counterfactual.
        :type comment: str
        """
        super(CounterfactualRequest, self).__init__()

        self.total_CFs = total_CFs
        self.method = method
        self.desired_class = desired_class
        self.desired_range = desired_range
        self.feature_importance = feature_importance
        self.features_to_vary = features_to_vary
        self.permitted_range = permitted_range
        self.comment = comment
