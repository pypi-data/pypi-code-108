from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.CompanyOUS.models import (
    CompanyOUSModel,
)
from .schemas import (
    CompanyOUSResourceSchema,
    CompanyOUSQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = CompanyOUSResourceSchema()
schema_params = CompanyOUSQueryParamsSchema()


class CompanyOUS(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(CompanyOUSResourceSchema)

        Returns: CompanyOUSResourceSchema

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
            params: dict(CompanyOUSQueryParamsSchema)

        Returns: List<CompanyOUSResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        company_ous_query = _build_query(params=data)
        response = schema_resource.dump(
            company_ous_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(CompanyOUSQueryParamsSchema)

        Returns: CompanyOUSResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        company_ous_query = _build_query(params=data).one()
        response = schema_resource.dump(company_ous_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: CompanyOUSResourceSchema

        Returns:
            CompanyOUSResourceSchema

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
            company_ous_query = _build_query(query_params).one()
            response = _helper_update(data, company_ous_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_company_ous = CompanyOUSModel(**data)
    try:
        db_session.add(new_company_ous)
        db_session.commit()
        company_ous_query = db_session.query(CompanyOUSModel).get(
            new_company_ous.id
        )
        response = schema_resource.dump(company_ous_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, company_ous_query):
    data['id'] = company_ous_query.id
    data['name'] = company_ous_query.name
    try:
        update_model(data, company_ous_query)
        db_session.commit()
        response = schema_resource.dump(company_ous_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        CompanyOUSModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('name'):
        q = q.filter_by(
            name=params.get('name'))
    if params.get('ticker'):
        q = q.filter_by(ticker=params.get('ticker'))
    return q
