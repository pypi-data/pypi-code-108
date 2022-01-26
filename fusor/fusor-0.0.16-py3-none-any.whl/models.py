"""Model for fusion class"""
from typing import Optional, List, Union, Literal
from enum import Enum

from pydantic import BaseModel, validator, StrictInt, StrictBool, StrictStr, \
    Extra, ValidationError, root_validator
from ga4gh.vrsatile.pydantic import return_value
from ga4gh.vrsatile.pydantic.vrsatile_models import GeneDescriptor, \
    LocationDescriptor, SequenceDescriptor, CURIE
from ga4gh.vrsatile.pydantic.vrs_models import Sequence


class AdditionalFields(str, Enum):
    """Define possible fields that can be added to Fusion object."""

    SEQUENCE_ID = "sequence_id"
    LOCATION_ID = "location_id"
    GENE_DESCRIPTOR = "gene_descriptor"


class DomainStatus(str, Enum):
    """Define possible statuses of functional domains."""

    LOST = "lost"
    PRESERVED = "preserved"


class FunctionalDomain(BaseModel):
    """Define FunctionalDomain class"""

    id: CURIE
    name: StrictStr
    status: DomainStatus
    gene_descriptor: GeneDescriptor
    location_descriptor: LocationDescriptor

    _get_id_val = validator("id", allow_reuse=True)(return_value)

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "status": "lost",
                "name": "Tyrosine-protein kinase, catalytic domain",
                "id": "interpro:IPR020635",
                "gene_descriptor": {
                    "id": "gene:NTRK1",
                    "gene_id": "hgnc:8031",
                    "label": "8031",
                    "type": "GeneDescriptor",
                },
                "location_descriptor": {
                    "id": "fusor.location_descriptor:NP_002520.2",
                    "type": "LocationDescriptor",
                    "location": {
                        "sequence_id": "ga4gh:SQ.vJvm06Wl5J7DXHynR9ksW7IK3_3jlFK6",  # noqa: E501
                        "type": "SequenceLocation",
                        "interval": {
                            "start": {
                                "type": "Number",
                                "value": 510
                            },
                            "end": {
                                "type": "Number",
                                "value": 781
                            }
                        }
                    }
                }
            }


class ComponentType(str, Enum):
    """Define possible structural components."""

    TRANSCRIPT_SEGMENT = "transcript_segment"
    TEMPLATED_SEQUENCE = "templated_sequence"
    LINKER_SEQUENCE = "linker_sequence"
    GENE = "gene"
    UNKNOWN_GENE = "unknown_gene"
    ANY_GENE = "any_gene"


class TranscriptSegmentComponent(BaseModel):
    """Define TranscriptSegment class"""

    component_type: Literal[ComponentType.TRANSCRIPT_SEGMENT] = ComponentType.TRANSCRIPT_SEGMENT  # noqa: E501
    transcript: CURIE
    exon_start: Optional[StrictInt]
    exon_start_offset: Optional[StrictInt] = 0
    exon_end: Optional[StrictInt]
    exon_end_offset: Optional[StrictInt] = 0
    gene_descriptor: GeneDescriptor
    component_genomic_start: Optional[LocationDescriptor]
    component_genomic_end: Optional[LocationDescriptor]

    @root_validator(pre=True)
    def check_exons(cls, values):
        """Check that at least one of {`exon_start`, `exon_end`} is set.
        If set, check that the corresponding `component_genomic` field is set.
        If not set, set corresponding offset to `None`

        """
        msg = "Must give values for either `exon_start`, `exon_end`, or both"
        exon_start = values.get("exon_start")
        exon_end = values.get("exon_end")
        assert exon_start or exon_end, msg

        if exon_start:
            msg = "Must give `component_genomic_start` if `exon_start` is given"  # noqa: E501
            assert values.get("component_genomic_start"), msg
        else:
            values["exon_start_offset"] = None

        if exon_end:
            msg = "Must give `component_genomic_end` if `exon_end` is given"
            assert values.get("component_genomic_end"), msg
        else:
            values["exon_end_offset"] = None
        return values

    _get_transcript_val = validator("transcript", allow_reuse=True)(return_value)  # noqa: E501

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "component_type": "transcript_segment",
                "transcript": "refseq:NM_152263.3",
                "exon_start": 1,
                "exon_start_offset": 0,
                "exon_end": 8,
                "exon_end_offset": 0,
                "gene_descriptor": {
                    "id": "gene:TPM3",
                    "gene_id": "hgnc:12012",
                    "type": "GeneDescriptor",
                    "label": "TPM3",
                },
                "component_genomic_start": {
                    "id": "TPM3:exon1",
                    "type": "LocationDescriptor",
                    "location_id": "ga4gh:VSL.vyyyExx4enSZdWZr3z67-T8uVKH50uLi",  # noqa: E501
                    "location": {
                        "sequence_id": "ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT",  # noqa: E501
                        "type": "SequenceLocation",
                        "interval": {
                            "start": {
                                "type": "Number",
                                "value": 154192135
                            },
                            "end": {
                                "type": "Number",
                                "value": 154192136
                            },
                            "type": "SequenceInterval"
                        }
                    }
                },
                "component_genomic_end": {
                    "id": "TPM3:exon8",
                    "type": "LocationDescriptor",
                    "location_id": "ga4gh:VSL._1bRdL4I6EtpBvVK5RUaXb0NN3k0gpqa",  # noqa: E501
                    "location": {
                        "sequence_id": "ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT",  # noqa: E501
                        "type": "SequenceLocation",
                        "interval": {
                            "start": {
                                "type": "Number",
                                "value": 154170398
                            },
                            "end": {
                                "type": "Number",
                                "value": 154170399
                            },
                            "type": "SequenceInterval"
                        }
                    }
                }
            }


class LinkerComponent(BaseModel):
    """Define Linker class (linker sequence)"""

    component_type: Literal[ComponentType.LINKER_SEQUENCE] = ComponentType.LINKER_SEQUENCE  # noqa: E501
    linker_sequence: SequenceDescriptor

    @validator("linker_sequence", pre=True)
    def validate_sequence(cls, v):
        """Enforce nucleotide base code requirements on sequence literals."""
        if isinstance(v, dict):
            try:
                v["sequence"] = v["sequence"].upper()
                seq = v["sequence"]
            except KeyError:
                raise TypeError
        elif isinstance(v, SequenceDescriptor):
            v.sequence = v.sequence.upper()
            seq = v.sequence
        else:
            raise TypeError

        try:
            Sequence(__root__=seq)
        except ValidationError:
            raise AssertionError("sequence does not match regex '^[A-Za-z*\\-]*$'")  # noqa: E501

        return v

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "component_type": "linker_sequence",
                "linker_sequence": {
                    "id": "sequence:ACGT",
                    "type": "SequenceDescriptor",
                    "sequence": "ACGT",
                    "residue_type": "SO:0000348"
                }
            }


class Strand(str, Enum):
    """Define possible values for strand"""

    POSITIVE = "+"
    NEGATIVE = "-"


class TemplatedSequenceComponent(BaseModel):
    """Define Templated Sequence Component class.
    A templated sequence is a contiguous genomic sequence found in the
    gene product
    """

    component_type: Literal[ComponentType.TEMPLATED_SEQUENCE] = ComponentType.TEMPLATED_SEQUENCE  # noqa: E501
    region: LocationDescriptor
    strand: Strand

    # add strand to sequencelocation, add chr property

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "component_type": "templated_sequence",
                "region": {
                    "id": "chr12:44908821-44908822(+)",
                    "type": "LocationDescriptor",
                    "location_id": "ga4gh:VSL.AG54ZRBhg6pwpPLafF4KgaAHpdFio6l5",  # noqa: E501
                    "location": {
                        "type": "SequenceLocation",
                        "sequence_id": "ga4gh:SQ.6wlJpONE3oNb4D69ULmEXhqyDZ4vwNfl",  # noqa: E501
                        "interval": {
                            "type": "SequenceInterval",
                            "start": {"type": "Number", "value": 44908821},
                            "end": {"type": "Number", "value": 44908822}
                        },
                    },
                    "label": "chr12:44908821-44908822(+)"
                },
                "strand": "+"
            }


class GeneComponent(BaseModel):
    """Define Gene component class."""

    component_type: Literal[ComponentType.GENE] = ComponentType.GENE
    gene_descriptor: GeneDescriptor

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "component_type": "gene",
                "gene_descriptor": {
                    "id": "gene:BRAF",
                    "gene_id": "hgnc:1097",
                    "label": "BRAF",
                    "type": "GeneDescriptor",
                }
            }


class UnknownGeneComponent(BaseModel):
    """Define UnknownGene class. This is primarily intended to represent a
    partner in the result of a fusion partner-agnostic assay, which identifies
    the absence of an expected gene. For example, a FISH break-apart probe may
    indicate rearrangement of an MLL gene, but by design, the test cannot
    provide the identity of the new partner. In this case, we would associate
    any clinical observations from this patient with the fusion of MLL with
    an UnknownGene component.
    """

    component_type: Literal[ComponentType.UNKNOWN_GENE] = ComponentType.UNKNOWN_GENE  # noqa: E501

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "component_type": "unknown_gene"
            }


class AnyGeneComponent(BaseModel):
    """Define AnyGene class. This is primarily intended to represent a partner
    in a categorical fusion, typifying generalizable characteristics of a class
    of fusions such as retained or lost regulatory elements and/or functional
    domains, often curated from biomedical literature for use in genomic
    knowledgebases. For example, EWSR1 rearrangements are often found in Ewing
    and Ewing-like small round cell sarcomas, regardless of the partner gene.
    We would associate this assertion with the fusion of EWSR1 with an
    AnyGene component.
    """

    component_type: Literal[ComponentType.ANY_GENE] = ComponentType.ANY_GENE

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "component_type": "any_gene"
            }


class Event(str, Enum):
    """Define Event class (causative event)"""

    REARRANGEMENT = "rearrangement"
    READTHROUGH = "read-through"
    TRANSSPLICING = "trans-splicing"


class RegulatoryElementType(str, Enum):
    """Define possible types of Regulatory Elements."""

    PROMOTER = "promoter"
    ENHANCER = "enhancer"


class RegulatoryElement(BaseModel):
    """Define RegulatoryElement class"""

    type: RegulatoryElementType
    gene_descriptor: GeneDescriptor

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "type": "promoter",
                "gene_descriptor": {
                    "id": "gene:BRAF",
                    "gene_id": "hgnc:1097",
                    "label": "BRAF",
                    "type": "GeneDescriptor",
                }
            }


class Fusion(BaseModel):
    """Define Fusion class"""

    r_frame_preserved: Optional[StrictBool]
    functional_domains: Optional[List[FunctionalDomain]]
    structural_components: List[Union[TranscriptSegmentComponent,
                                      GeneComponent,
                                      TemplatedSequenceComponent,
                                      LinkerComponent,
                                      UnknownGeneComponent,
                                      AnyGeneComponent]]
    causative_event: Optional[Event]
    regulatory_elements: Optional[List[RegulatoryElement]]

    @validator("structural_components")
    def structural_components_length(cls, v):
        """Ensure >=2 structural components"""
        if len(v) < 2:
            raise ValueError("Fusion must contain at least 2 structural "
                             "components.")
        else:
            return v

    class Config:
        """Configure class."""

        extra = Extra.forbid

        @staticmethod
        def schema_extra(schema, _):
            """Provide example"""
            if "title" in schema.keys():
                schema.pop("title", None)
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)
            schema["example"] = {
                "r_frame_preserved": True,
                "functional_domains": [
                    {
                        "status": "lost",
                        "name": "cystatin domain",
                        "id": "interpro:IPR000010",
                        "gene": {
                            "id": "gene:CST1",
                            "gene_id": "hgnc:2743",
                            "label": "CST1",
                            "type": "GeneDescriptor",
                        }
                    }
                ],
                "structural_components": [
                    {
                        "component_type": "transcript_segment",
                        "transcript": "refseq:NM_152263.3",
                        "exon_start": 1,
                        "exon_start_offset": 0,
                        "exon_end": 8,
                        "exon_end_offset": 0,
                        "gene": {
                            "id": "gene:TPM3",
                            "gene_id": "hgnc:12012",
                            "type": "GeneDescriptor",
                            "label": "TPM3",
                        },
                        "component_genomic_start": {
                            "id": "TPM3:exon1",
                            "type": "LocationDescriptor",
                            "location_id": "ga4gh:VSL.vyyyExx4enSZdWZr3z67-T8uVKH50uLi",  # noqa: E501
                            "location": {
                                "sequence_id": "ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT",  # noqa: E501
                                "type": "SequenceLocation",
                                "interval": {
                                    "start": {
                                        "type": "Number",
                                        "value": 154192135
                                    },
                                    "end": {
                                        "type": "Number",
                                        "value": 154192136
                                    },
                                    "type": "SequenceInterval"
                                }
                            }
                        },
                        "component_genomic_end": {
                            "id": "TPM3:exon8",
                            "type": "LocationDescriptor",
                            "location_id": "ga4gh:VSL._1bRdL4I6EtpBvVK5RUaXb0NN3k0gpqa",  # noqa: E501
                            "location": {
                                "sequence_id": "ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT",  # noqa: E501
                                "type": "SequenceLocation",
                                "interval": {
                                    "start": {
                                        "type": "Number",
                                        "value": 154170398
                                    },
                                    "end": {
                                        "type": "Number",
                                        "value": 154170399
                                    },
                                    "type": "SequenceInterval"
                                }
                            }
                        }
                    },
                    {
                        "component_type": "gene",
                        "gene": {
                            "id": "gene:ALK",
                            "type": "GeneDescriptor",
                            "gene_id": "hgnc:427",
                            "label": "ALK"
                        }
                    }
                ],
                "causative_event": "rearrangement",
                "regulatory_elements": [
                    {
                        "type": "promoter",
                        "gene": {
                            "id": "gene:BRAF",
                            "type": "GeneDescriptor",
                            "gene_id": "hgnc:1097",
                            "label": "BRAF"
                        }
                    }
                ]
            }
