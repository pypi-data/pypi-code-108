from stanfordcorenlp import StanfordCoreNLP

def get_entity_list(text,resource_path=r'./stanford-corenlp-full-2018-02-27',language='zh'):

    stanford_model = StanfordCoreNLP(resource_path, lang=language)

    res = stanford_model.ner(text)

    return res