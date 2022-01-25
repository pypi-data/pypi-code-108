import typing

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_survey.core.survey.managers import (
    SurveyAnswerManager,
    SurveyManager,
    SurveyQuestionManager,
    SurveyResponseManager,
)


class SurveySection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "The meta field is used to maintain meta data for survey sections. "
        ),
        default=dict,
    )

    def __str__(self):
        return self.name


class Survey(models.Model):
    class SubmissionType(models.TextChoices):
        FULL = "full", _("Full")
        PARTIAL = "partial", _("Partial")

    name = models.CharField(max_length=200, null=True, blank=True, unique=True)
    submission_type = models.CharField(
        max_length=10, choices=SubmissionType.choices, default=SubmissionType.PARTIAL
    )
    meta = models.JSONField(
        null=True,
        blank=True,
        help_text=_("The meta field is used to maintain meta data for survey"),
        default=dict,
    )
    callback = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "The callback field is used to maintain callback to other apps "
            "(For example, if survey medical_record require to callback another app and pass "
            "survey response parameters)"
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SurveyManager()

    def __str__(self):
        return self.name


class SurveyQuestion(models.Model):
    class QuestionTypes(models.TextChoices):
        TEXT = "text", _("text (multiple line)")
        SHORT_TEXT = "short-text", _("short text (one line)")
        RADIO = "radio", _("radio")
        YES_NO = "yes_no", _("Yes/No")
        SELECT = "select", _("select")
        SELECT_IMAGE = "select_image", _("Select Image")
        SELECT_MULTIPLE = "select_multiple", _("Select Multiple")
        INTEGER = "integer", _("integer")
        FLOAT = "float", _("float")
        DATE = "date", _("date")

    title = models.CharField(max_length=200)
    type = models.CharField(
        max_length=100, choices=QuestionTypes.choices, default=QuestionTypes.RADIO.value
    )
    surveys = models.ManyToManyField(Survey, blank=True, related_name="questions")
    section = models.ForeignKey(
        SurveySection,
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
    )
    meta = models.JSONField(
        null=True,
        blank=True,
        help_text=_("The meta field is used to maintain meta data for survey question"),
        default=dict,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SurveyQuestionManager()

    def __str__(self):
        return self.title

    def activate(self) -> typing.NoReturn:
        if self.is_active:
            raise ValidationError(_("Survey question is already active"))

        if (
            self.type
            in (
                self.QuestionTypes.SELECT.value
                or self.QuestionTypes.SELECT_MULTIPLE.value
            )
            and self.choices.count() < 1
        ):
            raise ValidationError(
                _("Please add minimum of 2 choices for survey question")
            )

        self.is_active = True
        self.save()


class SurveyChoice(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, default="")
    questions = models.ManyToManyField(
        SurveyQuestion, blank=True, related_name="choices"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(
        null=True,
        blank=True,
        help_text=_("The meta field is used to maintain meta data for survey choice"),
        default=dict,
    )

    def __str__(self):
        return self.title


class SurveyResponse(models.Model):
    question = models.ForeignKey(
        SurveyQuestion, on_delete=models.CASCADE, related_name="responses",
    )
    choice = models.ForeignKey(
        SurveyChoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="responses",
    )
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(
        null=True,
        blank=True,
        help_text=_("The meta field is used to maintain meta data for survey response"),
        default=dict,
    )

    objects = SurveyResponseManager()

    def __str__(self):
        return f"{self.__class__.__name__}(PK={self.pk})"

    def _validate_choices_question(self):
        if (
            self.question.type
            in [
                self.question.QuestionTypes.SELECT.value,
                self.question.QuestionTypes.SELECT_MULTIPLE.value,
                self.question.QuestionTypes.RADIO.value,
            ]
            and self.value not in self.question.choices.values_list("title", flat=True)
            and self.choice
        ):
            raise ValidationError(
                _(
                    f"The answer {self.value} for question {self.question.title} is invalid choice"
                )
            )

    def _validate_yes_no_question(self):
        if self.question.type == self.question.QuestionTypes.YES_NO.value and self.value.lower() not in (
            "yes",
            "no",
        ):
            raise ValidationError(
                _(f"The answer for {self.question.title} can accept yes/no values")
            )

    def clean(self) -> None:
        if not self.question.is_active:
            raise ValidationError(
                _(f"This question {self.question.title} is not active.")
            )
        self._validate_choices_question()
        self._validate_yes_no_question()

    def save(self, *args, **kwargs) -> typing.NoReturn:
        self.clean()
        super().save(*args, **kwargs)


class SurveyAnswer(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", _("Completed")
        PARTIAL = "partial", _("Partial")

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="answers")
    responses = models.ManyToManyField(
        SurveyResponse, blank=True, related_name="answers"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PARTIAL
    )
    meta = models.JSONField(
        null=True,
        blank=True,
        help_text=_("The meta field is used to maintain meta data for survey answers"),
        default=dict,
    )
    created_by = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.CASCADE
    )  # Anonymous
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SurveyAnswerManager()

    class Meta:
        verbose_name = _("Survey Answers")
        verbose_name_plural = _("Survey Answers")

    def __str__(self):
        return f"{self.__class__.__name__}(PK={self.pk})"

    def submit(
        self, answers: typing.List["SurveyChoice"],
    ):

        self.reset_survey_answers()
        validated_answers = []

        for answer in answers:
            # If Answer Object is Dict
            if isinstance(answer, dict):
                values = answer.pop("values", [])
                choices = answer.pop("choices", [])
                question = answer["question"]
                for choice in choices:
                    validated_answers.append(
                        SurveyResponse.objects.create(
                            question=question, choice=choice, value=choice.title
                        )
                    )
                for value in values:
                    validated_answers.append(
                        SurveyResponse.objects.create(question=question, value=value)
                    )

        self.responses.set(validated_answers)

        # we could have answers more than questions when we have questions
        # with type `SELECT` that have multiple answers for each question.
        if self.survey.questions.count() <= self.responses.count():
            self.status = self.Status.COMPLETED
        elif (
            self.survey.questions.count() > self.responses.count()
            and self.survey.submission_type != Survey.SubmissionType.FULL.value
        ):
            self.status = self.Status.PARTIAL
        else:
            raise ValidationError(_("This Survey should be Fully Answered."))
        self.save()

    def reset_survey_answers(self):
        # clean-up - delete all answers
        SurveyResponse.objects.filter(
            answers__created_by=self.created_by, answers__survey=self.survey
        ).delete()
        SurveyAnswer.objects.filter(
            created_by=self.created_by, survey=self.survey,
        ).delete()
