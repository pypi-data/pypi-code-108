from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.reverse import reverse

from mayan.apps.documents.serializers.document_type_serializers import DocumentTypeSerializer
from credentials.serializers import StoredCredentialSerializer

from .models import ImportSetup, ImportSetupItem


class ImportSetupSerializer(serializers.HyperlinkedModelSerializer):
    clear_url = serializers.SerializerMethodField()
    credential = StoredCredentialSerializer(read_only=True)
    credential_id = serializers.IntegerField(
        label=_('Credential ID'), required=False, write_only=True
    )
    document_type = DocumentTypeSerializer(read_only=True)
    document_type_id = serializers.IntegerField(
        label=_('Document type ID'), write_only=True
    )
    item_list_url = serializers.SerializerMethodField()
    populate_url = serializers.SerializerMethodField()
    process_url = serializers.SerializerMethodField()

    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'import_setup_id',
                'view_name': 'rest_api:importsetup-detail'
            }
        }
        fields = (
            'clear_url', 'credential', 'credential_id', 'document_type',
            'document_type_id', 'id', 'item_list_url', 'label',
            'populate_url', 'process_size', 'process_url', 'state', 'url'
        )
        model = ImportSetup

    def get_clear_url(self, instance):
        return reverse(
            'rest_api:importsetup-clear', kwargs={
                'import_setup_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )

    def get_item_list_url(self, instance):
        return reverse(
            'rest_api:importsetupitem-list', kwargs={
                'import_setup_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )

    def get_populate_url(self, instance):
        return reverse(
            'rest_api:importsetup-populate', kwargs={
                'import_setup_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )

    def get_process_url(self, instance):
        return reverse(
            'rest_api:importsetup-process', kwargs={
                'import_setup_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )


class ImportSetupItemSerializer(serializers.HyperlinkedModelSerializer):
    import_setup_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'import_setup_url', 'id', 'identifier', 'serialized_data',
            'state', 'state_data', 'url'
        )
        model = ImportSetupItem

    def get_import_setup_url(self, instance):
        return reverse(
            'rest_api:importsetup-detail', kwargs={
                'import_setup_id': instance.import_setup_id,
            }, request=self.context['request'], format=self.context['format']
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:importsetupitem-detail', kwargs={
                'import_setup_id': instance.import_setup_id,
                'import_setup_item_id': instance.pk,
            }, request=self.context['request'], format=self.context['format']
        )
