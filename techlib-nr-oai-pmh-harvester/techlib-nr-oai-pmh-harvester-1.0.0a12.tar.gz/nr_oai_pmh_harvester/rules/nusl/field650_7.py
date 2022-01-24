from invenio_db import db
from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer
from oarepo_taxonomies.utils import get_taxonomy_json
from sqlalchemy.exc import ProgrammingError

from nr_oai_pmh_harvester.query import get_query_by_slug


@rule("nusl", "marcxml", "/650_7", phase="pre")
def call_subject(el, **kwargs):
    return subject(el, **kwargs)  # pragma: no cover


def subject(el, **kwargs):
    res = {}
    subjects = []
    keywords = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            subjects, keywords = get_subject_keyword(_, keywords, subjects)
    if isinstance(el, dict):
        subjects, keywords = get_subject_keyword(el, keywords, subjects)
    if subjects:
        res["subject"] = subjects
    if keywords:
        res["keywords"] = keywords
    if res:
        return res
    else:
        return OAITransformer.PROCESSED  # pragma: no cover


def get_subject_keyword(_, keywords, subjects):
    subject = get_subject(_)
    if subject:
        subjects += subject
    else:
        keyword = get_keyword(_)
        if keyword:
            keywords.append(keyword)
    return subjects, keywords


def get_subject(el):
    type_ = el.get("2", "").lower()
    type_dict = {
        "psh": get_psh,
        "czmesh": get_czmesh,
        "mednas": get_mednas
    }
    handler = type_dict.get(type_)
    if not handler:  # pragma: no cover
        return
    res = handler(el)
    if res:
        return res


def get_psh(el):
    url = el.get("0")
    slug = url.split("/")[-1].lower()
    query = get_query_by_slug("subjects", slug)
    term = query.one_or_none()
    if not term:
        return
    return get_taxonomy_json(code="subjects", slug=term.slug).paginated_data


def get_czmesh(el):
    slug = el.get("7", "").lower()
    query = get_query_by_slug("subjects", slug)
    try:
        term = query.one_or_none()
    except ProgrammingError:  # pragma: no cover
        db.session.commit()
        return
    if not term: # pragma: no cover
        return
    return get_taxonomy_json(code="subjects", slug=term.slug).paginated_data


def get_mednas(el):
    slug = el.get("7") or el.get("a", "")
    query = get_query_by_slug("subjects", slug)
    try:
        term = query.one_or_none()
    except ProgrammingError:  # pragma: no cover
        db.session.commit()
        return
    if term:
        return get_taxonomy_json(code="subjects", slug=term.slug).paginated_data


def get_keyword(el):
    keyword = el.get("a")
    if keyword:
        return {"cs": keyword}
