from unittest.mock import patch
import json
from tests.utils import fixtures_path, TERM

from hestia_earth.models.utils.product import (
    _new_product, residue_nitrogen, abg_residue_nitrogen, blg_residue_nitrogen
)

class_path = 'hestia_earth.models.utils.product'
fixtures_folder = f"{fixtures_path}/utils/product"


@patch(f"{class_path}._include_methodModel", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_hestia", return_value=TERM)
def test_new_product(*args):
    # with a Term as string
    product = _new_product('term')
    assert product == {
        '@type': 'Product',
        'term': TERM
    }

    # with a Term as dict
    product = _new_product(TERM)
    assert product == {
        '@type': 'Product',
        'term': TERM
    }


def test_residue_nitrogen_no_products():
    assert residue_nitrogen({}) == 0


@patch(f"{class_path}.abg_residue_nitrogen", return_value=20)
@patch(f"{class_path}.blg_residue_nitrogen", return_value=30)
def test_residue_nitrogen(*args):
    assert residue_nitrogen([]) == 50


def testabg_residue_nitrogen_no_products():
    assert abg_residue_nitrogen([]) == 0


def testabg_residue_nitrogen():
    with open(f"{fixtures_folder}/products-cropResidue.jsonld", encoding='utf-8') as f:
        products = json.load(f)

    assert abg_residue_nitrogen(products) == 0.8445757894736851


def testblg_residue_nitrogen_no_products():
    assert blg_residue_nitrogen([]) == 0


def testblg_residue_nitrogen():
    with open(f"{fixtures_folder}/products-cropResidue.jsonld", encoding='utf-8') as f:
        products = json.load(f)

    assert blg_residue_nitrogen(products) == 13.606542431999996
