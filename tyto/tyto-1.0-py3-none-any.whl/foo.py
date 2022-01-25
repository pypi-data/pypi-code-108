import requests
import json

response = requests.get('http://www.ebi.ac.uk/ols/api/ontologies/so/terms')
response = response.json()
print(response)
raise Exception()
response = requests.get('http://www.ebi.ac.uk/ols/api/ontologies?size=1')
response = response.json()
total_pages = response['page']['totalElements']
response = requests.get(f'http://www.ebi.ac.uk/ols/api/ontologies?size={total_pages}')
response = response.json()
ontology_dict = {}
ontologies = response['_embedded']['ontologies']
for o in ontologies:
    short_id = o['ontologyId']
    iri = o['config']['id']
    ontology_dict[iri] = short_id
for iri, short_id in ontology_dict.items():
    print(iri, short_id)

"""
{'size': 20, 'totalElements': 264, 'totalPages': 14, 'number': 0}
{'first': {'href': 'https://www.ebi.ac.uk/ols/api/ontologies?page=0&size=20'}, 'self': {'href': 'https://www.ebi.ac.uk/ols/api/ontologies'}, 'next': {'href': 'https://www.ebi.ac.uk/ols/api/ontologies?page=1&size=20'}, 'last': {'href': 'https://www.ebi.ac.uk/ols/api/ontologies?page=13&size=20'}}
{'ontologies': [{'ontologyId': 'aeo', 
"""
