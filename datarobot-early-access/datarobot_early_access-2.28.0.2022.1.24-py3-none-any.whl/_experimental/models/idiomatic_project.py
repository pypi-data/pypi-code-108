#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import six

from datarobot import AUTOPILOT_MODE
from datarobot.enums import DEFAULT_MAX_WAIT, PROJECT_STAGE
from datarobot.models import Project


class IdiomaticProject(Project):
    """
    This class is an enhancement of the Project class. It has additional methods that are intended
    to work similarly to sklearn analogs, and bundle several existing smaller methods:
        - IdiomaticProject.fit : "fit" your project, by (re-)running Autopilot

        (yet to come in future PRs)
        - IdiomaticProject.predict : "predict" using your project's recommended model
        - IdiomaticProject.deploy : make a deployment from your project's recommended model

    This class is still in development and behavior may change! When it becomes GA, its methods will
    be moved to the regular Project class.
    """

    @staticmethod
    def _validate_refit(advanced_options, featurelist_id, metric, partitioning_method):
        valid_advanced_options = (
            not advanced_options
            or IdiomaticProject._validate_advanced_options_for_refit(advanced_options)
        )
        if not valid_advanced_options or metric is not None or partitioning_method is not None:
            raise ValueError(
                "Cannot reset advanced options or partitioning method on projects in manual mode."
            )
        if featurelist_id is None:
            raise ValueError("Feature list could not be resolved.")

    @staticmethod
    def _validate_advanced_options_for_refit(advanced_options):
        mock_payload = advanced_options.collect_payload()

        """
        These options are the only two in the AdvancedOptions object that are not 'None' by default;
        Check their "default" values before checking the rest of the object for refit-ability.
        """
        if (
            mock_payload["autopilot_with_feature_discovery"] is True
            or mock_payload["feature_discovery_supervised_feature_reduction"] is False
        ):
            return False

        """
        These are the only options that the client can pass on a subsequent run of autopilot.
        There are some options that are valid to pass through
        but are not available in the client yet.
        See: DSX-1340
        """
        valid_options = {
            "blend_best_models",
            "scoring_code_only",
            "prepare_model_for_deployment",
            "autopilot_with_feature_discovery",
            "feature_discovery_supervised_feature_reduction",
        }

        changed_options = mock_payload.keys() - valid_options
        return len(changed_options) == 0

    def fit(
        self,
        mode=AUTOPILOT_MODE.QUICK,
        metric=None,
        feature_list=None,
        partitioning_method=None,
        advanced_options=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Fit the existing project.

        Parameters
        ----------
        mode : str, optional
            You can use ``AUTOPILOT_MODE`` enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.MANUAL``
            * ``AUTOPILOT_MODE.QUICK``
            * ``AUTOPILOT_MODE.COMPREHENSIVE``: Runs all blueprints in the repository (warning:
              this may be extremely slow).

            If unspecified, ``QUICK`` is used. If the ``MANUAL`` value is used, the model
            creation process will need to be started by executing the ``start_autopilot``
            function with the desired featurelist. It will start immediately otherwise.
        metric : str, optional
            Name of the metric to use for evaluating models. You can query
            the metrics available for the target by way of
            ``Project.get_metrics``. If none is specified, then the default
            recommended by DataRobot is used.
        feature_list : str or list of str, optional
            Specifies which feature list to use. If type is str,
            can be either a feature list id or name.
            If a list of str, a dynamic feature list
            will be created with the features named in the list.
        partitioning_method : PartitioningMethod object, optional
            Instance of one of the :ref:`Partition Classes <partitions_api>` defined in
            ``datarobot.helpers.partitioning_methods``.
        advanced_options : AdvancedOptions object, optional
            Used to set advanced options of project creation.
        max_wait : int, optional
            Time in seconds after which fitting is considered unsuccessful.

        Returns
        -------
        project : Project
            The instance with updated attributes.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if target setting was unsuccessful
        AsyncTimeoutError
            Raised if target setting took more time, than specified
            by ``max_wait`` parameter
        TypeError
            Raised if ``advanced_options`` or ``partitioning_method`` are
            provided and not the correct types.
        """

        if self.use_time_series:
            raise ValueError("Cannot currently run fit on timeseries projects.")

        featurelist_id = self._resolve_fit_featurelist_id(feature_list)
        first_fit = self._is_first_fit()

        if first_fit:
            self.set_target(
                mode=mode,
                metric=metric,
                featurelist_id=featurelist_id,
                partitioning_method=partitioning_method,
                advanced_options=advanced_options,
                max_wait=max_wait,
            )
        else:
            self._validate_refit(advanced_options, featurelist_id, metric, partitioning_method)

            blend_best_models = advanced_options.blend_best_models if advanced_options else None
            scoring_code_only = advanced_options.scoring_code_only if advanced_options else None
            prepare_model_for_deployment = (
                advanced_options.prepare_model_for_deployment if advanced_options else None
            )

            self.start_autopilot(
                featurelist_id=featurelist_id,
                mode=mode,
                blend_best_models=blend_best_models,
                scoring_code_only=scoring_code_only,
                prepare_model_for_deployment=prepare_model_for_deployment,
            )
            self.refresh()

        return self

    def _is_first_fit(self):
        current_status = self.get_status()
        return current_status["stage"] not in [PROJECT_STAGE.MODELING, PROJECT_STAGE.EDA2]

    def _resolve_fit_featurelist_id(self, feature_list):
        feature_lists = self.get_featurelists()
        if type(feature_list) is list:
            # Incrementing to determine a unique feature list name
            inc = 1
            name = "custom_list_{}".format(inc)
            used_names = {feat_list.name for feat_list in feature_lists}
            while name in used_names:
                inc += 1
                name = "custom_list_{}".format(inc)
            new_feature_list = self.create_featurelist(name, feature_list)
            featurelist_id = new_feature_list.id
        elif isinstance(feature_list, six.string_types):
            feature_list = six.ensure_text(feature_list)
            # First check for IDs
            featurelist_id = next(
                (feature.id for feature in feature_lists if feature_list == feature.id),
                None,  # default
            )
            # Then check for names
            if featurelist_id is None:
                featurelist_id = next(
                    (feature.id for feature in feature_lists if feature_list == feature.name),
                    None,  # default
                )
        else:
            featurelist_id = next(
                (feature.id for feature in feature_lists if feature.name == "Informative Features"),
                None,  # default
            )
        if feature_list is not None and featurelist_id is None:
            raise ValueError(
                "feature_list is invalid. "
                "Please ensure the feature list exists, "
                "or pass in a list of features to create a new feature list."
            )
        return featurelist_id
