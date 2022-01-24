from flask_taxonomies.models import TaxonomyTerm
from flask_taxonomies.proxies import current_flask_taxonomies
from sqlalchemy import func


def find_in_json_list(taxonomy_code: str, field: str, value: str):
    sqlalchemy_query = current_flask_taxonomies.list_taxonomy(f'{taxonomy_code}')
    sqlalchemy_query = sqlalchemy_query.filter(
        func.jsonb_extract_path(TaxonomyTerm.extra_data, field).op('?')(
            value))
    return sqlalchemy_query


def find_in_json(taxonomy_code: str, field: str, value: str):
    sqlalchemy_query = current_flask_taxonomies.list_taxonomy(taxonomy_code)
    sqlalchemy_query = current_flask_taxonomies.apply_term_query(sqlalchemy_query,
                                                                 f'{field}:{value}', taxonomy_code)
    return sqlalchemy_query


def get_query_by_slug(taxonomy_code: str, slug: str):
    slug = f"*.{slug.lower()}"
    sqlalchemy_query = current_flask_taxonomies.list_taxonomy(f'{taxonomy_code}')
    sqlalchemy_query = sqlalchemy_query.filter(
        TaxonomyTerm.slug.op('~')(slug))
    return sqlalchemy_query


def find_in_title(field: str, taxonomy_code: str, first_lang: str = "cs", second_lang: str = "en"):
    sqlalchemy_query = current_flask_taxonomies.list_taxonomy(taxonomy_code)
    sqlalchemy_query = current_flask_taxonomies.apply_term_query(sqlalchemy_query,
                                                                 f'title.{first_lang}:"{field}" OR '
                                                                 f'title.{second_lang}:"{field}"',
                                                                 taxonomy_code)
    return sqlalchemy_query


def find_in_title_jsonb(value: str, taxonomy_code: str, lang: str = "cs"):
    json_ = '{"title": {"%s": "%s"}}' % (lang, value)
    sqlalchemy_query = current_flask_taxonomies.list_taxonomy(taxonomy_code)
    sqlalchemy_query = sqlalchemy_query.filter(TaxonomyTerm.extra_data.op("@>")(json_))
    return sqlalchemy_query
