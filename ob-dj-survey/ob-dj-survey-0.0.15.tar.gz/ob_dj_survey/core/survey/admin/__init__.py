from django.contrib import admin

from ob_dj_survey.core.survey.models import (
    Survey,
    SurveyAnswer,
    SurveyChoice,
    SurveyQuestion,
    SurveyResponse,
    SurveySection,
)


class SurveyQuestionInlineAdmin(admin.TabularInline):
    model = SurveyQuestion
    extra = 0


class SurveySectionInlineAdmin(admin.TabularInline):
    model = SurveySection
    extra = 0


class SurveyInlineAdmin(admin.TabularInline):
    model = Survey
    extra = 0


class SurveyChoiceInlineAdmin(admin.TabularInline):
    model = SurveyChoice
    extra = 0


class SurveyResponseInlineAdmin(admin.TabularInline):
    model = SurveyResponse
    extra = 0


class SurveyAnswerInlineAdmin(admin.TabularInline):
    model = SurveyAnswer
    extra = 0


class SurveyQuestionSurveysInline(admin.TabularInline):
    model = SurveyQuestion.surveys.through


class SurveyChoiceQuestionsInline(admin.TabularInline):
    model = SurveyChoice.questions.through


class SurveyResponsesAnswersInline(admin.TabularInline):
    model = SurveyAnswer.responses.through


@admin.register(SurveySection)
class SurveySectionAdmin(admin.ModelAdmin,):
    list_display = ["name", "description", "meta", "created_at"]
    inlines = [SurveyQuestionInlineAdmin]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin,):
    list_display = ["name", "meta", "created_at"]
    inlines = [SurveyQuestionSurveysInline, SurveyAnswerInlineAdmin]


@admin.register(SurveyChoice)
class SurveyChoiceAdmin(admin.ModelAdmin,):
    list_display = ["title", "description", "created_at"]
    inlines = [SurveyResponseInlineAdmin]
    list_filter = [
        "questions",
        "questions__surveys",
    ]


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin,):
    list_display = ["title", "type", "is_active", "section", "meta", "created_at"]
    inlines = [SurveyChoiceQuestionsInline, SurveyResponseInlineAdmin]
    list_filter = ["surveys", "section"]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin,):
    list_display = ["question", "choice", "value", "meta", "updated_at", "created_at"]
    list_display_links = ["question"]
    list_editable = ["choice", "value"]
    list_filter = ["question", "choice"]


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin,):
    list_display = ["status", "updated_at", "created_at"]
    inlines = [
        SurveyResponsesAnswersInline,
    ]
    list_filter = [
        "survey",
        "responses",
    ]
