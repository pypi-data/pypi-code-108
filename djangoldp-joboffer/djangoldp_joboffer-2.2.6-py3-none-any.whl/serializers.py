from rest_framework import serializers
from djangoldp_joboffer.models import JobOffer


class JobOfferModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'
        # NOTE: skills and author must be left as read_only, or the serialization of
        # backlinked job offers in views.py must change
        read_only_fields = ['author', 'skills']
