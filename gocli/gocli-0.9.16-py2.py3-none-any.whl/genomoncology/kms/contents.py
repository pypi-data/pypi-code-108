from cytoolz.curried import curry
from glom import Coalesce

from genomoncology.kms.match import (
    calls_to_alterations,
    transform_match_response,
)
from genomoncology.parse import DocType, __TYPE__
from genomoncology.parse.ensures import ensure_collection


@curry
def match_contents(calls, diseases=None, include_content=True, sdk=None):
    alterations = calls_to_alterations(calls)
    diseases = ensure_collection(diseases or ["ANY"])

    response = sdk.call_with_retry(
        sdk.contents.match_contents_post,
        alterations=alterations,
        diseases=diseases,
        include_content=include_content,
    )

    return transform_match_response(response, DEFAULT_SPEC)


DEFAULT_SPEC = {
    __TYPE__: Coalesce(default=DocType.CONTENT.value),
    "title": "title",
    "body": "body",
    "url": lambda content: f"https://www.mycancergenome.org{content.url}",
    "type": "type",
    "trigger_alterations": "trigger_alterations",
    "trigger_genes": "trigger_genes",
    "trigger_diseases": "trigger_diseases",
}
