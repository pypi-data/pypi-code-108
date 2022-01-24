from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer

from nr_oai_pmh_harvester.rules.nusl.field24500 import get_title_dict, get_title


@rule("nusl", "marcxml", "/24633", phase="pre")
def call_title_alternate(el, **kwargs):
    return title_alternate(el, **kwargs)  # pragma: no cover


def title_alternate(el, **kwargs):
    return get_title(el, kwargs, field="titleAlternate")
