# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""IoC container for data providers."""
from typing import Any, Dict, Optional

from .automl_wordembeddings_provider import AutoMLEmbeddingsProvider
from .automl_textdnn_provider import AutoMLPretrainedDNNProvider
from .word_embeddings_info import EmbeddingInfo


class DataProviders:
    """IoC container for data providers."""

    @classmethod
    def get(cls, embeddings_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Get data provider based on embedding name.

        :param embeddings_name: Name of the embeddings.
        """
        if embeddings_name in EmbeddingInfo._all_ or kwargs.get("model_name") in EmbeddingInfo._all_:
            factory_method = getattr(cls, embeddings_name)
            if factory_method:
                return factory_method(*args, **kwargs)
        return None

    @classmethod
    def wiki_news_300d_1M_subword(cls, *args: Any, **kwargs: Any) ->\
            AutoMLEmbeddingsProvider:
        """Create fast text based word embeddings provider."""
        kwargs["embeddings_name"] = "wiki_news_300d_1M_subword"
        return AutoMLEmbeddingsProvider(*args, **kwargs)

    @classmethod
    def glove_6B_300d_word2vec(cls, *args: Any, **kwargs: Any) -> AutoMLEmbeddingsProvider:
        """Create GloVe based word embeddings provider."""
        kwargs["embeddings_name"] = "glove_6B_300d_word2vec"
        return AutoMLEmbeddingsProvider(*args, **kwargs)

    @classmethod
    def pretrained_text_dnn(cls, *args: Any, **kwargs: Any) ->\
            AutoMLPretrainedDNNProvider:
        """Create BERT/XNET/etc provider."""
        return AutoMLPretrainedDNNProvider(*args, **kwargs)
