from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.blank_node import find_terms_value

COEFF_NH3NOX_N2O = 0.01
COEFF_NO3_N2O = 0.0075


def get_nh3_no3_nox_to_n(cycle: dict, nh3_term_id: str, no3_term_id: str, nox_term_id: str):
    nh3 = find_terms_value(cycle.get('emissions', []), nh3_term_id)
    nh3 = nh3 / get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    no3 = find_terms_value(cycle.get('emissions', []), no3_term_id)
    no3 = no3 / get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    nox = find_terms_value(cycle.get('emissions', []), nox_term_id)
    nox = nox / get_atomic_conversion(Units.KG_NOX, Units.TO_N)
    return nh3, no3, nox


def get_N_N2O_excreta_coeff_from_primary_product(cycle: dict):
    product = find_primary_product(cycle)
    term = product.get('term', {}) if product else {}
    # TODO: should use the coefficient from lookup table
    # percent = get_lookup_value(lookup, term, col)
    # return safe_parse_float(percent, 0.02)
    has_sheep_goat_products = term.get('@id') in ['sheep', 'goat']
    return 0.01 if has_sheep_goat_products else 0.02
