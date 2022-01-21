import requests

def_url = 'http://localhost:8000/api/'

url_list = [
    ["_list_countries_method", 'list_countries'],
    [
        '_list_countries_method?curr_iso=LSL',
        'list_countries filter currency=LSL (Lesotho loti)',
    ],
    ['_find_country_method?cca=ZAF', 'find_country filter cca3 = ZAF'],
    ['_find_country_method?cca=ZA', 'find_country filter cca3 = ZA'],
]

for method, end_point in url_list:
    print(f'API Endpoint: {end_point}')
    print(f'Method: {method}')
    response = requests.get(f'{def_url}{method}')
    ret_data = response.json()
    for rec in ret_data:
        print(rec)
    print(response.status_code)
    print()


print('API Endpoint: delete_country where cca = ZA')
print('Method: _delete_country_method')
response = requests.get(f'{def_url}_list_countries_method')
ret_data = response.json()
for rec in ret_data:
    print(rec)
response = requests.post(f'{def_url}_delete_country_method', {'cca': 'DER'})
ret_data = response.json()
for rec in ret_data:
    print(rec)
print(response.status_code)
response = requests.get(f'{def_url}_list_countries_method')
ret_data = response.json()
for rec in ret_data:
    print(rec)
print()

pass
