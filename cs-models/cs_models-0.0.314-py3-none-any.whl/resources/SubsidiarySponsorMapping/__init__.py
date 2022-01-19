from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.SubsidiarySponsorMapping.models import (
    SubsidiarySponsorMappingModel,
)
from .schemas import (
    SubsidiarySponsorMappingResourceSchema,
    SubsidiarySponsorMappingQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = SubsidiarySponsorMappingResourceSchema()
schema_params = SubsidiarySponsorMappingQueryParamsSchema()


class SubsidiarySponsorMapping(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(SubsidiarySponsorMappingResourceSchema)

        Returns: SubsidiarySponsorMappingResourceSchema

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
            params: dict(SubsidiarySponsorMappingQueryParamsSchema)

        Returns: List<SubsidiarySponsorMappingResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        subsidiary_sponsor_mapping_query = _build_query(params=data)
        response = schema_resource.dump(
            subsidiary_sponsor_mapping_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(SubsidiarySponsorMappingQueryParamsSchema)

        Returns: SubsidiarySponsorMappingResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        subsidiary_sponsor_mapping_query = _build_query(params=data).one()
        response = schema_resource.dump(subsidiary_sponsor_mapping_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: SubsidiarySponsorMappingResourceSchema

        Returns:
            SubsidiarySponsorMappingResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'sponsor_id': params['sponsor_id'],
                'sponsor_name': params['sponsor_name'],
                'subsidiary_id': params['subsidiary_id'],
            }
            subsidiary_sponsor_mapping_query = _build_query(query_params).one()
            response = _helper_update(data, subsidiary_sponsor_mapping_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_subsidiary_sponsor_map = SubsidiarySponsorMappingModel(**data)
    try:
        db_session.add(new_subsidiary_sponsor_map)
        db_session.commit()
        subsidiary_sponsor_map_query = db_session.query(
            SubsidiarySponsorMappingModel
        ).get(
            new_subsidiary_sponsor_map.id
        )
        response = schema_resource.dump(
            subsidiary_sponsor_map_query
        ).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _helper_update(data, subsidiary_sponsor_map_query):
    data['id'] = subsidiary_sponsor_map_query.id
    try:
        update_model(data, subsidiary_sponsor_map_query)
        db_session.commit()
        response = schema_resource.dump(subsidiary_sponsor_map_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        SubsidiarySponsorMappingModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('sponsor_id'):
        q = q.filter_by(
            sponsor_id=params.get('sponsor_id'))
    if params.get('subsidiary_id'):
        q = q.filter_by(
            subsidiary_id=params.get('subsidiary_id'))
    return q
