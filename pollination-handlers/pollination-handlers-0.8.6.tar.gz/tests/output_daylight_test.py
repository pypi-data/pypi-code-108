from pollination_handlers.outputs.daylight import read_df_from_folder, \
    sort_ill_from_folder, read_hours_from_folder, ill_credit_json_from_path


def test_read_df():
    res = read_df_from_folder('./tests/assets/df_results/')
    assert res == [[25.1, 0, 10, 100]]


def test_read_da():
    res = sort_ill_from_folder('./tests/assets/annual_dl_results/')
    assert res == [
        './tests/assets/annual_dl_results/TestRoom_1.ill',
        './tests/assets/annual_dl_results/TestRoom_2.ill',
        './tests/assets/annual_dl_results/sun-up-hours.txt'
    ]


def test_read_hours():
    res = read_hours_from_folder('./tests/assets/hours_results/')
    assert int(res[0][0]) == 206


def test_ill_credit_json_from_path():
    res = ill_credit_json_from_path('./tests/assets/credit_summary.json')
    print(res)
    assert 'credits: 2' in res    
