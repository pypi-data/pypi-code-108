from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from cs_models.utils.utils import update_model
from ...database import db_session
from ...resources.DocumentReference.models import (
    DocumentReferenceModel,
)
from .schemas import (
    DocumentReferenceResourceSchema,
    DocumentReferenceQueryParamsSchema,
    DocumentReferencePatchSchema,
)


schema_resource = DocumentReferenceResourceSchema()
schema_params = DocumentReferenceQueryParamsSchema()
schema_patch = DocumentReferencePatchSchema()


class DocumentReference(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(DocumentReferenceResourceSchema)

        Returns: DocumentReferenceResourceSchema

        Raises:
            ValidationError
            SQLAlchemyError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)
        response = _helper_create(data)
        return response

    @staticmethod
    def read(params):
        """
        Args:
            params: dict(DocumentReferenceQueryParamsSchema)

        Returns: List<DocumentReferenceResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        document_ref_query = _build_query(params=data)
        response = schema_resource.dump(
            document_ref_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(DocumentReferenceQueryParamsSchema)

        Returns: DocumentReferenceResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        document_ref_query = _build_query(params=data).one()
        response = schema_resource.dump(document_ref_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: DocumentReferencePatchSchema

        Returns:
            DocumentReferenceResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        document_reference_query = db_session.query(
            DocumentReferenceModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, document_reference_query)
        return response

    @staticmethod
    def delete(id):
        """
        Args:
            id: int

        Returns: string

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            SQLAlchemyError
        """
        document_ref_query = db_session.query(
            DocumentReferenceModel).filter_by(id=id).one()
        try:
            db_session.delete(document_ref_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    @staticmethod
    def bulk_delete(ptab2_document_id):
        try:
            db_session.query(
                DocumentReferenceModel).filter(
                DocumentReferenceModel.ptab2_document_id == ptab2_document_id
            ).delete(synchronize_session=False)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_document_reference = DocumentReferenceModel(**data)
    try:
        db_session.add(new_document_reference)
        db_session.commit()
        document_ref_query = db_session.query(
            DocumentReferenceModel).get(
            new_document_reference.id)
        response = schema_resource.dump(document_ref_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, document_reference_query):
    data['id'] = document_reference_query.id
    try:
        update_model(data, document_reference_query)
        db_session.commit()
        response = schema_resource.dump(document_reference_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        DocumentReferenceModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('ptab2_document_id'):
        q = q.filter_by(ptab2_document_id=params.get('ptab2_document_id'))
    if params.get('type'):
        q = q.filter_by(type=params.get('type'))
    if params.get('value'):
        q = q.filter_by(value=params.get('value'))
    if params.get('federal_case_number'):
        q = q.filter_by(federal_case_number=params.get('federal_case_number'))
    if params.get('link'):
        q = q.filter_by(link=params.get('link'))

    return q
