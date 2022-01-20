from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
# TODO : Base files should not rely on DRF. Add this to the base library.
from rest_framework import status


class DjangoBaseException(Exception):
    """
    Generic exception that handles a status code, default detail and slug.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('A server error occurred.')
    default_error_slug = 'internal_error'

    def __init__(self, detail=None, error_slug=None):
        if detail is not None:
            self.detail = force_str(detail)
            self.error_slug = force_str(error_slug)
        else:
            self.detail = force_str(self.default_detail)
            self.error_slug = force_str(self.default_error_slug)

    def __str__(self):
        return self.detail


class CannotModifyObjectWithArchivedParentError(DjangoBaseException):
    """
    Error for when modifications are disallowed on objects with archived
    parents.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cannot modify an object that has an archived parent.')
    default_error_slug = 'cannot_unarchive_object_with_archived_parent'


class CannotModifyArchivedObjectError(DjangoBaseException):
    """
    Error for when modifications are disallowed on archived objects.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cannot modify an archived object.')
    default_error_slug = 'cannot_modify_archived_object'


class CannotDeleteUnarchivedObjectError(DjangoBaseException):
    """
    Error for when deletes are disallowed on unarchived objects.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cannot delete an unarchived object.')
    default_error_slug = 'cannot_delete_unarchived_object'


class CannotArchiveObjectError(DjangoBaseException):
    """
    Error for when deletes are disallowed on objects.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cannot archive this object.')
    default_error_slug = 'cannot_archive_object'


class CannotDeleteObjectError(DjangoBaseException):
    """
    Error for when deletes are disallowed on objects.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Cannot delete this object.')
    default_error_slug = 'cannot_delete_object'