from hestia_earth.models.blonkConsultants2016.utils import get_emission_factor


def test_get_emission_factor_no_product_match():
    cycle = {'site': {'country': {'@id': 'GADM-ALB'}, 'siteType': 'permanent pasture'}}

    assert get_emission_factor(cycle, 'co2LandUseChange') == 566.523273292322
    assert get_emission_factor(cycle, 'ch4forestBiomassBurning') == 0.29
    assert get_emission_factor(cycle, 'n2oforestBiomassBurning') == 0.016
