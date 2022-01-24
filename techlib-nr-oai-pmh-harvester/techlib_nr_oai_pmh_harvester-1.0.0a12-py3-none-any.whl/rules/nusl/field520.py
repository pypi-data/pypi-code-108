from nr_oai_pmh_harvester.rules.nusl.field04107 import get_language_taxonomy

from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/520__", phase="pre")
def call_abstract(el, **kwargs):
    return abstract(el, **kwargs) # pragma: no cover


def abstract(el, **kwargs):
    res = {}
    if isinstance(el, (list, tuple)):
        for _ in el:
            add_abstract(_, res)
    if isinstance(el, dict):
        add_abstract(el, res)
    return {"abstract": res}


def add_abstract(_, res):
    abstract = get_abstract(_)
    if abstract:
        res.update(abstract)


def get_abstract(abstract_dict):
    taxonomy_list = get_language_taxonomy(abstract_dict.get("9", "cze"))
    if not taxonomy_list:
        return
    lang_json = taxonomy_list[0]
    return {
        lang_json["alpha2"]: abstract_dict.get("a")
    }
