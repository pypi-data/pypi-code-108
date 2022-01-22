from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.Subsidiary.models import (
    SubsidiaryModel,
)
from .schemas import (
    SubsidiaryResourceSchema,
    SubsidiaryQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = SubsidiaryResourceSchema()
schema_params = SubsidiaryQueryParamsSchema()


class Subsidiary(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(SubsidiaryResourceSchema)

        Returns: SubsidiaryResourceSchema

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
            params: dict(SubsidiaryQueryParamsSchema)

        Returns: List<SubsidiaryResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        subsidiary_query = _build_query(params=data)
        response = schema_resource.dump(
            subsidiary_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(SubsidiaryQueryParamsSchema)

        Returns: SubsidiaryResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        subsidiary_query = _build_query(params=data).one()
        response = schema_resource.dump(subsidiary_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: SubsidiaryResourceSchema

        Returns:
            SubsidiaryResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'name': params['name'],
            }
            subsidiary_query = _build_query(query_params).one()
            response = _helper_update(data, subsidiary_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_subsidiary = SubsidiaryModel(**data)
    try:
        db_session.add(new_subsidiary)
        db_session.commit()
        subsidiary_query = db_session.query(SubsidiaryModel).get(
            new_subsidiary.id
        )
        response = schema_resource.dump(subsidiary_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _helper_update(data, subsidiary_query):
    data['id'] = subsidiary_query.id
    data['name'] = subsidiary_query.name
    try:
        update_model(data, subsidiary_query)
        db_session.commit()
        response = schema_resource.dump(subsidiary_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        SubsidiaryModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('name'):
        q = q.filter_by(
            name=params.get('name'))
    return q
