from invenio_pidstore.models import PersistentIdentifier

from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.models import OAIIdentifier


@rule("uk", "xoai", "/others/identifier", phase="pre")
def call_original_record_oai(el, **kwargs):
    return original_record_oai(el, **kwargs)  # pragma: no cover


def original_record_oai(el, **kwargs):
    value = el[-1]
    assert isinstance(value, str)
    oai_identifer = OAIIdentifier.query.filter_by(oai_identifier=value).one_or_none()
    if oai_identifer:
        uuid = oai_identifer.oai_record_id
        pid = PersistentIdentifier.query.filter_by(object_uuid=uuid).one_or_none()
        control_number = pid.pid_value
        return {
            "control_number": control_number,
            "recordIdentifiers": {
                "originalRecordOAI": value
            }
        }
    return {
        "recordIdentifiers": {
            "originalRecordOAI": value
        }
    }
