# -*- coding: utf-8 -*-
from plone.app.querystring.registryreader import QuerystringRegistryReader


class CpskinQuerystringRegistryReader(QuerystringRegistryReader):
    """Adapts a registry object to parse the querystring data."""

    def getVocabularyValues(self, values):
        """Get all vocabulary values if a vocabulary is defined"""
        values = super(CpskinQuerystringRegistryReader,
                       self).getVocabularyValues(values)
        cpskin_indexes = ['hiddenTags',
                          'isearchTags', 'iamTags', 'standardTags']
        values.get(self.prefix + '.field')
        for cpskin_index in cpskin_indexes:
            index = values.get(self.prefix + '.field').get(cpskin_index, None)
            if index is None:
                continue
            for value in index.values():
                if isinstance(value, dict):
                    i18n_value = dict((k.encode('utf8'), v)
                                      for k, v in value.items())
                    values.get(self.prefix + '.field').get(
                        cpskin_index)['values'] = i18n_value
        return values
