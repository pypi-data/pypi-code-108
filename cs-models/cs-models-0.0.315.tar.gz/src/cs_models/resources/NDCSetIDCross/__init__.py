from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ...database import db_session
from ...resources.NDCSetIDCross.models import NDCSetIDCrossModel
from .schemas import (
    NDCSetIDCrossPatchSchema,
    NDCSetIDCrossQueryParamsSchema,
    NDCSetIDCrossResourceSchema,
)


schema_resource = NDCSetIDCrossResourceSchema()
schema_params = NDCSetIDCrossQueryParamsSchema()
schema_patch = NDCSetIDCrossPatchSchema()


class NDCSetIDCross(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(NDCSetIDCrossResourceSchema)

        Returns: NDCSetIDCrossResourceSchema

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
            params: dict(NDCSetIDCrossQueryParamsSchema)

        Returns: List<NDCSetIDCrossResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ndc_setid_cross_query = _build_query(params=data)
        response = schema_resource.dump(ndc_setid_cross_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(NDCSetIDCrossQueryParamsSchema)

        Returns: NDCSetIDCrossResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ndc_setid_cross_query = _build_query(params=data).one()
        response = schema_resource.dump(ndc_setid_cross_query).data
        return response


def _helper_create(data):
    new_ndc_setid_cross = NDCSetIDCrossModel(**data)
    try:
        db_session.add(new_ndc_setid_cross)
        db_session.commit()
        druglabel_query = db_session.query(NDCSetIDCrossModel).get(
            new_ndc_setid_cross.product_ndc)
        response = schema_resource.dump(druglabel_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(NDCSetIDCrossModel)
    if params.get("product_ndc"):
        q = q.filter_by(product_ndc=params.get("product_ndc"))
    if params.get("spl_set_id"):
        q = q.filter_by(spl_set_id=params.get("spl_set_id"))
    if params.get("package_ndc"):
        q = q.filter_by(package_ndc=params.get("package_ndc"))
    return q
