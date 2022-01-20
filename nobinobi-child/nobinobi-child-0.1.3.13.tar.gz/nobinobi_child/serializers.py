#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from nobinobi_staff.serializers import StaffSerializer
from rest_framework import serializers

from nobinobi_child.models import Child, Absence, ChildToContact, ChildSpecificNeed, Classroom, AgeGroup, AbsenceType, \
    AbsenceGroup, Contact, ReplacementClassroom


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(ContactSerializer, self).to_representation(instance)

        representation["phone"] = instance.phone.as_international if instance.phone else None
        representation["mobile_phone"] = instance.mobile_phone.as_international if instance.mobile_phone else None
        representation[
            "professional_phone"] = instance.professional_phone.as_international if instance.professional_phone else None
        return representation


class ChildToContactSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = ChildToContact
        fields = ('order', 'contact', 'link_with_child')
        depth = 1


class ChildSpecificNeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildSpecificNeed
        fields = '__all__'


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = "__all__"

class ReplacementClassroomSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(read_only=True)
    class Meta:
        model = ReplacementClassroom
        fields = ("classroom",)


class AgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        fields = "__all__"


class ChildSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(read_only=True)
    age_group = AgeGroupSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)

    # contacts = ContactSerializer(many=True)

    childtocontact_set = serializers.SerializerMethodField()
    childspecificneed = ChildSpecificNeedSerializer(read_only=True)
    replacementclassroom_set = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = (
            "id", "status", "birth_date", "first_name", "last_name", "usual_name", "classroom", "age_group", "gender",
            "picture",
            "staff", "childtocontact_set", "childspecificneed", "replacementclassroom_set")
        # depth = 2
        datatables_always_serialize = ("id", "first_name", "last_name", "usual_name", "gender")

    def get_childtocontact_set(self, instance):
        songs = instance.childtocontact_set.all().order_by('order')
        return ChildToContactSerializer(songs, many=True).data

    def get_replacementclassroom_set(self, instance):
        inst = instance.get_now_classroom()
        return ClassroomSerializer(inst).data

    def to_representation(self, instance):
        representation = super(ChildSerializer, self).to_representation(instance)
        #     representation['gender'] = instance.gender
        #     representation['picture'] = instance.picture.url if instance.picture else None
        #     representation['birth_date'] = arrow.get(instance.birth_date).format("DD.MM.YYYY",
        #                                                                          locale="fr_fr") if instance.birth_date else "-"
        #     representation['classroom'] = instance.classroom.name if instance.classroom else "-"
        #     representation['age_group'] = instance.age_group.name if instance.age_group else "-"
        #     representation['staff'] = instance.staff.full_name if instance.staff else "-"
        #     representation['renewal_date'] = arrow.get(instance.renewal_date).format("DD.MM.YYYY", locale="fr_fr")
        #
        return representation


class AbsenceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceGroup
        fields = "__all__"


class AbsenceTypeSerializer(serializers.ModelSerializer):
    group = AbsenceGroupSerializer(read_only=True)

    class Meta:
        model = AbsenceType
        fields = "__all__"


class AbsenceSerializer(serializers.ModelSerializer):
    child = ChildSerializer(read_only=True)
    type = AbsenceTypeSerializer(read_only=True)

    class Meta:
        model = Absence
        fields = '__all__'
        datatables_always_serialize = ("id", "child", "type")
