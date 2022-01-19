from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from cs_models.utils.utils import update_model
from ...database import db_session
from ...resources.NDC.models import NDCModel
from .schemas import (
    NDCPatchSchema,
    NDCQueryParamsSchema,
    NDCResourceSchema,
)


schema_resource = NDCResourceSchema()
schema_params = NDCQueryParamsSchema()
schema_patch = NDCPatchSchema()


class NDC(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(NDCResourceSchema)

        Returns: NDCResourceSchema

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
            params: dict(NDCQueryParamsSchema)

        Returns: List<NDCResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ndc_query = _build_query(params=data)
        response = schema_resource.dump(ndc_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(NDCQueryParamsSchema)

        Returns: NDCResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ndc_query = _build_query(params=data).one()
        response = schema_resource.dump(ndc_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: NDCPatchSchema

        Returns:
            NDCResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        ndc_query = db_session.query(NDCModel).filter_by(id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, ndc_query)
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: NDCResourceSchema

        Returns:
            NDCResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                "spl_id": params["spl_id"],
                "product_ndc": params["product_ndc"],
            }
            ndc_query = _build_query(query_params).one()
            response = _helper_update(data, ndc_query)
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
        ndc_query = db_session.query(NDCModel).filter_by(id=id).one()
        try:
            db_session.delete(ndc_query)
            db_session.commit()
            db_session.close()
            return "Successfully deleted"
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_ndc = NDCModel(**data)
    try:
        db_session.add(new_ndc)
        db_session.commit()
        druglabel_query = db_session.query(NDCModel).get(new_ndc.id)
        response = schema_resource.dump(druglabel_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, ndc_query):
    data["id"] = ndc_query.id
    try:
        update_model(data, ndc_query)
        db_session.commit()
        response = schema_resource.dump(ndc_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(NDCModel)
    if params.get("id"):
        q = q.filter_by(id=params.get("id"))
    if params.get("spl_id"):
        q = q.filter_by(spl_id=params.get("spl_id"))
    if params.get("product_ndc"):
        q = q.filter_by(product_ndc=params.get("product_ndc"))
    return q
