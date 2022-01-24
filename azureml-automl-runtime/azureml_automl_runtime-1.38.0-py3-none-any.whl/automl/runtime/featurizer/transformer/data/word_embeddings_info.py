# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holder for embedding information."""
from typing import Dict, Optional


class EmbeddingInfo:
    """Class to hold information of embeddings."""

    ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300 = "wiki_news_300d_1M_subword"
    BERT_BASE_CASED = "bert-base-cased"
    BERT_BASE_UNCASED = "bert-base-uncased"
    BERT_BASE_UNCASED_AUTONLP_3_1_0 = "bert-base-uncased-automlnlp-3.1.0"
    BERT_BASE_MULTLINGUAL_CASED = "bert-base-multilingual-cased"
    BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0 = "bert-base-multilingual-cased-automlnlp-3.1.0"
    BERT_BASE_CHINESE = "bert-base-chinese"
    BERT_BASE_CHINESE_AUTONLP_3_1_0 = "bert-base-chinese-automlnlp-3.1.0"
    BERT_BASE_GERMAN_CASED = "bert-base-german-cased"
    BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0 = "bert-base-german-cased-automlnlp-3.1.0"
    XLNET_BASE_CASED = "xlnet-base-cased"
    GLOVE_WIKIPEDIA_GIGAWORD_6B_300 = "glove_6B_300d_word2vec"

    _all_ = [ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300,
             GLOVE_WIKIPEDIA_GIGAWORD_6B_300,
             BERT_BASE_CASED,
             BERT_BASE_UNCASED,
             BERT_BASE_UNCASED_AUTONLP_3_1_0,
             BERT_BASE_MULTLINGUAL_CASED,
             BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0,
             BERT_BASE_CHINESE,
             BERT_BASE_CHINESE_AUTONLP_3_1_0,
             BERT_BASE_GERMAN_CASED,
             BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0,
             XLNET_BASE_CASED]

    def __init__(self, user_friendly_name: str, embedding_name: str,
                 download_prefix: str, language: str, file_name: str,
                 lower_case: bool, license: str, credits: str,
                 md5hash: str) -> None:
        """
        Create embedding info object.

        :param user_friendly_name: human readable name
        :param embedding_name: Name of the embedding.
        :param download_prefix: Prefix of the url to download from.
        :param language: 3 letter language abbreviation
        :param file_name: Name of the file to be appended to the prefix.
        :param lower_case: True if the embeddings were generated on strings
         after lower casing.
        """
        self._user_friendly_name = user_friendly_name
        self._embedding_name = embedding_name
        self._download_prefix = download_prefix
        self._file_name = file_name
        self._lower_case = lower_case
        self._license = license
        self._credits = credits
        self._md5hash = md5hash
        self._language = language


# TODO Make this a full fledged class and move to config
class WordEmbeddingsInfo:
    """Word embeddings information holder."""
    BERT_EMB_CASED_INFO = EmbeddingInfo.BERT_BASE_CASED
    BERT_EMB_INFO = EmbeddingInfo.BERT_BASE_UNCASED
    BERT_EMB_AUTONLP_3_1_0 = EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0
    BERT_MULTI_EMB_INFO = EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED
    BERT_MULTI_EMB_AUTONLP_3_1_0 = EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0
    BERT_GERMAN_EMB_INFO = EmbeddingInfo.BERT_BASE_GERMAN_CASED
    BERT_GERMAN_EMB_AUTO_NLP_3_1_0 = EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0
    BERT_CHINESE_EMB_INFO = EmbeddingInfo.BERT_BASE_CHINESE
    BERT_CHINESE_EMB_AUTONLP_3_1_0 = EmbeddingInfo.BERT_BASE_CHINESE_AUTONLP_3_1_0
    XLNET_EMB_INFO = EmbeddingInfo.XLNET_BASE_CASED
    WORD_VEC_LINK = "https://aka.ms/automl-resources/data/wordvectors/"

    # List of models under consideration for pretrained_text_dnn,
    # only one model per language code should be represented in this list (this is unit tested)
    pretrained_model_names_for_languages = [
        EmbeddingInfo.BERT_BASE_UNCASED,
        EmbeddingInfo.BERT_BASE_GERMAN_CASED,
        # EmbeddingInfo.BERT_BASE_CHINESE, # Disabled due to inferior ml perf compared to multilingual bert
        EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED
    ]
    embeddings = {
        EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300:
            EmbeddingInfo(
                user_friendly_name="English word embeddings trained on wikipedia and web",
                embedding_name=EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300,
                download_prefix="https://aka.ms/automl-resources/data/wordvectors/",
                file_name="{base}.pkl".format(base=EmbeddingInfo.ENGLISH_FASTTEXT_WIKI_NEWS_SUBWORDS_300),
                lower_case=False,
                license="Creative Commons Attribution-Share-Alike License (3.0). More information can be found at: "
                        "https://creativecommons.org/licenses/by-sa/3.0/",
                credits="Advances in Pre-Training Distributed Word Representations by "
                        "P. Bojanowski, E. Grave, A. Joulin, "
                        "T. Mikolov, Proceedings of the International Conference on Language Resources "
                        "and Evaluation (LREC 2018). More information can be found at: https://fasttext.cc and "
                        "http://https://arxiv.org/abs/1712.09405",
                md5hash="4fd6dce9765e619aca3d26481076763b",
                language="eng"),
        EmbeddingInfo.BERT_BASE_CASED:
            EmbeddingInfo(
                user_friendly_name="BERT pretrained cased model",
                embedding_name=EmbeddingInfo.BERT_BASE_CASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_EMB_CASED_INFO),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                        be found at: http://www.apache.org/licenses/",
                credits="Pretrained model on English language using a masked language modeling (MLM) "
                        "objective. It was introduced in https://arxiv.org/abs/1810.04805 "
                        "and first released in https://github.com/google-research/bert",
                md5hash="19f913bc60c6a024e6b5893258f395c1",
                language="eng"),
        EmbeddingInfo.BERT_BASE_UNCASED:
            EmbeddingInfo(
                user_friendly_name="BERT pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_UNCASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}-nohead.zip".format(base=BERT_EMB_INFO),
                lower_case=True,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="1ef1eedf2ade96a8ed82d47307a8de0f",
                language="eng"),
        EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0:
            EmbeddingInfo(
                user_friendly_name="BERT pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_EMB_AUTONLP_3_1_0),
                lower_case=True,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="c7360854bd23c87c99f7bb5bcf0926f0",
                language="eng"),
        EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED:
            EmbeddingInfo(
                user_friendly_name="BERT multilingual pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_MULTI_EMB_INFO),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="8e5f6bef8cacca52da418186957a06a3",
                language="mul"),
        EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0:
            EmbeddingInfo(
                user_friendly_name="BERT multilingual pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_MULTI_EMB_AUTONLP_3_1_0),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="72c309ab2aae9b02ffd27d7bcef096b2",
                language="mul"),
        EmbeddingInfo.BERT_BASE_GERMAN_CASED:
            EmbeddingInfo(
                user_friendly_name="BERT German pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_GERMAN_CASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_GERMAN_EMB_INFO),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="ff4569b05b594e66243ad63e691e08b1",
                language="deu"),
        EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0:
            EmbeddingInfo(
                user_friendly_name="BERT German pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_GERMAN_EMB_AUTO_NLP_3_1_0),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="38d99b71061e7b92ebf4300c9101067e",
                language="deu"),
        EmbeddingInfo.BERT_BASE_CHINESE:
            EmbeddingInfo(
                user_friendly_name="BERT Chinese pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_CHINESE,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_CHINESE_EMB_INFO),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="4ea5178a98b2c9a0d5b5500cfc39b407",
                language="zho"),
        EmbeddingInfo.BERT_BASE_CHINESE_AUTONLP_3_1_0:
            EmbeddingInfo(
                user_friendly_name="BERT Chinese pretrained model",
                embedding_name=EmbeddingInfo.BERT_BASE_CHINESE_AUTONLP_3_1_0,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=BERT_CHINESE_EMB_AUTONLP_3_1_0),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits="BERT: Pre-training of Deep Bidirectional Transformers\
                for Language Understanding by Devlin, Jacob and Chang, "
                "Ming-Wei and Lee, Kenton and Toutanova, Kristina,\
                arXiv preprint arXiv:1810.04805",
                md5hash="a70543a951a3f9a5afd284daadc80caa",
                language="zho"),
        EmbeddingInfo.XLNET_BASE_CASED:
            EmbeddingInfo(
                user_friendly_name="XLNET pretrained model",
                embedding_name=EmbeddingInfo.XLNET_BASE_CASED,
                download_prefix=WORD_VEC_LINK,
                file_name="{base}.zip".format(base=XLNET_EMB_INFO),
                lower_case=False,
                license="Apache License Version 2.0, More information can\
                be found at: "
                "http://www.apache.org/licenses/",
                credits=" XLNet: Generalized Autoregressive Pretraining for\
                Language Understanding by Zhilin Yang*, Zihang Dai*, "
                "Yiming Yang, Jaime Carbonell, Ruslan Salakhutdinov, Quoc V. Le,\
                arXiv preprint arXiv:1906.08237",
                md5hash="7ec3cc8d7a2fecffbf68a572cb38240f",
                language="eng"),
        EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300:
            EmbeddingInfo(
                user_friendly_name="Glove word embeddings trained on wikipedia and gigawords",
                embedding_name=EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300,
                download_prefix="https://aka.ms/automl-resources/data/wordvectors/",
                file_name="{base}.pkl".format(base=EmbeddingInfo.GLOVE_WIKIPEDIA_GIGAWORD_6B_300),
                lower_case=False,
                license="ODC Public Domain Dedication and Licence (PDDL). More information can be found at: "
                        "https://www.opendatacommons.org/licenses/pddl/1.0/",
                credits="GloVe: Global Vectors for Word Representation, "
                        "Empirical Methods in Natural Language Processing (EMNLP) 2014 "
                        "Jeffrey Pennington and Richard Socher and Christopher D. Manning "
                        "http://www.aclweb.org/anthology/D14-1162",
                md5hash="764913044de83d404ab095421291bda2",
                language="eng")
    }                                                               # type: Dict[str, EmbeddingInfo]

    @classmethod
    def get(cls, embeddings_name: str) -> Optional[EmbeddingInfo]:
        """
        Get embedding information given the name.

        :param embeddings_name: Name of the requested embeddings.
        :return: Information on the embeddings.
        """
        return cls.embeddings[embeddings_name]\
            if embeddings_name in cls.embeddings else None

    @classmethod
    def get_bert_model_name_based_on_language(cls, dataset_language: str = 'eng') -> str:
        """
        Get embedding information given.

        :param dataset_language: Language of the input text for text classification.
        :return: Transfomer model name, e.g. bert-base-uncased, corresponding to that language
        """
        # get list of languages that bert models cover
        bert_languages = [cls.embeddings[name]._language
                          for name in cls.pretrained_model_names_for_languages]
        if dataset_language not in bert_languages:
            # If the language is not explicitly in the map, then use multilingual bert
            dataset_language = "mul"
        model_name = next(name for name in cls.pretrained_model_names_for_languages
                          if cls.embeddings[name]._language == dataset_language)
        return model_name
