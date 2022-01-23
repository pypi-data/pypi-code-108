from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import filter_list_term_type, find_term_match, linked_node
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.utils.blank_node import get_total_value, get_total_value_converted
from . import _term_id, _include_methodModel
from .constant import Units
from .property import _get_nitrogen_content, get_node_property
from .term import get_rice_paddy_terms


def _new_product(term, model=None):
    node = {'@type': SchemaType.PRODUCT.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def has_flooded_rice(products: list):
    """
    Checks if one of the product is a flooded rice.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        True if one product matches a rice paddy crop.
    """
    terms = get_rice_paddy_terms()
    return any([True for p in products if p.get('term', {}).get('@id') in terms])


def abg_total_residue_nitrogen_content(products: list):
    """
    Get the nitrogen content from the `aboveGroundCropResidueTotal` product.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    return _get_nitrogen_content(find_term_match(products, 'aboveGroundCropResidueTotal'))


def abg_residue_nitrogen(products: list):
    """
    Get the total nitrogen content from all the `aboveGroundCropResidue` products.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    left_on_field = find_term_match(products, 'aboveGroundCropResidueLeftOnField').get('value', [0])
    incorporated = find_term_match(products, 'aboveGroundCropResidueIncorporated').get('value', [0])
    return list_sum(left_on_field + incorporated) * abg_total_residue_nitrogen_content(products) / 100


def blg_residue_nitrogen(products: list):
    """
    Get the total nitrogen content from the `belowGroundCropResidue` product.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    residue = find_term_match(products, 'belowGroundCropResidue')
    return list_sum(residue.get('value', [0])) * _get_nitrogen_content(residue) / 100


def residue_nitrogen(products: list) -> float:
    """
    Get the total nitrogen content from the `cropResidue` products.

    Parameters
    ----------
    products : list
        List of `Product`s.

    Returns
    -------
    float
        The total value as a number.
    """
    return abg_residue_nitrogen(products) + blg_residue_nitrogen(products)


def animal_produced(products: list, prop: str = 'nitrogenContent') -> float:
    products = (
        filter_list_term_type(products, TermTermType.LIVEANIMAL) +
        filter_list_term_type(products, TermTermType.ANIMALPRODUCT) +
        filter_list_term_type(products, TermTermType.LIVEAQUATICSPECIES)
    )

    def product_value(product: dict):
        value = convert_animalProduct_to_unit(product, Units.KG_LIVEWEIGHT)
        property = get_node_property(product, prop)
        return value * property.get('value', 0) if property else 0

    return list_sum(list(map(product_value, products)))


PRODUCT_UNITS_CONVERSIONS = {
    Units.KG.value: {
         Units.KG_LIVEWEIGHT.value: []
    },
    Units.KG_LIVEWEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [],
        Units.KG_CARCASS_WEIGHT.value: [
            ('processingConversionLiveweightToCarcassWeight', True)
        ],
        Units.KG_DRESSED_CARCASS_WEIGHT.value: [
            ('processingConversionLiveweightToDressedCarcassWeight', True)
        ],
        Units.KG_READY_TO_COOK_WEIGHT.value: [
            (
                [
                    'processingConversionLiveweightToCarcassWeight',
                    'processingConversionCarcassWeightToReadyToCookWeight'
                ],
                True
            ),
            (
                [
                    'processingConversionLiveweightToDressedCarcassWeight',
                    'processingConversionDressedCarcassWeightToReadyToCookWeight'
                ],
                True
            )
        ]
    },
    Units.KG_CARCASS_WEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [
            ('processingConversionLiveweightToCarcassWeight', False)
        ],
        Units.KG_CARCASS_WEIGHT.value: [],
        Units.KG_READY_TO_COOK_WEIGHT.value: [
            ('processingConversionCarcassWeightToReadyToCookWeight', True)
        ]
    },
    Units.KG_DRESSED_CARCASS_WEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [
            ('processingConversionLiveweightToDressedCarcassWeight', False)
        ],
        Units.KG_DRESSED_CARCASS_WEIGHT.value: [],
        Units.KG_READY_TO_COOK_WEIGHT.value: [
            ('processingConversionDressedCarcassWeightToReadyToCookWeight', True)
        ]
    },
    Units.KG_READY_TO_COOK_WEIGHT.value: {
        Units.KG_LIVEWEIGHT.value: [
            (
                [
                    'processingConversionCarcassWeightToReadyToCookWeight',
                    'processingConversionLiveweightToCarcassWeight',
                ],
                False
            ),
            (
                [
                    'processingConversionDressedCarcassWeightToReadyToCookWeight',
                    'processingConversionLiveweightToDressedCarcassWeight'
                ],
                False
            )
        ],
        Units.KG_CARCASS_WEIGHT.value: [
            ('processingConversionCarcassWeightToReadyToCookWeight', False)
        ],
        Units.KG_DRESSED_CARCASS_WEIGHT.value: [
            ('processingConversionDressedCarcassWeightToReadyToCookWeight', False)
        ],
        Units.KG_READY_TO_COOK_WEIGHT.value: []
    }
}


def convert_animalProduct_to_unit(product: dict, dest_unit: Units):
    units = product.get('term', {}).get('units')
    dest_key = dest_unit if isinstance(dest_unit, str) else dest_unit.value
    conversions = PRODUCT_UNITS_CONVERSIONS.get(units, {}).get(dest_key)
    return 0 if conversions is None else list_sum(
        flatten([
            get_total_value_converted([product], properties, multiply) for properties, multiply in conversions
        ]) if len(conversions) > 0 else get_total_value([product])
    )


def liveweight_produced(products: list):
    return list_sum([convert_animalProduct_to_unit(p, Units.KG_LIVEWEIGHT) for p in products])
