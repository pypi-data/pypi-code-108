from elasticsearch import Elasticsearch


class ElasticsearchUtils:
    """
    This class provides all necessary functions to interact with Elasticsearch
    """

    def __init__(self):
        self._es = Elasticsearch('http://141.5.110.132:9200')

    def search(self, term: str, title=None, date=None, format=None, language=None, author=None):
        """

        :param term:
        :param title:
        :param date:
        :param format:
        :param language:
        :param author:
        :return:
        """
        filters = []
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": term
                            }
                        }
                    ]
                }
            }
        }
        # Add the filter is query for elasticsearch
        if title:
            titles = ', '.join(title)
            filters.append({"match": {"mine.dc_title": titles}})
        if date:
            dates = ', '.join("{0}".format(i) for i in date)
            filters.append({"match": {"mine.dc_date": dates}})
        if format:
            formats = ', '.join(format)
            filters.append({"match": {"mine.dc_format": formats}})
        if language:
            languages = ', '.join(language)
            filters.append({"match": {"mine.dc_language": languages}})
        if author:
            authors = ', '.join(author)
            filters.append({"match": {"mine.schema_org_Person": authors}})

        if len(filters) > 0:
            search_body['query']['bool']['filter'] = filters

        s = self._es.search(index='goescholar', body=search_body, scroll='2m')
        return s


if __name__ == '__main__':
    es = ElasticsearchUtils()
    print(es.search('Simon', [], [2013],None,None,['Hamer']))
