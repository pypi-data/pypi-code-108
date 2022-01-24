from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/035__", phase="pre")
def call_original_record_oai(el, **kwargs):
    return original_record_oai(el, **kwargs) # pragma: no cover


def original_record_oai(el, **kwargs):
    return {
        "recordIdentifiers": {
            "originalRecordOAI": el["a"]
        }
    }
