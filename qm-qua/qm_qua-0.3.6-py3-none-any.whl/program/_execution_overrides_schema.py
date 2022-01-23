from marshmallow_polyfield import PolyField

from qm.pb.frontend_pb2 import ExecutionOverrides
from marshmallow import Schema, fields, post_load, ValidationError


def load_overrides(overrides):
    return ExecutionOverridesSchema().load(overrides)


def _non_empty(v):
    if len(v) == 0:
        raise ValidationError("List must be non-empty")


def _waveforms_schema_deserialization_disambiguation(data, _o):
    if isinstance(data, list):
        return fields.List(fields.Float(), required=True, validate=_non_empty)
    else:
        return fields.Float(required=True)


class ExecutionOverridesSchema(Schema):
    waveforms = fields.Dict(
        keys=fields.String(),
        values=PolyField(
            deserialization_schema_selector=_waveforms_schema_deserialization_disambiguation,
            required=True,
        ),
    )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        result = ExecutionOverrides()

        try:
            waveforms = data["waveforms"]
        except KeyError:
            waveforms = {}

        for k, v in waveforms.items():
            iw = result.waveforms.get_or_create(k)
            samples = v if isinstance(v, list) else [v]
            for s in samples:
                iw.samples.append(s)

        return result
