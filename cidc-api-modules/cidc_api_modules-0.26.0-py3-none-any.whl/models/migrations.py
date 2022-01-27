import os, traceback
from contextlib import contextmanager
from functools import partial
from typing import Callable, List, NamedTuple

from alembic import op
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.attributes import flag_modified
from google.cloud import storage

from cidc_schemas.migrations import MigrationResult
from cidc_schemas.prism.merger import _get_uuid_path_map, get_source

from .models import (
    TrialMetadata,
    DownloadableFiles,
    CommonColumns,
    UploadJobStatus,
    UploadJobs,
    String,
    Column,
)
from ..shared.gcloud_client import publish_artifact_upload
from ..config.settings import GOOGLE_ACL_DATA_BUCKET, GOOGLE_UPLOAD_BUCKET


class PieceOfWork(NamedTuple):
    do: Callable[[], None]
    undo: Callable[[], None]


class RollbackableQueue:
    """A collection of reversible pieces-of-work."""

    def __init__(self):
        self.tasks = []
        self.done = set()

    def schedule(self, task: PieceOfWork):
        """Add a task to the task queue."""
        self.tasks.append(task)

    def run_all(self):
        """
        Attempt to run all tasks in the queue, rolling back
        successfully completed tasks if a subsequent task fails.
        """
        for i, task in enumerate(self.tasks):
            try:
                task.do()
                self.done.add(i)
            except:
                self.rollback()
                raise

    def rollback(self):
        """
        Undo any work that has been carried out.
        """
        for i, task in enumerate(self.tasks):
            if i in self.done:
                task.undo()
                self.done.discard(i)


@contextmanager
def migration_session():
    session = Session(bind=op.get_bind())
    task_queue = RollbackableQueue()

    try:
        yield session, task_queue
        print("Commiting SQL session...")
        session.commit()
        print("Session commit succeeded.")
    except Exception as e:
        print(f"Encountered exception: {e.__class__}\n{e}")
        print("Running SQL rollback...")
        session.rollback()
        print("SQL rollback succeeded.")
        if task_queue:
            try:
                print("Running GCS rollback...")
                task_queue.rollback()
                print("GCS rollback succeeded.")
            except Exception as e:
                print(f"GCS rollback failed: {e.__class__}\n{e}")
        raise
    finally:
        session.close()


def run_metadata_migration(
    metadata_migration: Callable[[dict], MigrationResult], use_upload_jobs_table: bool
):
    """Migrate trial metadata, upload job patches, and downloadable files according to `metadata_migration`"""
    with migration_session() as (session, task_queue):
        try:
            _run_metadata_migration(
                metadata_migration, use_upload_jobs_table, task_queue, session
            )
        except:
            traceback.print_exc()
            raise


def _select_trials(session: Session) -> List[TrialMetadata]:
    return session.query(TrialMetadata).with_for_update().all()


class AssayUploads(CommonColumns):
    """This model no longer exists in cidc_api.models, but a partial model is required for migrations."""

    __tablename__ = "assay_uploads"
    status = Column(String)


class ManifestUploads(CommonColumns):
    """This model no longer exists in cidc_api.models, but a partial model is required for migrations."""

    __tablename__ = "manifest_uploads"


def _select_successful_assay_uploads(
    use_upload_jobs_table: bool, session: Session
) -> List[UploadJobs]:
    if use_upload_jobs_table:
        return (
            session.query(UploadJobs)
            .filter_by(status=UploadJobStatus.MERGE_COMPLETED.value, multifile=True)
            .with_for_update()
            .all()
        )

    return (
        session.query(AssayUploads)
        .filter_by(status=UploadJobStatus.MERGE_COMPLETED.value)
        .with_for_update()
        .all()
    )


def _select_manifest_uploads(
    use_upload_jobs_table: bool, session: Session
) -> List[UploadJobs]:
    if use_upload_jobs_table:
        return (
            session.query(UploadJobs).filter_by(multifile=False).with_for_update().all()
        )

    return session.query(ManifestUploads).with_for_update().all()


def _run_metadata_migration(
    metadata_migration: Callable[[dict], MigrationResult],
    use_upload_jobs_table: bool,
    gcs_tasks: RollbackableQueue,
    session: Session,
):
    # Migrate all trial records
    trials = _select_trials(session)
    for trial in trials:
        print(f"Running metadata migration for trial: {trial.trial_id}")
        migration = metadata_migration(trial.metadata_json)

        # Update the trial metadata object
        trial.safely_set_metadata_json(migration.result)

        # A workaround fix for JSON field modifications not being tracked
        # by SQLalchemy for some reason. Using MutableDict.as_mutable(JSON)
        # in the model doesn't seem to help.
        flag_modified(trial, "metadata_json")

        # If this trial has no file updates, move on to the next one
        if len(migration.file_updates) == 0:
            continue

        # Update the relevant downloadable files and GCS objects
        uuid_path_map = _get_uuid_path_map(migration.result)
        for old_gcs_uri, artifact in migration.file_updates.items():
            print(f"Updating GCS and artifact info for {old_gcs_uri}: {artifact}")
            # Update the downloadable file associated with this blob
            df = DownloadableFiles.get_by_object_url(old_gcs_uri, session=session)
            for column, value in artifact.items():
                if hasattr(df, column):
                    setattr(df, column, value)

            # Regenerate additional metadata from the migrated clinical trial
            # metadata object.
            print(
                f"Regenerating additional metadata for artifact with uuid {artifact['upload_placeholder']}"
            )
            artifact_path = uuid_path_map[artifact["upload_placeholder"]]
            df.additional_metadata = get_source(
                migration.result, artifact_path, skip_last=True
            )[1]

            # If the GCS URI has changed, rename the blob
            # makes call to bucket.rename_blob 
            new_gcs_uri = artifact["object_url"]
            if old_gcs_uri != new_gcs_uri:
                print(
                    f"Encountered GCS data bucket artifact URI to update: {old_gcs_uri}"
                )
                renamer = PieceOfWork(
                    partial(
                        rename_gcs_blob, GOOGLE_ACL_DATA_BUCKET, old_gcs_uri, new_gcs_uri
                    ),
                    partial(
                        rename_gcs_blob, GOOGLE_ACL_DATA_BUCKET, new_gcs_uri, old_gcs_uri
                    ),
                )
                gcs_tasks.schedule(renamer)

    # Migrate all assay upload successes
    successful_assay_uploads = _select_successful_assay_uploads(
        use_upload_jobs_table, session
    )
    for upload in successful_assay_uploads:
        print(f"Running metadata migration for assay upload: {upload.id}")
        if use_upload_jobs_table:
            migration = metadata_migration(upload.metadata_patch)
            upload.metadata_patch = migration.result
            # A workaround fix for JSON field modifications not being tracked
            # by SQLalchemy for some reason. Using MutableDict.as_mutable(JSON)
            # in the model doesn't seem to help.
            flag_modified(upload, "metadata_patch")
        else:
            migration = metadata_migration(upload.assay_patch)
            upload.assay_patch = migration.result
            flag_modified(upload, "assay_patch")

        # Update the GCS URIs of files that were part of this upload
        new_file_map = {}
        for (
            old_upload_uri,
            old_target_uri,
            artifact_uuid,
        ) in upload.upload_uris_with_data_uris_with_uuids():
            upload_timestamp = old_upload_uri[len(old_target_uri) + 1 :]
            if old_target_uri in migration.file_updates:
                new_target_uri = migration.file_updates[old_target_uri]["object_url"]
                if old_target_uri != new_target_uri:
                    print(
                        f"Encountered GCS upload bucket artifact URI to update: {old_upload_uri}"
                    )
                    new_upload_uri = "/".join([new_target_uri, upload_timestamp])
                    renamer = PieceOfWork(
                        partial(
                            rename_gcs_blob,
                            GOOGLE_UPLOAD_BUCKET,
                            old_upload_uri,
                            new_upload_uri,
                        ),
                        partial(
                            rename_gcs_blob,
                            GOOGLE_UPLOAD_BUCKET,
                            new_upload_uri,
                            old_upload_uri,
                        ),
                    )
                    gcs_tasks.schedule(renamer)
                new_file_map[new_upload_uri] = artifact_uuid

        # Update the upload's file map to use new GCS URIs
        upload.gcs_file_map = new_file_map

    # Migrate all manifest records
    manifest_uploads = _select_manifest_uploads(use_upload_jobs_table, session)
    for upload in manifest_uploads:
        print(f"Running metadata migration for manifest upload: {upload.id}")
        migration = metadata_migration(upload.metadata_patch)

        # Update the metadata patch
        upload.metadata_patch = migration.result

        # A workaround fix for JSON field modifications not being tracked
        # by SQLalchemy for some reason. Using MutableDict.as_mutable(JSON)
        # in the model doesn't seem to help.
        flag_modified(upload, "metadata_patch")

    # Attempt to make GCS updates
    print(f"Running all GCS tasks...")
    gcs_tasks.run_all()
    print(f"GCS tasks succeeded.")


dont_run = os.environ.get("TESTING") or os.environ.get("ENV") == "dev"


def rename_gcs_blob(bucket, old_name, new_name):
    full_old_uri = f"gs://{bucket}/{old_name}"
    full_new_uri = f"gs://{bucket}/{new_name}"
    message = f"GCS: moving {full_old_uri} to {full_new_uri}"
    if dont_run:
        print(f"SKIPPING: {message}")
        return

    print(message)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    old_blob = bucket.blob(old_name)
    new_blob = bucket.rename_blob(old_blob, new_name)
    return new_blob


def republish_artifact_uploads():
    """
    Publish all downloadable_file IDs to the `artifact_upload` Pub/Sub topic,
    triggering downstream file post-processing (e.g., pre-computation for visualization
    purposes).
    """
    if dont_run:
        print("Skipping 'republish_artifact_uploads' because this is a test")
        return

    with migration_session() as (session, _):
        files = session.query(DownloadableFiles).all()
        for f in files:
            print(
                f"Publishing to 'artifact_upload' topic for downloadable file with in bucket url {f.object_url}"
            )
            publish_artifact_upload(f.object_url)
