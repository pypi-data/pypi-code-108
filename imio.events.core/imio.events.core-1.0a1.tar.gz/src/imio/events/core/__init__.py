# -*- coding: utf-8 -*-

from imio.smartweb.common.config import VOCABULARIES_MAPPING

VOCABULARIES_MAPPING.update(
    {
        "category": "imio.events.vocabulary.EventsCategories",
        "local_category": "imio.events.vocabulary.EventsLocalCategories",
    }
)
