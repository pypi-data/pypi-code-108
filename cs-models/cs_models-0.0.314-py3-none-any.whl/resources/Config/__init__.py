from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from cs_models.utils.utils import update_model
from ...database import db_session
from ...resources.Config.models import (
    ConfigModel,
)
from .schemas import (
    ConfigResourceSchema,
    ConfigQueryParamsSchema,
    ConfigPatchSchema,
)


schema_resource = ConfigResourceSchema()
schema_params = ConfigQueryParamsSchema()
schema_patch = ConfigPatchSchema()


class Config(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(ConfigResourceSchema)

        Returns: ConfigResourceSchema

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
            params: dict(ConfigQueryParamsSchema)

        Returns: List<ConfigResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        config_query = _build_query(params=data)
        response = schema_resource.dump(
            config_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(ConfigQueryParamsSchema)

        Returns: ConfigResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        config_query = _build_query(params=data).one()
        response = schema_resource.dump(config_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: ConfigPatchSchema

        Returns:
            ConfigResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        config_query = db_session.query(
            ConfigModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, config_query)
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: ConfigResourceSchema

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
                'table_name': params['table_name'],
                'field_name': params['field_name'],
            }
            config_query = _build_query(query_params).one()
            response = _helper_update(data, config_query)
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
        config_query = db_session.query(
            ConfigModel).filter_by(id=id).one()
        try:
            db_session.delete(config_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_config = ConfigModel(**data)
    try:
        db_session.add(new_config)
        db_session.commit()
        config_query = db_session.query(
            ConfigModel).get(
            new_config.id)
        response = schema_resource.dump(config_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, config_query):
    data['id'] = config_query.id
    try:
        update_model(data, config_query)
        db_session.commit()
        response = schema_resource.dump(config_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        ConfigModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('table_name'):
        q = q.filter_by(table_name=params.get('table_name'))
    if params.get('field_name'):
        q = q.filter_by(field_name=params.get('field_name'))
    return q
