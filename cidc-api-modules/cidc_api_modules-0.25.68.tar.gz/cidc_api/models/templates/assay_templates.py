__all__ = [
    "HandeAssay",
    "WesBamAssay",
    "WesFastqAssay",
]

from .core import Entry, MetadataTemplate, WorksheetConfig
from .model_core import get_property

from .assay_metadata import (
    HandeImage,
    HandeRecord,
    HandeUpload,
    WESRecord,
    WESUpload,
)
from .file_metadata import (
    BamFile,
    Fastq_gzFile,
    NGSAssayFiles,
)


HandeAssay = MetadataTemplate(
    upload_type="hande",
    purpose="assay",
    worksheet_configs=[
        WorksheetConfig(
            "H&E",
            [
                Entry(HandeUpload.trial_id, name="Protocol identifier"),
                Entry(HandeUpload.assay_creator),
            ],
            {
                "Samples": [
                    Entry(HandeRecord.cimac_id),
                    Entry(
                        HandeImage.local_path,
                        name="Image file",
                        gcs_uri_format="{trial_id}/hande/{cimac_id}/image_file.svs",
                        process_as={HandeRecord.image_url: get_property("object_url")},
                    ),
                    Entry(
                        HandeRecord.tumor_tissue_percentage,
                        name="Tumor tissue (% total area)",
                    ),
                    Entry(
                        HandeRecord.viable_tumor_percentage,
                        name="Viable tumor (% area)",
                    ),
                    Entry(
                        HandeRecord.viable_stroma_percentage,
                        name="Viable stroma (% area)",
                    ),
                    Entry(HandeRecord.necrosis_percentage, name="Necrosis (% area)",),
                    Entry(HandeRecord.fibrosis_percentage, name="Fibrosis (% area)",),
                    Entry(HandeRecord.comment),
                ]
            },
        )
    ],
    constants={HandeUpload.upload_type: "hande", HandeUpload.multifile: True,},
)

WesFastqAssay = MetadataTemplate(
    upload_type="wes",
    purpose="assay",
    worksheet_configs=[
        WorksheetConfig(
            "WES",
            [
                Entry(WESUpload.trial_id, name="Protocol identifier"),
                Entry(WESUpload.assay_creator),
                Entry(WESUpload.sequencing_protocol),
                Entry(WESUpload.library_kit),
                Entry(WESUpload.sequencer_platform),
                Entry(WESUpload.paired_end_reads),
                Entry(WESUpload.read_length),
                Entry(WESUpload.bait_set),
            ],
            {
                "Samples": [
                    Entry(WESRecord.cimac_id),
                    Entry(NGSAssayFiles.lane),
                    Entry(
                        Fastq_gzFile.local_path,
                        name="Forward fastq",
                        gcs_uri_format="{trial_id}/wes/{cimac_id}/r1_L{lane}.fastq.gz",
                        process_as={
                            NGSAssayFiles.r1_object_url: get_property("object_url"),
                        },
                    ),
                    Entry(
                        Fastq_gzFile.local_path,
                        name="Reverse fastq",
                        gcs_uri_format="{trial_id}/wes/{cimac_id}/r2_L{lane}.fastq.gz",
                        process_as={
                            NGSAssayFiles.r2_object_url: get_property("object_url"),
                        },
                    ),
                    Entry(WESRecord.sequencing_date),
                    Entry(WESRecord.quality_flag),
                ]
            },
        )
    ],
    constants={WESUpload.upload_type: "wes", WESUpload.multifile: True,},
)

WesBamAssay = MetadataTemplate(
    upload_type="wes",
    purpose="assay",
    worksheet_configs=[
        WorksheetConfig(
            "WES",
            [
                Entry(WESUpload.trial_id, name="Protocol identifier"),
                Entry(WESUpload.assay_creator),
                Entry(WESUpload.sequencing_protocol),
                Entry(WESUpload.library_kit),
                Entry(WESUpload.sequencer_platform),
                Entry(WESUpload.paired_end_reads),
                Entry(WESUpload.read_length),
                Entry(WESUpload.bait_set),
            ],
            {
                "Samples": [
                    Entry(WESRecord.cimac_id),
                    Entry(NGSAssayFiles.number),
                    Entry(
                        BamFile.local_path,
                        name="Bam file",
                        gcs_uri_format="{trial_id}/wes/{cimac_id}/reads_{number}.bam",
                        process_as={
                            NGSAssayFiles.bam_object_url: get_property("object_url"),
                        },
                    ),
                    Entry(WESRecord.sequencing_date),
                    Entry(WESRecord.quality_flag),
                ]
            },
        )
    ],
    constants={WESUpload.upload_type: "wes", WESUpload.multifile: True,},
)


if __name__ == "__main__":
    WesFastqAssay.write("tests/models/templates/examples/wes_fastq_assay.xlsx")
    WesBamAssay.write("tests/models/templates/examples/wes_bam_assay.xlsx")
