from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from cs_models.utils.utils import update_model
from ...database import db_session
from ...resources.Newswire.models import (
    NewswireModel,
)
from .schemas import (
    NewswireResourceSchema,
    NewswireQueryParamsSchema,
    NewswirePatchSchema,
)


schema_resource = NewswireResourceSchema()
schema_params = NewswireQueryParamsSchema()
schema_patch = NewswirePatchSchema()


class Newswire(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(NewswireResourceSchema)

        Returns: NewswireResourceSchema

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
            params: dict(NewswireQueryParamsSchema)

        Returns: List<NewswireResourceSchema>

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
            params: dict(NewswireQueryParamsSchema)

        Returns: NewswireResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        newswire_query = _build_query(params=data).one()
        response = schema_resource.dump(newswire_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: NewswirePatchSchema

        Returns:
            NewswireResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        newswire_query = db_session.query(
            NewswireModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, newswire_query)
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: NewswireResourceSchema

        Returns:
            NewswireResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'headline': params['headline'],
                'subsidiary_id': params['subsidiary_id'],
            }
            newswire_query = _build_query(query_params).one()
            response = _helper_update(data, newswire_query)
        except NoResultFound:
            response = _helper_create(data)
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
        newswire_query = db_session.query(
            NewswireModel).filter_by(id=id).one()
        try:
            db_session.delete(newswire_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_newswire = NewswireModel(**data)
    try:
        db_session.add(new_newswire)
        db_session.commit()
        newswire_query = db_session.query(
            NewswireModel).get(
            new_newswire.id)
        response = schema_resource.dump(newswire_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, newswire_query):
    data['id'] = newswire_query.id
    try:
        update_model(data, newswire_query)
        db_session.commit()
        response = schema_resource.dump(newswire_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        NewswireModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('date'):
        q = q.filter_by(date=params.get('date'))
    if params.get('headline'):
        q = q.filter_by(headline=params.get('headline'))
    if params.get('source'):
        q = q.filter_by(source=params.get('source'))
    if params.get('subsidiary_id'):
        q = q.filter_by(subsidiary_id=params.get('subsidiary_id'))
    return q
