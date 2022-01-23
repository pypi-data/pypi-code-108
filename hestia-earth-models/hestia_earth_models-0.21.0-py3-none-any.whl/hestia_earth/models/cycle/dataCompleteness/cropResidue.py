from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logger
from hestia_earth.models.utils.term import get_crop_residue_terms
from . import MODEL

MODEL_KEY = 'cropResidue'
REQUIRED_TERM_IDS = [
    'belowGroundCropResidue',
    'aboveGroundCropResidueTotal'
]


def _optional_term_ids():
    terms = get_crop_residue_terms()
    return [term for term in terms if term not in REQUIRED_TERM_IDS]


def run(cycle: dict):
    products = cycle.get('products', [])
    # all required terms + at least one of the optional terms must be present
    required_valid = all([find_term_match(products, term_id, False) for term_id in REQUIRED_TERM_IDS])
    optional_valid = any([find_term_match(products, term_id, False) for term_id in _optional_term_ids()])
    is_complete = required_valid and optional_valid
    logger.info('model=%s, key=%s, is_complete=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
