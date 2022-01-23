#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import datetime
import json
import redis
import unittest
import uuid
from unittest.mock import patch, Mock
from typing import Dict, List

# Library dependencies
from kink import inject

# Library libs
import fastybird_redisdb_storage_plugin
from fastybird_redisdb_storage_plugin.bootstrap import register_services
from fastybird_redisdb_storage_plugin.manager import StorageManagerFactory
from fastybird_redisdb_storage_plugin.repository import StorageRepositoryFactory
from fastybird_redisdb_storage_plugin.state import StorageItem


class CustomStateItem(StorageItem):

    @property
    def value(self) -> bool or int or float or str or None:
        if "value" in self._raw:
            return self._raw.get("value", None)

        return None

    # -----------------------------------------------------------------------------

    @property
    def expected(self) -> bool or int or float or str or None:
        if "expected" in self._raw:
            return self._raw.get("expected", None)

        return None

    # -----------------------------------------------------------------------------

    @property
    def is_pending(self) -> bool:
        if "pending" in self._raw:
            return bool(self._raw.get("pending", False))

        return False

    # -----------------------------------------------------------------------------

    @staticmethod
    def create_fields() -> Dict[str or int, str or int or float]:
        return {
            0: "id",
            "value": None,
            "expected": None,
            "pending": False,
        }

    # -----------------------------------------------------------------------------

    @staticmethod
    def update_fields() -> List[str]:
        return [
            "value",
            "expected",
            "pending",
        ]


class TestStorageReading(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        register_services()

    @inject
    def test_read_record(self, repository_factory: StorageRepositoryFactory):
        item_id: uuid.UUID = uuid.uuid4()

        raw_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": None,
            "pending": False,
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            mock_redis_get.return_value = json.dumps(raw_dict)

            storage_repository = repository_factory.create(
                host="127.0.0.1",
                port=6379,
                database=1,
            )

            stored_record = storage_repository.find_one(item_id)

            self.assertTrue(isinstance(stored_record, StorageItem))
            self.assertEqual(raw_dict, stored_record.raw)

    @inject
    def test_read_custom_record(self, repository_factory: StorageRepositoryFactory):
        item_id: uuid.UUID = uuid.uuid4()

        raw_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": None,
            "pending": False,
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            mock_redis_get.return_value = json.dumps(raw_dict)

            storage_repository = repository_factory.create(
                host="127.0.0.1",
                port=6379,
                database=1,
                entity=CustomStateItem,
            )

            stored_record = storage_repository.find_one(item_id)

            self.assertTrue(isinstance(stored_record, CustomStateItem))
            self.assertEqual(raw_dict, stored_record.raw)
            self.assertEqual(raw_dict.get("value"), stored_record.raw.get("value"))
            self.assertEqual(raw_dict.get("expected"), stored_record.raw.get("expected"))
            self.assertEqual(raw_dict.get("pending"), stored_record.raw.get("pending"))


class TestStorageCreating(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        register_services()

    @inject
    def test_create_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        create_dict = {
            "value": 10,
            "expected": None,
            "pending": False,
        }

        expected_dict = {
            "id": item_id.__str__(),
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "set") as mock_redis_set:
                mock_redis_get.return_value = json.dumps(expected_dict)

                storage_manager = manager_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                )

                result = storage_manager.create(item_id, create_dict)

                self.assertTrue(isinstance(result, StorageItem))

            mock_redis_set.assert_called_with(item_id.__str__(), json.dumps(expected_dict))

    @inject
    def test_create_custom_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        create_dict = {
            "value": 10,
        }

        expected_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": None,
            "pending": False,
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "set") as mock_redis_set:
                mock_redis_get.return_value = json.dumps(expected_dict)

                storage_manager = manager_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                    entity=CustomStateItem,
                )

                storage_manager.create(item_id, create_dict)

                mock_redis_set.assert_called_with(item_id.__str__(), json.dumps(expected_dict))

                create_dict = {
                    "value": 10,
                    "expected": 20,
                    "pending": True,
                }

                result = storage_manager.create(item_id, create_dict)

                expected_dict = {
                    "id": item_id.__str__(),
                    "value": 10,
                    "expected": 20,
                    "pending": True,
                }

                self.assertTrue(isinstance(result, CustomStateItem))

            mock_redis_set.assert_called_with(item_id.__str__(), json.dumps(expected_dict))


class TestStorageUpdating(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        register_services()

    @inject
    def test_update_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        raw_dict = {
            "id": item_id.__str__(),
            "custom": "value",
        }

        update_dict = {
            "custom": "updated",
        }

        expected_dict = {
            "id": item_id.__str__(),
            "custom": "value",
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "set") as mock_redis_set:
                mock_redis_get.return_value = json.dumps(expected_dict)

                stored_record = StorageItem(item_id, raw_dict)

                storage_manager = manager_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                )

                result = storage_manager.update(stored_record, update_dict)

                self.assertTrue(isinstance(result, StorageItem))

            mock_redis_set.assert_not_called()

    @inject
    def test_update_custom_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        raw_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": None,
            "pending": False,
        }

        update_dict = {
            "expected": 20,
            "pending": True,
        }

        expected_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": 20,
            "pending": True,
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "set") as mock_redis_set:
                mock_redis_get.return_value = json.dumps(expected_dict)

                stored_record = StorageItem(item_id, raw_dict)

                storage_manager = manager_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                    entity=CustomStateItem,
                )

                result = storage_manager.update(stored_record, update_dict)

                self.assertTrue(isinstance(result, CustomStateItem))

            mock_redis_set.assert_called_with(item_id.__str__(), json.dumps(expected_dict))


class TestStorageDeleting(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        register_services()

    @inject
    def test_delete_record(self, repository_factory: StorageRepositoryFactory, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        raw_dict = {
            "id": item_id.__str__(),
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "delete") as mock_redis_delete:
                mock_redis_get.return_value = json.dumps(raw_dict)

                storage_repository = repository_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                )
                storage_manager = manager_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                )

                stored_record = storage_repository.find_one(item_id)

                storage_manager.delete(stored_record)

            mock_redis_delete.assert_called_with(item_id.__str__())

    @inject
    def test_delete_unknown_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "delete") as mock_redis_delete:
                mock_redis_get.return_value = None

                storage_manager = manager_factory.create(
                    host="127.0.0.1",
                    port=6379,
                    database=1,
                )

                stored_record = StorageItem(item_id)

                storage_manager.delete(stored_record)

            mock_redis_delete.assert_not_called()


class CustomStateWithTimeItem(StorageItem):

    @staticmethod
    def create_fields() -> Dict[str or int, str or int or float]:
        return {
            0: "id",
            "value": None,
            "expected": None,
            "pending": False,
            "created_at": None,
            "updated_at": None,
        }

    # -----------------------------------------------------------------------------

    @staticmethod
    def update_fields() -> List[str]:
        return [
            "value",
            "expected",
            "pending",
            "updated_at",
        ]


class TestStorageCreatingWithTime(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        register_services()

    @inject
    def test_create_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        create_dict = {
            "value": 10,
            "expected": None,
            "pending": False,
        }

        expected_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": None,
            "pending": False,
            "created_at": "2021-08-14T08:00:00+00:00",
            "updated_at": None,
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "set") as mock_redis_set:
                with patch.object(fastybird_redisdb_storage_plugin.manager, "datetime") as mock_dt:
                    mock_dt.utcnow = Mock(return_value=datetime.datetime(2021, 8, 14, 8, 0, 0))

                    mock_redis_get.return_value = json.dumps(expected_dict)

                    storage_manager = manager_factory.create(
                        host="127.0.0.1",
                        port=6379,
                        database=1,
                        entity=CustomStateWithTimeItem,
                    )

                    result = storage_manager.create(item_id, create_dict)

                    self.assertTrue(isinstance(result, CustomStateWithTimeItem))

            mock_redis_set.assert_called_with(item_id.__str__(), json.dumps(expected_dict))

    @inject
    def test_update_record(self, manager_factory: StorageManagerFactory):
        item_id: uuid.UUID = uuid.uuid4()

        raw_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": None,
            "pending": False,
            "created_at": "2021-08-14T08:00:00+00:00",
            "updated_at": None,
        }

        update_dict = {
            "expected": 20,
            "pending": True,
        }

        expected_dict = {
            "id": item_id.__str__(),
            "value": 10,
            "expected": 20,
            "pending": True,
            "created_at": "2021-08-14T08:00:00+00:00",
            "updated_at": "2021-08-14T10:00:00+00:00",
        }

        with patch.object(redis.Redis, "get") as mock_redis_get:
            with patch.object(redis.Redis, "set") as mock_redis_set:
                with patch.object(fastybird_redisdb_storage_plugin.manager, "datetime") as mock_dt:
                    mock_dt.utcnow = Mock(return_value=datetime.datetime(2021, 8, 14, 10, 0, 0))

                    mock_redis_get.return_value = json.dumps(expected_dict)

                    stored_record = StorageItem(item_id, raw_dict)

                    storage_manager = manager_factory.create(
                        host="127.0.0.1",
                        port=6379,
                        database=1,
                        entity=CustomStateWithTimeItem,
                    )

                    result = storage_manager.update(stored_record, update_dict)

                    self.assertTrue(isinstance(result, CustomStateWithTimeItem))

            mock_redis_set.assert_called_with(item_id.__str__(), json.dumps(expected_dict))


if __name__ == '__main__':
    unittest.main()
