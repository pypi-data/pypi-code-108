from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from cs_models.utils.utils import update_model
from ...database import db_session
from ...resources.DrugIndication.models import (
    DrugIndicationModel,
)
from .schemas import (
    DrugIndicationPatchSchema,
    DrugIndicationQueryParamsSchema,
    DrugIndicationResourceSchema,
)


schema_resource = DrugIndicationResourceSchema()
schema_params = DrugIndicationQueryParamsSchema()
schema_patch = DrugIndicationPatchSchema()


class DrugIndication(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(IndicationResourceSchema)

        Returns: IndicationResourceSchema

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
            params: dict(IndicationQueryParamsSchema)

        Returns: List<IndicationResourceSchema>

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
            params: dict(IndicationQueryParamsSchema)

        Returns: IndicationResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        indication_query = _build_query(params=data).one()
        response = schema_resource.dump(indication_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: IndicationPatchSchema

        Returns:
            IndicationResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        indication_query = db_session.query(
            DrugIndicationModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, indication_query)
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: IndicationResourceSchema

        Returns:
            IndicationResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'set_id': params['set_id'],
                'indication': params['indication'],
                'lowercase_indication': params['lowercase_indication'],
            }
            indication_query = _build_query(query_params).one()
            response = _helper_update(data, indication_query)
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
        indication_query = db_session.query(
            DrugIndicationModel).filter_by(id=id).one()
        try:
            db_session.delete(indication_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_indication = DrugIndicationModel(**data)
    try:
        db_session.add(new_indication)
        db_session.commit()
        indication_query = db_session.query(
            DrugIndicationModel).get(
            new_indication.id)
        response = schema_resource.dump(indication_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, indication_query):
    data['id'] = indication_query.id
    try:
        update_model(data, indication_query)
        db_session.commit()
        response = schema_resource.dump(indication_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        DrugIndicationModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('set_id'):
        q = q.filter_by(set_id=params.get('set_id'))
    if params.get('lowercase_indication'):
        q = q.filter_by(lowercase_indication=params.get(
            'lowercase_indication'))
    return q
