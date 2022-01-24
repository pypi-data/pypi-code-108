from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/identifier/uri/value", phase="pre")
def call_original_record_id(el, **kwargs):
    return original_record_id(el, **kwargs)  # pragma: no cover


def original_record_id(el, **kwargs):
    id_ = el[0][0]
    assert isinstance(id_, str)
    return {
        "recordIdentifiers": {
            "originalRecord": id_
        }
    }
