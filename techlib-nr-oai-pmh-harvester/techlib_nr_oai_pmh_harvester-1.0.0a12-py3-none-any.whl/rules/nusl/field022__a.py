from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/022__/a", phase="pre")
def call_issn(el, **kwargs):
    return issn(el, **kwargs) # pragma: no cover


def issn(el, **kwargs):
    return {
        "workIdentifiers": {
            "issn": [el]
        }
    }
