from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from edc_constants.constants import DEAD, NO, YES
from edc_dashboard import url_names

from ..models import (
    CareModelMixin,
    CareStatus,
    MoccaRegisterContact,
    SubjectRefusalScreening,
    SubjectScreening,
)


class ChangelistButton:
    """A base class that renders a changelist button for the MoccaRegister
    changelist.

    You need to override `context`.

    Usage:
        button = MyButton(...)
        button.rendered
    """

    template = "mocca_screening/bootstrap3/dashboard_button.html"

    def __init__(
        self,
        mocca_register=None,
        changelist_url_name=None,
    ):
        self._care_status_obj = None
        self._last_mocca_register_contact = None
        self._subject_screening_obj = None
        self._subject_screening_refusal_obj = None
        self.changelist_url_name = changelist_url_name
        self.mocca_register = mocca_register
        self.value_display = None

    def __repr__(self):
        return f"{self.__class__.__name__}(<{self.mocca_register}>)"

    def __str__(self):
        return self.rendered

    @property
    def context(self):
        """Returns the template context for the button
        or None.

        Override.
        """
        return None

    @property
    def rendered(self):
        """Returns a rendered button or a value string or None"""
        if self.context:
            return render_to_string(self.template, context=self.context)
        return self.value_display

    @property
    def subject_screening_obj(self):
        if not self._subject_screening_obj:
            try:
                self._subject_screening_obj = SubjectScreening.objects.get(
                    mocca_register=self.mocca_register
                )
            except ObjectDoesNotExist:
                pass
        return self._subject_screening_obj

    @property
    def subject_screening_refusal_obj(self):
        if not self._subject_screening_refusal_obj:
            try:
                self._subject_screening_refusal_obj = SubjectRefusalScreening.objects.get(
                    mocca_register=self.mocca_register
                )
            except ObjectDoesNotExist:
                pass
        return self._subject_screening_refusal_obj

    @property
    def care_status_obj(self):
        if not self._care_status_obj:
            try:
                self._care_status_obj = CareStatus.objects.get(
                    mocca_register=self.mocca_register
                )
            except ObjectDoesNotExist:
                pass
        return self._care_status_obj

    @property
    def last_mocca_register_contact(self):
        """Returns the last model instance from model
        MoccaRegisterContact or None.
        """
        if not self._last_mocca_register_contact:
            self._last_mocca_register_contact = (
                MoccaRegisterContact.objects.filter(mocca_register=self.mocca_register)
                .order_by("created")
                .last()
            )
        return self._last_mocca_register_contact

    @property
    def willing_or_present(self):
        """Returns True if the subject is either willing to screen
        or present today to screen.
        """
        if self.last_mocca_register_contact:
            return self.last_mocca_register_contact.willing_to_attend == YES
        return self.mocca_register.subject_present == YES

    @property
    def deceased(self):
        """Returns True if subject reported as deceased at the
        last contact.
        """
        return getattr(self.last_mocca_register_contact, "survival_status", "") == DEAD


class CareStatusButton(ChangelistButton):

    care_status_add_url_name = "mocca_screening_admin:mocca_screening_carestatus_add"
    care_status_change_url_name = "mocca_screening_admin:mocca_screening_carestatus_change"

    @property
    def context(self):
        """Returns the template context for the button
        or None.
        """

        if self.deceased:
            context = None
            self.value_display = "deceased"
        elif self.subject_screening_obj:
            context = None
        elif self.care_status_obj:
            context = self.change_button_context
        elif not self.willing_or_present:
            context = None
        else:
            context = self.add_button_context
        return context

    @property
    def add_button_context(self):
        """Returns a dictionary of additional context for the button
        if adding a model instance.
        """

        return dict(
            title=f"Add {CareStatus._meta.verbose_name}",
            url=self.add_url,
            label="Add",
            fa_icon="fas fa-plus",
            button_type="add",
        )

    @property
    def add_url(self):
        url = reverse(self.care_status_add_url_name)
        return (
            f"{url}?next={self.changelist_url_name}"
            f"&mocca_register={str(self.mocca_register.id)}"
        )

    @property
    def change_button_context(self):
        """Returns a dictionary of additional context for the button
        if editing the model instance.
        """
        return dict(
            title=f"Change {CareStatus._meta.verbose_name}",
            url=self.change_url,
            label="Edit",
            fa_icon="fas fa-pen",
            button_type="edit",
        )

    @property
    def change_url(self):
        url = reverse(self.care_status_change_url_name, args=(self.care_status_obj.id,))
        return f"{url}?next={self.changelist_url_name}"


class SubjectRefusalScreeningButton(ChangelistButton):
    refusal_add_url_name = "mocca_screening_admin:mocca_screening_subjectrefusalscreening_add"
    refusal_change_url_name = (
        "mocca_screening_admin:mocca_screening_subjectrefusalscreening_change"
    )

    @property
    def context(self):
        """Returns an url to Add/Edit the SubjectRefusalScreening
        or the empty_value string.
        """
        if self.subject_screening_refusal_obj:
            context = self.change_button_context
        elif self.subject_screening_obj:
            context = None
        elif self.deceased:
            context = None
        else:
            context = self.add_button_context
        return context

    @property
    def add_button_context(self):
        """Returns a dictionary of additional context for the button
        if adding a model instance.
        """

        return dict(
            url=self.add_url,
            label="Add",
            fa_icon="fas fa-plus",
            button_type="add",
            title=f"Add {SubjectRefusalScreening._meta.verbose_name}",
        )

    @property
    def add_url(self):
        url = reverse(self.refusal_add_url_name)
        return (
            f"{url}?next={self.changelist_url_name}"
            f"&mocca_register={str(self.mocca_register.id)}"
        )

    @property
    def change_button_context(self):
        """Returns a dictionary of additional context for the button
        if editing the model instance.
        """
        return dict(
            url=self.change_url,
            label="Edit",
            fa_icon="fas fa-pen",
            button_type="edit",
            title=f"Edit {SubjectRefusalScreening._meta.verbose_name}",
        )

    @property
    def change_url(self):
        url = reverse(
            self.refusal_change_url_name, args=(self.subject_screening_refusal_obj.id,)
        )
        return f"{url}?next={self.changelist_url_name}"


class ScreeningButton(ChangelistButton):

    screening_listboard_url_name = "screening_listboard_url"
    screening_add_url_name = "mocca_screening_admin:mocca_screening_subjectscreening_add"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screening_listboard_url = url_names.get(self.screening_listboard_url_name)
        self.screening_listboard_url_kwargs = dict(
            screening_identifier=self.mocca_register.screening_identifier
        )
        self.screening_add_url = reverse(self.screening_add_url_name)

    @property
    def context(self):
        """Returns the template context for the screening button
        or None.
        """
        mocca_register_contact = self.last_mocca_register_contact
        if self.subject_screening_obj:
            context = self.change_button_context
        elif self.subject_screening_refusal_obj:
            context = None
        elif not mocca_register_contact and self.mocca_register.subject_present == NO:
            context = None
        elif self.deceased:
            context = None
        elif self.willing_or_present:
            context = self.add_button_context
        else:
            context = None
        return context

    @property
    def add_button_context(self):
        """Returns a dictionary of additional context for the button
        if adding a model instance.
        """
        return dict(
            url=self.add_url,
            label="Add",
            fa_icon="fas fa-plus",
            fa_icon_after=None,
            button_type="add",
            title=f"Add {SubjectScreening._meta.verbose_name}",
        )

    @property
    def add_url(self):
        add_url = (
            f"{self.screening_add_url}?next={self.changelist_url_name}"
            f"&mocca_register={str(self.mocca_register.id)}"
        )
        return "&".join([x for x in [add_url, self.care_status_query_string] if x])

    @property
    def change_button_context(self):
        """Returns a dictionary of additional context for the button
        if editing the model instance.
        """
        return dict(
            url=self.change_url,
            label=self.mocca_register.screening_identifier,
            fa_icon="fas fa-share",
            fa_icon_after=True,
            button_type="go",
            title="Go to subject screening listboard",
        )

    @property
    def change_url(self):
        return (
            f"{reverse(self.screening_listboard_url)}?"
            f"q={self.mocca_register.screening_identifier}"
        )

    @property
    def care_status_query_string(self):
        """Return a querystring of carestatus fields=values"""
        query_string = None
        if self.care_status_obj:
            query_string = "&".join(
                [
                    f"{f}={getattr(self.care_status_obj, f) or ''}"
                    for f in [f.name for f in CareModelMixin._meta.fields]
                ]
            )
        return query_string
