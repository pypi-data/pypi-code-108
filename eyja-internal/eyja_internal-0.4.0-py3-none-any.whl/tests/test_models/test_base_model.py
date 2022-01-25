from unittest import IsolatedAsyncioTestCase

from eyja.interfaces.db import BaseStorageModel
from eyja.hubs import DataHub
from eyja.errors import (
    ParseModelNamespaceError,
)


class BaseModelTest(IsolatedAsyncioTestCase):
    class ModelWithWrongNamespace(BaseStorageModel):
        _namespace = 'test'

        name: str
        article: str

    class ModelWithUnknownStorage(BaseStorageModel):
        _namespace = 'postgres:test:test_base_model:test_models'

        name: str
        article: str

    async def test_use_wrong_model(self):
        await DataHub.init()

        wrong_object = self.ModelWithWrongNamespace(
            name='Test',
            article='Test article',
        )

        with self.assertRaises(ParseModelNamespaceError):
            await wrong_object.save()

    async def test_use_model_with_wrong_storage(self):
        await DataHub.init()

        wrong_object = self.ModelWithUnknownStorage(
            name='Test',
            article='Test article',
        )

        with self.assertRaises(ParseModelNamespaceError):
            await wrong_object.save()
