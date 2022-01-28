#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


from nobinobi_child.serializers import ChildSerializer
from rest_framework import serializers

from nobinobi_daily_follow_up.models import Reception, Presence, DailyFollowUp, Activity, MealDailyFollowUp, Nap, \
    DiaperChange, LotionDailyFollowUp, Lotion, Meal, TypeActivity, ActivityGroup, Medication, TypeMedication, \
    GiveMedication, DailyFollowUpToMedication, EarlyTroubleshooting


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ["name", "image"]


class MealDailyFollowUpSerializer(serializers.ModelSerializer):
    snack_meals = MealSerializer(many=True)
    lunch_meals = MealSerializer(many=True)
    afternoon_snack_meals = MealSerializer(many=True)

    class Meta:
        model = MealDailyFollowUp
        fields = ["pk", "snack_time", "snack_quality", "snack_meals", "lunch_time", "lunch_quality", "lunch_meals",
                  "afternoon_snack_time", "afternoon_snack_quality", "afternoon_snack_meals", "comment"]


class ActivityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityGroup
        fields = ["name"]


class TypeActivitySerializer(serializers.ModelSerializer):
    group = ActivityGroupSerializer(read_only=True)

    class Meta:
        model = TypeActivity
        fields = ["name", "group", "order"]


class ActivitySerializer(serializers.ModelSerializer):
    type_activity = TypeActivitySerializer(read_only=True)

    class Meta:
        model = Activity
        fields = ["pk", "comment", "_comment_excerpt", "type_activity"]
        depth = 1


class ReceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = ['pk', "breakfast", "breakfast_time", "sleep", "sick", "fever", "condition", "wake_up_time",
                  "comment", ]


class NapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nap
        fields = ["pk", "start_time", "end_time"]


class DiaperChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaperChange
        fields = ["pk", "hour", "feces"]


class LotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lotion
        fields = ['name']


class LotionDailyFollowUpSerializer(serializers.ModelSerializer):
    lotion = LotionSerializer(read_only=True)

    class Meta:
        model = LotionDailyFollowUp
        fields = ['pk', 'lotion', "comment"]


class TypeMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeMedication
        fields = ["name"]


class GiveMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveMedication
        fields = ["pk", "staff", "give_hour", "given_hour", "date"]


class MedicationSerializer(serializers.ModelSerializer):
    type_medication = TypeMedicationSerializer(read_only=True)
    givemedication_set = GiveMedicationSerializer(many=True)

    class Meta:
        model = Medication
        fields = ["pk", "from_date", "end_date", "type_medication", "comment", "givemedication_set", "attachment"]


class DailyFollowUpToMedicationSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer(read_only=True)

    class Meta:
        model = DailyFollowUpToMedication
        fields = ["pk", "medication", "daily_follow_up"]


class DailyFollowUpSerializer(serializers.ModelSerializer):
    reception = ReceptionSerializer(read_only=True)
    activity_set = ActivitySerializer(read_only=True, many=True)
    mealdailyfollowup = MealDailyFollowUpSerializer(read_only=True)
    nap_set = NapSerializer(read_only=True, many=True)
    diaperchange_set = DiaperChangeSerializer(read_only=True, many=True)
    lotiondailyfollowup_set = LotionDailyFollowUpSerializer(read_only=True, many=True)
    dailyfollowuptomedication_set = DailyFollowUpToMedicationSerializer(read_only=True, many=True)

    class Meta:
        model = DailyFollowUp
        fields = ["pk", 'important', 'comment', 'reception', "mealdailyfollowup", "activity_set", "nap_set",
                  "diaperchange_set",
                  "lotiondailyfollowup_set", "dailyfollowuptomedication_set"]


class PresenceSerializer(serializers.ModelSerializer):
    dailyfollowup = DailyFollowUpSerializer(read_only=True)
    child = ChildSerializer(read_only=True)

    class Meta:
        model = Presence
        fields = ["pk", "child", "dailyfollowup", "departure_time", "arrival_time", "intermediate_departure_time",
                  "intermediate_arrival_time", "date"]
        # depth = 2
        datatables_always_serialize = (
            "pk", "child", "dailyfollowup", "departure_time", "arrival_time", "intermediate_departure_time",
            "intermediate_arrival_time", "date"
        )


class EarlyTroubleshootingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarlyTroubleshooting
        fields = ("id", "child", "date", "periods")
        datatables_always_serialize = ("id", "child", "date", "periods")

    def to_representation(self, instance):
        representation = super(EarlyTroubleshootingSerializer, self).to_representation(instance)
        format = "%d.%m.%Y"
        representation['child'] = instance.child.full_name
        representation['date'] = instance.date.strftime(format)
        # representation['periods'] = [name for name in instance.periods]
        return representation
