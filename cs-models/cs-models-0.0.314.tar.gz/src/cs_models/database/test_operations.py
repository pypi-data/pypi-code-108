# pylint: disable=duplicate-code
from test.backendtestcase import TestCase

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from freezegun import freeze_time

from src.cs_models.database import engine, operations
from src.cs_models.resources.File import models, schemas


@freeze_time("2020-01-01")
class OperationsTestCase(TestCase):
    def test_create_inside_context_manager(self):
        """Provides example of how to use the `create` method
        inside a context manager."""
        with operations.session_scope() as session:
            instance = operations.create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            self.assertEqual(
                schemas.FileResourceSchema().dump(instance).data,
                {
                    "content_length": None,
                    "file_format": "txt",
                    "id": 1,
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )

    def test_create(self):
        """Provides an example on how to use the `create` method
        by manually managing the database session."""
        session = Session(bind=engine)
        try:
            instance = operations.create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            self.assertEqual(
                schemas.FileResourceSchema().dump(instance).data,
                {
                    "content_length": None,
                    "file_format": "txt",
                    "id": 1,
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )

            # This commit is not really needed since
            # we commit in `create` but is done for consistency.
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_get_or_create(self):
        """Verifies the if the `obj` doesn't exist, a new row
        is created. If `obj` already exists, then the existing
        row is returned."""
        with operations.session_scope() as session:
            instance, created = operations.get_or_create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            self.assertEqual(
                schemas.FileResourceSchema().dump(instance).data,
                {
                    "content_length": None,
                    "file_format": "txt",
                    "id": 1,
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )
            self.assertTrue(created)

            instance, created = operations.get_or_create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            self.assertEqual(
                schemas.FileResourceSchema().dump(instance).data,
                {
                    "content_length": None,
                    "file_format": "txt",
                    "id": 1,
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )
            self.assertFalse(created)

    def test_update_or_create(self):
        with operations.session_scope() as session:
            instance, created = operations.update_or_create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                query_fields=["s3_key_name", "s3_bucket_name"],
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            self.assertEqual(
                schemas.FileResourceSchema().dump(instance).data,
                {
                    "content_length": None,
                    "file_format": "txt",
                    "id": 1,
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )
            self.assertTrue(created)

            instance, created = operations.update_or_create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                query_fields=["s3_key_name", "s3_bucket_name"],
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            self.assertEqual(
                schemas.FileResourceSchema().dump(instance).data,
                {
                    "content_length": None,
                    "file_format": "txt",
                    "id": 1,
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )
            self.assertFalse(created)

    def test_bulk_save(self):
        """Verifies that new objects are created in bulk."""
        with operations.session_scope() as session:
            operations.bulk_save(
                session=session,
                instances=[
                    models.FileModel(**obj)
                    for obj in [
                        {
                            "file_format": "txt",
                            "s3_bucket_name": "test-bucket",
                            "s3_key_name": "key1",
                        },
                        {
                            "file_format": "txt",
                            "s3_bucket_name": "test-bucket",
                            "s3_key_name": "key2",
                        },
                    ]
                ],
            )
            self.assertEqual(
                schemas.FileResourceSchema()
                .dump(session.query(models.FileModel).all(), many=True)
                .data,
                [
                    {
                        "content_length": None,
                        "file_format": "txt",
                        "id": 1,
                        "s3_bucket_name": "test-bucket",
                        "s3_key_name": "key1",
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "content_length": None,
                        "file_format": "txt",
                        "id": 2,
                        "s3_bucket_name": "test-bucket",
                        "s3_key_name": "key2",
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                ],
            )

    def test_bulk_save_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            with operations.session_scope() as session:
                operations.bulk_save(
                    session=session,
                    instances=[
                        models.FileModel(**obj)
                        for obj in [
                            {
                                "file_format": "txt",
                                "s3_bucket_name": "test-bucket",
                                "s3_key_name": "key1",
                            },
                            {
                                "file_format": "txt",
                                "s3_bucket_name": "test-bucket",
                                "s3_key_name": "key1",
                            },
                        ]
                    ],
                )

    def test_bulk_save_updates_and_creates(self):
        with operations.session_scope() as session:
            instance1 = operations.create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key1",
                },
            )
            instance2 = operations.create(
                session=session,
                model=models.FileModel,
                schema=schemas.FileResourceSchema,
                obj={
                    "file_format": "txt",
                    "s3_bucket_name": "test-bucket",
                    "s3_key_name": "key2",
                },
            )
            instance1.s3_key_name = "key1000"
            instance2.s3_key_name = "key2000"

            operations.bulk_save(
                session=session,
                instances=[
                    instance1,
                    instance2,
                    models.FileModel(
                        **{
                            "file_format": "txt",
                            "s3_bucket_name": "test-bucket",
                            "s3_key_name": "key2",
                        }
                    ),
                    models.FileModel(
                        **{
                            "file_format": "txt",
                            "s3_bucket_name": "test-bucket",
                            "s3_key_name": "key3",
                        }
                    ),
                ],
            )

            self.assertEqual(
                [
                    {
                        "content_length": None,
                        "file_format": "txt",
                        "id": 1,
                        "s3_bucket_name": "test-bucket",
                        "s3_key_name": "key1000",
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "content_length": None,
                        "file_format": "txt",
                        "id": 2,
                        "s3_bucket_name": "test-bucket",
                        "s3_key_name": "key2000",
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "content_length": None,
                        "file_format": "txt",
                        "id": 3,
                        "s3_bucket_name": "test-bucket",
                        "s3_key_name": "key2",
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "content_length": None,
                        "file_format": "txt",
                        "id": 4,
                        "s3_bucket_name": "test-bucket",
                        "s3_key_name": "key3",
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                ],
                schemas.FileResourceSchema()
                .dump(session.query(models.FileModel).all(), many=True)
                .data,
            )

    @staticmethod
    def test_assert_sql_queries():
        """Provides an example on how to assert evaluated SQL queries."""
        with operations.assert_sql(
            [
                (
                    "INSERT INTO files (file_format, s3_bucket_name, s3_key_name, updated_at) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        (
                            "txt",
                            "test-bucket",
                            "key1",
                            "2020-01-01 00:00:00.000000",
                        ),
                        (
                            "txt",
                            "test-bucket",
                            "key2",
                            "2020-01-01 00:00:00.000000",
                        ),
                    ),
                )
            ]
        ):
            with operations.session_scope() as session:
                operations.bulk_save(
                    session=session,
                    instances=[
                        models.FileModel(**obj)
                        for obj in [
                            {
                                "file_format": "txt",
                                "s3_bucket_name": "test-bucket",
                                "s3_key_name": "key1",
                            },
                            {
                                "file_format": "txt",
                                "s3_bucket_name": "test-bucket",
                                "s3_key_name": "key2",
                            },
                        ]
                    ],
                )
