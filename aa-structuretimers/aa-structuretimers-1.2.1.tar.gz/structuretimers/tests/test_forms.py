from unittest.mock import Mock, patch

from requests.exceptions import ConnectionError as NewConnectionError
from requests.exceptions import HTTPError

from app_utils.testing import NoSocketsTestCase

from ..forms import TimerForm
from ..models import Timer
from .testdata import test_image_filename
from .testdata.factory import create_user
from .testdata.fixtures import LoadTestDataMixin

FORMS_PATH = "structuretimers.forms"
MODELS_PATH = "structuretimers.models"


def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break


def create_form_data(**kwargs):
    form_data = {
        "eve_solar_system_2": 30004984,
        "structure_type_2": 35832,
        "timer_type": Timer.Type.NONE,
        "objective": Timer.Objective.UNDEFINED,
        "visibility": Timer.Visibility.UNRESTRICTED,
    }
    if kwargs:
        form_data.update(kwargs)
    return form_data


class TestTimerFormIsValid(LoadTestDataMixin, NoSocketsTestCase):
    def test_should_accept_normal_timer(self):
        # given
        form_data = create_form_data(days_left=0, hours_left=3, minutes_left=30)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())

    def test_should_accept_normal_timer_with_partial_date_1(self):
        # given
        form_data = create_form_data(days_left=1)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timer_type"], Timer.Type.NONE)

    def test_should_accept_normal_timer_with_partial_date_2(self):
        # given
        form_data = create_form_data(hours_left=1)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timer_type"], Timer.Type.NONE)

    def test_should_accept_normal_timer_with_partial_date_3(self):
        # given
        form_data = create_form_data(minutes_left=1)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timer_type"], Timer.Type.NONE)

    def test_should_accept_preliminary_timer_without_date(self):
        # given
        form_data = create_form_data(timer_type=Timer.Type.PRELIMINARY)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())

    def test_should_upgrade_preliminary_timer_when_date_specified(self):
        # given
        form_data = create_form_data(
            timer_type=Timer.Type.PRELIMINARY,
            days_left=0,
            hours_left=3,
            minutes_left=30,
        )
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timer_type"], Timer.Type.NONE)
        self.assertIsNotNone(form.cleaned_data["days_left"])
        self.assertIsNotNone(form.cleaned_data["hours_left"])
        self.assertIsNotNone(form.cleaned_data["minutes_left"])

    def test_should_upgrade_preliminary_timer_when_date_specified_2(self):
        # given
        form_data = create_form_data(timer_type=Timer.Type.PRELIMINARY, days_left=5)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timer_type"], Timer.Type.NONE)
        self.assertIsNotNone(form.cleaned_data["days_left"])
        self.assertIsNotNone(form.cleaned_data["hours_left"])
        self.assertIsNotNone(form.cleaned_data["minutes_left"])

    def test_should_set_timer_as_preliminary_timer_when_no_date_specified(self):
        # given
        form_data = create_form_data(timer_type=Timer.Type.ARMOR)
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["timer_type"], Timer.Type.PRELIMINARY)
        self.assertIsNone(form.cleaned_data["days_left"])
        self.assertIsNone(form.cleaned_data["hours_left"])
        self.assertIsNone(form.cleaned_data["minutes_left"])

    def test_should_not_accept_timer_without_solar_system(self):
        # given
        form_data = create_form_data(days_left=0, hours_left=3, minutes_left=30)
        del form_data["eve_solar_system_2"]
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())

    def test_should_not_accept_timer_without_structure_type(self):
        # given
        form_data = create_form_data(days_left=0, hours_left=3, minutes_left=30)
        del form_data["structure_type_2"]
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())

    def test_should_not_accept_invalid_days(self):
        # given
        form_data = create_form_data(days_left=-1, hours_left=3, minutes_left=30)
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())

    def test_should_not_accept_moon_mining_type_for_non_mining_structures(self):
        # given
        form_data = create_form_data(
            timer_type=Timer.Type.MOONMINING,
            structure_type_2=self.type_astrahus.id,
            days_left=0,
            hours_left=3,
            minutes_left=30,
        )
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())

    @patch(FORMS_PATH + ".requests.get", spec=True)
    def test_should_create_timer_with_valid_details_image(self, mock_get):
        # given
        image_file = bytearray(bytes_from_file(test_image_filename()))
        mock_get.return_value.content = image_file
        form_data = create_form_data(
            days_left=0,
            hours_left=3,
            minutes_left=30,
            details_image_url="http://www.example.com/image.png",
        )
        form = TimerForm(data=form_data)
        # when / then
        self.assertTrue(form.is_valid())

    @patch(FORMS_PATH + ".requests.get", spec=True)
    def test_should_not_allow_invalid_link_for_detail_images(self, mock_get):
        # given
        image_file = bytearray(bytes_from_file(test_image_filename()))
        mock_get.return_value.content = image_file
        form_data = create_form_data(
            days_left=0,
            hours_left=3,
            minutes_left=30,
            details_image_url="invalid-url",
        )
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())

    @patch(FORMS_PATH + ".requests.get", spec=True)
    def test_should_show_error_when_image_can_not_be_loaded_1(self, mock_get):
        # given
        mock_get.side_effect = NewConnectionError
        form_data = create_form_data(
            days_left=0,
            hours_left=3,
            minutes_left=30,
            details_image_url="http://www.example.com/image.png",
        )
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())

    @patch(FORMS_PATH + ".requests.get", spec=True)
    def test_should_show_error_when_image_can_not_be_loaded_2(self, mock_get):
        # given
        mock_get.side_effect = HTTPError
        form_data = create_form_data(
            days_left=0,
            hours_left=3,
            minutes_left=30,
            details_image_url="http://www.example.com/image.png",
        )
        form = TimerForm(data=form_data)
        # when / then
        self.assertFalse(form.is_valid())


@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
@patch(MODELS_PATH + "._task_schedule_notifications_for_timer", Mock())
class TestTimerFormSave(LoadTestDataMixin, NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user(cls.character_1)

    def test_should_create_new_normal_timer(self):
        # given
        form_data = create_form_data(
            days_left=0, hours_left=3, minutes_left=30, timer_type=Timer.Type.ARMOR
        )
        form = TimerForm(user=self.user, data=form_data)
        # when
        form.save()
        # then
        timer = Timer.objects.first()
        self.assertEqual(timer.timer_type, Timer.Type.ARMOR)
        self.assertIsNotNone(timer.date)

    def test_should_create_new_preliminary_timer(self):
        # given
        form_data = create_form_data()
        form = TimerForm(user=self.user, data=form_data)
        # when
        form.save()
        # then
        timer = Timer.objects.first()
        self.assertEqual(timer.timer_type, Timer.Type.PRELIMINARY)
        self.assertIsNone(timer.date)

    def test_should_promote_preliminary_timer_to_normal_timer(self):
        # given
        form_data = create_form_data(timer_type=Timer.Type.PRELIMINARY, days_left=1)
        form = TimerForm(user=self.user, data=form_data)
        # when
        form.save()
        # then
        timer = Timer.objects.first()
        self.assertEqual(timer.timer_type, Timer.Type.NONE)
        self.assertIsNotNone(timer.date)
