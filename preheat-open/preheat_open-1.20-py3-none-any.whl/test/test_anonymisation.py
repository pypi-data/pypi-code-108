def test_anonymised_api_usage():
    from preheat_open import set_api_key
    from preheat_open.building import Building, available_buildings
    from preheat_open.test import ANONYMISED_API_KEY, SHORT_TEST_PERIOD

    set_api_key(ANONYMISED_API_KEY)

    df = available_buildings()
    b = Building(int(df["locationId"][0]))
    assert isinstance(b, Building)
    assert b.location["address"] == ""
    assert b.location["organizationName"] == ""
    assert b.location["parentOrganizationName"] == ""

    b.load_data(*SHORT_TEST_PERIOD)
