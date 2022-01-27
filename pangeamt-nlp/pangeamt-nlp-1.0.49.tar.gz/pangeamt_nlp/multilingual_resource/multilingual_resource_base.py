class MultilingualResourceBase:
    TYPE_TMX = 'tmx'
    TYPE_AF = 'af'
    TYPE_BILINGUAL = 'bilingual'

    def __init__(self, type):
        self._multilingual_resource_type = type

    def get_multilingual_resource_type(self):
        return self._multilingual_resource_type
    multilingual_resource_type = property(get_multilingual_resource_type)