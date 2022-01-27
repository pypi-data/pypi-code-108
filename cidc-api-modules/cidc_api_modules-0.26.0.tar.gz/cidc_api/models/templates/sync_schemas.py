__all__ = [
    "syncall_from_blobs",
    "update_trial_from_metadata_json",
]

from collections import OrderedDict
from copy import deepcopy
from sqlalchemy.orm.session import Session
from typing import Any, Dict, List, Optional, Tuple

from ..models import TrialMetadata, UploadJobs
from .model_core import MetadataModel, with_default_session
from .trial_metadata import (
    ClinicalTrial,
    Cohort,
    CollectionEvent,
    Participant,
    Sample,
    Shipment,
)
from .utils import *
from ...config.logging import get_logger

logger = get_logger(__name__)


@with_default_session
def _make_sample_to_shipment_map(trial_id: str, *, session: Session) -> Dict[str, str]:
    """
    For a given trial, generate a mapping from a cimac_id to the manifest_id it was loaded.
    Uses the UploadJobs where each patch contains only a single shipment and its samples.
    """
    sample_to_shipment_map = {}

    uploads = (
        session.query(UploadJobs)
        .filter(UploadJobs.trial_id == trial_id)
        .order_by(UploadJobs._created)
        .all()
    )
    for upload in uploads:
        shipments = upload.metadata_patch.get("shipments", [])
        if len(shipments) == 0:
            continue
        elif len(shipments) > 1:
            raise Exception(
                f"Multiple shipments in single upload: {upload.id} on trial {upload.trial_id}"
            )
        # else: # len(shipments) == 1

        manifest_id = shipments[0]["manifest_id"]

        for partic in upload.metadata_patch["participants"]:
            for sample in partic["samples"]:
                sample_to_shipment_map[sample["cimac_id"]] = manifest_id

    return sample_to_shipment_map


def update_trial_from_metadata_json(trial_md: dict) -> List[Exception]:
    db_trial = ClinicalTrial.get_by_id(trial_md["protocol_identifier"])
    if db_trial is None:
        raise Exception(
            f"Trial {trial_md['protocol_identifier']} not found in relational tables."
        )

    # relational hook validates by "upsert"
    # also might need to remove cohorts / collection event too
    ordered_records_to_add, records_to_remove = OrderedDict(), []
    ordered_records_to_add[ClinicalTrial] = [
        ClinicalTrial(
            # borrowing from sync_schemas since we're already unmarshalling
            # better handled by a UI change to {key: value}, then old=**request.json
            **_get_all_values(target=ClinicalTrial, old=trial_md)
        )
    ]

    # currently need to compare metadata to look for changes in other tables
    # as UI always returns full list of all values
    old_cohorts = set(db_trial.allowed_cohort_names)
    new_cohorts = set(trial_md.get("allowed_cohort_names", []))
    ordered_records_to_add[Cohort] = [
        Cohort(trial_id=trial_md["protocol_identifier"], cohort_name=value)
        for value in new_cohorts.difference(old_cohorts)
    ]
    records_to_remove.extend(
        Cohort.get_by_id(trial_md["protocol_identifier"], value)
        for value in old_cohorts.difference(new_cohorts)
    )

    old_collections = set(db_trial.allowed_collection_event_names)
    new_collections = set(trial_md.get("allowed_collection_event_names", []))
    ordered_records_to_add[CollectionEvent] = [
        CollectionEvent(trial_id=trial_md["protocol_identifier"], event_name=value)
        for value in new_collections.difference(old_collections)
    ]
    records_to_remove.extend(
        CollectionEvent.get_by_id(trial_md["protocol_identifier"], value)
        for value in old_collections.difference(new_collections)
    )

    return in_single_transaction(
        {
            insert_record_batch: {"ordered_records": ordered_records_to_add},
            remove_record_batch: {"records": records_to_remove},
        }
    )


@with_default_session
def syncall_from_blobs(dry_run: bool = False, *, session: Session) -> List[Exception]:
    """
    Sync all trials from the JSON blobs in TrialMetadata to the new relational tables.
    Handles ClinicalTrial, CollectionEvent, Cohort, Shipment, Participant, and Sample.
    Return a list of all errors encountered.
    """
    errors = []

    trials = session.query(TrialMetadata).all()
    for trial in trials:
        new_errors, new_trial = _generate_new_trial(trial, session=session)
        errors.extend(new_errors)
        if new_trial is None:
            continue

        errors.extend(_sync_collection_events(trial, new_trial))
        errors.extend(_sync_cohorts(trial, new_trial))
        errors.extend(_sync_shipments(trial, new_trial))

        # Since we'll be referencing these for Participant and Sample
        session.flush()

        errors.extend(_sync_participants_and_samples(trial, new_trial))

    # final flush before commit / rollback
    session.flush()

    if dry_run or len(errors):
        session.rollback()
    else:
        session.commit()
    session.close()

    if len(errors):
        logger.error(
            f"Errors in syncall_from_blobs: {len(errors)}\n"
            + "\n".join([str(e) for e in errors])
        )
    else:
        logger.info("No errors in syncall_from_blobs")

    return errors


def _get_all_values(
    target: MetadataModel, old: dict, drop: List[str] = []
) -> Dict[str, Any]:
    """Returns all of the values from `old` that are columns of `target` excepting anything keys in `drop`"""
    columns_to_check = [c for c in target.__table__.columns]
    for b in _all_bases(type(target)):
        if hasattr(b, "__table__"):
            columns_to_check.extend(b.__table__.columns)

    ret = {
        c.name: old[c.name]
        for c in columns_to_check
        if c.name not in drop and c.name in old
    }

    # put all original data into the json_data column
    if "json_data" not in drop and any(c.name == "json_data" for c in columns_to_check):
        ret["json_data"] = deepcopy(old)

    return ret


def _generate_new_trial(
    trial: TrialMetadata, *, session: Session
) -> Tuple[List[Exception], Optional[ClinicalTrial]]:
    """
    Given a TrialMetadata, set up a new ClinicalTrial.
    Returns one of:
        [Exception()], None
        [], ClinicalTrial()
    """
    try:
        new_trial = session.merge(
            ClinicalTrial(
                protocol_identifier=trial.trial_id,
                **_get_all_values(
                    target=ClinicalTrial,
                    old=trial.metadata_json,
                    drop=["protocol_identifier"],
                ),
            )
        )
        session.flush()
        return [], new_trial

    except Exception as e:
        return [e], None


def _sync_collection_events(
    trial: TrialMetadata, new_trial: ClinicalTrial
) -> List[Exception]:
    """
    Given corresponding TrialMetadata and ClinicalTrial instances, copy over collection events.
    In JSON, stored as list[string] at /allowed_collection_event_names.
    """
    records = {
        CollectionEvent: [
            CollectionEvent(
                event_name=event_name, trial_id=new_trial.protocol_identifier
            )
            for event_name in trial.metadata_json["allowed_collection_event_names"]
        ]
    }

    return insert_record_batch(records, hold_commit=True)


def _sync_cohorts(trial: TrialMetadata, new_trial: ClinicalTrial) -> List[Exception]:
    """
    Given corresponding TrialMetadata and ClinicalTrial instances, copy over cohorts.
    In JSON, stored as list[string] at /allowed_cohort_names.
    """
    records = {
        Cohort: [
            Cohort(cohort_name=cohort_name, trial_id=new_trial.protocol_identifier)
            for cohort_name in trial.metadata_json["allowed_cohort_names"]
        ]
    }

    return insert_record_batch(records, hold_commit=True)


def _sync_shipments(trial: TrialMetadata, new_trial: ClinicalTrial) -> List[Exception]:
    """
    Given corresponding TrialMetadata and ClinicalTrial instances, copy over shipments.
    In JSON, stored as list[shipment] at /shipments, where each shipment is dict[<column name> : <value>]
    """
    records = {
        Shipment: [
            Shipment(
                trial_id=new_trial.protocol_identifier,
                **_get_all_values(target=Shipment, old=shipment),
            )
            for shipment in trial.metadata_json.get("shipments", [])
        ]
    }

    return insert_record_batch(records, hold_commit=True)


def _sync_participants_and_samples(
    trial: TrialMetadata, new_trial: ClinicalTrial,
) -> List[Exception]:
    """
    Given corresponding TrialMetadata and ClinicalTrial instances, copy over participants and samples.
    In JSON, stored as list[participant] at /participants, where each participant is dict[<column name> : <value>]
    with /participants/*/samples : list[sample] where each sample is dict[<column name> : <value>].

    For Participant, JSON participant_id becomes relational trial_participant_id for clarity.
    """
    errors = []
    shipment_map = _make_sample_to_shipment_map(trial.trial_id)

    participants = trial.metadata_json["participants"]
    for partic in participants:
        # special handling for name change
        partic["trial_participant_id"] = partic.pop("participant_id")

        records = {
            Participant: [
                Participant(
                    trial_id=new_trial.protocol_identifier,
                    **_get_all_values(target=Participant, old=partic),
                )
            ]
        }

        records[Sample] = []
        samples = partic.get("samples", [])
        for sample in samples:
            if sample["cimac_id"] not in shipment_map:
                errors.append(
                    Exception(f"No manifest_id found for sample {sample['cimac_id']}")
                )
                continue

            records[Sample].append(
                Sample(
                    trial_id=new_trial.protocol_identifier,
                    manifest_id=shipment_map[sample["cimac_id"]],
                    # neither of the above are in sample, so don't need a `drop`
                    **_get_all_values(target=Sample, old=sample),
                )
            )

        errors.extend(insert_record_batch(records, hold_commit=True))

    return errors
