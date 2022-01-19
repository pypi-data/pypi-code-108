from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError
from ...database import db_session
from ...resources.FederalCaseRef.models import FederalCaseRefModel
from .schemas import (
    FederalCaseRefResourceSchema,
)
from ...utils.utils import update_model


schema_resource = FederalCaseRefResourceSchema()


class FederalCaseRef(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (FederalCaseRefResourceSchema)
        Returns:
            FederalCaseRefResourceSchema
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
            params: Dict (FederalCaseRefResourceSchema)
        Returns:
            FederalCaseRefResourceSchema
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
        federal_case_ref_query = db_session.query(
            FederalCaseRefModel).filter_by(id=id).one()
        try:
            db_session.delete(federal_case_ref_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_federal_case_ref = FederalCaseRefModel(**data)
    try:
        db_session.add(new_federal_case_ref)
        db_session.commit()
        federal_case_ref_query = db_session.query(
            FederalCaseRefModel).get(new_federal_case_ref.id)
        response = schema_resource.dump(federal_case_ref_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_upsert(data):
    try:
        q = db_session.query(FederalCaseRefModel).filter(
            FederalCaseRefModel.volume == data['volume'],
            FederalCaseRefModel.reporter_type == data['reporter_type'],
            FederalCaseRefModel.page == data['page'],
            FederalCaseRefModel.title == data['title']
        )
        federal_case_ref = q.one()
        # update
        update_model(data, federal_case_ref)
        db_session.commit()
        response = schema_resource.dump(federal_case_ref).data
        return response
    except NoResultFound:
        # create
        response = _helper_create(data)
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise
