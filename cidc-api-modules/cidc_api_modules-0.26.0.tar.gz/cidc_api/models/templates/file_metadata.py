__all__ = [
    "ArtifactCreator",
    "ArtifactCategory",
    "BamFile",
    "Bam_baiFile",
    "BinaryFile",
    "CsvFile",
    "ElisaFile",
    "FastaFile",
    "Fastq_gzFile",
    "FcsFile",
    "File",
    "GzFile",
    "ImageFile",
    "JsonFile",
    "MafFile",
    "NGSAssayFiles",
    "NGSUpload",
    "NpxFile",
    "RccFile",
    "TextFile",
    "TsvFile",
    "Upload",
    "UploadStatus",
    "Vcf_gzFile",
    "VcfFile",
    "XlsxFile",
    "YamlFile",
    "ZipFile",
]

from flask import current_app
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import case

from ..models import Users, with_default_session

from .model_core import MetadataModel
from .trial_metadata import ClinicalTrial, Sample, Shipment


ArtifactCreator = Enum(
    "DFCI", "Mount Sinai", "Stanford", "MD Anderson", name="artifact_creator_enum"
)
ArtifactCategory = Enum(
    "Assay Artifact from CIMAC",
    "Pipeline Artifact",
    "Manifest File",
    name="artifact_category_enum",
)
AssayCreator = Enum(
    "DFCI", "Mount Sinai", "Stanford", "MD Anderson", "TWIST", name="assay_creator_enum"
)
UploadStatus = Enum(
    "started",
    "upload-completed",
    "upload-failed",
    "merge-completed",
    "merge-failed",
    name="upload_status_enum",
)


class Upload(MetadataModel):
    __tablename__ = "uploads"
    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        doc="A unique ID to identify this upload.",
    )
    trial_id = Column(
        String,
        ForeignKey(ClinicalTrial.protocol_identifier),
        primary_key=True,  # both True allows for use as multi Foreign Key
    )

    status = Column(
        UploadStatus,
        nullable=False,
        server_default=UploadStatus.enums[0],  # 'started'
        doc="The current status of the upload.",
    )
    token = Column(
        UUID,
        server_default=text("gen_random_uuid()"),
        nullable=False,
        doc="A long, random identifier for this upload.",
    )
    status_details = Column(
        String,
        nullable=True,
        doc="Text containing feedback on why the upload status is what it is.",
    )
    multifile = Column(
        Boolean, nullable=False, doc="Whether the upload contains multiple files."
    )
    gcs_file_map = Column(
        JSONB,
        nullable=True,
        doc="If multifile, object names for the files to be uploaded mapped to upload_placeholder uuids; else null.",
    )
    gcs_xlsx_uri = Column(
        String,
        nullable=True,
        doc="Track the GCS URI of the .xlsx file used for this upload.",
    )
    upload_type = Column(
        String,
        nullable=False,
        doc="The type of upload (pbmc, wes, olink, wes_analysis, ...)",
    )
    assay_creator = Column(
        AssayCreator, nullable=False, doc="Which CIMAC site created the data"
    )
    uploader_email = Column(
        String,
        ForeignKey(Users.email),
        nullable=False,
        doc="Link to the user who created this upload.",
    )
    shipment_manifest_id = Column(
        String, nullable=True, doc="Only for manifest uploads",
    )

    # Create a GIN index on the GCS object names
    _gcs_objects_idx = Index(
        "upload_gcs_file_map_idx", gcs_file_map, postgresql_using="gin"
    )
    CheckConstraint("multifile or (gcs_file_map is not null)")

    __mapper_args__ = {
        "polymorphic_on": case(
            [(upload_type.in_(["hande", "wes_uploads"]), upload_type)], else_="base"
        ),
        "polymorphic_identity": "base",
    }
    __table_args__ = (
        ForeignKeyConstraint(
            [trial_id, shipment_manifest_id], [Shipment.trial_id, Shipment.manifest_id]
        ),
    )

    def __init__(self, **kwargs):
        if "uploader_email" not in kwargs:
            from ...shared.auth import get_current_user

            kwargs["uploader_email"] = get_current_user().email

        super().__init__(**kwargs)


class NGSUpload(Upload):
    __tablename__ = "ngs_uploads"

    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        doc="A unique ID to identify this upload.",
    )
    trial_id = Column(
        String, primary_key=True,  # both True allows for use as multi Foreign Key
    )
    sequencer_platform = Column(
        Enum(
            "Illumina - HiSeq 2500",
            "Illumina - HiSeq 3000",
            "Illumina - NextSeq 550",
            "Illumina - HiSeq 4000",
            "Illumina - NovaSeq 6000",
            "MiSeq",
            name="sequencer_platform_enum",
        ),
        doc="Sequencer Model, e.g. HiSeq 2500, NextSeq, NovaSeq.",
    )
    library_kit = Column(
        Enum(
            "Hyper Prep ICE Exome Express: 1.0",
            "KAPA HyperPrep",
            "IDT duplex UMI adapters",
            "TWIST",
            name="library_kit_enum",
        ),
        doc="The library construction kit.",
    )
    paired_end_reads = Column(
        Enum("Paired", "Single", name="paired_end_reads_enum"),
        doc="Indicates if the sequencing was performed paired or single ended.",
    )

    __table_args__ = (
        ForeignKeyConstraint([id, trial_id], [Upload.id, Upload.trial_id]),
    )

    records = relationship(
        "NGSAssayFiles", back_populates="upload", sync_backref=False, viewonly=True
    )

    __mapper_args__ = {"polymorphic_identity": "ngs_base"}


class NGSAssayFiles(MetadataModel):
    __tablename__ = "ngs_assay_file_collections"
    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        doc="A unique ID to identify this upload.",
    )

    upload_id = Column(Integer, nullable=False)
    cimac_id = Column(String, nullable=False)
    trial_id = Column(String, nullable=False)

    r1_object_url = Column(String, doc="Fastq file for the first fragment.",)
    r2_object_url = Column(String, doc="Fastq file for the second fragment.",)
    lane = Column(Integer, doc="The lane number from which the reads were generated.")

    bam_object_url = Column(String, doc="Bam file",)
    number = Column(
        Integer,
        doc="An arbitrary number assigned to identify different otherwise equivalent replicates.",
    )

    upload = relationship(
        NGSUpload, back_populates="records", sync_backref=False, viewonly=True
    )
    __table_args__ = (
        ForeignKeyConstraint([trial_id, upload_id], [NGSUpload.trial_id, NGSUpload.id]),
        ForeignKeyConstraint([trial_id, cimac_id], [Sample.trial_id, Sample.cimac_id]),
        CheckConstraint(
            "(r1_object_url is not null and r2_object_url is not null) or bam_object_url is not null"
        ),
        ForeignKeyConstraint(
            [trial_id, upload_id, r1_object_url],
            ["files.trial_id", "files.upload_id", "files.object_url"],
        ),
        ForeignKeyConstraint(
            [trial_id, upload_id, r2_object_url],
            ["files.trial_id", "files.upload_id", "files.object_url"],
        ),
        ForeignKeyConstraint(
            [trial_id, upload_id, bam_object_url],
            ["files.trial_id", "files.upload_id", "files.object_url"],
        ),
    )

    @classmethod
    @with_default_session
    def get_by_id(cls, upload_id, cimac_id, trial_id, session):
        """While a primary key needs to be unique, we want there to be multiple records returned given the ids."""
        with current_app.app_context():
            ret = session.query(cls).filter(
                cls.upload_id == upload_id,
                cls.cimac_id == cimac_id,
                cls.trial_id == trial_id,
            )
        return ret

    @property
    def r1(self):
        return Fastq_gzFile.get_by_id(self.r1_object_url)

    @property
    def r2(self):
        return Fastq_gzFile.get_by_id(self.r2_object_url)

    @property
    def bam(self):
        return BamFile.get_by_id(self.bam_object_url)


class File(MetadataModel):
    __tablename__ = "files"
    object_url = Column(String, primary_key=True)
    upload_id = Column(Integer, primary_key=True)
    trial_id = Column(String, primary_key=False)
    local_path = Column(String, unique=True, doc="Path to a file on a user's computer.")

    upload_placeholder = Column(
        String, doc="A placeholder for when artifact file is being uploaded."
    )
    artifact_creator = Column(
        ArtifactCreator, doc="The name of the center that created this artifact."
    )
    uploader = Column(String, doc="The name of the person uploading the artifact.")
    file_name = Column(
        String,
        doc="The name of the file with extension. Generated from 'gcs_uri_format' fields in templates.",
    )
    uploaded_timestamp = Column(
        String, doc="Timestamp of when artifact was loaded into the system."
    )
    file_size_bytes: Column(Integer, doc="File size in bytes.")
    md5_hash = Column(
        String, doc="MD5 Hash of artifact. Not available for composite GCS objects."
    )
    crc32_hash = Column(String, doc="CRC32c Hash of artifact.")
    visible: Column(
        Boolean,
        doc="Indicates if the artifact is visible. If set to false, the artifact is effectively deleted.",
    )
    artifact_category = Column(ArtifactCategory, doc="Artifact category.")
    data_format = Column(String, doc="Data Format.")
    facet_group = Column(String, doc="The internal data category for this artifact")

    __table_args__ = (
        ForeignKeyConstraint([trial_id, upload_id], [Upload.trial_id, Upload.id],),
        UniqueConstraint(trial_id, upload_id, object_url),
    )
    __mapper_args__ = {"polymorphic_on": data_format, "polymorphic_identity": "base"}


# As the subclasses below do NOT have __tablename__ defined
# they will all be included in `files` with any subclass-specific
# columns being NULL for any other object.

# To use a separate table that will be JOINed, define a table name and add
# object_url = Column(String, ForeignKey(<parent>.object_url), primary_key=True)


class FastaFile(File):
    __mapper_args__ = {"polymorphic_identity": "fasta"}


class Fastq_gzFile(File):
    __mapper_args__ = {"polymorphic_identity": "fastq.gz"}


class Vcf_gzFile(File):
    __mapper_args__ = {"polymorphic_identity": "vcf.gz"}


class ImageFile(File):
    __mapper_args__ = {"polymorphic_identity": "image"}


class VcfFile(File):
    __mapper_args__ = {"polymorphic_identity": "vcf"}


class CsvFile(File):
    __mapper_args__ = {"polymorphic_identity": "csv"}


class TsvFile(File):
    __mapper_args__ = {"polymorphic_identity": "tsv"}


class XlsxFile(File):
    __mapper_args__ = {"polymorphic_identity": "xlsx"}


class NpxFile(File):
    __mapper_args__ = {"polymorphic_identity": "npx"}


class ElisaFile(File):
    __mapper_args__ = {"polymorphic_identity": "elisa"}


class BamFile(File):
    __mapper_args__ = {"polymorphic_identity": "bam"}


class Bam_baiFile(File):
    __mapper_args__ = {"polymorphic_identity": "bam.bai"}


class MafFile(File):
    __mapper_args__ = {"polymorphic_identity": "maf"}


class BinaryFile(File):
    __mapper_args__ = {"polymorphic_identity": "binary"}


class TextFile(File):
    __mapper_args__ = {"polymorphic_identity": "text"}


class ZipFile(File):
    __mapper_args__ = {"polymorphic_identity": "zip"}


class FcsFile(File):
    __mapper_args__ = {"polymorphic_identity": "fcs"}


class GzFile(File):
    __mapper_args__ = {"polymorphic_identity": "gz"}


class RccFile(File):
    __mapper_args__ = {"polymorphic_identity": "rcc"}


class JsonFile(File):
    __mapper_args__ = {"polymorphic_identity": "json"}


class YamlFile(File):
    __mapper_args__ = {"polymorphic_identity": "yaml"}
