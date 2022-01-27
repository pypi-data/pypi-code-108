# -*- coding: utf-8 -*-
import json
import os
import sqlite3

from peewee import (
    BooleanField,
    CharField,
    Check,
    CompositeKey,
    Field,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
    UUIDField,
)

from arkindex_worker import logger
from arkindex_worker.image import open_image, polygon_bounding_box

db = SqliteDatabase(None)


class JSONField(Field):
    field_type = "text"

    def db_value(self, value):
        if value is None:
            return
        return json.dumps(value)

    def python_value(self, value):
        if value is None:
            return
        return json.loads(value)


class CachedImage(Model):
    id = UUIDField(primary_key=True)
    width = IntegerField()
    height = IntegerField()
    url = TextField()

    class Meta:
        database = db
        table_name = "images"


class CachedElement(Model):
    id = UUIDField(primary_key=True)
    parent_id = UUIDField(null=True)
    type = CharField(max_length=50)
    image = ForeignKeyField(CachedImage, backref="elements", null=True)
    polygon = JSONField(null=True)
    rotation_angle = IntegerField(default=0)
    mirrored = BooleanField(default=False)
    initial = BooleanField(default=False)
    worker_version_id = UUIDField(null=True)

    class Meta:
        database = db
        table_name = "elements"

    def open_image(self, *args, max_size=None, **kwargs):
        """
        Open this element's image as a Pillow image.
        This does not crop the image to the element's polygon.
        IIIF servers with maxWidth, maxHeight or maxArea restrictions on image size are not supported.

        :param max_size: Subresolution of the image.
        """
        if not self.image_id or not self.polygon:
            raise ValueError(f"Element {self.id} has no image")

        # Always fetch the image from the bounding box when size differs from full image
        bounding_box = polygon_bounding_box(self.polygon)
        if (
            bounding_box.width != self.image.width
            or bounding_box.height != self.image.height
        ):
            box = f"{bounding_box.x},{bounding_box.y},{bounding_box.width},{bounding_box.height}"
        else:
            box = "full"

        if max_size is None:
            resize = "full"
        else:
            # Do not resize for polygons that do not exactly match the images
            # as the resize is made directly by the IIIF server using the box parameter
            if (
                bounding_box.width != self.image.width
                or bounding_box.height != self.image.height
            ):
                resize = "full"

            # Do not resize when the image is below the maximum size
            elif self.image.width <= max_size and self.image.height <= max_size:
                resize = "full"
            else:
                ratio = max_size / max(self.image.width, self.image.height)
                new_width, new_height = int(self.image.width * ratio), int(
                    self.image.height * ratio
                )
                resize = f"{new_width},{new_height}"

        url = self.image.url
        if not url.endswith("/"):
            url += "/"

        return open_image(
            f"{url}{box}/{resize}/0/default.jpg",
            *args,
            rotation_angle=self.rotation_angle,
            mirrored=self.mirrored,
            **kwargs,
        )


class CachedTranscription(Model):
    id = UUIDField(primary_key=True)
    element = ForeignKeyField(CachedElement, backref="transcriptions")
    text = TextField()
    confidence = FloatField()
    orientation = CharField(max_length=50)
    worker_version_id = UUIDField()

    class Meta:
        database = db
        table_name = "transcriptions"


class CachedClassification(Model):
    id = UUIDField(primary_key=True)
    element = ForeignKeyField(CachedElement, backref="classifications")
    class_name = TextField()
    confidence = FloatField()
    state = CharField(max_length=10)
    worker_version_id = UUIDField()

    class Meta:
        database = db
        table_name = "classifications"


class CachedEntity(Model):
    id = UUIDField(primary_key=True)
    type = CharField(max_length=50)
    name = TextField()
    validated = BooleanField(default=False)
    metas = JSONField(null=True)
    worker_version_id = UUIDField()

    class Meta:
        database = db
        table_name = "entities"


class CachedTranscriptionEntity(Model):
    transcription = ForeignKeyField(
        CachedTranscription, backref="transcription_entities"
    )
    entity = ForeignKeyField(CachedEntity, backref="transcription_entities")
    offset = IntegerField(constraints=[Check("offset >= 0")])
    length = IntegerField(constraints=[Check("length > 0")])
    worker_version_id = UUIDField()
    confidence = FloatField(null=True)

    class Meta:
        primary_key = CompositeKey("transcription", "entity")
        database = db
        table_name = "transcription_entities"


# Add all the managed models in that list
# It's used here, but also in unit tests
MODELS = [
    CachedImage,
    CachedElement,
    CachedTranscription,
    CachedClassification,
    CachedEntity,
    CachedTranscriptionEntity,
]


def init_cache_db(path):
    db.init(
        path,
        pragmas={
            # SQLite ignores foreign keys and check constraints by default!
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
        },
    )
    db.connect()
    logger.info(f"Connected to cache on {path}")


def create_tables():
    """
    Creates the tables in the cache DB only if they do not already exist.
    """
    db.create_tables(MODELS)


def retrieve_parents_cache_path(parent_ids, data_dir="/data", chunk=None):
    assert isinstance(parent_ids, list)
    assert os.path.isdir(data_dir)

    # Handle possible chunk in parent task name
    # This is needed to support the init_elements databases
    filenames = [
        "db.sqlite",
    ]
    if chunk is not None:
        filenames.append(f"db_{chunk}.sqlite")

    # Find all the paths for these databases
    return list(
        filter(
            lambda p: os.path.isfile(p),
            [
                os.path.join(data_dir, parent, name)
                for parent in parent_ids
                for name in filenames
            ],
        )
    )


def merge_parents_cache(paths, current_database):
    """
    Merge all the potential parent task's databases into the existing local one
    """
    assert os.path.exists(current_database)

    if not paths:
        logger.info("No parents cache to use")
        return

    # Open a connection on current database
    connection = sqlite3.connect(current_database)
    cursor = connection.cursor()

    # Merge each table into the local database
    for idx, path in enumerate(paths):
        with SqliteDatabase(path) as source:
            with source.bind_ctx(MODELS):
                source.create_tables(MODELS)

        logger.info(f"Merging parent db {path} into {current_database}")
        statements = [
            "PRAGMA page_size=80000;",
            "PRAGMA synchronous=OFF;",
            f"ATTACH DATABASE '{path}' AS source_{idx};",
            f"REPLACE INTO images SELECT * FROM source_{idx}.images;",
            f"REPLACE INTO elements SELECT * FROM source_{idx}.elements;",
            f"REPLACE INTO transcriptions SELECT * FROM source_{idx}.transcriptions;",
            f"REPLACE INTO classifications SELECT * FROM source_{idx}.classifications;",
        ]

        for statement in statements:
            cursor.execute(statement)
        connection.commit()
