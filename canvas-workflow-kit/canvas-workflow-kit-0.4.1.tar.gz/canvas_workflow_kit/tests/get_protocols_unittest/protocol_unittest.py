from canvas_workflow_kit.protocol import ClinicalQualityMeasure, ProtocolResult
from canvas_workflow_kit.recommendation import Recommendation


class ProtoUnitTestAllTrue(ClinicalQualityMeasure):

    class Meta:

        references = [
            'This is the proto test all true. www.unittests.med/protounittest?id=alltrue',
        ]
        responds_to_event_types = [
            'HEALTH_MAINTENANCE',
            'UNIT_TESTS',
        ]
        identifiers = ['ProtoUnitTestAllTrue']

        compute_on_change_types = []

    def in_initial_population(self) -> bool:
        return True

    def in_denominator(self) -> bool:
        return True

    def in_numerator(self) -> bool:
        return True

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = 'Current'
        result.add_narrative('This is the narrative for the proto test all true')
        result.add_recommendation(TestAResult())
        result.add_recommendation(TestBResult())
        result.due_in = 17
        return result


class ProtoUnitTestDisabled(ClinicalQualityMeasure):

    class Meta:

        references = [
            'This is the proto test X. www.unittests.med/protounittest?id=X',
        ]
        responds_to_event_types = [
            'HEALTH_MAINTENANCE',
            'UNIT_TESTS',
        ]
        identifiers = ['ProtoUnitTestDisabled']

    @classmethod
    def enabled(cls) -> bool:
        return False

    def in_initial_population(self) -> bool:
        return True

    def in_denominator(self) -> bool:
        return True

    def in_numerator(self) -> bool:
        return True

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = 'Current'
        result.add_narrative('This is the narrative for the proto test x')
        result.add_recommendation(TestAResult())
        result.add_recommendation(TestBResult())
        result.due_in = 5
        return result


class ProtoUnitTestX(ClinicalQualityMeasure):
    class Meta:

        references = [
            'This is the proto test X. www.unittests.med/protounittest?id=X',
        ]
        responds_to_event_types = [
            'UNIT_TESTS',
        ]
        identifiers = ['ProtoUnitTestX']

        compute_on_change_types = [
            'change_C',
        ]

    def in_initial_population(self) -> bool:
        return True

    def in_denominator(self) -> bool:
        return True

    def in_numerator(self) -> bool:
        return True

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = 'Current'
        result.add_narrative('This is the narrative for the proto test x')
        result.add_recommendation(TestBResult())
        result.due_in = -3
        return result


class ProtoUnitTestY(ClinicalQualityMeasure):

    class Meta:

        references = [
            'This is the proto test Y. www.unittests.med/protounittest?id=Y',
        ]
        responds_to_event_types = [
            'HEALTH_MAINTENANCE',
            'UNIT_TESTS',
        ]
        identifiers = ['ProtoUnitTestY']

    def in_initial_population(self) -> bool:
        return True

    def in_denominator(self) -> bool:
        return True

    def in_numerator(self) -> bool:
        return True

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = 'not_applicable'
        result.add_narrative('This is the narrative for the proto test Y')
        result.add_recommendation(TestAResult())
        result.due_in = None
        return result


class ProtoUnitTestZ(ClinicalQualityMeasure):
    class Meta:

        references = [
            'This is the proto test Z. www.unittests.med/protounittest?id=Y',
        ]
        responds_to_event_types = [
            'HEALTH_MAINTENANCE',
            'UNIT_TESTS',
        ]
        identifiers = ['ProtoUnitTestZ']

        compute_on_change_types = [
            'change_B',
        ]

    def in_initial_population(self) -> bool:
        return True

    def in_denominator(self) -> bool:
        return True

    def in_numerator(self) -> bool:
        return True

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = 'not_applicable'
        result.add_narrative('This is the narrative for the proto test Y')
        result.add_recommendation(TestAResult())
        result.due_in = 33
        return result


class TestAResult(Recommendation):

    def __init__(self):
        command = {'type': 'TestAResult'}

        super().__init__(
            key='KEY-AR',
            rank=123,
            button='ACT',
            title='Title TestAResult',
            narrative='Narrative TestAResult',
            command=command)


class TestBResult(Recommendation):

    def __init__(self):
        command = {'type': 'TestBResult'}

        super().__init__(
            key='KEY-BR',
            rank=456,
            button='RUN',
            title='Title TestBResult',
            narrative='Narrative TestBResult',
            command=command)
