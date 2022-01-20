# pylint: disable=unnecessary-lambda
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    file_format = Column(String(128), nullable=False)
    s3_bucket_name = Column(String(128), nullable=False)
    s3_key_name = Column(String(128), nullable=False)
    content_length = Column(Integer)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("s3_bucket_name", "s3_key_name",),)
