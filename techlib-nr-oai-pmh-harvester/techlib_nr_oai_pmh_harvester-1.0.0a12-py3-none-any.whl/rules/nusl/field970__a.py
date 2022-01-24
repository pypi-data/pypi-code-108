from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/970__/a", phase="pre")
def call_nusl_oai(el, **kwargs):
    return catalogue_sys_no(el, **kwargs) # pragma: no cover


def catalogue_sys_no(el, **kwargs):
    return {
        "recordIdentifiers":
            {
                "catalogueSysNo": el
            }
    }
