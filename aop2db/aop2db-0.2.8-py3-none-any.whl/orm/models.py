"""Model definitions."""

from sqlalchemy import TEXT, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# AOP
stressor_chemical = Table(
    "stressor_chemical_association",
    Base.metadata,
    Column("stressor_id", ForeignKey("aop_stressor.id"), primary_key=True),
    Column("chemical_id", ForeignKey("aop_chemical.id"), primary_key=True),
)

ke_be = Table(
    "key_event_bio_event_association",
    Base.metadata,
    Column("key_event_id", ForeignKey("aop_key_event.id"), primary_key=True),
    Column("bio_event_id", ForeignKey("aop_bio_event.id"), primary_key=True),
)

stressor_ke = Table(
    "stressor_key_event_association",
    Base.metadata,
    Column("key_event_id", ForeignKey("aop_key_event.id"), primary_key=True),
    Column("stressor_id", ForeignKey("aop_stressor.id"), primary_key=True),
)


class Chemical(Base):
    """Table with all AOP chemical compounds."""

    __tablename__ = "aop_chemical"

    id = Column(Integer, primary_key=True)
    aop_hash = Column(String(45), index=True)
    casrn = Column(String(45), index=True)
    jchem_inchi_key = Column(String(255))
    indigo_inchi_key = Column(String(255))
    name = Column(String(255), index=True)
    dsstox_id = Column(String(45))

    synonyms = relationship("Synonym", back_populates="chemical")
    stressors = relationship(
        "Stressor", secondary=stressor_chemical, back_populates="chemicals"
    )


class Stressor(Base):
    """Table with all AOP stressors i.e. chemicals that affect AOPs."""

    __tablename__ = "aop_stressor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_id = Column(Integer, index=True)
    aop_hash = Column(String(45), index=True)
    name = Column(String(255), index=True)
    description = Column(TEXT)
    exposure_characterization = Column(TEXT)
    creation = Column(DateTime)
    last_modified = Column(DateTime)

    chemicals = relationship(
        "Chemical", secondary=stressor_chemical, back_populates="stressors"
    )
    aops = relationship("AopStressor", back_populates="stressor")


class Synonym(Base):
    """Table with all AOP synonyms used for the chemical compounds."""

    __tablename__ = "aop_chemical_synonym"
    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String(255))

    chemical_id = Column(Integer, ForeignKey(Chemical.id))
    chemical = relationship("Chemical", back_populates="synonyms")


class CellTerm(Base):
    """Cell terms for KeyEvents."""

    __tablename__ = "aop_cell_term"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(45), index=True)
    source_id = Column(Integer)
    name = Column(String(45))

    # key_events = relationship("KeyEvent", backref="cell_term")


class OrganTerm(Base):
    """Organ terms for KeyEvents."""

    __tablename__ = "aop_organ_term"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(45), index=True)
    source_id = Column(Integer)
    name = Column(String(45))


class LifeStage(Base):
    """Life stage terms for AOPs and KeyEvents."""

    __tablename__ = "aop_life_stage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    life_stage = Column(String(255))

    # many to many rels
    aops = relationship("LifeStageAop", back_populates="life_stage")
    key_events = relationship("LifeStageKeyEvent", back_populates="life_stage")
    kers = relationship("LifeStageKeyEventRelationship", back_populates="life_stage")


class Sex(Base):
    """Sex terms for AOPs and KeyEvents."""

    __tablename__ = "aop_sex"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sex = Column(String(45))

    # many to many rels
    aops = relationship("SexAop", back_populates="sex")
    key_events = relationship("SexKeyEvent", back_populates="sex")
    kers = relationship("SexKeyEventRelationship", back_populates="sex")


class Taxonomy(Base):
    """Taxonomy terms for AOPs and KeyEvents."""

    __tablename__ = "aop_taxonomy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(String(45), index=True)
    source = Column(String(45))
    source_id = Column(String(45))
    tax_id = Column(Integer, index=True)
    species = Column(String(255), index=True)
    name = Column(String(255))

    # many to many rels
    aops = relationship("TaxonomyAop", back_populates="taxonomy")
    key_events = relationship("TaxonomyKeyEvent", back_populates="taxonomy")
    kers = relationship("TaxonomyKeyEventRelationship", back_populates="taxonomy")


class BiologicalObject(Base):
    """Biological objects referenced by KeyEvents."""

    __tablename__ = "aop_bio_object"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(String(45), index=True)
    source = Column(String(45))
    source_id = Column(String(45), index=True)
    name = Column(String(255))

    # events = relationship("BiologicalEvent", backref="bio_object")


class BiologicalProcess(Base):
    """Biological processes referenced by KeyEvents."""

    __tablename__ = "aop_bio_process"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(String(45), index=True)
    source = Column(String(45))
    source_id = Column(String(45), index=True)
    name = Column(String(255))

    # events = relationship("BiologicalEvent", backref="bio_process")


class BiologicalAction(Base):
    """Biological actions referenced by KeyEvents."""

    __tablename__ = "aop_bio_action"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(String(45), index=True)
    source = Column(String(45))
    source_id = Column(String(45), index=True)
    name = Column(String(255))

    # events = relationship("BiologicalEvent", backref="bio_action")


class BiologicalEvent(Base):
    """Biological events are some combination of a biological process, biological action, and biological object."""

    __tablename__ = "aop_bio_event"

    id = Column(Integer, primary_key=True, autoincrement=True)

    bio_action_id = Column(Integer, ForeignKey(BiologicalAction.id))
    bio_process_id = Column(Integer, ForeignKey(BiologicalProcess.id))
    bio_object_id = Column(Integer, ForeignKey(BiologicalObject.id))

    bio_action = relationship(
        "BiologicalAction", backref="events", foreign_keys=[bio_action_id]
    )
    bio_process = relationship(
        "BiologicalProcess", backref="events", foreign_keys=[bio_process_id]
    )
    bio_object = relationship(
        "BiologicalObject", backref="events", foreign_keys=[bio_object_id]
    )

    key_events = relationship("KeyEvent", secondary=ke_be, backref="bio_events")


class KeyEvent(Base):
    """A discrete biological change that can be measured."""

    __tablename__ = "aop_key_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_id = Column(Integer, index=True)
    aop_hash = Column(String(45), index=True)
    title = Column(String(255))
    source = Column(String(45))
    short_name = Column(String(255))
    biological_organization_level = Column(String(45))
    description = Column(TEXT)
    measurement_methodology = Column(TEXT)
    references = Column(TEXT)
    evidence_supporting_taxonomic_applicability = Column(TEXT)

    # TODO: Add evidence and description metatable for stressor/KE
    stressors = relationship(
        "Stressor", secondary=stressor_ke, backref="key_events"
    )  # many-to-many

    # New tables for cell_term and organ_term - many-to-one
    organ_term_id = Column(Integer, ForeignKey(OrganTerm.id))
    organ_term = relationship(
        "OrganTerm", backref="key_events", foreign_keys=[organ_term_id]
    )

    cell_term_id = Column(Integer, ForeignKey(CellTerm.id))
    cell_term = relationship(
        "CellTerm", backref="key_events", foreign_keys=[cell_term_id]
    )

    # Many to many rels
    sexes = relationship("SexKeyEvent", back_populates="key_event")
    taxonomies = relationship("TaxonomyKeyEvent", back_populates="key_event")
    life_stages = relationship("LifeStageKeyEvent", back_populates="key_event")

    # KeyEvent Relationships = many-to-one
    # up_events = relationship("KeyEventRelationship", back_populates="up_event")
    # down_events = relationship("KeyEventRelationship", back_populates="down_event")

    # Map to BioEvent to the combo of object/process/action
    # bio_event_id = Column(Integer, ForeignKey(BiologicalEvent.id))
    # bio_event = relationship("BiologicalEvent", backref="key_events")

    # Links to AOP table
    # Key events occur in between initiating event and outcome, these are the extras: many-to-many
    # Molecular Initiating Event -> KE -> KE -> Adverse Outcome (for example)
    aops = relationship("AopKeyEvent", back_populates="key_event")


class KeyEventRelationship(Base):
    """An evidence-based relationship between two key events."""

    __tablename__ = "aop_key_event_relationship"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(String(45), index=True)
    description = Column(TEXT)
    quantitative_understanding = Column(TEXT)
    evidence_supporting_taxonomic_applicability = Column(TEXT)
    source = Column(String(45))
    creation = Column(DateTime)
    last_modified = Column(DateTime)
    references = Column(TEXT)

    # Link to KeyEvents = many-to-one
    up_event_id = Column(Integer, ForeignKey(KeyEvent.id))
    down_event_id = Column(Integer, ForeignKey(KeyEvent.id))

    up_event = relationship("KeyEvent", backref="up_events", foreign_keys=[up_event_id])
    down_event = relationship(
        "KeyEvent", backref="down_events", foreign_keys=[down_event_id]
    )

    # Evidence columns
    evidence_value = Column(TEXT)
    evidence_biological_plausibility = Column(TEXT)
    evidence_emperical_support_linkage = Column(TEXT)
    evidence_uncertainties_or_inconsistencies = Column(TEXT)

    # Sex evidence, life stages, and taxonomy evidence are many to many relationships
    sexes = relationship("SexKeyEventRelationship", back_populates="ker")
    taxonomies = relationship("TaxonomyKeyEventRelationship", back_populates="ker")
    life_stages = relationship("LifeStageKeyEventRelationship", back_populates="ker")

    aops = relationship("AopKer", back_populates="ker")


class Aop(Base):
    """Table describing AOPs.

    An adverse outcome pathway is a chain of Key Events starting with a molecular initiating events and ending with
    an adverse outcome.
    """

    __tablename__ = "aop"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_id = Column(Integer, index=True)
    aop_hash = Column(String(45), index=True)
    title = Column(String(255))
    background = Column(TEXT)
    short_name = Column(String(255))
    abstract = Column(TEXT)
    source = Column(String(45))
    creation = Column(DateTime)
    last_modified = Column(DateTime)
    authors = Column(TEXT)
    references = Column(TEXT)

    wiki_status = Column(String(100))
    oecd_status = Column(String(100))
    saaop_status = Column(String(100))
    oecd_project = Column(String(45))

    essentiality_support = Column(TEXT)  # May be a lot of text
    potential_applications = Column(TEXT)

    # TODO - decide if "overall-assessment" property needed
    #  => {"overall-assessment": {"description": TEXT, "applicability": TEXT,
    #  "key-event-essentiality-summary": TEXT, "weight-of-evidence-summary": TEXT, "quantitative-considerations: TEXT}}

    # Key events occur in between initiating event and outcome, these are the extras: many-to-many
    # Molecular Initiating Event -> KE -> KE -> Adverse Outcome (for example)
    key_events = relationship("AopKeyEvent", back_populates="aop")

    # many-to-many relations
    sexes = relationship("SexAop", back_populates="aop")
    taxonomies = relationship("TaxonomyAop", back_populates="aop")
    life_stages = relationship("LifeStageAop", back_populates="aop")
    kers = relationship("AopKer", back_populates="aop")
    stressors = relationship("AopStressor", back_populates="aop")

    # Skipped overall_assessment


# Custom association tables
# Key Event Links
class SexKeyEvent(Base):
    """Association table connecting Sex and KeyEvent models."""

    __tablename__ = "aop_sex_key_event_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sex_id = Column(Integer, ForeignKey(Sex.id), index=True)
    key_event_id = Column(Integer, ForeignKey(KeyEvent.id), index=True)
    evidence = Column(TEXT)

    sex = relationship(Sex, back_populates="key_events")
    key_event = relationship(KeyEvent, back_populates="sexes")


class LifeStageKeyEvent(Base):
    """Association table connecting LifeStage and KeyEvent models."""

    __tablename__ = "aop_life_stage_key_event_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    life_stage_id = Column(Integer, ForeignKey(LifeStage.id), index=True)
    key_event_id = Column(Integer, ForeignKey(KeyEvent.id), index=True)
    evidence = Column(TEXT)

    life_stage = relationship(LifeStage, back_populates="key_events")
    key_event = relationship(KeyEvent, back_populates="life_stages")


class TaxonomyKeyEvent(Base):
    """Association table connecting Taxonomy and KeyEvent models."""

    __tablename__ = "aop_taxonomy_key_event_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tax_id = Column(Integer, ForeignKey(Taxonomy.id), index=True)
    key_event_id = Column(Integer, ForeignKey(KeyEvent.id), index=True)
    evidence = Column(TEXT)

    taxonomy = relationship(Taxonomy, back_populates="key_events")
    key_event = relationship(KeyEvent, back_populates="taxonomies")


# Key Event Relationship Links
class SexKeyEventRelationship(Base):
    """Association table connecting Sex and KeyEventRelationship models."""

    __tablename__ = "aop_sex_ker_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sex_id = Column(Integer, ForeignKey(Sex.id), index=True)
    ker_id = Column(Integer, ForeignKey(KeyEventRelationship.id), index=True)
    evidence = Column(TEXT)

    sex = relationship(Sex, back_populates="kers")
    ker = relationship(KeyEventRelationship, back_populates="sexes")


class LifeStageKeyEventRelationship(Base):
    """Association table connecting LifeStage and KeyEventRelationship models."""

    __tablename__ = "aop_life_stage_ker_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    life_stage_id = Column(Integer, ForeignKey(LifeStage.id), index=True)
    ker_id = Column(Integer, ForeignKey(KeyEventRelationship.id), index=True)
    evidence = Column(TEXT)

    life_stage = relationship(LifeStage, back_populates="kers")
    ker = relationship(KeyEventRelationship, back_populates="life_stages")


class TaxonomyKeyEventRelationship(Base):
    """Association table connecting Taxonomy and KeyEventRelationship models."""

    __tablename__ = "aop_taxonomy_ker_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tax_id = Column(Integer, ForeignKey(Taxonomy.id), index=True)
    ker_id = Column(Integer, ForeignKey(KeyEventRelationship.id), index=True)
    evidence = Column(TEXT)

    taxonomy = relationship(Taxonomy, back_populates="kers")
    ker = relationship(KeyEventRelationship, back_populates="taxonomies")


# AOP Links
class SexAop(Base):
    """Association table connecting Sex and Aop models."""

    __tablename__ = "aop_sex_aop_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sex_id = Column(Integer, ForeignKey(Sex.id), index=True)
    aop_hash = Column(Integer, ForeignKey(Aop.id), index=True)
    evidence = Column(TEXT)

    sex = relationship(Sex, back_populates="aops")
    aop = relationship(Aop, back_populates="sexes")


class LifeStageAop(Base):
    """Association table connecting LifeStage and Aop models."""

    __tablename__ = "aop_life_stage_aop_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    life_stage_id = Column(Integer, ForeignKey(LifeStage.id), index=True)
    aop_hash = Column(Integer, ForeignKey(Aop.id), index=True)
    evidence = Column(TEXT)

    life_stage = relationship(LifeStage, back_populates="aops")
    aop = relationship(Aop, back_populates="life_stages")


class TaxonomyAop(Base):
    """Association table connecting Taxonomy and Aop models."""

    __tablename__ = "aop_taxonomy_aop_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tax_id = Column(Integer, ForeignKey(Taxonomy.id), index=True)
    aop_hash = Column(Integer, ForeignKey(Aop.id), index=True)
    evidence = Column(TEXT)

    taxonomy = relationship(Taxonomy, back_populates="aops")
    aop = relationship(Aop, back_populates="taxonomies")


class AopKer(Base):
    """Association table connecting KeyEventRelationship and Aop models."""

    __tablename__ = "aop_kers_aop_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(Integer, ForeignKey(Aop.id), index=True)
    ker_id = Column(Integer, ForeignKey(KeyEventRelationship.id), index=True)
    adjacency = Column(String(45))
    quantitative_understanding_value = Column(String(45))
    evidence = Column(String(45))

    aop = relationship(Aop, back_populates="kers")
    ker = relationship(KeyEventRelationship, back_populates="aops")


class AopKeyEvent(Base):
    """Association table connecting KeyEvent and Aop models."""

    __tablename__ = "aop_key_event_aop_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(Integer, ForeignKey(Aop.id), index=True)
    key_event_id = Column(Integer, ForeignKey(KeyEvent.id), index=True)
    evidence = Column(TEXT)
    key_event_type = Column(String(45))

    aop = relationship(Aop, back_populates="key_events")
    key_event = relationship(KeyEvent, back_populates="aops")


class AopStressor(Base):
    """Association table connecting Stressor and Aop models."""

    __tablename__ = "aop_stressor_aop_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aop_hash = Column(Integer, ForeignKey(Aop.id), index=True)
    stressor_id = Column(Integer, ForeignKey(Stressor.id), index=True)
    description = Column(TEXT)
    evidence = Column(String(45))

    aop = relationship(Aop, back_populates="stressors")
    stressor = relationship(Stressor, back_populates="aops")
