import requests

ENDPOINT = 'https://openlibrary.org/search/authors.json'
ENDPOINT_WORKS = 'https://openlibrary.org/authors'


def get_author(
        requested_author: str,
        split_list_into_batches: bool = False
) -> tuple:
    params = {}
    params['q'] = requested_author
    print(f'Calling endpoint Get Authors'  + ENDPOINT)
    response = requests.get(ENDPOINT, params=params)
    docs = []
    for doc in response.json()['docs']:
        doc['requested_author'] =  requested_author
        docs.append(doc)
    if split_list_into_batches:
        yield from docs
    else:
        yield docs


if __name__ == '__main__':
    i = 0 
    for a in get_author('George R. R. Martin', True):
        
        print(a)
        print (i)
        i = i + 1
    