from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError
from ...database import db_session
from ...resources.CompanySEC.models import CompanySECModel
from .schemas import (
    CompanySECResourceSchema,
)
from ...utils.utils import update_model


schema_resource = CompanySECResourceSchema()


class CompanySEC(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (CompanySECResourceSchema)
        Returns:
            CompanySECResourceSchema
        Raises:
            ValidationError
            DBException
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)
        response = _helper_create(data)
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: Dict (CompanySECResourceSchema)
        Returns:
            CompanySECResourceSchema
        Raises:
            ValidationError
            DBException
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)
        response = _helper_upsert(data)
        return response

    @staticmethod
    def delete(id):
        """
        :param
            id
        :return:
            delete message
        :exception:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            SQLAlchemyError
        """
        company_sec_query = db_session.query(
            CompanySECModel).filter_by(id=id).one()
        try:
            db_session.delete(company_sec_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_company_sec = CompanySECModel(**data)
    try:
        db_session.add(new_company_sec)
        db_session.commit()
        company_sec_query = db_session.query(
            CompanySECModel).get(new_company_sec.id)
        response = schema_resource.dump(company_sec_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_upsert(data):
    try:
        q = db_session.query(CompanySECModel).filter(
            CompanySECModel.cik_str == data['cik_str'],
            CompanySECModel.ticker == data['ticker'],
        )
        company_sec = q.one()
        # update
        update_model(data, company_sec)
        db_session.commit()
        response = schema_resource.dump(company_sec).data
        return response
    except NoResultFound:
        # create
        response = _helper_create(data)
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise
