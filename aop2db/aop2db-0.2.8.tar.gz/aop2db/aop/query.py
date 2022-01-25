"""Query the AOP tables."""
import pandas as pd
from sqlalchemy import select

from aop2db.orm.manager import CONN
from aop2db.orm.models import (
    Aop,
    AopKeyEvent,
    AopStressor,
    BiologicalAction,
    BiologicalEvent,
    BiologicalObject,
    BiologicalProcess,
    CellTerm,
    Chemical,
    KeyEvent,
    KeyEventRelationship,
    LifeStage,
    LifeStageAop,
    LifeStageKeyEvent,
    LifeStageKeyEventRelationship,
    OrganTerm,
    Sex,
    Stressor,
    Synonym,
    Taxonomy,
    TaxonomyKeyEvent,
    TaxonomyKeyEventRelationship,
)


def get_aops(verbose: bool = False) -> pd.DataFrame:
    """Get AOP rows.

    NOTE: AOP has no links to Taxonomy.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    stmt = (
        select(
            Aop,
            KeyEvent.id.label("key_event_id"),
            AopKeyEvent.key_event_type,
            Stressor.name.label("stressor"),
            AopStressor.evidence.label("stressor_evidence"),
            LifeStage.life_stage,
        )
        .join(
            AopStressor,
            Aop.id == AopStressor.aop_hash,
            isouter=True,
        )
        .join(
            Stressor,
            isouter=True,
        )
        .join(
            AopKeyEvent,
            Aop.id == AopKeyEvent.aop_hash,
            isouter=True,
        )
        .join(
            KeyEvent,
            isouter=True,
        )
        .join(
            LifeStageAop,
            Aop.id == LifeStageAop.aop_hash,
            isouter=True,
        )
        .join(
            LifeStage,
            isouter=True,
        )
    )

    if verbose:
        print(stmt)

    return pd.read_sql(stmt, con=CONN, index_col="id")


def get_bio_events(verbose: bool = False) -> pd.DataFrame:
    """Get Biological Events rows with KeyEvent foreign key.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    stmt = (
        select(
            BiologicalEvent.id.label("id"),
            BiologicalAction.name.label("bio_action"),
            BiologicalProcess.name.label("bio_process"),
            BiologicalObject.name.label("bio_object"),
            KeyEvent.id.label("key_event_id"),
        )
        .select_from(BiologicalEvent)
        .join(
            BiologicalAction,
            BiologicalAction.id == BiologicalEvent.bio_action_id,
            isouter=True,
        )
        .join(
            BiologicalProcess,
            BiologicalProcess.id == BiologicalEvent.bio_process_id,
            isouter=True,
        )
        .join(
            BiologicalObject,
            BiologicalObject.id == BiologicalEvent.bio_object_id,
            isouter=True,
        )
        .join(
            BiologicalEvent.key_events,
            isouter=True,
        )
    )

    if verbose:
        print(stmt)

    return pd.read_sql(stmt, con=CONN, index_col="id")


def get_key_event_relationships(
    species: int = None, verbose: bool = False
) -> pd.DataFrame:
    """Get a table of Key Event Relationships.

    Parameters
    ----------
    species : int
        The taxonomic ID of a species. Restricts the output to only that species e.g. 9606 for humans.
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    stmt = (
        select(
            KeyEventRelationship,
            Taxonomy.tax_id,
            LifeStage.life_stage,
        )
        .join(
            TaxonomyKeyEventRelationship,
            KeyEventRelationship.id == TaxonomyKeyEventRelationship.ker_id,
            isouter=True,
        )
        .join(
            Taxonomy,
            isouter=True,
        )
        .join(
            LifeStageKeyEventRelationship,
            KeyEventRelationship.id == LifeStageKeyEventRelationship.ker_id,
            isouter=True,
        )
        .join(
            LifeStage,
            isouter=True,
        )
    )

    if species:
        stmt = stmt.where(Taxonomy.tax_id == species)

    if verbose:
        print(stmt)

    return pd.read_sql(stmt, con=CONN, index_col="id")


def get_key_events(
    bio_events: bool = False,
    stressors: bool = False,
    detailed: bool = False,
    species: int = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Get table of key events.

    Parameters
    ----------
    bio_events : bool
        If True, produces a detailed DataFrame with extra information on joined bio events.
    stressors : bool
        If True, produces a detailed DataFrame with extra information on joined stressors.
    detailed : bool
        If True, produces a detailed DataFrame with the table IDs for AOPs, stressors, and bio events..
    species : int
        The taxonomic ID of a species. Restricts the output to only that species e.g. 9606 for humans.
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    if any(
        [bio_events, stressors, detailed]
    ):  # If any of these are true then need detailed df
        stmt = (
            select(
                KeyEvent.id,
                KeyEvent.aop_id,
                KeyEvent.aop_hash,
                KeyEvent.title,
                KeyEvent.short_name,
                KeyEvent.biological_organization_level,
                CellTerm.name.label("cell_term"),
                OrganTerm.name.label("organ_term"),
                Stressor.name.label("stressor_id"),
                Taxonomy.tax_id,
                LifeStage.life_stage,
            )
            .join(
                CellTerm,
                isouter=True,
            )
            .join(
                OrganTerm,
                isouter=True,
            )
            .join(
                KeyEvent.stressors,
                isouter=True,
            )
            .join(
                TaxonomyKeyEvent,
                KeyEvent.id == TaxonomyKeyEvent.key_event_id,
                isouter=True,
            )
            .join(
                Taxonomy,
                isouter=True,
            )
            .join(
                LifeStageKeyEvent,
                KeyEvent.id == LifeStageKeyEvent.key_event_id,
                isouter=True,
            )
            .join(
                LifeStage,
                isouter=True,
            )
        )

    else:  # Simplified version
        stmt = (
            select(
                KeyEvent.id,
                KeyEvent.aop_id,
                KeyEvent.aop_hash,
                KeyEvent.title,
                KeyEvent.short_name,
                KeyEvent.biological_organization_level,
                CellTerm.name.label("cell_term"),
                OrganTerm.name.label("organ_term"),
                Taxonomy.tax_id,
            )
            .join(
                CellTerm,
                isouter=True,
            )
            .join(
                OrganTerm,
                isouter=True,
            )
            .join(
                TaxonomyKeyEvent,
                KeyEvent.id == TaxonomyKeyEvent.key_event_id,
                isouter=True,
            )
            .join(
                Taxonomy,
                isouter=True,
            )
        )

    if species:
        stmt = stmt.where(Taxonomy.tax_id == species)

    if verbose:
        print(stmt)

    ke_df = pd.read_sql(stmt, con=CONN, index_col="id")

    if bio_events:
        be_df = get_bio_events()
        ke_df = ke_df.join(be_df)

    if stressors:
        stressor_df = get_stressors()
        ke_df = (
            ke_df.set_index("stressor_id")
            .join(stressor_df, rsuffix="_stressor")
            .reset_index(drop=True)
        )

    return ke_df


def get_stressors(verbose: bool = False) -> pd.DataFrame:
    """Get table of stressors.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    stmt = select(
        Stressor.id,
        Stressor.aop_hash,
        Stressor.name,
        Chemical.name.label("chemical_name"),
        Chemical.casrn.label("chemical_casrn"),
    ).join(
        Stressor.chemicals,
        isouter=True,
    )

    if verbose:
        print(stmt)

    return pd.read_sql(stmt, con=CONN, index_col="id")


def get_chemicals(synonyms: bool = False, verbose: bool = False) -> pd.DataFrame:
    """Get table of chemicals.

    Parameters
    ----------
    synonyms : bool
        If True, expands the DataFrame to include synonyms for each chemical.
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    if synonyms:
        stmt = select(
            Chemical.id,
            Chemical.name,
            Chemical.casrn,
            Chemical.jchem_inchi_key,
            Chemical.indigo_inchi_key,
            Chemical.dsstox_id,
            Synonym.term.label("synonym"),
        ).join(Synonym)

        if verbose:
            print(stmt)

        return pd.read_sql(stmt, con=CONN, index_col="id")

    else:
        return __basic_query(Chemical, verbose=verbose)


def get_taxonomies(verbose: bool = False) -> pd.DataFrame:
    """Get table of taxonomies.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(Taxonomy, verbose=verbose)


def get_life_stages(verbose: bool = False) -> pd.DataFrame:
    """Get table of life stages.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(LifeStage, verbose=verbose)


def get_sexes(verbose: bool = False) -> pd.DataFrame:
    """Get table of life stages.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(Sex, verbose=verbose)


def get_bio_objects(verbose: bool = False) -> pd.DataFrame:
    """Get table of biological objects.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(BiologicalObject, verbose=verbose)


def get_bio_actions(verbose: bool = False) -> pd.DataFrame:
    """Get table of biological actions.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(BiologicalAction, verbose=verbose)


def get_bio_processes(verbose: bool = False) -> pd.DataFrame:
    """Get table of biological processes.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(BiologicalProcess, verbose=verbose)


def get_cell_terms(verbose: bool = False) -> pd.DataFrame:
    """Get table of cell terms.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(CellTerm, verbose=verbose)


def get_organ_terms(verbose: bool = False) -> pd.DataFrame:
    """Get table of organ terms.

    Parameters
    ----------
    verbose : bool
        If True, prints the SQL statement used to query the database.

    Returns
    -------
    pandas DataFrame
    """
    return __basic_query(OrganTerm, verbose=verbose)


def __basic_query(model, verbose: bool = False) -> pd.DataFrame:
    """Execute and return basic query."""
    stmt = select(model)
    if verbose:
        print(stmt)
    return pd.read_sql(stmt, con=CONN, index_col="id")
