#! /usr/bin/env python
import sys
from elasticsearch import Elasticsearch
from yscoverage import dataset

"""Install elasticsearch docker container

https://www.elastic.co/guide/en/elasticsearch/reference/7.8/docker.html

Download container:
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.8.0

Start a single node:
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.8.0

Now you can access the REST APIs at http://localhost:9200

Configuration:
https://www.elastic.co/guide/en/elasticsearch/reference/7.8/settings.html

Production settings:
https://www.elastic.co/guide/en/elasticsearch/reference/7.8/important-settings.html

General recommendations:
https://www.elastic.co/guide/en/elasticsearch/reference/7.8/general-recommendations.html

- Limit doc default size is 100MB

Core concepts:
https://docs.bonsai.io/article/121-elasticsearch-core-concepts

- Indexes point to primary shard (the document)
"""


def populate_index(index, data):

    es = Elasticsearch()

    for i, row in enumerate(data, start=1):
        es.index(index=index, id=i, body=row)


def search_index_leaf(index, name, line):

    should = []

    for item in line:
        should.append({'term': {'xpath': item}})

    query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'match': {
                            'leaf': name
                        }
                    }
                ],
                'should': should
            }
        }
    }

    es = Elasticsearch()
    res = es.search(index=index, body=query)
    return res


if __name__ == '__main__':
    path = sys.argv[1]
    model = sys.argv[2]
    leaf = sys.argv[3]
    cli = sys.argv[4]
    addons = ['nodetype', 'datatype']
    print('create dataset')
    ds = dataset.dataset_for_directory(
        path, model, addons=addons, reference=None, all_data=False
    )
    print('populate index')
    populate_index(model, ds)
    print('search index')
    res = search_index_leaf(model, leaf, cli)
    print(res)
