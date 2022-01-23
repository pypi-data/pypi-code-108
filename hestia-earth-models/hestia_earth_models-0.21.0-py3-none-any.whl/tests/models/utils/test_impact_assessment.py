from hestia_earth.models.utils.impact_assessment import get_product, impact_value, get_region_id


def test_get_product():
    term_id = 'id'
    product = {
        'term': {'@id': term_id}
    }
    cycle = {'products': [product]}
    impact = {'product': {'@id': term_id}}

    # no product
    assert not get_product(impact)

    # with cycle and product
    impact['cycle'] = cycle
    assert get_product(impact) == product


def test_impact_value():
    impact = {
        'emissionsResourceUse': [
            {
                'term': {
                    '@id': 'ch4ToAirSoilFlux',
                    'termType': 'emission'
                },
                'value': 100
            }
        ]
    }
    # multiplies the emissionsResourceUse values with a coefficient
    assert impact_value('', impact, 'co2EqGwp100ExcludingClimate-CarbonFeedbacksIpcc2013') == 2850


def test_get_region_id():
    impact = {'country': {'@id': ''}}

    impact['country']['@id'] = 'region-world'
    assert get_region_id(impact) == 'region-world'
    impact['country']['@id'] = 'GADM-AUS'
    assert get_region_id(impact) == 'GADM-AUS'
    impact['country']['@id'] = 'GADM-AUS.101_1'
    assert get_region_id(impact) == 'GADM-AUS.101_1'
    impact['country']['@id'] = 'GADM-AUS.1.2_1'
    assert get_region_id(impact) == 'GADM-AUS.1_1'
    impact['country']['@id'] = 'GADM-ZAF.5.1.2_1'
    assert get_region_id(impact) == 'GADM-ZAF.5_1'
