from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from ...database import db_session
from ...resources.OrangeBookExclusivity.models import (
    OrangeBookExclusivityModel,
)
from .schemas import (
    OrangeBookExclusivityResourceSchema,
    OrangeBookExclusivityQueryParamsSchema,
)
from ...utils.utils import update_model


schema_resource = OrangeBookExclusivityResourceSchema()
schema_params = OrangeBookExclusivityQueryParamsSchema()


class OrangeBookExclusivity(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(OrangeBookExclusivityResourceSchema)

        Returns: OrangeBookExclusivityResourceSchema

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
            params: dict(OrangeBookExclusivityQueryParamsSchema)

        Returns: List<OrangeBookExclusivityResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ob_exclusivity_query = _build_query(params=data)
        response = schema_resource.dump(
            ob_exclusivity_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(OrangeBookExclusivityQueryParamsSchema)

        Returns: OrangeBookExclusivityResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        ob_exclusivity_query = _build_query(params=data).one()
        response = schema_resource.dump(ob_exclusivity_query).data
        return response

    @staticmethod
    def upsert(params):
        """
        Args:
            params: OrangeBookExclusivityResourceSchema

        Returns:
            OrangeBookExclusivityResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)

        try:
            query_params = {
                'appl_type': params['appl_type'],
                'appl_no': params['appl_no'],
                'product_no': params['product_no'],
                'exclusivity_code': params['exclusivity_code'],
            }
            ob_exclusivity_query = _build_query(query_params).one()
            response = _helper_update(data, ob_exclusivity_query)
        except NoResultFound:
            response = _helper_create(data)
        return response


def _helper_create(data):
    new_ob_exclusivity = OrangeBookExclusivityModel(**data)
    try:
        db_session.add(new_ob_exclusivity)
        db_session.commit()
        ob_exclusivity_query = db_session.query(
            OrangeBookExclusivityModel).get(new_ob_exclusivity.id)
        response = schema_resource.dump(ob_exclusivity_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, ob_exclusivity_query):
    data['id'] = ob_exclusivity_query.id
    data['appl_no'] = ob_exclusivity_query.appl_no
    data['product_no'] = ob_exclusivity_query.product_no
    data['exclusivity_code'] = ob_exclusivity_query.exclusivity_code

    data['exclusivity_date'] = (
        data['exclusivity_date']
        if data['exclusivity_date'] > ob_exclusivity_query.exclusivity_date
        else ob_exclusivity_query.exclusivity_date
    )

    try:
        update_model(data, ob_exclusivity_query)
        db_session.commit()
        response = schema_resource.dump(ob_exclusivity_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(
        OrangeBookExclusivityModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('appl_type'):
        q = q.filter_by(appl_type=params.get('appl_type'))
    if params.get('appl_no'):
        q = q.filter_by(appl_no=params.get('appl_no'))
    if params.get('product_no'):
        q = q.filter_by(product_no=params.get('product_no'))
    if params.get('exclusivity_code'):
        q = q.filter_by(exclusivity_code=params.get('exclusivity_code'))
    return q
