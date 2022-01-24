# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for selecting requested model and provider given dataset language."""

from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.runtime.featurizer.transformer.data.automl_textdnn_provider import AutoMLPretrainedDNNProvider
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo
from typing import Tuple

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TextDnnModelDownloadFailed
from azureml.automl.core.shared.reference_codes import ReferenceCodes


def get_model_from_language(dataset_language: str,
                            need_path: bool = False,
                            is_multilabel_training: bool = False) -> Tuple[str, str]:
    """
    return corresponding model name and download path given requested language

    :param dataset_language: user-inputted language from FeaturizationConfig
    :param need_path: whether fetching model provider path is necessary
    :param is_multilabel_training: whether being used for multilabel task
    """
    if dataset_language.lower() == 'eng':
        if is_multilabel_training:
            model_name = ModelNames.BERT_BASE_UNCASED
        else:
            model_name = ModelNames.BERT_BASE_CASED
    elif dataset_language.lower() == 'deu':
        model_name = ModelNames.BERT_BASE_GERMAN_CASED
    else:
        model_name = ModelNames.BERT_BASE_MULTILINGUAL_CASED
    if need_path:
        model_path = get_path(dataset_language, is_multilabel_training)
        if model_path is None:
            e = AzureMLError.create(TextDnnModelDownloadFailed, transformer='PretrainedBERT',
                                    reference_code=ReferenceCodes._TEXT_DNN_FIT_INITIALIZE,
                                    error_details="BERT CDN failed to download",
                                    target="PretrainedBERTModel")
            raise ClientException._with_error(e)
    else:
        model_path = ""

    return model_name, model_path


def get_path(dataset_language: str, is_multilabel_training: str):
    """
    return corresponding download path given requested language

    :param dataset_language: user-inputted language from FeaturizationConfig
    """
    if dataset_language.lower() == 'eng':
        if is_multilabel_training:
            provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0)
        else:
            provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_CASED)
    elif dataset_language.lower() == 'deu':
        provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0)
    else:
        provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0)
    return provider.get_model_dirname()
