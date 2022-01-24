from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_taxonomies.utils import get_taxonomy_json
from sqlalchemy.orm.exc import NoResultFound


@rule("nusl", "marcxml", "/04107", phase="pre")
def call_language(el, **kwargs):
    return language(el, **kwargs)  # pragma: no cover


def language(el, **kwargs):
    data = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            data.extend(get_language_list(_))
            # data = get_language_list(data, _)
    if isinstance(el, dict):
        data.extend(get_language_list(el))
    return {
        "language": data
    }


def get_language_list(el):
    res = []
    for v in el.values():
        lang_taxonomy = get_language_taxonomy(v)
        if lang_taxonomy:
            res.extend(lang_taxonomy)
    return res


def get_language_taxonomy(lang_code):
    try:
        return get_taxonomy_json(code="languages", slug=lang_code).paginated_data
    except NoResultFound:
        pass
