__all__ = [
    "HandeImage",
    "HandeRecord",
    "HandeUpload",
    "WESRecord",
    "WESUpload",
]

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from .file_metadata import ImageFile, NGSAssayFiles, NGSUpload, Upload
from .model_core import MetadataModel
from .trial_metadata import Sample


class HandeUpload(Upload):
    records = relationship(
        "HandeRecord", back_populates="upload", sync_backref=False, viewonly=True
    )
    images = relationship(
        "HandeImage", back_populates="upload", sync_backref=False, viewonly=True
    )

    __mapper_args__ = {"polymorphic_identity": "hande"}


class HandeImage(ImageFile):
    __tablename__ = "hande_images"
    __mapper_args__ = {"polymorphic_identity": "hande_image.svs"}

    object_url = Column(String, primary_key=True)
    upload_id = Column(Integer, nullable=False)

    upload = relationship(
        HandeUpload, back_populates="images", sync_backref=False, viewonly=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            [upload_id, object_url], [ImageFile.upload_id, ImageFile.object_url]
        ),
    )


class HandeRecord(MetadataModel):
    __tablename__ = "hande_records"
    upload_id = Column(Integer, nullable=False, primary_key=True)
    cimac_id = Column(String, nullable=False, primary_key=True)
    trial_id = Column(String, nullable=False)
    image_url = Column(String, nullable=False)

    tumor_tissue_percentage = Column(
        Numeric,
        CheckConstraint(
            "tumor_tissue_percentage >= 0 and tumor_tissue_percentage <= 100"
        ),
    )
    viable_tumor_percentage = Column(
        Numeric,
        CheckConstraint(
            "viable_tumor_percentage >= 0 and viable_tumor_percentage <= 100"
        ),
    )
    viable_stroma_percentage = Column(
        Numeric,
        CheckConstraint(
            "viable_stroma_percentage >= 0 and viable_stroma_percentage <= 100"
        ),
    )
    necrosis_percentage = Column(
        Numeric,
        CheckConstraint("necrosis_percentage >= 0 and necrosis_percentage <= 100"),
    )
    fibrosis_percentage = Column(
        Numeric,
        CheckConstraint("fibrosis_percentage >= 0 and fibrosis_percentage <= 100"),
    )
    comment = Column(String)

    upload = relationship(
        HandeUpload, back_populates="records", sync_backref=False, viewonly=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            [trial_id, upload_id], [HandeUpload.trial_id, HandeUpload.id]
        ),
        ForeignKeyConstraint([trial_id, cimac_id], [Sample.trial_id, Sample.cimac_id]),
    )

    @property
    def image(self) -> HandeImage:
        return HandeImage.get_by_id(self.image_url, self.upload_id)


class WESUpload(NGSUpload):
    __tablename__ = "wes_uploads"

    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        doc="A unique ID to identify this upload.",
    )
    trial_id = Column(
        String, primary_key=True,  # both True allows for use as multi Foreign Key
    )
    sequencing_protocol = Column(
        Enum(
            "Express Somatic Human WES (Deep Coverage) v1.1",
            "Somatic Human WES v6",
            "TWIST",
            name="sequencing_protocol_enum",
        ),
        doc="Protocol and version used for the sequencing.",
    )
    bait_set = Column(
        Enum(
            "whole_exome_illumina_coding_v1",
            "broad_custom_exome_v1",
            "TWIST Dana Farber Custom Panel",
            "TWIST Custom Panel PN 101042",
            name="bait_set_enum",
        ),
        nullable=False,
        doc="Bait set ID.",
    )
    read_length = Column(
        Integer,
        CheckConstraint("read_length > 0 and read_length <= 1000"),
        nullable=False,
        doc="Number of cycles for each sequencing read.",
    )

    __table_args__ = (
        ForeignKeyConstraint([id, trial_id], [NGSUpload.id, NGSUpload.trial_id]),
    )

    records = relationship(
        "WESRecord", back_populates="upload", sync_backref=False, viewonly=True
    )

    __mapper_args__ = {"polymorphic_identity": "wes"}


class WESRecord(MetadataModel):
    __tablename__ = "wes_records"

    upload_id = Column(Integer, nullable=False, primary_key=True)
    cimac_id = Column(String, nullable=False, primary_key=True)
    trial_id = Column(String, nullable=False)

    sequencing_date = Column(Date, doc="Date of sequencing.")
    quality_flag = Column(Numeric, doc="Flag used for quality.",)

    upload = relationship(
        WESUpload, back_populates="records", sync_backref=False, viewonly=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            [trial_id, upload_id], [HandeUpload.trial_id, HandeUpload.id]
        ),
        ForeignKeyConstraint([trial_id, cimac_id], [Sample.trial_id, Sample.cimac_id]),
    )

    @property
    def files(self) -> NGSAssayFiles:
        return NGSAssayFiles.get_by_id(
            upload_id=self.upload_id, cimac_id=self.cimac_id, trial_id=self.trial_id
        )
