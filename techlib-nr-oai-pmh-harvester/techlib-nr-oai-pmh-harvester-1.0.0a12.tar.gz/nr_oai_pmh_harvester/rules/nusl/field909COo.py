from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/909CO", phase="pre")
def call_nusl_oai(el, **kwargs):
    return nusl_oai(el, **kwargs)  # pragma: no cover


def nusl_oai(el, **kwargs):
    url = el.get("o")
    if url:
        return {
            "recordIdentifiers": {
                "nuslOAI": url
            }
        }
    return {  # pragma: no cover
        "recordIdentifiers": {
            "nuslOAI": ["Nutná kontrola"]
        }
    }
