from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ...database import db_session
from ...resources.ProceedingStage.models import ProceedingStageModel
from .schemas import (
    ProceedingStageResourceSchema,
)


schema_resource = ProceedingStageResourceSchema()


class ProceedingStage(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: Dict (ProceedingStageResourceSchema)

        Returns:
            ProceedingStageResourceSchema

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
        proceeding_stage_query = db_session.query(
            ProceedingStageModel).filter_by(id=id).one()
        try:
            db_session.delete(proceeding_stage_query)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise

    @staticmethod
    def bulk_delete(ptab2_proceeding_id):
        try:
            db_session.query(
                ProceedingStageModel).filter(
                ProceedingStageModel.ptab2_proceeding_id == ptab2_proceeding_id
            ).delete(synchronize_session=False)
            db_session.commit()
            db_session.close()
            return 'Successfully deleted'
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_proceeding_stage = ProceedingStageModel(**data)
    try:
        db_session.add(new_proceeding_stage)
        db_session.commit()
        proceeding_stage_query = db_session.query(
            ProceedingStageModel).get(new_proceeding_stage.id)
        response = schema_resource.dump(proceeding_stage_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise
