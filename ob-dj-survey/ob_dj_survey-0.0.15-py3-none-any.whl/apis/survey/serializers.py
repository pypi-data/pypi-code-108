import logging
import typing

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ob_dj_survey.apis.user.serializers import UserSerializer
from ob_dj_survey.core.survey.models import (
    Survey,
    SurveyAnswer,
    SurveyChoice,
    SurveyQuestion,
    SurveyResponse,
    SurveySection,
)

logger = logging.getLogger(__name__)


class SurveySectionSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)

    class Meta:
        model = SurveySection
        fields = (
            "id",
            "name",
            "description",
            "meta",
        )


class SurveyQuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    class Meta:
        model = SurveyQuestion
        fields = (
            "id",
            "title",
            "type",
            "section",
            "meta",
            "is_active",
            "created_at",
            "choices",
        )
        extra_kwargs = {
            "created_at": {"read_only": True},
        }

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["section"] = SurveySectionSerializer(instance.section).data
        return data

    def get_choices(self, obj):
        return SurveyChoiceSerializer(obj.choices.all(), many=True).data


class SurveySerializer(serializers.ModelSerializer):
    questions = SurveyQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = (
            "id",
            "name",
            "questions",
            "created_at",
            "meta",
        )


class SurveyChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyChoice
        fields = ("id", "title", "description", "meta", "created_at")


class AnswersSerializer(serializers.Serializer):
    """
        * Serializer for Submitting Answers

    - Answers Example :
        "answers": [
            {"question": question_1.pk, "choices": [ab_choice.pk]},
            { "question": question_2.pk, "choices": [fish_choice.pk], "values": ["Gluten"],},
            ....
    """

    question = serializers.PrimaryKeyRelatedField(
        queryset=SurveyQuestion.objects.all(), required=False
    )
    choices = serializers.PrimaryKeyRelatedField(
        queryset=SurveyChoice.objects.all(), many=True, required=False
    )
    values = serializers.ListField(required=False)
    meta = serializers.JSONField(required=False)

    def validate(self, attrs):
        if not attrs.get("choices") and not attrs.get("values"):
            raise serializers.ValidationError(_("No Answers Provided"))
        return attrs


class SurveyResponseSerializer(serializers.ModelSerializer):
    question = SurveyQuestionSerializer(read_only=True)
    choice = SurveyChoiceSerializer(read_only=True)

    class Meta:
        model = SurveyResponse
        fields = (
            "id",
            "question",
            "choice",
            "value",
            "meta",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["question"] = SurveyQuestionSerializer(instance.question).data
        data["choice"] = SurveyChoiceSerializer(instance.choice).data
        return data

    def validate(self, data):
        # TODO: Validate Each type of Question by the choices sent within it.
        return data


class SurveyAnswerSerializer(serializers.ModelSerializer):
    answers = AnswersSerializer(many=True, write_only=True)
    responses = SurveyResponseSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = SurveyAnswer
        fields = (
            "id",
            "survey",
            "responses",
            "answers",
            "status",
            "meta",
            "created_by",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["survey"] = SurveySerializer(instance.survey).data
        return data

    def validate(self, attrs):
        attrs["created_by"] = self.context["request"].user
        return attrs
