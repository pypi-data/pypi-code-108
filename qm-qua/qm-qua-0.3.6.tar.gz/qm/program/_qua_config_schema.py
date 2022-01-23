from typing import List, Any, Mapping

import numpy as np
from marshmallow import Schema, fields, post_load, ValidationError, validates_schema
from marshmallow_polyfield import PolyField

from qm._errors import ConfigValidationException
from qm.capabilities import ServerCapabilities
from qm.logger import logger
from qm.pb.inc_qua_config_pb2 import QuaConfig


def validate_config(config):
    pass


def _validate_config_capabilities(pb_config, server_capabilities: ServerCapabilities):
    if not server_capabilities.supports_multiple_inputs_for_element:
        for el_name, el in list(pb_config.v1beta.elements.items()):
            if el.HasField("multipleInputs"):
                raise ConfigValidationException(
                    f"Server does not support multiple inputs for elements used in "
                    f"'{el_name}'"
                )

    if not server_capabilities.supports_analog_delay:
        for con_name, con in list(pb_config.v1beta.controllers.items()):
            for port_id, port in list(con.analogOutputs.items()):
                if port.delay != 0:
                    raise ConfigValidationException(
                        f"Server does not support analog delay used in controller "
                        f"'{con_name}', port {port_id}"
                    )

    if not server_capabilities.supports_shared_oscillators:
        for el_name, el in list(pb_config.v1beta.elements.items()):
            if el.HasField("namedOscillator"):
                raise ConfigValidationException(
                    f"Server does not support shared oscillators for elements used in "
                    f"'{el_name}'"
                )

    if not server_capabilities.supports_channel_weights:
        for con_name, con in list(pb_config.v1beta.controllers.items()):
            for port_id, port in list(con.analogOutputs.items()):
                if len(port.channelWeights) > 0:
                    raise ConfigValidationException(
                        f"Server does not support channel weights used in controller "
                        f"'{con_name}', port {port_id}"
                    )


def load_config(config):
    return QuaConfigSchema().load(config)


PortReferenceSchema = fields.Tuple(
    (fields.String(), fields.Int()),
    description="Controller port to use. "
    "Tuple of: ([str] controller name, [int] controller port)",
)


class UnionField(fields.Field):
    """Field that deserializes multi-type input data to app-level objects."""

    def __init__(self, val_types: List[fields.Field], **kwargs):
        self.valid_types = val_types
        super().__init__(**kwargs)

    def _deserialize(
        self, value: Any, attr: str = None, data: Mapping[str, Any] = None, **kwargs
    ):
        """
        _deserialize defines a custom Marshmallow Schema Field that takes in
        mutli-type input data to app-level objects.

        Parameters
        ----------
        value : {Any}
            The value to be deserialized.

        Keyword Parameters
        ----------
        attr : {str} [Optional]
            The attribute/key in data to be deserialized. (default: {None})
        data : {Optional[Mapping[str, Any]]}
            The raw input data passed to the Schema.load. (default: {None})

        Raises
        ----------
        ValidationError : Exception
            Raised when the validation fails on a field or schema.
        """
        errors = []
        # iterate through the types being passed into UnionField via val_types
        for field in self.valid_types:
            try:
                # inherit deserialize method from Fields class
                return field.deserialize(value, attr, data, **kwargs)
            # if error, add error message to error list
            except ValidationError as error:
                errors.append(error.messages)

        raise ValidationError(errors)


class AnalogOutputFilterDefSchema(Schema):
    feedforward = fields.List(
        fields.Float(),
        description="Feedforward taps for the analog output filter, range: [-1,1]. "
        "List of double",
    )
    feedback = fields.List(
        fields.Float(),
        description="Feedback taps for the analog output filter, range: (-1,1). "
        "List of double",
    )


class AnalogOutputPortDefSchema(Schema):
    offset = fields.Number(
        description="DC offset to the output, range: (-0.5, 0.5). "
        "Will be applied while quantum machine is open."
    )
    filter = fields.Nested(AnalogOutputFilterDefSchema)
    delay = fields.Int(description="Output's delay, in units of ns.")
    channel_weights = fields.Dict(
        keys=fields.Int(), values=fields.Number(), description=""
    )  # TODO: add description

    class Meta:
        title = "Analog output port"
        description = (
            "The specifications and properties of an analog output "
            "port of the controller."
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.AnalogOutputPortDec()
        item.offset = data["offset"]

        item.filter.SetInParent()
        if "filter" in data:
            if "feedforward" in data["filter"]:
                item.filter.feedforward.extend(data["filter"]["feedforward"])

            if "feedback" in data["filter"]:
                item.filter.feedback.extend(data["filter"]["feedback"])

        if "delay" in data:
            item.delay = data["delay"]
        else:
            item.delay = 0

        if "channel_weights" in data:
            for k, v in data["channel_weights"].items():
                item.channelWeights[k] = v

        return item


class AnalogInputPortDefSchema(Schema):
    offset = fields.Number(
        description="DC offset to the input, range: (-0.5, 0.5). "
        "Will be applied only when program runs."
    )

    gain_db = fields.Int(
        strict=True,
        description="Gain of the pre-ADC amplifier, in dB. Accepts integers in the "
        "range: -3 to 3",
    )

    class Meta:
        title = "Analog input port"
        description = (
            "The specifications and properties of an analog input "
            "port of the controller."
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.AnalogInputPortDec()
        if "offset" in data:
            item.offset = data["offset"]
        else:
            item.offset = 0.0
        if "gain_db" in data:
            item.gainDb.value = data["gain_db"]

        return item


class DigitalOutputPortDefSchema(Schema):
    offset = fields.Number()

    class Meta:
        title = "Digital port"
        description = (
            "The specifications and properties of a digital "
            "output port of the controller."
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalOutputPortDec()
        return item


class DigitalInputPortDefSchema(Schema):
    window = fields.Int(description="")  # TODO: add description
    polarity = fields.String(description="")  # TODO: add description
    threshold = fields.Number(description="")  # TODO: add description

    class Meta:
        title = "Digital input port"
        description = (
            "The specifications and properties of a digital input "
            "port of the controller."
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalInputPortDec()
        item.window = data["window"]
        if data["polarity"].upper() == "HIGH":
            item.polarity = QuaConfig.DigitalInputPortDec.ACTIVE_HIGH
        elif data["polarity"].upper() == "LOW":
            item.polarity = QuaConfig.DigitalInputPortDec.ACTIVE_LOW

        item.threshold = data["threshold"]

        return item


class ControllerSchema(Schema):
    type = fields.Constant("opx1")
    analog = fields.Dict(
        fields.Int(),
        fields.Nested(AnalogOutputPortDefSchema),
        description="a collection of analog output ports and the properties associated with them.",
    )

    analog_outputs = fields.Dict(
        fields.Int(),
        fields.Nested(AnalogOutputPortDefSchema),
        description="The analog output ports and their properties.",
    )
    analog_inputs = fields.Dict(
        fields.Int(),
        fields.Nested(AnalogInputPortDefSchema),
        description="The analog input ports and their properties.",
    )
    digital_outputs = fields.Dict(
        fields.Int(),
        fields.Nested(DigitalOutputPortDefSchema),
        description="The digital output ports and their properties.",
    )
    digital_inputs = fields.Dict(
        fields.Int(),
        fields.Nested(DigitalInputPortDefSchema),
        description="The digital inputs ports and their properties.",
    )

    class Meta:
        title = "controller"
        description = "The specification of a single controller and its properties."

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.ControllerDec()
        item.type = data["type"]

        if "analog" in data:
            # Deprecated in 0.0.41
            logger.warning(
                "'analog' under controllers.<controller> is deprecated. "
                "use 'analog_outputs' instead"
            )
            if "analog_outputs" in data:
                for k, v in data["analog_outputs"].items():
                    item.analogOutputs.get_or_create(k).CopyFrom(v)
            else:
                for k, v in data["analog"].items():
                    item.analogOutputs.get_or_create(k).CopyFrom(v)
        elif "analog_outputs" in data:
            for k, v in data["analog_outputs"].items():
                item.analogOutputs.get_or_create(k).CopyFrom(v)

        if "analog_inputs" in data:
            for k, v in data["analog_inputs"].items():
                item.analogInputs.get_or_create(k).CopyFrom(v)

        if "digital_outputs" in data:
            for k, v in data["digital_outputs"].items():
                item.digitalOutputs.get_or_create(k).CopyFrom(v)

        if "digital_inputs" in data:
            for k, v in data["digital_inputs"].items():
                item.digitalInputs.get_or_create(k).CopyFrom(v)

        return item


class DigitalInputSchema(Schema):
    delay = fields.Int(
        description="The delay to apply to the digital pulses. In ns."
        "An intrinsic negative delay of 136 ns exists by default"
    )
    buffer = fields.Int(
        description="Digital pulses played to this element will be convolved"
        "with a digital pulse of value 1 with this length [ns]"
    )
    output = PortReferenceSchema
    port = PortReferenceSchema

    class Meta:
        title = "Digital input"
        description = "The specification of the digital input of an element"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalInputPortReference()
        item.delay = data["delay"]
        item.buffer = data["buffer"]
        item.port.SetInParent()
        if "output" in data:
            # deprecation from 0.0.28
            logger.warning(
                "'output' under elements.<el>.digitalInputs.<name>.output is deprecated. "
                "use 'port' instead elements.<el>.digitalInputs.<name>.port"
            )
            item.port.controller = data["output"][0]
            item.port.number = data["output"][1]
        if "port" in data:
            item.port.controller = data["port"][0]
            item.port.number = data["port"][1]
        return item


class IntegrationWeightSchema(Schema):
    cosine = UnionField(
        [
            fields.List(fields.Tuple([fields.Float(), fields.Int()])),
            fields.List(fields.Float()),
        ],
        description="The integration weights for the cosine. "
        "Given as a list of tuples, each tuple in the format of: "
        "([double] weight, [int] duration). "
        "weight range: [-2048, 2048] in steps of 2**-15. "
        "duration is in ns and must be a multiple of 4.",
    )
    sine = UnionField(
        [
            fields.List(fields.Tuple([fields.Float(), fields.Int()])),
            fields.List(fields.Float()),
        ],
        description="The integration weights for the sine. "
        "Given as a list of tuples, each tuple in the format of: "
        "([double] weight, [int] duration). "
        "weight range: [-2048, 2048] in steps of 2**-15. "
        "duration is in ns and must be a multiple of 4.",
    )

    class Meta:
        title = "Integration weights"
        description = "The specification of measurements' integration weights."

    @staticmethod
    def build_iw_sample(data):
        if len(data) > 0 and not isinstance(data[0], tuple):
            data = np.round(2 ** -15 * np.round(np.array(data) / 2 ** -15), 20)
            new_data = []
            for s in data:
                if len(new_data) == 0 or new_data[-1][0] != s:
                    new_data.append((s, 4))
                else:
                    new_data[-1] = (new_data[-1][0], new_data[-1][1] + 4)
            data = new_data
        res = []
        for s in data:
            sample = QuaConfig.IntegrationWeightSample()
            sample.value = s[0]
            sample.length = s[1]
            res.append(sample)
        return res

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.IntegrationWeightDec()
        if "cosine" in data:
            item.cosine.extend(self.build_iw_sample(data["cosine"]))
        if "sine" in data:
            item.sine.extend(self.build_iw_sample(data["sine"]))
        return item


class WaveFormSchema(Schema):
    pass


class ConstantWaveFormSchema(WaveFormSchema):
    type = fields.String(description='"constant"')
    sample = fields.Float(description="Waveform amplitude, range: (-0.5, 0.5)")

    class Meta:
        title = "Constant waveform"
        description = "A waveform with a constant amplitude"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.WaveformDec()
        item.constant.SetInParent()
        item.constant.sample = data["sample"]
        return item


class ArbitraryWaveFormSchema(WaveFormSchema):
    type = fields.String(description='"arbitrary"')
    samples = fields.List(
        fields.Float(),
        description="list of values of an arbitrary waveforms, range: (-0.5, 0.5)",
    )
    max_allowed_error = fields.Float(
        description='"Maximum allowed error for automatic compression"'
    )
    sampling_rate = fields.Number(
        description='"Sampling rate to use in units of S/s (samples per second). '
        "Default is 1e9."
        'Cannot be set when is_overridable=True"'
    )
    is_overridable = fields.Bool(
        default=False,
        description="Allows overriding the waveform after"
        "compilation. Cannot use with the "
        "non-default sampling_rate",
    )

    class Meta:
        title = "arbitrary waveform"
        description = "The modulating envelope of an arbitrary waveform"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.WaveformDec()
        item.arbitrary.SetInParent()
        item.arbitrary.samples.extend(data["samples"])
        is_overridable = data.get("is_overridable", False)
        item.arbitrary.isOverridable = is_overridable
        max_allowed_error_key = "max_allowed_error"
        sampling_rate_key = "sampling_rate"
        has_max_allowed_error = max_allowed_error_key in data
        has_sampling_rate = sampling_rate_key in data
        if is_overridable and has_max_allowed_error:
            raise ValidationError(
                f"Overridable waveforms cannot have property ${max_allowed_error_key}"
            )
        if is_overridable and has_sampling_rate:
            raise ValidationError(
                f"Overridable waveforms cannot have property ${sampling_rate_key}"
            )
        if has_max_allowed_error and has_sampling_rate:
            raise ValidationError(
                f"Cannot use both '{max_allowed_error_key}' and '{sampling_rate_key}'"
            )
        if has_max_allowed_error:
            item.arbitrary.maxAllowedError.value = data[max_allowed_error_key]
        elif has_sampling_rate:
            item.arbitrary.samplingRate.value = data[sampling_rate_key]
        elif not is_overridable:
            item.arbitrary.maxAllowedError.value = 1e-4
        return item


def _waveform_schema_deserialization_disambiguation(object_dict, data):
    type_to_schema = {
        "constant": ConstantWaveFormSchema,
        "arbitrary": ArbitraryWaveFormSchema,
    }
    try:
        return type_to_schema[object_dict["type"]]()
    except KeyError:
        pass

    raise TypeError(
        "Could not detect type. "
        "Did not have a base or a length. "
        "Are you sure this is a shape?"
    )


_waveform_poly_field = PolyField(
    deserialization_schema_selector=_waveform_schema_deserialization_disambiguation,
    required=True,
)


class DigitalWaveFormSchema(Schema):
    samples = fields.List(
        fields.Tuple([fields.Int(), fields.Int()]),
        description="The digital waveform. "
        "Given as a list of tuples, each tuple in the format of: "
        "([int] state, [int] duration). "
        "state is either 0 or 1 indicating whether the digital output is off or on. "
        "duration is in ns. "
        "If the duration is 0, it will be played until the reminder of the analog pulse",
    )

    class Meta:
        title = "Digital waveform"
        description = "The samples of a digital waveform"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalWaveformDec()
        for sample in data["samples"]:
            s = item.samples.add()
            s.value = bool(sample[0])
            s.length = int(sample[1])
        return item


class MixerSchema(Schema):
    freq = fields.Int(
        description="element resonance frequency associated with correction matrix"
    )
    intermediate_frequency = fields.Int(
        description="The intermediate frequency associated with the correction matrix"
    )
    lo_freq = fields.Int(description="LO frequency associated with correction matrix")
    lo_frequency = fields.Int(
        description="The LO frequency associated with the correction matrix"
    )
    correction = fields.Tuple(
        (fields.Number(), fields.Number(), fields.Number(), fields.Number()),
        description="A 2x2 matrix entered as a 4 elements list specifying the "
        "correction matrix. "
        "Each element is a double in the range of (-2,2)",
    )

    class Meta:
        title = "Mixer"
        description = """The specification of the correction matrix for an IQ mixer. 
        This is a list of correction matrices for each LO and IF frequencies."""

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.CorrectionEntry()

        lo_frequency = 0
        if "lo_freq" in data:
            # Deprecated in 0.0.45
            logger.warning(
                "'lo_freq' under mixers.<mixer> is deprecated. "
                "use 'lo_frequency' instead"
            )

            item.loFrequency = data["lo_freq"]
            lo_frequency = data["lo_freq"]

        if "lo_frequency" in data:
            item.loFrequency = data["lo_frequency"]
            lo_frequency = data["lo_frequency"]

        if "freq" in data:
            # Deprecated in 0.0.45
            logger.warning(
                "'freq' under mixers.<mixer> is deprecated. "
                "use 'intermediate_frequency' instead"
            )
            item.frequency = data["freq"] - lo_frequency

        if "intermediate_frequency" in data:
            item.frequency = abs(data["intermediate_frequency"])
            item.frequencyNegative = data["intermediate_frequency"] < 0

        item.correction.SetInParent()
        item.correction.v00 = data["correction"][0]
        item.correction.v01 = data["correction"][1]
        item.correction.v10 = data["correction"][2]
        item.correction.v11 = data["correction"][3]
        return item


class PulseSchema(Schema):
    operation = fields.String(
        description="The type of operation. Possible values: 'control', 'measurement'"
    )
    length = fields.Int(
        description="The length of pulse [ns]. Possible values: 16 to 2^31-1 in steps "
        "of 4"
    )
    waveforms = fields.Dict(
        fields.String(),
        fields.String(description="The name of analog waveform to be played."),
        description="""The specification of the analog waveform to be played.
        If the associated element has a single input, then the key is "single".
        If the associated element has "mixInputs", then the keys are "I" and "Q".""",
    )
    digital_marker = fields.String(
        description="The name of the digital waveform to be played with this pulse."
    )
    integration_weights = fields.Dict(
        fields.String(),
        fields.String(
            description="The name of the integration weights as it appears under the"
            ' "integration_weigths" entry in the configuration dict.'
        ),
        description="The name of the integration weight to be used in the program.",
    )

    class Meta:
        title = "pulse"
        description = """The specification and properties of a single pulse and to the 
          measurement associated with it."""

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.PulseDec()
        item.length = data["length"]
        if data["operation"] == "measurement":
            item.operation = QuaConfig.PulseDec.MEASUREMENT
        elif data["operation"] == "control":
            item.operation = QuaConfig.PulseDec.CONTROL
        if "integration_weights" in data:
            for k, v in data["integration_weights"].items():
                item.integrationWeights[k] = v
        if "waveforms" in data:
            for k, v in data["waveforms"].items():
                item.waveforms[k] = v
        if "digital_marker" in data:
            item.digitalMarker.value = data["digital_marker"]
        return item


class SingleInputSchema(Schema):
    port = PortReferenceSchema

    class Meta:
        title = "Single input"
        description = (
            "The specification of the input of an element which has a single input port"
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.SingleInput()
        _port(item.port, data["port"])
        return item


class HoldOffsetSchema(Schema):
    duration = fields.Int(description="""The ramp to zero duration, in ns""")

    class Meta:
        title = "Hold offset"
        description = "When defined, makes the element sticky"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.HoldOffset()
        item.duration = data["duration"]
        return item


class MixInputSchema(Schema):
    I = PortReferenceSchema
    Q = PortReferenceSchema
    mixer = fields.String(
        description="""The mixer used to drive the input of the element,
        taken from the names in mixers entry in the main configuration."""
    )
    lo_frequency = fields.Int(
        description="The frequency of the local oscillator which drives the mixer."
    )

    class Meta:
        title = "Mixer input"
        description = (
            "The specification of the input of an element which is driven by an "
            " IQ mixer"
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.MixInputs()
        _port(item.I, data["I"])
        _port(item.Q, data["Q"])
        item.mixer = data.get("mixer", "")
        item.loFrequency = data.get("lo_frequency", 0)
        return item


class SingleInputCollectionSchema(Schema):
    inputs = fields.Dict(
        keys=fields.String(),
        values=PortReferenceSchema,
        description="""A collection of multiple single inputs to the port""",
    )

    class Meta:
        title = "Single input collection"
        description = (
            "Defines a set of single inputs which can be switched during play"
            " statements"
        )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.SingleInputCollection()
        for (name, pair) in data["inputs"].items():
            port = item.inputs.get_or_create(name)
            _port(port, pair)
        return item


class MultipleInputsSchema(Schema):
    inputs = fields.Dict(
        keys=fields.String(),
        values=PortReferenceSchema,
        description="""A collection of multiple single inputs to the port""",
    )

    class Meta:
        title = "Multiple inputs"
        description = "Defines a set of single inputs which are all played at once"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.MultipleInputs()
        for (name, pair) in data["inputs"].items():
            port = item.inputs.get_or_create(name)
            _port(port, pair)
        return item


class OscillatorSchema(Schema):
    intermediate_frequency = fields.Int(
        description="""The frequency of this oscillator [Hz].""",
        allow_none=True,
    )
    mixer = fields.String(
        description="""The mixer used to drive the input of the oscillator,
        taken from the names in mixers entry in the main configuration"""
    )
    lo_frequency = fields.Int(
        description="The frequency of the local oscillator which drives the mixer [Hz]."
    )

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        osc = QuaConfig.Oscillator()
        if (
            "intermediate_frequency" in data
            and data["intermediate_frequency"] is not None
        ):
            osc.intermediateFrequency.value = data["intermediate_frequency"]
        if "mixer" in data and data["mixer"] is not None:
            osc.mixer.mixer = data["mixer"]
            osc.mixer.loFrequency = data.get("lo_frequency", 0)
        return osc


class ElementSchema(Schema):
    frequency = fields.Int(
        description="""resonance frequency [Hz].
        Actual carrier frequency output by the OPX to the input of this element is frequency - lo_frequency.
        """
    )
    intermediate_frequency = fields.Int(
        description="""The frequency at which the controller modulates the output to 
        this element [Hz].""",
        allow_none=True,
    )
    oscillator = fields.String(
        description="""The oscillator which is used by the controller to modulates the 
        output to this element [Hz]. Can be used to share oscillators between 
        elements""",
        allow_none=True,
    )

    measurement_qe = fields.String(description="not implemented")
    operations = fields.Dict(
        keys=fields.String(),
        values=fields.String(
            description='The name of the pulse as it appears under the "pulses" entry '
            "in the configuration dict"
        ),
        description="""A collection of all pulse names to be used in play and measure 
        commands""",
    )
    singleInput = fields.Nested(SingleInputSchema)
    mixInputs = fields.Nested(MixInputSchema)
    singleInputCollection = fields.Nested(SingleInputCollectionSchema)
    multipleInputs = fields.Nested(MultipleInputsSchema)
    time_of_flight = fields.Int(
        description="""The delay time, in ns, from the start of pulse until it reaches 
        the controller. Needs to be calibrated by looking at the raw ADC data.
        Needs to be a multiple of 4 and the minimal value is 24. """
    )
    smearing = fields.Int(
        description="""Padding time, in ns, to add to both the start and end of the raw
         ADC data window during a measure command."""
    )
    outputs = fields.Dict(
        keys=fields.String(),
        values=PortReferenceSchema,
        description="The output ports of the element.",
    )
    digitalInputs = fields.Dict(
        keys=fields.String(), values=fields.Nested(DigitalInputSchema)
    )
    digitalOutputs = fields.Dict(keys=fields.String(), values=PortReferenceSchema)
    outputPulseParameters = fields.Dict(description="Pulse parameters for Time-Tagging")

    hold_offset = fields.Nested(HoldOffsetSchema)

    thread = fields.String(description="QE thread")

    class Meta:
        title = "Element"
        description = """The specifications, parameters and connections of a single
         element."""

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        el = QuaConfig.ElementDec()
        if "frequency" in data:
            # Deprecated in 0.0.43
            logger.warning(
                "'frequency' under elements.<element> is deprecated. "
                "use 'intermediate_frequency' instead"
            )
            if "mixInputs" in data:
                el.intermediateFrequency.value = (
                    data["frequency"] - data["mixInputs"].loFrequency
                )
            else:
                el.intermediateFrequency.value = data["frequency"]

        if (
            "intermediate_frequency" in data
            and data["intermediate_frequency"] is not None
        ):
            el.intermediateFrequency.value = abs(data["intermediate_frequency"])
            el.intermediateFrequencyNegative = data["intermediate_frequency"] < 0
            el.intermediateFrequencyOscillator.value = data["intermediate_frequency"]
        elif "oscillator" in data and data["oscillator"] is not None:
            el.namedOscillator.value = data["oscillator"]
        else:
            el.noOscillator.SetInParent()

        # validate we have only 1 set of input defined
        used_inputs = list(
            filter(
                lambda it: it in data,
                ["singleInput", "mixInputs", "singleInputCollection", "multipleInputs"],
            )
        )
        if len(used_inputs) > 1:
            raise ValidationError(
                f"Can't support more than a single input type. "
                f"Used {', '.join(used_inputs)}",
                field_name="",
            )

        if "singleInput" in data:
            el.singleInput.CopyFrom(data["singleInput"])
        if "mixInputs" in data:
            el.mixInputs.CopyFrom(data["mixInputs"])
        if "singleInputCollection" in data:
            el.singleInputCollection.CopyFrom(data["singleInputCollection"])
        if "multipleInputs" in data:
            el.multipleInputs.CopyFrom(data["multipleInputs"])
        if "measurement_qe" in data:
            el.measurementQe.value = data["measurement_qe"]
        if "time_of_flight" in data:
            el.timeOfFlight.value = data["time_of_flight"]
        if "smearing" in data:
            el.smearing.value = data["smearing"]
        if "operations" in data:
            for k, v in data["operations"].items():
                el.operations[k] = v
        if "inputs" in data:
            _build_port(el.inputs, data["inputs"])
        if "outputs" in data:
            _build_port(el.outputs, data["outputs"])
        if "digitalInputs" in data:
            for k, v in data["digitalInputs"].items():
                item = el.digitalInputs.get_or_create(k)
                item.CopyFrom(v)
        if "digitalOutputs" in data:
            for k, v in data["digitalOutputs"].items():
                item = el.digitalOutputs.get_or_create(k)
                item.port.controller = v[0]
                item.port.number = v[1]
        if "outputPulseParameters" in data:
            pulseParameters = data["outputPulseParameters"]
            el.outputPulseParameters.signalThreshold = pulseParameters[
                "signalThreshold"
            ]

            signal_polarity = pulseParameters["signalPolarity"].upper()
            if signal_polarity == "RISING" or signal_polarity == "ASCENDING":
                el.outputPulseParameters.signalPolarity = (
                    QuaConfig.OutputPulseParameters.ASCENDING
                )
            elif signal_polarity == "FALLING" or signal_polarity == "DESCENDING":
                el.outputPulseParameters.signalPolarity = (
                    QuaConfig.OutputPulseParameters.DESCENDING
                )

            if "derivativeThreshold" in pulseParameters:
                el.outputPulseParameters.derivativeThreshold = pulseParameters[
                    "derivativeThreshold"
                ]

                polarity = pulseParameters["derivativePolarity"].upper()
                if polarity == "ABOVE" or polarity == "ASCENDING":
                    el.outputPulseParameters.derivativePolarity = (
                        QuaConfig.OutputPulseParameters.ASCENDING
                    )
                elif polarity == "BELOW" or polarity == "DESCENDING":
                    el.outputPulseParameters.derivativePolarity = (
                        QuaConfig.OutputPulseParameters.DESCENDING
                    )

        if "hold_offset" in data:
            el.holdOffset.CopyFrom(data["hold_offset"])
        if "thread" in data:
            el.thread.threadName = data["thread"]
        return el

    @validates_schema
    def validate_timetagging_parameters(self, data, **kwargs):
        if "outputPulseParameters" in data:
            pulseParameters = data["outputPulseParameters"]
            neededParameters = [
                "signalThreshold",
                "signalPolarity",
                "derivativeThreshold",
                "derivativePolarity",
            ]
            missingParameters = []
            for parameter in neededParameters:
                if parameter not in pulseParameters:
                    missingParameters.append(parameter)
            if len(missingParameters) > 0:
                raise ConfigValidationException(
                    "An element defining the output pulse parameters must either "
                    f"define all of the parameters: {neededParameters}. "
                    f"Parameters defined: {pulseParameters}"
                )
            validSignalPolarity = {"ASCENDING", "DESCENDING", "RISING", "FALLING"}
            validDerivativePolarity = {"ASCENDING", "DESCENDING", "ABOVE", "BELOW"}
            if (
                data["outputPulseParameters"]["signalPolarity"].upper()
                not in validSignalPolarity
            ):
                raise ConfigValidationException(
                    f"'signalPolarity' is {data['outputPulseParameters']['signalPolarity'].upper()} but it must be one of {validSignalPolarity}"
                )
            if (
                data["outputPulseParameters"]["derivativePolarity"].upper()
                not in validDerivativePolarity
            ):
                raise ConfigValidationException(
                    f"'derivativePolarity' is {data['outputPulseParameters']['derivativePolarity'].upper()} but it must be one of {validDerivativePolarity}"
                )

    @validates_schema
    def validate_output_tof(self, data, **kwargs):
        if "outputs" in data and data["outputs"] != {} and "time_of_flight" not in data:
            raise ValidationError(
                "An element with an output must have time_of_flight defined"
            )
        if "outputs" not in data and "time_of_flight" in data:
            raise ValidationError(
                "time_of_flight should be used only with elements that have outputs"
            )

    @validates_schema
    def validate_output_smearing(self, data, **kwargs):
        if "outputs" in data and data["outputs"] != {} and "smearing" not in data:
            raise ValidationError(
                "An element with an output must have smearing defined"
            )
        if "outputs" not in data and "smearing" in data:
            raise ValidationError(
                "smearing should be used only with elements that have outputs"
            )

    @validates_schema
    def validate_oscillator(self, data, **kwargs):
        if "intermediate_frequency" in data and "oscillator" in data:
            raise ValidationError(
                "'intermediate_frequency' and 'oscillator' cannot be defined together"
            )


def _build_port(col, data):
    if data is not None:
        for k, (controller, number) in data.items():
            col[k].controller = controller
            col[k].number = number


def _port(port, data):
    port.controller = data[0]
    port.number = data[1]


class QuaConfigSchema(Schema):
    version = fields.Int(description="Config version.")
    oscillators = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(OscillatorSchema),
        description="""The oscillators used to drive the elements. 
        Can be used to share oscillators between elements""",
    )

    elements = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(ElementSchema),
        description="""The elements. Each element represents and
         describes a controlled entity which is connected to the ports of the 
         controller.""",
    )

    controllers = fields.Dict(
        fields.String(),
        fields.Nested(ControllerSchema),
        description="""The controllers. """,
    )

    integration_weights = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(IntegrationWeightSchema),
        description="""The integration weight vectors used in the integration 
        and demodulation of data returning from a element.""",
    )

    waveforms = fields.Dict(
        keys=fields.String(),
        values=_waveform_poly_field,
        description="""The analog waveforms sent to an element when a pulse is 
        played.""",
    )
    digital_waveforms = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(DigitalWaveFormSchema),
        description="""The digital waveforms sent to an element when a pulse is 
        played.""",
    )
    pulses = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(PulseSchema),
        description="""The pulses to be played to the elements. """,
    )
    mixers = fields.Dict(
        keys=fields.String(),
        values=fields.List(fields.Nested(MixerSchema)),
        description="""The IQ mixer calibration properties, used to post-shape the pulse
         to compensate for imperfections in the mixers used for up-converting the 
         analog waveforms.""",
    )

    class Meta:
        title = "QUA Config"
        description = "QUA program config root object"

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        configWrapper = QuaConfig()
        configWrapper.v1beta.SetInParent()
        config = configWrapper.v1beta
        version = data["version"]
        if str(version) != "1":
            raise RuntimeError(
                "Version must be set to 1 (was set to " + str(version) + ")"
            )
        if "elements" in data:
            for el_name, el in data["elements"].items():
                config.elements.get_or_create(el_name).CopyFrom(el)
        if "oscillators" in data:
            for osc_name, osc in data["oscillators"].items():
                config.oscillators.get_or_create(osc_name).CopyFrom(osc)
        if "controllers" in data:
            for k, v in data["controllers"].items():
                config.controllers.get_or_create(k).CopyFrom(v)
        if "integration_weights" in data:
            for k, v in data["integration_weights"].items():
                iw = config.integrationWeights.get_or_create(k)
                iw.CopyFrom(v)
        if "waveforms" in data:
            for k, v in data["waveforms"].items():
                iw = config.waveforms.get_or_create(k)
                iw.CopyFrom(v)
        if "digital_waveforms" in data:
            for k, v in data["digital_waveforms"].items():
                iw = config.digitalWaveforms.get_or_create(k)
                iw.CopyFrom(v)
        if "mixers" in data:
            for k, v in data["mixers"].items():
                iw = config.mixers.get_or_create(k)
                iw.correction.extend(v)
        if "pulses" in data:
            for k, v in data["pulses"].items():
                iw = config.pulses.get_or_create(k)
                iw.CopyFrom(v)
        return configWrapper
