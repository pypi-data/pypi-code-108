import pytest
from canvas_workflow_kit.patient import Patient
from canvas_workflow_kit.intervention import (
    Intervention, BannerAlertIntervention
)

from .base import SDKBaseTest


class InterventionTest(SDKBaseTest):

    def test___init__(self):
        intervention1 = Intervention(
            title='Do Something', narrative="I'm not sure what, but do something!",
            href="https://www.canvasmedical.com/")
        self.assertTrue(isinstance(intervention1, Intervention))
        self.assertEqual(intervention1.title, 'Do Something')
        self.assertEqual(intervention1.narrative, "I'm not sure what, but do something!")
        self.assertEqual(intervention1.href, "https://www.canvasmedical.com/")

        intervention2 = Intervention(title='other title')
        self.assertEqual(intervention2.title, 'other title')
        self.assertIsNone(intervention2.narrative)
        self.assertEqual(intervention2.href, '')

        intervention3 = Intervention()
        self.assertIsNone(intervention3.title)
        self.assertIsNone(intervention3.narrative)
        self.assertEqual(intervention3.href, '')


class BannerAlertInterventionTest(SDKBaseTest):
    def test___init__error_no_narrative(self):
        with pytest.raises(TypeError) as init_error:
            BannerAlertIntervention(intent='warning', placement=['scheduling_card'])
        self.assertIn(
            "__init__() missing 1 required positional argument: 'narrative'",
            str(init_error.value))

    def test___init__error_no_narrative_no_placement(self):
        with pytest.raises(TypeError) as init_error:
            BannerAlertIntervention(intent='warning')
        self.assertIn(
            "__init__() missing 2 required positional arguments: 'narrative' and 'placement'",
            str(init_error.value))

    def test___init__error_no_intent_no_placement(self):
        with pytest.raises(TypeError) as init_error:
            BannerAlertIntervention(narrative='Call your mom!')
        self.assertIn(
            "__init__() missing 2 required positional arguments: 'placement' and 'intent'",
            str(init_error.value))

    def test___init__error_no_placement(self):
        with pytest.raises(TypeError) as init_error:
            BannerAlertIntervention(narrative='Call your mom!', intent='warning')
        self.assertIn(
            "__init__() missing 1 required positional argument: 'placement'",
            str(init_error.value))

    def test___init__error_no_intent_no_narrative(self):
        with pytest.raises(TypeError) as init_error:
            BannerAlertIntervention(placement=['scheduling_card'])
        self.assertIn(
            "__init__() missing 2 required positional arguments: 'narrative' and 'intent'",
            str(init_error.value))

    def test___init__error_no_intent(self):
        with pytest.raises(TypeError) as init_error:
            BannerAlertIntervention(placement=['scheduling_card'], narrative='Call your mom!')
        self.assertIn(
            "__init__() missing 1 required positional argument: 'intent'",
            str(init_error.value))

    def test___init__(self):
        alert = BannerAlertIntervention(
            narrative='Call your mom!', intent='warning',
            placement=['scheduling_card', 'appointment_card'])
        self.assertTrue(isinstance(alert, BannerAlertIntervention))
        self.assertEqual(alert.narrative, 'Call your mom!')
        self.assertEqual(alert.intent, 'warning')
        self.assertEqual(alert.placement, ['scheduling_card', 'appointment_card'])

    def test_narrative_limit_error_too_long(self):
        with pytest.raises(ValueError) as narrative_error:
            BannerAlertIntervention(
                narrative='abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz',
                intent='warning', placement=['scheduling'])
        self.assertEqual(
            'Narrative of Banner Alert Intervention must be between 1 and 90 characters',
            str(narrative_error.value))

    def test_narrative_limit_error_too_short(self):
        with pytest.raises(ValueError) as narrative_error:
            BannerAlertIntervention(narrative='', intent='warning', placement=['scheduling'])
        self.assertIn(
            'Narrative of Banner Alert Intervention must be between 1 and 90 characters',
            str(narrative_error.value))

    def test_narrative(self):
        alert1 = BannerAlertIntervention(
            narrative='H', intent='alert', placement=['scheduling_card'])
        self.assertTrue(isinstance(alert1, BannerAlertIntervention))

        alert2 = BannerAlertIntervention(
            narrative='1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 12',
            intent='info', placement=['scheduling_card'])
        self.assertTrue(isinstance(alert2, BannerAlertIntervention))

    def test_placement_type_error_string(self):
        with pytest.raises(TypeError) as placement_error_string:
            BannerAlertIntervention(narrative='Do pushups!', intent='info', placement='chart')
        self.assertIn(
            'Placement of Banner Alert Intervention must be a List of strings. The options are: ',
            str(placement_error_string.value))

    def test_placement_type_error_empty(self):
        with pytest.raises(ValueError) as placement_error_empty:
            BannerAlertIntervention(narrative='Do pushups!', intent='info', placement=[])
        self.assertIn(
            'Placement of Banner Alert Intervention must have at least one value. The options are: ',
            str(placement_error_empty.value))

    def test_placement_type_error_wrong(self):
        with pytest.raises(ValueError) as placement_error_wrong:
            BannerAlertIntervention(
                narrative='Do pushups!', intent='info', placement=['here'])
        self.assertIn(
            '"here" is not an accepted option for Banner Alert Intervention placement. The options are: ',
            str(placement_error_wrong.value))

    def test_placement_type(self):
        alert1 = BannerAlertIntervention(
            narrative='Do pushups!', intent='info',
            placement=['scheduling_card', 'chart', 'profile', 'appointment_card', 'timeline'])
        self.assertEqual(alert1.placement, ['scheduling_card', 'chart',
                         'profile', 'appointment_card', 'timeline'])

    def test_intent_types(self):
        with pytest.raises(ValueError) as intent_error_empty:
            BannerAlertIntervention(narrative='Do pushups!', intent='', placement=['chart'])
        self.assertIn(
            '"" is not an accepted option for Banner Alert Intervention intent. The options are: ',
            str(intent_error_empty.value))

        with pytest.raises(ValueError) as intent_error_wrong:
            BannerAlertIntervention(narrative='Do pushups!',
                                    intent='negative', placement=['chart'])
        self.assertIn(
            '"negative" is not an accepted option for Banner Alert Intervention intent. The options are: ',
            str(intent_error_wrong.value))

        alert1 = BannerAlertIntervention(narrative='Do pushups!',
                                         intent='info', placement=['chart'])
        self.assertEqual(alert1.intent, 'info')

        alert3 = BannerAlertIntervention(narrative='Do pushups!',
                                         intent='warning', placement=['chart'])
        self.assertEqual(alert3.intent, 'warning')

        alert4 = BannerAlertIntervention(narrative='Do pushups!',
                                         intent='alert', placement=['chart'])
        self.assertEqual(alert4.intent, 'alert')
