import os
import json
import pickle
import math
import logging
import string
from django.conf import settings
from ..searchbot.settings import APP_DIR

logger = logging.getLogger(__name__)

def generate_tfidf_index():
    tfidf = {}
    try:
        os.remove(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'))
    except OSError:
        pass
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/discovered_pages.json')) as f:
        data = json.loads(f.read())
        with open(os.path.join(APP_DIR, 'data/stopwords.txt')) as f:
            stopwords = f.read().split("\n")
            for document in data:
                bag_of_words = ""
                bag_of_words = ' '.join([document['title'].lower(), document['keywords'].lower()])
                clean_bag_of_words = [w.translate(str.maketrans('', '', string.punctuation)) for w in bag_of_words.split()]
                #words = bag_of_words.split()
                for word in set(clean_bag_of_words):
                    if word not in stopwords:
                        if word not in tfidf.keys():
                            tfidf[word] = []
                        tfidf[word].append({
                            **document,
                            'termFrequency' :clean_bag_of_words.count(word)/ len(clean_bag_of_words),
                            'inverseDocumentFrequency': math.log10(len(data) / len([x for x in data if word in x['title'].lower().translate(str.maketrans('', '', string.punctuation)) or word in x['keywords'].lower().translate(str.maketrans('', '', string.punctuation))])),
                            'tfidf': (clean_bag_of_words.count(word)/ len(clean_bag_of_words)) * (math.log10(len(data) / len([x for x in data if word in x['title'].lower().translate(str.maketrans('', '', string.punctuation)) or word in x['keywords'].lower().translate(str.maketrans('', '', string.punctuation))])))
                        })
            with open(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'), 'wb') as f:
                pickle.dump(tfidf, f)
                logger.debug("Completed indexing exported data")

def query_document_index(query):
    results = []
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'), 'rb') as dbindex:
        data = pickle.load(dbindex)
        for q in query.lower().translate(str.maketrans('', '', string.punctuation)).split():
            try:
                results.append(data[q])
            except:
                continue
        return sorted([item for sublist in results for item in sublist], key=lambda k: k['tfidf'], reverse=True)
