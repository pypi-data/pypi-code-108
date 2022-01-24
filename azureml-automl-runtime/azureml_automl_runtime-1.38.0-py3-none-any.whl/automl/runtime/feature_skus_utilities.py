# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code to handle AutoML feature SKUs in the SDK."""
from typing import Any, Optional, Set, Tuple

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.constants import FeaturizationConfigMode


class FeatureSkus:
    DNN_FORECASTING = 'automatedml_sdk_dnnforecasting'
    DNN_NLP = 'automatedml_sdk_dnnnlp'
    IMAGE_CLASSIFICATION = 'automatedml_sdk_imageclassificationsupport'
    IMAGE_CLASSIFICATION_MULTILABEL = 'automatedml_sdk_imageclassificationmultilabelsupport'
    IMAGE_MULTI_LABEL_CLASSIFICATION = 'automatedml_sdk_imagesmultilabellingsupport'  # for temporary back-compat
    IMAGE_OBJECT_DETECTION = 'automatedml_sdk_objectdetectionsupport'
    IMAGE_INSTANCE_SEGMENTATION = 'automatedml_sdk_imageinstancesegmentationsupport'
    STREAMING = 'automatedml_sdk_largedatasupport'
    FEATURIZATION_CUSTOMIZATION = 'automatedml_sdk_featureengineeringcustomization'
    GUARDRAILS = 'automatedml_sdk_guardrails'
    FORECASTING_NEW_LEARNERS = 'automatedml_sdk_forecastingnewlearners'

    # These ones aren't being used right now (?)
    PARALLEL_FEATURIZATION = 'automatedml_sdk_parallelizedfeaturization'
    HIERARCHAL_FORECASTING = 'automatedml_sdk_forecastinghierarchy'
    GROUPED_FORECASTING = 'automatedml_sdk_forecastinggrouping'
    MANY_MODEL_TRAINING = 'automatedml_sdk_manymodelstraining'
    RAW_FEATURE_EXPLANATION = 'automatedml_modelexplainability'


def get_feature_skus_from_settings(automl_settings: AutoMLBaseSettings) -> Set[str]:
    skus = set()
    if automl_settings.enable_dnn:
        if automl_settings.task_type == Tasks.CLASSIFICATION:
            skus.add(FeatureSkus.DNN_NLP)
        elif automl_settings.task_type == Tasks.REGRESSION:
            skus.add(FeatureSkus.DNN_FORECASTING)

    if automl_settings.task_type == Tasks.IMAGE_CLASSIFICATION:
        skus.add(FeatureSkus.IMAGE_CLASSIFICATION)
    elif automl_settings.task_type == Tasks.IMAGE_CLASSIFICATION_MULTILABEL:
        skus.add(FeatureSkus.IMAGE_CLASSIFICATION_MULTILABEL)
    elif automl_settings.task_type == Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION:
        skus.add(FeatureSkus.IMAGE_MULTI_LABEL_CLASSIFICATION)
    elif automl_settings.task_type == Tasks.IMAGE_OBJECT_DETECTION:
        skus.add(FeatureSkus.IMAGE_OBJECT_DETECTION)
    elif automl_settings.task_type == Tasks.IMAGE_INSTANCE_SEGMENTATION:
        skus.add(FeatureSkus.IMAGE_INSTANCE_SEGMENTATION)

    if automl_settings.enable_streaming:
        skus.add(FeatureSkus.STREAMING)

    if automl_settings._get_featurization_config_mode() == FeaturizationConfigMode.Customized:
        skus.add(FeatureSkus.FEATURIZATION_CUSTOMIZATION)

    # Currently we always run guardrails
    skus.add(FeatureSkus.GUARDRAILS)

    return skus


def serialize_skus(feature_skus: Set[str]) -> str:
    return ','.join(sorted(feature_skus))


def _check_for_new_learner(feature_skus: Set[str], pipeline_spec: Optional[str]) -> Set[str]:
    if pipeline_spec is not None:
        if 'ProphetModel' in pipeline_spec or 'AutoArima' in pipeline_spec:
            feature_skus.add(FeatureSkus.FORECASTING_NEW_LEARNERS)
    return feature_skus
