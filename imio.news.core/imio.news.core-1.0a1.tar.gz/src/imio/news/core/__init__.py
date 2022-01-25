# -*- coding: utf-8 -*-

from imio.smartweb.common.config import VOCABULARIES_MAPPING

VOCABULARIES_MAPPING.update(
    {
        "category": "imio.news.vocabulary.NewsCategories",
        "local_category": "imio.news.vocabulary.NewsLocalCategories",
    }
)
