import enum

__all__ = ['BundleCategory', 'BundleFormat']


class BundleFormat(enum.Enum):
    """ Bundle format constants """
    XML = 'xml'
    ZIP = 'zip'


class BundleCategory(enum.Enum):
    """ Bundle category constants """
    RECIPE = 'recipe'
    CONFIG = 'config'
    PRODUCT = 'product'
    RESULTS = 'results'
    TEST_RESULTS = 'test_results'
