import traceback
from typing import Union, List

from flask_taxonomies.query import TaxonomyQueryNotSupported
from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.query import find_in_title_jsonb
from nr_oai_pmh_harvester.rules.utils import filter_language, remove_country_from_lang_codes
from nr_oai_pmh_harvester.rules.utils.subject import fix_mesh
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/subject", phase="pre")
def call_subject(el, **kwargs):
    return subject(el, **kwargs)  # pragma: no cover


def subject(el, **kwargs):
    assert len(el) <= 1
    filtred_el = filter_language(el)
    reformated_el = reformat(filtred_el)
    res = get_subject_or_keyword(reformated_el)
    return res



def get_subject_or_keyword(reformated_el):
    subjects = []
    keywords = []
    for word_dict in reformated_el:
        try:
            res = []
            links = []
            for k, v in word_dict.items():
                subject = get_subject_by_title(v, k)
                if isinstance(subject, dict):
                    subject = [subject]
                if subject:
                    assert isinstance(subject, list), f"{subject} is not list"
                    only_subject = [_ for _ in subject if not _["is_ancestor"]][0]
                    link = only_subject["links"]["self"]
                    if link not in links:
                        links.append(link)
                        res.extend(subject)
            new_subject = res
        except (TaxonomyQueryNotSupported, AttributeError):
            new_subject = None
        if new_subject:
            subjects.extend(new_subject)
        else:
            keywords.append(remove_country_from_lang_codes(word_dict))
    return {
        "subject": fix_mesh(subjects),
        "keywords": keywords
    }


def reformat(el):
    new_el = {}
    for k, v in el.items():
        if isinstance(v, list):
            new_el[k] = v
        elif isinstance(v, str):
            new_el[k] = [v]
        else:
            raise Exception(f'Value "{v}" must be string or list instead of {type(v)}')
    el = new_el
    res = []
    values = el.values()
    keys = list(el.keys())
    iterator_ = zip(*values)
    for word_set in iterator_:
        dict_ = {}
        for i, word in enumerate(word_set):
            dict_[keys[i]] = word
        res.append(dict_)
    return res


def get_subject_by_title(value: str, lang: str, ) -> Union[None, List]:
    value = value.strip()
    value = value.replace('"', '')
    value = value.replace('\\', '')
    if len(lang) != 2:
        lang = lang[:2]
    if len(value) == 0 or not value:
        return
    query = find_in_title_jsonb("subjects", f"title.{lang}", value)
    terms = query.all()
    if not terms:
        return
    elif len(terms) == 1:
        return get_taxonomy_json(code="subjects", slug=terms[0].slug).paginated_data
    else:
        res = []
        for term in terms:
            extra_data = term.extra_data
            title = extra_data.get("title", {}).get(lang)
            if title == value:
                res.extend(get_taxonomy_json(code="subjects", slug=term.slug).paginated_data)
        return res
