from minetext.ElasticsearchUtils import ElasticsearchUtils
from minetext.FiledownloadUtil import FileDownloadUtil
from minetext.count_txt import count_words_txt
from minetext.mine import Mine
from typing import List, Optional


def search(term: str, title: Optional[List[str]] = None, date: Optional[List[str]] = None,
           format: Optional[List[str]] = None, language: Optional[List[str]] = None,
           author: Optional[List[str]] = None):
    """

    :param term:
    :param title:
    :param date:
    :param format:
    :param language:
    :param author:
    :return:
    """
    print(f'Search with term: {term}')
    es = ElasticsearchUtils()

    # Loop through all documents in Elasticsearch
    page = es.search(term, title, date, format, language, author)
    mine_list = []

    for hit in page['hits']['hits']:
        mine = Mine(hit['_source']['mine'])
        mine.content = hit['_source']['content']
        mine.files = hit['_source']['origin']['files']
        mine_list.append(mine)

    return mine_list


def download_files(files):
    """

    :param files:
    :return:
    """
    for file in files:
        for k in file:
            if k == 'normalized_filename':
                file_name = file[k]
            if k == 'url':
                file_url = file[k]
    fd = FileDownloadUtil()
    fd.save(file_url, file_name)
    print('Download files...')


def count_words(text):
    """

    :param text:
    :return:
    """
    word_count = count_words_txt(text)
    return word_count


rs = search('Simon', [], [2016,2013], None, None,['Hamer'])
print(rs[0].dc_abstract)
download_files(rs[0].files)
print('file downloaded...')
print('exiting program...')
