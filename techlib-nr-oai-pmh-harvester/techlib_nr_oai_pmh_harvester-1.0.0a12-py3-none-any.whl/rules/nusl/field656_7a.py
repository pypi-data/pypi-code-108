from nr_oai_pmh_harvester.rules.utils.study_field import get_study_field
from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/656_7/a", phase="pre")
def call_studyfield(el, **kwargs):
    return studyfield(el, **kwargs)


def studyfield(el, **kwargs):
    if "/" not in el:
        return get_study_field(el.strip())
    else:
        programme, field = el.split("/", maxsplit=1)
        field = field.strip()
        return get_study_field(field, programme=programme)
