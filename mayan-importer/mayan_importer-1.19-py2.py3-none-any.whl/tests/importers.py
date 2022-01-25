from collections import namedtuple
import shutil

from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.models import SharedUploadedFile
from mayan.apps.documents.tests.literals import TEST_SMALL_DOCUMENT_PATH
from mayan.apps.storage.utils import NamedTemporaryFile

from ..classes import ImportSetupBackend


class TestImporter(ImportSetupBackend):
    label = _('Test importer')
    item_identifier = 'id'
    item_label = 'name'

    @staticmethod
    def get_test_item():
        TestItem = namedtuple(typename='TestItem', field_names=('id', 'name',))
        return TestItem(id='test_id_01', name='test_item')

    def item_process(self, identifier, data):
        # Copy the Dropbox file to a temporary location using streaming
        # download.
        # The create a shared upload instance from the temporary file.
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as document_file_object:
            with NamedTemporaryFile() as file_object:
                shutil.copyfileobj(fsrc=document_file_object, fdst=file_object)

                file_object.seek(0)

                return SharedUploadedFile.objects.create(
                    file=File(file_object),
                )

    def get_item_list(self):
        return [TestImporter.get_test_item()]
