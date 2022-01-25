__all__ = [
    "BaseModel",
    "CIDCRole",
    "Column",
    "CommonColumns",
    "DownloadableFiles",
    "EXTRA_DATA_TYPES",
    "IntegrityError",
    "IAMException",
    "NoResultFound",
    "Permissions",
    "prism",  # for CFns
    "ROLES",
    "Session",
    "String",
    "TrialMetadata",
    "unprism",  # for CFns
    "UploadJobs",
    "UploadJobStatus",
    "Users",
    "ValidationMultiError",
    "with_default_session",
]

from collections import defaultdict
import re
import hashlib
import os

os.environ["TZ"] = "UTC"
from datetime import datetime, timedelta
from enum import Enum as EnumBaseClass
from functools import wraps
from typing import Any, BinaryIO, Dict, Optional, List, Union, Callable, Tuple

import pandas as pd
from flask import current_app as app
from google.cloud.storage import Blob
from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    Integer,
    BigInteger,
    String,
    Enum,
    Index,
    func,
    CheckConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
    tuple_,
    asc,
    desc,
    update,
    case,
    select,
    literal_column,
    not_,
    literal,
    or_,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.engine import ResultProxy

from cidc_schemas import prism, unprism, json_validation

from .files import (
    build_trial_facets,
    build_data_category_facets,
    get_facet_groups_for_paths,
    facet_groups_to_categories,
    details_dict,
    FilePurpose,
    FACET_NAME_DELIM,
)

from ..config.db import BaseModel
from ..config.settings import (
    ENV,
    PAGINATION_PAGE_SIZE,
    MAX_PAGINATION_PAGE_SIZE,
    TESTING,
    INACTIVE_USER_DAYS,
    GOOGLE_MAX_DOWNLOAD_PERMISSIONS,
)
from ..shared import emails
from ..shared.gcloud_client import (
    grant_lister_access,
    grant_download_access,
    publish_artifact_upload,
    refresh_intake_access,
    revoke_download_access,
    revoke_intake_access,
    revoke_lister_access,
)
from ..config.logging import get_logger

logger = get_logger(__name__)


def with_default_session(f):
    """
    For some `f` expecting a database session instance as a keyword argument,
    set the default value of the session keyword argument to the current app's
    database driver's session. We need to do this in a decorator rather than
    inline in the function definition because the current app is only available
    once the app is running and an application context has been pushed.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        if "session" not in kwargs:
            kwargs["session"] = app.extensions["sqlalchemy"].db.session
        return f(*args, **kwargs)

    return wrapped


def make_etag(args: Union[dict, list]):
    """Make an etag by hashing the representation of the provided `args` dict"""
    argbytes = bytes(repr(args), "utf-8")
    return hashlib.md5(argbytes).hexdigest()


class CommonColumns(BaseModel):  # type: ignore
    """Metadata attributes shared by all resources"""

    __abstract__ = True  # Indicate that this isn't a Table schema

    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now())
    _etag = Column(String(40))
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    def compute_etag(self) -> str:
        """Calculate the etag for this instance"""
        columns = self.__table__.columns.keys()
        etag_fields = [getattr(self, c) for c in columns if not c.startswith("_")]
        return make_etag(etag_fields)

    @with_default_session
    def insert(self, session: Session, commit: bool = True, compute_etag: bool = True):
        """Add the current instance to the session."""
        # Compute an _etag if none was provided
        self._etag = self._etag or self.compute_etag()

        session.add(self)
        if commit:
            session.commit()

    @with_default_session
    def update(self, session: Session, changes: dict = None, commit: bool = True):
        """
        Update the current instance if it exists in the session.
        `changes` should be a dictionary mapping column names to updated values.
        """
        # Ensure the record exists in the database
        if not self.find_by_id(self.id, session=session):
            raise NoResultFound()

        # Update this record's fields if changes were provided
        if changes:
            for column in self.__table__.columns.keys():
                if column in changes:
                    setattr(self, column, changes[column])

        # Set the _updated field to now
        self._updated = datetime.now()

        # Update the instance etag
        self._etag = self.compute_etag()

        session.merge(self)
        if commit:
            session.commit()

    @with_default_session
    def delete(self, session: Session, commit: bool = True):
        """Delete the current instance from the session."""
        session.delete(self)
        if commit:
            session.commit()

    @classmethod
    @with_default_session
    def list(cls, session: Session, **pagination_args):
        """List records in this table, with pagination support."""
        query = session.query(cls)
        query = cls._add_pagination_filters(query, **pagination_args)
        return query.all()

    @classmethod
    def _add_pagination_filters(
        cls,
        query: Query,
        page_num: int = 0,
        page_size: int = PAGINATION_PAGE_SIZE,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
        filter_: Callable[[Query], Query] = lambda q: q,
    ) -> Query:
        # Enforce positive page numbers
        page_num = 0 if page_num < 0 else page_num

        # Enforce maximum page size
        page_size = min(page_size, MAX_PAGINATION_PAGE_SIZE)

        # Handle sorting
        if sort_field:
            # Get the attribute from the class, in case this is a hybrid attribute
            sort_attribute = getattr(cls, sort_field)
            field_with_dir = (
                asc(sort_attribute) if sort_direction == "asc" else desc(sort_attribute)
            )
            query = query.order_by(field_with_dir)

        # Apply filter function
        query = filter_(query)

        # Handle pagination
        query = query.offset(page_num * page_size)
        query = query.limit(page_size)

        return query

    @classmethod
    @with_default_session
    def count(cls, session: Session, filter_: Callable[[Query], Query] = lambda q: q):
        """Return the total number of records in this table."""
        filtered_query = filter_(session.query(cls.id))
        return filtered_query.count()

    @classmethod
    @with_default_session
    def count_by(
        cls, expr, session: Session, filter_: Callable[[Query], Query] = lambda q: q
    ) -> Dict[str, int]:
        """
        Return a dictionary mapping results of `expr` to the number of times each result
        occurs in the table related to this model. E.g., for the `UploadJobs` model, 
        `UploadJobs.count_by_column(UploadJobs.upload_type)` would return a dictionary mapping
        upload types to the number of jobs for each type.
        """
        results = filter_(session.query(expr, func.count(cls.id)).group_by(expr)).all()
        return dict(results)

    @classmethod
    @with_default_session
    def find_by_id(cls, id: int, session: Session):
        """Find the record with this id"""
        return session.query(cls).get(id)

    @classmethod
    @with_default_session
    def get_distinct(
        cls,
        column_name: str,
        session: Session,
        filter_: Callable[[Query], Query] = lambda q: q,
    ):
        """Get a list of distinct values for the given column."""
        assert (
            column_name in cls.__table__.columns.keys()
        ), f"{cls.__tablename__} has no column {column_name}"

        base_query = session.query(getattr(cls, column_name))
        filtered_query = filter_(base_query)
        distinct_query = filtered_query.distinct()

        return list(v[0] for v in distinct_query)

    def validate(self):
        """Run custom validations on attributes set on this instance."""
        pass

    @classmethod
    def get_unique_columns(cls):
        """Get a list of all the unique columns in this table."""
        return [
            column for column in cls.__table__.c if column.unique or column.primary_key
        ]


class CIDCRole(EnumBaseClass):
    ADMIN = "cidc-admin"
    CIDC_BIOFX_USER = "cidc-biofx-user"
    CIMAC_BIOFX_USER = "cimac-biofx-user"
    CIMAC_USER = "cimac-user"
    DEVELOPER = "developer"
    DEVOPS = "devops"
    NCI_BIOBANK_USER = "nci-biobank-user"
    NETWORK_VIEWER = "network-viewer"


ROLES = [role.value for role in CIDCRole]
ORGS = ["CIDC", "DFCI", "ICAHN", "STANFORD", "ANDERSON"]


class Users(CommonColumns):
    __tablename__ = "users"

    _accessed = Column(DateTime, default=func.now(), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    contact_email = Column(String)
    first_n = Column(String)
    last_n = Column(String)
    organization = Column(Enum(*ORGS, name="orgs"))
    approval_date = Column(DateTime)
    role = Column(Enum(*ROLES, name="role"))
    disabled = Column(Boolean, default=False, server_default="false")

    @validates("approval_date")
    def send_approval_confirmation(self, key, new_approval_date):
        """Send this user an approval email if their account has just been approved"""
        if self.approval_date is None and new_approval_date is not None:
            emails.confirm_account_approval(self, send_email=True)

        return new_approval_date

    def is_admin(self) -> bool:
        """Returns true if this user is a CIDC admin."""
        return self.role == CIDCRole.ADMIN.value

    def is_nci_user(self) -> bool:
        """Returns true if this user is an NCI Biobank user."""
        return self.role == CIDCRole.NCI_BIOBANK_USER.value

    @with_default_session
    def update_accessed(self, session: Session, commit: bool = True):
        """Set this user's last system access to now."""
        today = datetime.now()
        if not self._accessed or (today - self._accessed).days > 1:
            self._accessed = today
            session.merge(self)
            if commit:
                session.commit()

    @staticmethod
    @with_default_session
    def find_by_email(email: str, session: Session) -> Optional["Users"]:
        """
        Search for a record in the Users table with the given email.
        If found, return the record. If not found, return None.
        """
        user = session.query(Users).filter_by(email=email).first()
        return user

    @staticmethod
    @with_default_session
    def create(profile: dict, session: Session):
        """
        Create a new record for a user if one doesn't exist
        for the given email. Return the user record associated
        with that email.
        """
        email = profile.get("email")
        first_n = profile.get("given_name")
        last_n = profile.get("family_name")

        user = Users.find_by_email(email)
        if not user:
            logger.info(f"Creating new user with email {email}")
            user = Users(
                email=email, contact_email=email, first_n=first_n, last_n=last_n
            )
            user.insert(session=session)
        return user

    @staticmethod
    @with_default_session
    def disable_inactive_users(session: Session, commit: bool = True) -> List[str]:
        """
        Disable any users who haven't accessed the API in more than `settings.INACTIVE_USER_DAYS`.
        Returns list of user emails that have been disabled.
        """
        user_inactivity_cutoff = datetime.today() - timedelta(days=INACTIVE_USER_DAYS)
        update_query = (
            update(Users)
            .where(Users._accessed < user_inactivity_cutoff)
            .values(disabled=True)
            .returning(Users.id)
        )
        disabled_user_ids: List[int] = [uid for uid in session.execute(update_query)]
        if commit:
            session.commit()

        disabled_users = [
            Users.find_by_id(uid, session=session) for uid in disabled_user_ids
        ]
        for u in disabled_users:
            Permissions.revoke_user_permissions(u, session=session)

        return [u.email for u in disabled_users]

    @staticmethod
    @with_default_session
    def get_data_access_report(io: BinaryIO, session: Session) -> pd.DataFrame:
        """
        Generate an XLSX containing an overview of trial/assay data access permissions
        for every active user in the database. The report will have a sheet per protocol
        identifier, with each sheet containing columns corresponding to a user's email,
        organization, role, and upload type access permissions.

        Save an excel file to the given file handler, and return the pandas dataframe
        used to generate that excel file.
        """
        user_columns = (Users.email, Users.organization, Users.role)

        query = (
            session.query(
                *user_columns,
                Permissions.trial_id,
                func.string_agg(Permissions.upload_type, ","),
            )
            .filter(
                Users.id == Permissions.granted_to_user,
                Users.disabled == False,
                Users.role != None,
                # Exclude admins, since perms in the Permissions table don't impact them.
                # Admin users are handled below.
                Users.role != CIDCRole.ADMIN.value,
            )
            .group_by(Users.id, Permissions.trial_id)
            .union_all(
                # Handle admins separately, since they can view all data for all
                # trials even if they have no permissions assigned to them.
                session.query(
                    *user_columns, TrialMetadata.trial_id, literal("*")
                ).filter(Users.role == CIDCRole.ADMIN.value)
            )
        )

        df = pd.DataFrame(
            query, columns=["email", "organization", "role", "trial_id", "permissions"]
        ).fillna("*")

        with pd.ExcelWriter(
            io
        ) as writer:  # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
            for trial_id in df["trial_id"].unique():
                if trial_id == "*":
                    continue

                trial_group = df[(df["trial_id"] == trial_id) | (df["trial_id"] == "*")]
                trial_group.to_excel(writer, sheet_name=trial_id, index=False)

        return df


class IAMException(Exception):
    pass


EXTRA_DATA_TYPES = ["participants info", "samples info"]
ALL_UPLOAD_TYPES = set(
    [
        *prism.SUPPORTED_MANIFESTS,
        *prism.SUPPORTED_ASSAYS,
        *prism.SUPPORTED_ANALYSES,
        *EXTRA_DATA_TYPES,
    ]
)

# see also: https://github.com/CIMAC-CIDC/cidc-cloud-functions/blob/2e27faca1062adf8143a7c33e0c382e833fd0726/functions/uploads.py#L173
# # there is a separate permissions system that applies the expiring IAM role
# # `CIDC_biofx` to the `cidc-dfci-biofx-[wes/rna]@ds` emails using a `trial/assay` prefix
# # while removing any existing perm for the same prefix
class Permissions(CommonColumns):
    __tablename__ = "permissions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["granted_by_user"],
            ["users.id"],
            name="ix_permissions_granted_by_user",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["granted_to_user"],
            ["users.id"],
            name="ix_permissions_granted_to_user",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["trial_id"],
            ["trial_metadata.trial_id"],
            name="ix_permissions_trial_id",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "granted_to_user", "trial_id", "upload_type", name="unique_perms"
        ),
        CheckConstraint("trial_id is not null or upload_type is not null"),
    )
    __mapper_args__ = {"confirm_deleted_rows": False}

    # If user who granted this permission is deleted, this permission will be deleted.
    # TODO: is this what we want?
    granted_by_user = Column(Integer)
    granted_to_user = Column(Integer, nullable=False, index=True)
    trial_id = Column(String, index=True)
    upload_type = Column(String)

    # Shorthand to make code related to trial- and upload-type-level permissions
    # easier to interpret.
    EVERY = None

    @validates("upload_type")
    def validate_upload_type(self, key, value: Any) -> Any:
        if value not in ALL_UPLOAD_TYPES and value != self.EVERY:
            raise ValueError(f"cannot grant permission on invalid upload type: {value}")
        return value

    @with_default_session
    def insert(
        self, session: Session, commit: bool = True, compute_etag: bool = True
    ) -> None:
        """
        Insert this permission record into the database and add a corresponding IAM policy binding
        on the GCS data bucket.

        If only a trial_id value is provided, then the permission denotes access to all upload_types
        for the given trial.

        If only an upload_type value is provided, then the permission denotes access to data of that
        upload_type for all trials.

        NOTE: values provided to the `commit` argument will be ignored. This method always commits.
        """
        if self.upload_type == self.EVERY and self.trial_id == self.EVERY:
            raise ValueError("A permission must have a trial id or upload type.")

        grantee = Users.find_by_id(self.granted_to_user, session=session)
        if grantee is None:
            raise IntegrityError(
                params=None,
                statement=None,
                orig=f"`granted_to_user` user must exist, but no user found with id {self.granted_to_user}",
            )

        grantor = None
        if self.granted_by_user is not None:
            grantor = Users.find_by_id(self.granted_by_user, session=session)
        else:
            raise IntegrityError(
                params=None,
                statement=None,
                orig=f"`granted_by_user` user must be given",
            )
        if grantor is None:
            raise IntegrityError(
                params=None,
                statement=None,
                orig=f"`granted_by_user` user must exist, but no user found with id {self.granted_by_user}",
            )

        is_network_viewer = grantee.role == CIDCRole.NETWORK_VIEWER.value

        # IAM on prod
        # A user can only have 20 granular permissions at a time, due to GCS constraints
        # (with the exception of Network Viewers, who can't download data from GCS and aren't
        # subject to this constraint.)
        if (
            ENV == "prod"
            and not is_network_viewer
            and (
                len(Permissions.find_for_user(self.granted_to_user, session=session))
                >= GOOGLE_MAX_DOWNLOAD_PERMISSIONS
            )
        ):
            raise IntegrityError(
                params=None,
                statement=None,
                orig=f"{grantee.email} has greater than or equal to the maximum number of allowed granular permissions ({GOOGLE_MAX_DOWNLOAD_PERMISSIONS}). Remove unused permissions to add others.",
            )

        logger.info(
            f"admin-action: {grantor.email} gave {grantee.email} the permission {self.upload_type or 'all assays'} on {self.trial_id or 'all trials'}"
        )

        # If this is a permission granting the user access to all trials for
        # a given upload type or all upload types for a given trial, delete
        # any related trial-upload type specific permissions to avoid
        # redundancy in the database and in conditional IAM bindings.
        perms_to_delete = (
            session.query(Permissions)
            .filter(
                Permissions.granted_to_user == self.granted_to_user,
                # If inserting a cross-trial perm, then select relevant
                # trial-specific perms for deletion.
                Permissions.trial_id != self.EVERY
                if self.trial_id == self.EVERY
                else Permissions.trial_id == self.trial_id,
                # If inserting a cross-upload type perm, then select relevant
                # upload type-specific perms for deletion.
                Permissions.upload_type != self.EVERY
                if self.upload_type == self.EVERY
                else Permissions.upload_type == self.upload_type,
            )
            .all()
        )

        # Add any related permission deletions to the insertion transaction.
        # If a delete operation fails, all other deletes and the insertion will
        # be rolled back.
        for perm in perms_to_delete:
            session.delete(perm)

        # Always commit, because we don't want to grant IAM download unless this insert succeeds.
        super().insert(session=session, commit=True, compute_etag=compute_etag)

        # Don't make any GCS changes if this user doesn't have download access
        if is_network_viewer:
            return

        try:
            # Grant ACL download permissions in GCS
            # if they have any download permissions, they need the CIDC Lister role
            grant_lister_access(grantee.email)
            grant_download_access(grantee.email, self.trial_id, self.upload_type)
            # Remove permissions staged for deletion, if any
            for perm in perms_to_delete:
                revoke_download_access(grantee.email, perm.trial_id, perm.upload_type)
        except Exception as e:
            # Add back deleted permissions, if any
            for perm in perms_to_delete:
                perm.insert(session=session)
            # Delete the just-created permissions record
            super().delete(session=session)

            logger.warning(str(e))
            raise IAMException("IAM grant failed.") from e

    @with_default_session
    def delete(
        self, deleted_by: Union[Users, int], session: Session, commit: bool = True
    ) -> None:
        """
        Delete this permission record from the database and revoke the corresponding IAM policy binding
        on the GCS data bucket.

        NOTE: values provided to the `commit` argument will be ignored. This method always commits.
        """
        grantee = Users.find_by_id(self.granted_to_user, session=session)
        if grantee is None:
            raise NoResultFound(f"no user with id {self.granted_to_user}")

        if not isinstance(deleted_by, Users):
            deleted_by_user = Users.find_by_id(deleted_by, session=session)
        else:
            deleted_by_user = deleted_by
        if deleted_by_user is None:
            raise NoResultFound(f"no user with id {deleted_by}")

        # Only make GCS ACL changes if this user has download access
        if grantee.role != CIDCRole.NETWORK_VIEWER.value:
            try:
                # Revoke ACL permission in GCS
                revoke_download_access(grantee.email, self.trial_id, self.upload_type)

                # If the permission to delete is the last one, also revoke Lister access
                filter_ = lambda q: q.filter(Permissions.granted_to_user == grantee.id)
                if Permissions.count(session=session, filter_=filter_) <= 1:
                    # this one hasn't been deleted yet, so 1 means this is the last one
                    revoke_lister_access(grantee.email)

            except Exception as e:
                raise IAMException(
                    "IAM revoke failed, and permission db record not removed."
                ) from e

        logger.info(
            f"admin-action: {deleted_by_user.email} removed from {grantee.email} the permission {self.upload_type or 'all assays'} on {self.trial_id or 'all trials'}"
        )
        super().delete(session=session, commit=True)

    @staticmethod
    @with_default_session
    def find_for_user(user_id: int, session: Session) -> List["Permissions"]:
        """Find all Permissions granted to the given user."""
        return session.query(Permissions).filter_by(granted_to_user=user_id).all()

    @staticmethod
    @with_default_session
    def get_for_trial_type(
        trial_id: str, upload_type: str, session: Session
    ) -> List["Permissions"]:
        """
        Check if a Permissions record exists for the given user, trial, and type.
        The result may be a trial- or assay-level permission that encompasses the 
        given trial id or upload type.
        """
        return (
            session.query(Permissions)
            .filter(
                (
                    (Permissions.trial_id == trial_id)
                    & (Permissions.upload_type == upload_type)
                )
                | (
                    (Permissions.trial_id == Permissions.EVERY)
                    & (Permissions.upload_type == upload_type)
                )
                | (
                    (Permissions.trial_id == trial_id)
                    & (Permissions.upload_type == Permissions.EVERY)
                ),
            )
            .all()
        )

    @staticmethod
    @with_default_session
    def find_for_user_trial_type(
        user_id: int, trial_id: str, upload_type: str, session: Session
    ) -> Optional["Permissions"]:
        """
        Check if a Permissions record exists for the given user, trial, and type.
        The result may be a trial- or assay-level permission that encompasses the 
        given trial id or upload type.
        """
        return (
            session.query(Permissions)
            .filter(
                Permissions.granted_to_user == user_id,
                (
                    (Permissions.trial_id == trial_id)
                    & (Permissions.upload_type == upload_type)
                )
                | (
                    (Permissions.trial_id == Permissions.EVERY)
                    & (Permissions.upload_type == upload_type)
                )
                | (
                    (Permissions.trial_id == trial_id)
                    & (Permissions.upload_type == Permissions.EVERY)
                ),
            )
            .first()
        )

    @staticmethod
    @with_default_session
    def grant_user_permissions(user: Users, session: Session) -> None:
        """
        Grant each of the given `user`'s permissions. Idempotent.
        """
        # Don't make any GCS changes if this user doesn't have download access
        if user.role == CIDCRole.NETWORK_VIEWER.value:
            return

        perms = Permissions.find_for_user(user.id)
        # if they have any download permissions, they need the CIDC Lister role
        if len(perms):
            grant_lister_access(user.email)
        for perm in perms:
            # Regrant each permission: idempotent.
            grant_download_access(user.email, perm.trial_id, perm.upload_type)

        # Regrant all of the user's intake bucket upload permissions, if they have any
        refresh_intake_access(user.email)

    @staticmethod
    @with_default_session
    def revoke_user_permissions(user: Users, session: Session) -> None:
        """
        Revoke each of the given `user`'s permissions. Idempotent.
        """
        # Don't make any GCS changes if this user doesn't have download access
        if user.role == CIDCRole.NETWORK_VIEWER.value:
            return

        perms = Permissions.find_for_user(user.id, session=session)
        # since we're revoking all, should revoke the CIDC Lister role too
        if len(perms):
            revoke_lister_access(user.email)
        for perm in perms:
            # Revoke each permission.
            revoke_download_access(user.email, perm.trial_id, perm.upload_type)

        # Revoke all of the user's intake bucket upload permissions, if they have any
        revoke_intake_access(user.email)

    @classmethod
    @with_default_session
    def grant_download_permissions_for_upload_job(
        cls, upload: "UploadJobs", session: Session
    ) -> None:
        perms = (
            session.query(cls)
            .filter_by(trial_id=upload.trial_id, upload_type=upload.upload_type)
            .all()
        )
        for perm in perms:
            user = Users.find_by_id(perm.granted_to_user, session=session)
            if user.is_admin() or user.is_nci_user() or user.disabled:
                continue

            grant_download_access(user.email, perm.trial_id, perm.upload_type)

    @staticmethod
    @with_default_session
    def grant_download_permissions(
        trial_id: str, upload_type: str, session: Session
    ) -> None:
        Permissions._change_download_permissions(
            trial_id=trial_id, upload_type=upload_type, grant=True, session=session
        )

    @staticmethod
    @with_default_session
    def revoke_download_permissions(
        trial_id: str, upload_type: str, session: Session
    ) -> None:
        Permissions._change_download_permissions(
            trial_id=trial_id, upload_type=upload_type, grant=False, session=session
        )

    @staticmethod
    @with_default_session
    def _change_download_permissions(
        trial_id: str, upload_type: str, grant: bool, session: Session
    ) -> None:
        """
        Allows for widespread granting/revoking of existing download permissions in GCS ACL
        Optionally filtered for specific trials and upload types
        If granting, also adds lister IAM permission for each user
        If revoking, DOES NOT remove lister IAM permission from any user

        Parameters
        ----------
        trial_id: str
            only affect permissions for this trial
            None for all trials
        upload_type: str
            only affect permissions for this upload type 
            None for all upload types
        grant: bool
            whether to grant or remove the (filtered) permissions
            if True, adds lister IAM permission
        session: Session
            filled by @with_default_session if not provided
        """
        filters = [
            # set the condition for the join
            Permissions.granted_to_user == Users.id,
            # admins have blanket access via IAM
            Users.role != CIDCRole.ADMIN.value,
        ]
        if grant:
            # NCI users and disable aren't granted download permissions
            # but we should be able to un-grant ie revoke them
            filters.extend(
                [
                    Users.role != CIDCRole.NCI_BIOBANK_USER.value,
                    Users.disabled == False,
                ]
            )
        if trial_id:
            filters.append(
                or_(
                    Permissions.trial_id == trial_id, Permissions.trial_id == None
                ),  # null for cross-trial
            )
        if upload_type:
            filters.append(
                or_(
                    Permissions.upload_type == upload_type,
                    Permissions.upload_type == None,
                ),  # null for cross-assay
            )

        # List[Tuple[Permissions, Users]]
        perms_and_users = session.query(Permissions, Users).filter(*filters).all()

        # group by trial and upload type
        # Dict[str, Dict[str, List[str]]] = {trial_id: {upload_type: [user_email, ...], ...}, ...}
        sorted_permissions = defaultdict(lambda: defaultdict(list))
        # also handle user lister IAM permission if granting
        already_listed: List[str] = []
        for perm, user in perms_and_users:
            # make sure we put it only for the desired scope
            sorted_permissions[trial_id if trial_id else perm.trial_id][
                upload_type if upload_type else perm.upload_type
            ].append(user.email)

            # if granting things, grant_lister_access on every user
            # idempotent, amounting to "add or refresh"
            if grant and user.email not in already_listed:
                grant_lister_access(user.email)
                already_listed.append(user.email)
            # if un-granting ie revoking things, don't call revoke_lister_access
            # with the filtering, we don't know if the users have any other
            # ACL permissions remaining that weren't affected here

        # now that we've filtered and separated, just do them all
        # new values will override passed args
        for trial_id, trial_perms in sorted_permissions.items():
            for upload_type, users in trial_perms.items():
                (grant_download_access if grant else revoke_download_access)(
                    users, trial_id, upload_type
                )


class ValidationMultiError(Exception):
    """Holds multiple jsonschema.ValidationErrors"""

    pass


trial_metadata_validator: json_validation._Validator = (
    json_validation.load_and_validate_schema(
        "clinical_trial.json", return_validator=True
    )
)

FileBundle = Dict[str, Dict[FilePurpose, List[int]]]


class TrialMetadata(CommonColumns):
    __tablename__ = "trial_metadata"
    # The CIMAC-determined trial id
    trial_id = Column(String, unique=True, nullable=False, index=True)
    metadata_json = Column(JSONB, nullable=False)

    # Create a GIN index on the metadata JSON blobs
    _metadata_idx = Index("metadata_idx", metadata_json, postgresql_using="gin")

    @staticmethod
    def validate_metadata_json(metadata_json: dict) -> dict:
        errs = trial_metadata_validator.iter_error_messages(metadata_json)
        messages = list(f"'metadata_json': {err}" for err in errs)
        if messages:
            raise ValidationMultiError(messages)
        return metadata_json

    def validate(self):
        """Run custom validations on attributes set on this instance."""
        if self.metadata_json is not None:
            self.validate_metadata_json(self.metadata_json)

    def safely_set_metadata_json(self, metadata_json: dict):
        """
        Validate `metadata_json` according to the trial metadata schema before setting
        the `TrialMetadata.metadata_json` attribute.
        """
        self.validate_metadata_json(metadata_json)
        self.metadata_json = metadata_json

    @staticmethod
    @with_default_session
    def find_by_trial_id(trial_id: str, session: Session):
        """
        Find a trial by its CIMAC id.
        """
        return session.query(TrialMetadata).filter_by(trial_id=trial_id).first()

    @staticmethod
    @with_default_session
    def select_for_update_by_trial_id(trial_id: str, session: Session):
        """
        Find a trial by its CIMAC id.
        """
        try:
            trial = (
                session.query(TrialMetadata)
                .filter_by(trial_id=trial_id)
                .with_for_update()
                .one()
            )
        except NoResultFound as e:
            raise NoResultFound(f"No trial found with id {trial_id}") from e
        return trial

    @staticmethod
    @with_default_session
    def patch_assays(
        trial_id: str, assay_patch: dict, session: Session, commit: bool = False
    ):
        """
        Applies assay updates to the metadata object from the trial with id `trial_id`.

        TODO: apply this update directly to the not-yet-existent TrialMetadata.manifest field
        """
        return TrialMetadata._patch_trial_metadata(
            trial_id, assay_patch, session=session, commit=commit
        )

    @staticmethod
    @with_default_session
    def patch_manifest(
        trial_id: str, manifest_patch: dict, session: Session, commit: bool = False
    ):
        """
        Applies manifest updates to the metadata object from the trial with id `trial_id`.

        TODO: apply this update directly to the not-yet-existent TrialMetadata.assays field
        """
        return TrialMetadata._patch_trial_metadata(
            trial_id, manifest_patch, session=session, commit=commit
        )

    @staticmethod
    @with_default_session
    def _patch_trial_metadata(
        trial_id: str, json_patch: dict, session: Session, commit: bool = False
    ):
        """
        Applies updates to the metadata object from the trial with id `trial_id`
        and commits current session.

        TODO: remove this function and dependency on it, in favor of separate assay
        and manifest patch strategies.
        """

        trial = TrialMetadata.select_for_update_by_trial_id(trial_id, session=session)

        # Merge assay metadata into the existing clinical trial metadata
        updated_metadata, errs = prism.merge_clinical_trial_metadata(
            json_patch, trial.metadata_json
        )
        if errs:
            raise ValidationMultiError(errs)
        # Save updates to trial record
        trial.safely_set_metadata_json(updated_metadata)
        trial._etag = make_etag([trial.trial_id, updated_metadata])

        session.add(trial)
        if commit:
            session.commit()

        return trial

    @staticmethod
    @with_default_session
    def create(
        trial_id: str, metadata_json: dict, session: Session, commit: bool = True
    ):
        """
        Create a new clinical trial metadata record.
        """

        logger.info(f"Creating new trial metadata with id {trial_id}")
        trial = TrialMetadata(trial_id=trial_id, metadata_json=metadata_json)
        trial.insert(session=session, commit=commit)

        return trial

    @staticmethod
    def merge_gcs_artifact(
        metadata: dict, upload_type: str, uuid: str, gcs_object: Blob
    ):
        return prism.merge_artifact(
            ct=metadata,
            assay_type=upload_type,  # assay_type is the old name for upload_type
            artifact_uuid=uuid,
            object_url=gcs_object.name,
            file_size_bytes=gcs_object.size,
            uploaded_timestamp=gcs_object.time_created.isoformat(),
            md5_hash=gcs_object.md5_hash,
            crc32c_hash=gcs_object.crc32c,
        )

    @staticmethod
    def merge_gcs_artifacts(
        metadata: dict, upload_type: str, uuids_and_gcs_objects: List[Tuple[str, Blob]]
    ):
        return prism.merge_artifacts(
            metadata,
            [
                prism.ArtifactInfo(
                    upload_type=upload_type,
                    artifact_uuid=uuid,
                    object_url=gcs_object.name,
                    file_size_bytes=gcs_object.size,
                    uploaded_timestamp=gcs_object.time_created.isoformat(),
                    md5_hash=gcs_object.md5_hash,
                    crc32c_hash=gcs_object.crc32c,
                )
                for uuid, gcs_object in uuids_and_gcs_objects
            ],
        )

    @classmethod
    @with_default_session
    def generate_patient_csv(cls, trial_id: str, session: Session) -> str:
        """Get the current patient CSV for this trial."""
        trial = cls.find_by_trial_id(trial_id, session=session)
        if not trial:
            raise NoResultFound(f"No trial found with id {trial_id}")
        return unprism.unprism_participants(trial.metadata_json)

    @classmethod
    @with_default_session
    def generate_sample_csv(cls, trial_id: str, session: Session) -> str:
        """Get the current sample CSV for this trial."""
        trial = cls.find_by_trial_id(trial_id, session=session)
        if not trial:
            raise NoResultFound(f"No trial found with id {trial_id}")
        return unprism.unprism_samples(trial.metadata_json)

    file_bundle: Optional[FileBundle]
    num_participants: Optional[int]
    num_samples: Optional[int]

    # List of metadata JSON fields that should not be sent to clients
    # in queries that list trial metadata, because they may contain a lot
    # of data.
    PRUNED_FIELDS = ["participants", "assays", "analysis", "shipments"]

    # List of metadata JSON fields that should only be settable via
    # manifest and metadata templates.
    PROTECTED_FIELDS = [*PRUNED_FIELDS, "protocol_identifier"]

    @classmethod
    def _pruned_metadata_json(cls):
        """
        Builds a modified metadata_json column selector with the "assays", "analysis",
        "shipments", and "participants" properties removed.
        """
        query = cls.metadata_json
        for field in cls.PRUNED_FIELDS:
            query = query.op("-")(field)

        return query.label("metadata_json")

    @classmethod
    @with_default_session
    def _num_participants_query(cls, session: Session):
        """
        Build a query that counts the number of participants in each trial
        """
        participant_counts = func.jsonb_array_length(
            cls.metadata_json.op("->")("participants")
        ).alias("np")
        return (
            session.query(
                cls.trial_id, func.sum(literal_column("np")).label("num_participants")
            )
            .select_from(cls, participant_counts)
            .group_by(cls.trial_id)
        )

    @classmethod
    @with_default_session
    def _num_samples_query(cls, session: Session):
        """
        Build a query that counts the number of samples in each trial
        """
        participants_array = func.jsonb_array_elements(
            cls.metadata_json.op("->")("participants")
        ).alias("ps")
        sample_counts = func.jsonb_array_length(
            literal_column("ps").op("->")("samples")
        ).alias("ns")
        return (
            session.query(
                cls.trial_id, func.sum(literal_column("ns")).label("num_samples")
            )
            .select_from(cls, participants_array, sample_counts)
            .group_by(cls.trial_id)
        )

    @classmethod
    @with_default_session
    def list(
        cls,
        session: Session,
        include_file_bundles: bool = False,
        include_counts: bool = False,
        **pagination_args,
    ):
        """
        List `TrialMetadata` records from the database with pruned metadata JSON blobs.
        If `file_bundle=True`, include the file bundle associated with each trial.
        If `include_counts=True`, include participant and sample counts for this trial.

        NOTE: use find_by_id or find_by_trial_id to get the full metadata JSON blob
        for a particular trial. We don't want lists of trials to include full metadata,
        because doing so can require loading lots of data at once.
        """
        # Instead of selecting the raw "metadata_json" for each trial,
        # select a pruned version with data-heavy attributes removed.]
        columns = [c for c in cls.__table__.c if c.name != "metadata_json"]
        columns.append(cls._pruned_metadata_json())

        # Add other subqueries/columns to include in the query
        subqueries = []
        if include_file_bundles:
            file_bundle_query = DownloadableFiles.build_file_bundle_query()
            columns.append(file_bundle_query.c.file_bundle)
            subqueries.append(file_bundle_query)
        if include_counts:
            participant_counts = cls._num_participants_query().subquery()
            sample_counts = cls._num_samples_query().subquery()
            columns.extend(
                [
                    participant_counts.c.num_participants,
                    case(
                        [(participant_counts.c.num_participants == 0, 0)],
                        else_=sample_counts.c.num_samples,
                    ).label("num_samples"),
                ]
            )
            subqueries.extend([participant_counts, sample_counts])

        # Combine all query components
        query = session.query(*columns)
        for subquery in subqueries:
            # Each subquery will have a trial_id column and one record per trial id
            query = query.outerjoin(subquery, cls.trial_id == subquery.c.trial_id)
        query = cls._add_pagination_filters(query, **pagination_args)

        trials = []
        for result in query:
            # result._asdict gives us a dictionary mapping column names
            # to values for this result
            result_dict = result._asdict()

            # Create a TrialMetadata model instance from the result
            trial = cls()
            for column, value in result_dict.items():
                if value is not None:
                    setattr(trial, column, value)

            trials.append(trial)

        return trials

    @with_default_session
    def insert(
        self,
        session: Session,
        commit: bool = True,
        compute_etag: bool = True,
        validate_metadata: bool = True,
    ):
        """Add the current instance to the session. Skip JSON metadata validation validate_metadata=False."""
        if self.metadata_json is not None and validate_metadata:
            self.validate_metadata_json(self.metadata_json)

        return super().insert(session=session, commit=commit, compute_etag=compute_etag)

    @with_default_session
    def update(
        self,
        session: Session,
        changes: dict = None,
        commit: bool = True,
        validate_metadata: bool = True,
    ):
        """
        Update the current TrialMetadata instance if it exists. `changes` should be
        a dictionary mapping column names to updated values. Skip JSON metadata validation 
        if validate_metadata=False.
        """
        # Since commit=False, this will only apply changes to the in-memory
        # TrialMetadata instance, not the corresponding db record
        super().update(session=session, changes=changes, commit=False)

        # metadata_json was possibly updated in above method call,
        # so check that it's still valid if validate_metadata=True
        if validate_metadata:
            self.validate_metadata_json(self.metadata_json)

        if commit:
            session.commit()

    @classmethod
    def build_trial_filter(cls, user: Users, trial_ids: List[str] = []):
        filters = []
        if trial_ids:
            filters.append(cls.trial_id.in_(trial_ids))
        if not user.is_admin() and not user.is_nci_user():
            has_cross_trial_perms = False
            granular_trial_perms = []
            for perm in Permissions.find_for_user(user.id):
                # If perm.trial_id is None, then the user has a cross-trial permission
                if perm.trial_id is None:
                    has_cross_trial_perms = True
                else:
                    granular_trial_perms.append(perm.trial_id)
            # If the user has a cross-trial permission, then they should be able
            # to list all trials, so don't include granular permission filters
            # in that case.
            if not has_cross_trial_perms:
                filters.append(cls.trial_id.in_(granular_trial_perms))

        # possible TODO: filter by assays in a trial
        return lambda q: q.filter(*filters)

    @classmethod
    @with_default_session
    def get_metadata_counts(cls, session: Session) -> dict:
        """
        Return a dictionary with the following structure:
        ```
            {
                "num_trials": <count of all trials>,
                "num_participants": <count of all participants across all trials>,
                "num_samples": <count of all samples across all participants across all trials>
            }
        ```
        """
        # Count all trials, participants, and samples in the database
        [(num_trials, num_participants, num_samples)] = session.execute(
            """
            SELECT
                COUNT(DISTINCT trial_id),
                COUNT(participants),
                SUM(jsonb_array_length(participants->'samples'))
            FROM
                trial_metadata,
                LATERAL jsonb_array_elements(metadata_json->'participants') participants;
            """
        )

        return {
            "num_trials": num_trials,
            "num_participants": num_participants,
            "num_samples": num_samples,
        }

    @staticmethod
    @with_default_session
    def get_summaries(session: Session) -> List[dict]:
        """
        Return a list of trial summaries, where each summary has structure like:
        ```python
            {
                "trial_id": ...,
                "expected_assays": ..., # list of assays the trial should have data for
                "file_size_bytes": ..., # total file size for the trial
                "clinical_participants": ..., # number of participants with clinical data
                "wes": ..., # wes sample count
                "cytof": ..., # cytof sample count
                ... # other assays
            }
        ```
        NOTE: if the metadata model for any existing assays substantially changes,
        or if new assays are introduced that don't follow the typical structure 
        (batches containing sample-level records), then this method will need to
        be updated to accommodate those changes.
        """
        # Compute the total count of participants for each trial
        participants_subquery = """
            select
                trial_id,
                'total_participants' as key,
                jsonb_array_length(metadata_json->'participants') as value
            from
                trial_metadata
        """

        # Compute the total  count of samples for each trial
        samples_subquery = """
            select
                trial_id,
                'total_samples' as key,
                sum(num_samples) as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json->'participants') participants,
                jsonb_array_length(participants->'samples') num_samples
            group by trial_id
        """

        # Compute the total amount of data in bytes stored for each trial
        files_subquery = """
            select
                trial_id,
                'file_size_bytes' as key,
                file_size_bytes as value
            from
                downloadable_files
        """

        # Count how many participants have associated clinical data. The same
        # participant may appear in multiple clinical data files, so deduplicate
        # participants before counting them.
        clinical_subquery = """
            select
                trial_id,
                'clinical_participants' as key,
                count(distinct participants) as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{clinical_data,records}') as records,
                jsonb_array_elements(records#>'{clinical_file,participants}') as participants
            group by
                trial_id
        """

        # Compute the number of samples associated with each assay type for
        # assays whose metadata follows the typical structure: an array of batches,
        # with each batch containing an array of records, where each record
        # corresponds to a unique sample.
        generic_assay_subquery = """
            select
                trial_id,
                case
                    when key = 'hande' then 'h&e'
                    else key
                end as key,
                jsonb_array_length(batches->'records') as value
            from
                trial_metadata,
                jsonb_each(metadata_json->'assays') assays,
                jsonb_array_elements(value) batches
            where key not in ('olink', 'nanostring', 'elisa', 'wes', 'misc_data')
        """

        # Compute the number of samples associated with nanostring uploads.
        # Nanostring metadata has a slightly different structure than typical
        # assays, where each batch has an array of runs, and each run has
        # an array of sample-level entries.
        nanostring_subquery = """
            select
                trial_id,
                'nanostring' as key,
                jsonb_array_length(runs->'samples') as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{assays,nanostring}') batches,
                jsonb_array_elements(batches->'runs') runs
        """

        # Compute the number of samples associated with olink uploads.
        # Unlike other assays, olink metadata is an object at the top level
        # rather than an array of batches. This object has a "batches"
        # property that points to an array of batches, and each batch contains
        # an array of records. These records are *not* sample-level; rather,
        # the number of samples corresponding to a given record is stored
        # like: record["files"]["assay_npx"]["number_of_samples"].
        olink_subquery = """
            select
                trial_id,
                'olink' as key,
                (records#>'{files,assay_npx,number_of_samples}')::text::integer as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{assays,olink,batches}') batches,
                jsonb_array_elements(batches->'records') records
        """

        # Compute the number of samples associated with elisa uploads.
        # Unlike other assays, elisa metadata is an array of entries, each containing a single data file.
        # The number of samples corresponding to a given entry is stored like:
        # entry["assay_xlsx"]["number_of_samples"].
        elisa_subquery = """
            select
                trial_id,
                'elisa' as key,
                (entry#>'{assay_xlsx,number_of_samples}')::text::integer as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{assays,elisa}') entry
        """

        # Count the distinct tumor and normal samples that have associated analysis data.
        # Multiple normal samples might be paired with the same tumor sample, so we need
        # to de-duplicate them before counting.
        wes_analysis_subquery = """
            select
                trial_id,
                'wes_analysis' as key,
                count(distinct pair#>'{tumor,cimac_id}') + count(distinct pair#>'{normal,cimac_id}') as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{analysis,wes_analysis,pair_runs}') pair
            where
                pair#>'{report,report}' is not null
            group by trial_id, key
        """

        wes_tumor_only_analysis_subquery = """
            select
                trial_id,
                'wes_tumor_only_analysis' as key,
                jsonb_array_length(metadata_json#>'{analysis,wes_tumor_only_analysis,runs}') as value
            from
                trial_metadata
        """

        wes_assay_subquery = """
            select
                trial_id,
                'wes' as key,
                count(distinct pair#>'{tumor,cimac_id}') + count(distinct pair#>'{normal,cimac_id}') as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{analysis,wes_analysis,pair_runs}') pair
            group by trial_id
        """

        ## Calculate # of WES TO assay samples as (all - # paired WES samples)
        # As jsonb_array_length is called for each entry in /assays/wes : array,
        # it returns several rows which if `join`ed against wes_assay_subquery
        # duplicates the value to be subtracted so `sum` doesn't work.
        # Instead, `union` these two queries (`all` because repeated values)
        # with opposing signs to subtract via `sum`
        # Since # paired WES samples = `wes_assay_subquery` is a positive number,
        # subtract total number of samples from it and negate

        ## Eg
        # /assays/wes : [{records: 3}, {records: 3}]
        # wes_assay_subquery: 4
        # so want 3+3 - 4 = 2

        ## With double negative
        # key           value
        # --------------------
        # wes             4
        # wes_tumor_only -3
        # wes_tumor_only -3
        # --------------------
        # -sum            2
        wes_tumor_only_assay_subquery = f"""
            select
                trial_id,
                'wes_tumor_only' as key,
                -sum(value)
            from (
                select
                    trial_id,
                    key,
                    - jsonb_array_length(batches->'records') as value
                from
                    trial_metadata,
                    jsonb_each(metadata_json->'assays') assays,
                    jsonb_array_elements(value) batches
                where key = 'wes'
            union all 
                {wes_assay_subquery}
            ) tbl
            group by trial_id, key
        """

        rna_level1_analysis_subquery = """
            select
                trial_id,
                'rna_level1_analysis' as key,
                jsonb_array_length(metadata_json#>'{analysis,rna_analysis,level_1}') as value
            from
                trial_metadata
        """

        tcr_analysis_subquery = """
            select
                trial_id,
                'tcr_analysis' as key,
                jsonb_array_length(batches->'records') as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{analysis,tcr_analysis,batches}') batches
        """

        cytof_analysis_subquery = """
            select
                trial_id,
                'cytof_analysis' as key,
                case
                    when record->'output_files' is not null then 1 else 0
                end as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{assays,cytof}') batch,
                jsonb_array_elements(batch->'records') record
        """

        atacseq_analysis_subquery = """
            select
                trial_id,
                'atacseq_analysis' as key,
                jsonb_array_length(batch->'records') as value
            from
                trial_metadata,
                jsonb_array_elements(metadata_json#>'{analysis,atacseq_analysis}') batch
        """

        # Build up a JSON object mapping analysis types to arrays of excluded samples.
        # The resulting object will have structure like:
        # {
        #   "cytof_analysis": [missing samples],
        #   "wes_analysis": [missing samples],
        #   ...
        # }
        excluded_samples_subquery = """
            select
                trial_id,
                jsonb_object_agg(key, value) as value
            from (
                select 
                    trial_id,
                    key,
                    jsonb_agg(sample) as value
                from (
                    select
                        trial_id,
                        'cytof_analysis' as key,
                        jsonb_array_elements(batch->'excluded_samples') as sample
                    from
                        trial_metadata,
                        jsonb_array_elements(metadata_json#>'{assays,cytof}') batch
                    union all
                    select
                        trial_id,
                        'wes_analysis' as key,
                        jsonb_array_elements(metadata_json#>'{analysis,wes_analysis,excluded_samples}') as sample
                    from
                        trial_metadata
                    union all
                    select
                        trial_id,
                        'wes_tumor_only_analysis' as key,
                        jsonb_array_elements(metadata_json#>'{analysis,wes_tumor_only_analysis,excluded_samples}') as sample
                    from
                        trial_metadata
                    union all
                    select
                        trial_id,
                        'rna_level1_analysis' as key,
                        jsonb_array_elements(metadata_json#>'{analysis,rna_analysis,excluded_samples}') as sample
                    from
                        trial_metadata
                    union all
                    select
                        trial_id,
                        'tcr_analysis' as key,
                        jsonb_array_elements(batches->'excluded_samples') as sample
                    from
                        trial_metadata,
                        jsonb_array_elements(metadata_json#>'{analysis,tcr_analysis,batches}') batches
                ) excluded_q1
                group by trial_id, key
            ) excluded_q2
            group by trial_id
        """

        # Extract an array of expected assays or an empty array if expected assays is null.
        expected_assays_subquery = """
            select
                trial_id,
                coalesce(metadata_json->'expected_assays', '[]'::jsonb) as expected_assays
            from
                trial_metadata
        """

        # All the subqueries produce the same set of columns, so UNION ALL
        # them together into a single query, aggregating results into
        # trial-level JSON dictionaries with the shape described in the docstring.
        # NOTE: we use UNION ALL instead of just UNION to prevent unwanted
        # de-duplication within subquery results.
        combined_query = f"""
            select
                jsonb_object_agg(sample_summaries.key, sample_summaries.value)
                || jsonb_object_agg('excluded_samples', excluded_sample_lists.value)
                || jsonb_object_agg('trial_id', sample_summaries.trial_id)
                || jsonb_object_agg('expected_assays', expected_assays)
            from (
                select
                    trial_id,
                    key,
                    sum(value) as value
                from (
                    {participants_subquery}
                    union all
                    {samples_subquery}
                    union all
                    {files_subquery}
                    union all
                    {clinical_subquery}
                    union all
                    {generic_assay_subquery}
                    union all
                    {nanostring_subquery}
                    union all
                    {olink_subquery}
                    union all
                    {elisa_subquery}
                    union all
                    {wes_analysis_subquery}
                    union all
                    {wes_tumor_only_analysis_subquery}
                    union all
                    {wes_assay_subquery}
                    union all
                    {wes_tumor_only_assay_subquery}
                    union all
                    {rna_level1_analysis_subquery}
                    union all
                    {tcr_analysis_subquery}
                    union all
                    {cytof_analysis_subquery}
                    union all
                    {atacseq_analysis_subquery}
                ) q
                group by trial_id, key
            ) sample_summaries
            join ({expected_assays_subquery}) expected_assays
            on sample_summaries.trial_id = expected_assays.trial_id
            full join ({excluded_samples_subquery}) excluded_sample_lists
            on sample_summaries.trial_id = excluded_sample_lists.trial_id
            group by sample_summaries.trial_id;
        """

        # Run the query and extract the trial-level summary dictionaries
        summaries = [summary for (summary,) in session.execute(combined_query)]

        # Shortcut to impute 0 values for assays where trials don't yet have data
        summaries = pd.DataFrame(summaries).fillna(0).to_dict("records")

        return summaries


class UploadJobStatus(EnumBaseClass):
    STARTED = "started"
    # Set by CLI based on GCS upload results
    UPLOAD_COMPLETED = "upload-completed"
    UPLOAD_FAILED = "upload-failed"
    # Set by ingest_UploadJobs cloud function based on merge / transfer results
    MERGE_COMPLETED = "merge-completed"
    MERGE_FAILED = "merge-failed"

    @classmethod
    def is_valid_transition(
        cls, current: str, target: str, is_manifest: bool = False
    ) -> bool:
        """
        Enforce logic about which state transitions are valid. E.g.,
        an upload whose status is "merge-completed" should never be updated
        to "started".
        """
        c = cls(current)
        t = cls(target)
        upload_statuses = [cls.UPLOAD_COMPLETED, cls.UPLOAD_FAILED]
        merge_statuses = [cls.MERGE_COMPLETED, cls.MERGE_FAILED]
        if c != t:
            if t == cls.STARTED:
                return False
            if c in upload_statuses:
                if t not in merge_statuses:
                    return False
            if c in merge_statuses:
                return False
            if c == cls.STARTED and t in merge_statuses and not is_manifest:
                return False
        return True


UPLOAD_STATUSES = [s.value for s in UploadJobStatus]


class UploadJobs(CommonColumns):
    __tablename__ = "upload_jobs"
    # An upload job must contain a gcs_file_map is it isn't a manifest upload
    __table_args__ = (
        CheckConstraint(f"multifile = true OR gcs_file_map != null"),
        ForeignKeyConstraint(
            ["uploader_email"],
            ["users.email"],
            name="upload_jobs_uploader_email_fkey",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["trial_id"],
            ["trial_metadata.trial_id"],
            name="assay_uploads_trial_id_fkey",
        ),
    )

    # The current status of the upload job
    _status = Column(
        "status", Enum(*UPLOAD_STATUSES, name="upload_job_status"), nullable=False
    )
    # A long, random identifier for this upload job
    token = Column(UUID, server_default=text("gen_random_uuid()"), nullable=False)
    # Text containing feedback on why the upload status is what it is
    status_details = Column(String, nullable=True)
    # Whether the upload contains multiple files
    multifile = Column(Boolean, nullable=False)
    # For multifile UploadJobs, object names for the files to be uploaded mapped to upload_placeholder uuids.
    # For single file UploadJobs, this field is null.
    gcs_file_map = Column(JSONB, nullable=True)
    # track the GCS URI of the .xlsx file used for this upload
    gcs_xlsx_uri = Column(String, nullable=True)
    # The parsed JSON metadata blob associated with this upload
    metadata_patch = Column(JSONB, nullable=False)
    # The type of upload (pbmc, wes, olink, wes_analysis, ...)
    upload_type = Column(String, nullable=False)
    # Link to the user who created this upload.
    uploader_email = Column(String, nullable=False)
    # The trial that this is an upload for.
    trial_id = Column(String, nullable=False, index=True)

    # Create a GIN index on the GCS object names
    _gcs_objects_idx = Index(
        "upload_jobs_gcs_gcs_file_map_idx", gcs_file_map, postgresql_using="gin"
    )

    @hybrid_property
    def status(self):
        return self._status

    @status.setter
    def status(self, status: str):
        """Set the status if given value is valid."""
        # If old status isn't set on this instance, then this instance hasn't
        # yet been saved to the db, so default to the old status to STARTED.
        old_status = self.status or UploadJobStatus.STARTED.value
        is_manifest = self.upload_type in prism.SUPPORTED_MANIFESTS
        if not UploadJobStatus.is_valid_transition(old_status, status, is_manifest):
            raise ValueError(
                f"Upload job with status {self.status} can't transition to status {status}"
            )
        self._status = status

    def _set_status_no_validation(self, status: str):
        """Set the status without performing validations."""
        assert TESTING, "status_no_validation should only be used in tests"
        self._status = status

    def alert_upload_success(self, trial: TrialMetadata):
        """Send an email notification that an upload has succeeded."""
        # Send admin notification email
        emails.new_upload_alert(self, trial.metadata_json, send_email=True)

    def upload_uris_with_data_uris_with_uuids(self):
        for upload_uri, uuid in (self.gcs_file_map or {}).items():
            # URIs in the upload bucket have a structure like (see ingestion.upload_assay)
            # [trial id]/{prismify_generated_path}/[timestamp].
            # We strip off the /[timestamp] suffix from the upload url,
            # since we don't care when this was uploaded.
            target_url = "/".join(upload_uri.split("/")[:-1])

            yield upload_uri, target_url, uuid

    @staticmethod
    @with_default_session
    def create(
        upload_type: str,
        uploader_email: str,
        gcs_file_map: dict,
        metadata: dict,
        gcs_xlsx_uri: str,
        session: Session,
        commit: bool = True,
        send_email: bool = False,
        status: UploadJobStatus = UploadJobStatus.STARTED.value,
    ):
        """Create a new upload job for the given trial metadata patch."""
        assert prism.PROTOCOL_ID_FIELD_NAME in metadata, "metadata must have a trial ID"

        is_manifest_upload = upload_type in prism.SUPPORTED_MANIFESTS
        assert (
            gcs_file_map is not None or is_manifest_upload
        ), "assay/analysis uploads must have a gcs_file_map"

        trial_id = metadata[prism.PROTOCOL_ID_FIELD_NAME]

        job = UploadJobs(
            multifile=is_manifest_upload,
            trial_id=trial_id,
            upload_type=upload_type,
            gcs_file_map=gcs_file_map,
            metadata_patch=metadata,
            uploader_email=uploader_email,
            gcs_xlsx_uri=gcs_xlsx_uri,
            status=status,
        )
        job.insert(session=session, commit=commit)

        if send_email:
            trial = TrialMetadata.find_by_trial_id(trial_id)
            job.alert_upload_success(trial)

        return job

    @staticmethod
    @with_default_session
    def merge_extra_metadata(job_id: int, files: dict, session: Session):
        """
        Args:
            job_id: the ID of the UploadJob to merge
            files: mapping from uuid of the artifact-to-update to metadata file-to-update-from
            session: the current session; uses default if not passed
        Returns:
            None
        Raises:
            ValueError
                if `job_id` doesn't exist or is already merged
                from prism.merge_artifact_extra_metadata
        """

        job = UploadJobs.find_by_id(job_id, session=session)

        if job is None or job.status == UploadJobStatus.MERGE_COMPLETED:
            raise ValueError(f"Upload job {job_id} doesn't exist or is already merged")

        logger.info(f"About to merge extra md to {job.id}/{job.status}")

        for uuid, file in files.items():
            logger.info(f"About to parse/merge extra md on {uuid}")
            (
                job.metadata_patch,
                updated_artifact,
                _,
            ) = prism.merge_artifact_extra_metadata(
                job.metadata_patch, uuid, job.upload_type, file
            )
            logger.info(f"Updated md for {uuid}: {updated_artifact.keys()}")

        # A workaround fix for JSON field modifications not being tracked
        # by SQLalchemy for some reason. Using MutableDict.as_mutable(JSON)
        # in the model doesn't seem to help.
        flag_modified(job, "metadata_patch")

        logger.info(f"Updated {job.id}/{job.status} patch: {job.metadata_patch}")
        session.commit()

    @classmethod
    @with_default_session
    def find_by_id_and_email(cls, id, email, session):
        upload = super().find_by_id(id, session=session)
        if upload and upload.uploader_email != email:
            return None
        return upload

    @with_default_session
    def ingestion_success(
        self, trial, session: Session, commit: bool = False, send_email: bool = False
    ):
        """Set own status to reflect successful merge and trigger email notifying CIDC admins."""
        # Do status update if the transition is valid
        if not UploadJobStatus.is_valid_transition(
            self.status, UploadJobStatus.MERGE_COMPLETED.value
        ):
            raise Exception(
                f"Cannot declare ingestion success given current status: {self.status}"
            )
        self.status = UploadJobStatus.MERGE_COMPLETED.value

        if commit:
            session.commit()

        if send_email:
            self.alert_upload_success(trial)


class DownloadableFiles(CommonColumns):
    """
    Store required fields from:
    https://github.com/CIMAC-CIDC/cidc-schemas/blob/master/cidc_schemas/schemas/artifacts/artifact_core.json
    """

    __tablename__ = "downloadable_files"
    __table_args__ = (
        ForeignKeyConstraint(
            ["trial_id"],
            ["trial_metadata.trial_id"],
            name="downloadable_files_trial_id_fkey",
        ),
    )

    file_size_bytes = Column(BigInteger, nullable=False)
    uploaded_timestamp = Column(DateTime, nullable=False)
    facet_group = Column(String, nullable=False)
    # NOTE: this column actually has type CITEXT.
    additional_metadata = Column(JSONB, nullable=False)
    # TODO rename upload_type, because we store manifests in there too.
    # NOTE: this column actually has type CITEXT.
    upload_type = Column(String, nullable=False)
    md5_hash = Column(String, nullable=True)
    crc32c_hash = Column(String, nullable=True)
    trial_id = Column(String, nullable=False)
    object_url = Column(String, nullable=False, index=True, unique=True)
    visible = Column(Boolean, default=True)

    # Would a bioinformatician likely use this file in an analysis?
    analysis_friendly = Column(Boolean, default=False)

    # Visualization data columns (should always be nullable)
    clustergrammer = Column(JSONB, nullable=True)
    ihc_combined_plot = Column(JSONB, nullable=True)

    # This fields are optional and should eventually be removed:
    # - object_url should be used instead of file_name
    # - some combo of object_url/data_category/upload_type should be
    #   used instead of data_format.
    # The columns are left as optional for short term backwards compatibility.
    file_name = Column(String, nullable=True)
    data_format = Column(String, nullable=True)

    FILE_EXT_REGEX = r"\.([^./]*(\.gz)?)$"

    @hybrid_property
    def file_ext(self):
        match = re.search(self.FILE_EXT_REGEX, self.object_url)
        return match.group(1) if match else None

    @file_ext.expression
    def file_ext(cls):
        return func.substring(cls.object_url, cls.FILE_EXT_REGEX)

    @hybrid_property
    def data_category(self):
        return facet_groups_to_categories.get(self.facet_group)

    @data_category.expression
    def data_category(cls):
        return DATA_CATEGORY_CASE_CLAUSE

    @hybrid_property
    def data_category_prefix(self):
        """
        The overarching data category for a file. E.g., files with `upload_type` of
        "cytof"` and `"cytof_analyis"` should both have a `data_category_prefix` of `"CyTOF"`.
        """
        if self.data_category is None:
            return None
        return self.data_category.split(FACET_NAME_DELIM, 1)[0]

    @data_category_prefix.expression
    def data_category_prefix(cls):
        return func.split_part(DATA_CATEGORY_CASE_CLAUSE, FACET_NAME_DELIM, 1)

    @hybrid_property
    def file_purpose(self):
        return details_dict.get(self.facet_group).file_purpose

    @file_purpose.expression
    def file_purpose(cls):
        return FILE_PURPOSE_CASE_CLAUSE

    @property
    def short_description(self):
        return details_dict.get(self.facet_group).short_description

    @property
    def long_description(self):
        return details_dict.get(self.facet_group).long_description

    @property
    def cimac_id(self):
        """
        Extract the `cimac_id` associated with this file, if any, by searching the file's 
        additional metadata for a field with a key like `<some>.<path>.cimac_id`.

        NOTE: this is not a sqlalchemy hybrid_property, and it can't be used directly in queries.
        """
        for key, value in self.additional_metadata.items():
            if key.endswith("cimac_id"):
                return value
        return None

    @validates("additional_metadata")
    def check_additional_metadata_default(self, key, value):
        return {} if value in ["null", None, {}] else value

    @with_default_session
    def get_related_files(self, session: Session) -> list:
        """
        Return a list of file records related to this file. We could define "related"
        in any number of ways, but currently, a related file:
            * is sample-specific, and relates to the same sample as this file if this file 
              has an associated `cimac_id`.
            * isn't sample-specific, and relates to the same `data_category_prefix`.
        """
        # If this file has an associated sample, get other files associated with that sample.
        # Otherwise, get other non-sample-specific files for this trial and data category.
        if self.cimac_id is not None:
            query = text(
                "SELECT DISTINCT downloadable_files.* "
                "FROM downloadable_files, LATERAL jsonb_each_text(additional_metadata) addm_kv "
                "WHERE addm_kv.value LIKE :cimac_id AND trial_id = :trial_id AND id != :id"
            )
            params = {
                "cimac_id": f"%{self.cimac_id}",
                "trial_id": self.trial_id,
                "id": self.id,
            }
            related_files = result_proxy_to_models(
                session.execute(query, params), DownloadableFiles
            )
        else:
            not_sample_specific = not_(
                literal_column("additional_metadata::text").like('%.cimac_id":%')
            )
            related_files = (
                session.query(DownloadableFiles)
                .filter(
                    DownloadableFiles.trial_id == self.trial_id,
                    DownloadableFiles.data_category_prefix == self.data_category_prefix,
                    DownloadableFiles.id != self.id,
                    not_sample_specific,
                )
                .all()
            )

        return related_files

    @staticmethod
    def build_file_filter(
        trial_ids: List[str] = [], facets: List[List[str]] = [], user: Users = None
    ) -> Callable[[Query], Query]:
        """
        Build a file filter function based on the provided parameters. The resultant
        filter can then be passed as the `filter_` argument of `DownloadableFiles.list`
        or `DownloadableFiles.count`.

        Args:
            trial_ids: if provided, the filter will include only files with these trial IDs.
            upload_types: if provided, the filter will include only files with these upload types.
            analysis_friendly: if True, the filter will include only files that are "analysis-friendly".
            non_admin_user_id: if provided, the filter will include only files that satisfy
                this user's data access permissions.
        Returns:
            A function that adds filters to a query against the DownloadableFiles table.
        """
        file_filters = []
        if trial_ids:
            file_filters.append(DownloadableFiles.trial_id.in_(trial_ids))
        if facets:
            facet_groups = get_facet_groups_for_paths(facets)
            file_filters.append(DownloadableFiles.facet_group.in_(facet_groups))
        # Admins and NCI biobank users can view all files
        if user and not user.is_admin() and not user.is_nci_user():
            permissions = Permissions.find_for_user(user.id)
            full_trial_perms, full_type_perms, trial_type_perms = [], [], []
            for perm in permissions:
                if perm.upload_type is None:
                    full_trial_perms.append(perm.trial_id)
                elif perm.trial_id is None:
                    full_type_perms.append(perm.upload_type)
                else:
                    trial_type_perms.append((perm.trial_id, perm.upload_type))
            df_tuples = tuple_(
                DownloadableFiles.trial_id, DownloadableFiles.upload_type
            )
            file_filters.append(
                or_(
                    DownloadableFiles.trial_id.in_(full_trial_perms),
                    DownloadableFiles.upload_type.in_(full_type_perms),
                    df_tuples.in_(trial_type_perms),
                )
            )

        def filter_files(query: Query) -> Query:
            return query.filter(*file_filters)

        return filter_files

    @staticmethod
    @with_default_session
    def create_from_metadata(
        trial_id: str,
        upload_type: str,
        file_metadata: dict,
        session: Session,
        additional_metadata: Optional[dict] = None,
        commit: bool = True,
        alert_artifact_upload: bool = False,
    ):
        """
        Create a new DownloadableFiles record from artifact metadata.
        """

        # Filter out keys that aren't columns
        supported_columns = DownloadableFiles.__table__.columns.keys()
        filtered_metadata = {
            "trial_id": trial_id,
            "upload_type": upload_type,
            "additional_metadata": additional_metadata,
        }

        for key, value in file_metadata.items():
            if key in supported_columns:
                filtered_metadata[key] = value
        # TODO maybe put non supported stuff from file_metadata to some misc jsonb column?

        etag = make_etag(filtered_metadata.values())

        object_url = filtered_metadata["object_url"]
        df = (
            session.query(DownloadableFiles)
            .filter_by(object_url=object_url)
            .with_for_update()
            .first()
        )
        if df:
            df = session.merge(
                DownloadableFiles(id=df.id, _etag=etag, **filtered_metadata)
            )
        else:
            df = DownloadableFiles(_etag=etag, **filtered_metadata)

        df.insert(session=session, commit=commit)

        if alert_artifact_upload:
            publish_artifact_upload(object_url)

        return df

    @staticmethod
    @with_default_session
    def create_from_blob(
        trial_id: str,
        upload_type: str,
        data_format: str,
        facet_group: str,
        blob: Blob,
        session: Session,
        commit: bool = True,
        alert_artifact_upload: bool = False,
    ):
        """
        Create a new DownloadableFiles record from from a GCS blob,
        or update an existing one, with the same object_url.
        """

        # trying to find existing one
        df = (
            session.query(DownloadableFiles)
            .filter_by(object_url=blob.name)
            .with_for_update()
            .first()
        )
        if not df:
            df = DownloadableFiles()

        df.trial_id = trial_id
        df.upload_type = upload_type
        df.data_format = data_format
        df.facet_group = facet_group
        df.object_url = blob.name
        df.file_name = blob.name
        df.file_size_bytes = blob.size
        df.md5_hash = blob.md5_hash
        df.crc32c_hash = blob.crc32c
        df.uploaded_timestamp = blob.time_created

        df.insert(session=session, commit=commit)

        if alert_artifact_upload:
            publish_artifact_upload(blob.name)

        return df

    @staticmethod
    @with_default_session
    def get_by_object_url(object_url: str, session: Session):
        """
        Look up the downloadable file record associated with
        the given GCS object url.
        """
        return session.query(DownloadableFiles).filter_by(object_url=object_url).one()

    @classmethod
    @with_default_session
    def list_object_urls(
        cls, ids: List[int], session: Session, filter_: Callable[[Query], Query]
    ) -> List[str]:
        """Get all object_urls for a batch of downloadable file record IDs"""
        query = session.query(cls.object_url).filter(cls.id.in_(ids))
        query = filter_(query)
        return [r[0] for r in query.all()]

    @classmethod
    def build_file_bundle_query(cls) -> Query:
        """
        Build a query that selects nested file bundles from the downloadable files table.
        The `file_bundles` query below should produce one bundle per unique `trial_id` that
        appears in the downloadable files table. Each bundle will have shape like:
        ```
          {
              <type 1>: {
                <purpose 1>: [<file id 1>, <file id 2>, ...],
                <purpose 2>: [...]
              },
              <type 2>: {...}
          }
        ```
        where "type" is something like `"Olink"` or `"Participants Info"` and "purpose" is a `FilePurpose` string.
        """
        tid_col, type_col, purp_col, ids_col, purps_col = (
            literal_column("trial_id"),
            literal_column("type"),
            literal_column("purpose"),
            literal_column("ids"),
            literal_column("purposes"),
        )

        id_bundles = (
            select(
                [
                    cls.trial_id,
                    cls.data_category_prefix.label(type_col.key),
                    cls.file_purpose.label(purp_col.key),
                    func.json_agg(cls.id).label(ids_col.key),
                ]
            )
            .group_by(cls.trial_id, cls.data_category_prefix, cls.file_purpose)
            .alias("id_bundles")
        )
        purpose_bundles = (
            select(
                [
                    tid_col,
                    type_col,
                    func.json_object_agg(
                        func.coalesce(purp_col, "miscellaneous"), ids_col
                    ).label(purps_col.key),
                ]
            )
            .select_from(id_bundles)
            .group_by(tid_col, type_col)
            .alias("purpose_bundles")
        )
        file_bundles = (
            select(
                [
                    tid_col.label(tid_col.key),
                    func.json_object_agg(
                        func.coalesce(type_col, "other"), purps_col
                    ).label("file_bundle"),
                ]
            )
            .select_from(purpose_bundles)
            .group_by(tid_col)
            .alias("file_bundles")
        )
        return file_bundles

    @classmethod
    @with_default_session
    def get_total_bytes(
        cls, session: Session, filter_: Callable[[Query], Query] = lambda q: q
    ) -> int:
        """Get the total number of bytes of data stored across all files."""
        filtered_query = filter_(session.query(func.sum(cls.file_size_bytes)))
        total_bytes = filtered_query.one()[0]
        return int(total_bytes)

    @classmethod
    @with_default_session
    def get_trial_facets(
        cls, session: Session, filter_: Callable[[Query], Query] = lambda q: q
    ):
        trial_file_counts = cls.count_by(
            cls.trial_id,
            session=session,
            # Apply the provided filter, and also exclude files with null `data_category`s
            filter_=lambda q: filter_(q).filter(cls.data_category != None),
        )
        trial_facets = build_trial_facets(trial_file_counts)
        return trial_facets

    @classmethod
    @with_default_session
    def get_data_category_facets(
        cls, session: Session, filter_: Callable[[Query], Query] = lambda q: q
    ):
        facet_group_file_counts = cls.count_by(
            cls.facet_group, session=session, filter_=filter_
        )
        data_category_facets = build_data_category_facets(facet_group_file_counts)
        return data_category_facets


# Query clause for computing a downloadable file's data category.
# Used above in the DownloadableFiles.data_category computed property.
DATA_CATEGORY_CASE_CLAUSE = case(
    [
        (DownloadableFiles.facet_group == k, v)
        for k, v in facet_groups_to_categories.items()
    ]
)

# Query clause for computing a downloadable file's file purpose.
# Used above in the DownloadableFiles.file_purpose computed property.
FILE_PURPOSE_CASE_CLAUSE = case(
    [
        (DownloadableFiles.facet_group == facet_group, file_details.file_purpose)
        for facet_group, file_details in details_dict.items()
    ]
)


def result_proxy_to_models(
    result_proxy: ResultProxy, model: BaseModel
) -> List[BaseModel]:
    """Materialize a sqlalchemy `result_proxy` iterable as a list of `model` instances"""
    return [model(**dict(row_proxy.items())) for row_proxy in result_proxy]
