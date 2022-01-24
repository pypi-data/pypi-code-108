from oarepo_taxonomies.utils import get_taxonomy_json
from slugify import slugify

from nr_oai_pmh_harvester.query import find_in_title, find_in_json_list
from oarepo_oai_pmh_harvester.transformer import OAITransformer


def get_study_field(field: str, programme: str = None, akvo: str = None,  is_program: bool = False):
    sqlalchemy_query = find_in_title(field, "studyfields")
    terms = sqlalchemy_query.all()
    if not terms:
        sqlalchemy_query = find_in_title(field, "studyfields", first_lang="de", second_lang="fr")
        terms = sqlalchemy_query.all()
    if not terms:
        terms = find_in_json_list("studyfields", "aliases", field).all()
    if not terms:
        return OAITransformer.PROCESSED
    if terms:
        return choose_term(terms, programme, akvo=akvo, is_program=is_program)


def choose_term(terms, programme: str = None, akvo: str = None, is_program: bool = False):
    res = []
    l = len(terms)
    if l == 1:
        term = terms[0]
        res += get_taxonomy_json("studyfields", slug=term.slug).paginated_data
    if l > 1:
        if is_program:
            new_terms = [term for term in terms if not term.parent_slug]
            if new_terms:
                terms = new_terms
        if akvo:
            for term in terms:
                extra_data = term.extra_data
                term_akvo = extra_data.get("AKVO")
                if term_akvo and term_akvo == akvo:
                    return get_taxonomy_json("studyfields", slug=term.slug).paginated_data
        if programme:
            parent_slug = f"p-{slugify(programme)}"
            for term in terms:
                if term.parent_slug == parent_slug:
                    res += get_taxonomy_json("studyfields", slug=term.slug).paginated_data
                    break
            if len(res) == 0:
                res += get_taxonomy_json("studyfields", slug=terms[0].slug).paginated_data
        else:
            res += get_taxonomy_json("studyfields", slug=terms[0].slug).paginated_data
    return {"studyField": res}