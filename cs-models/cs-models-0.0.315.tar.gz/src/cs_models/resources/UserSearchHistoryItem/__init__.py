from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ...database import db_session
from ...resources.UserSearchHistoryItem.models import (
    UserSearchHistoryItemModel,
)
from .schemas import (
    UserSearchHistoryItemResourceSchema,
    UserSearchHistoryItemQueryParamsSchema,
)


schema_resource = UserSearchHistoryItemResourceSchema()
schema_params = UserSearchHistoryItemQueryParamsSchema()


class UserSearchHistoryItem(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(UserSearchHistoryItemResourceSchema)

        Returns: UserSearchHistoryItemResourceSchema

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
            params: dict(UserSearchHistoryItemQueryParamsSchema)

        Returns: List<UserSearchHistoryItemResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        user_search_history_item_query = _build_query(params=data)
        response = schema_resource.dump(
            user_search_history_item_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(UserSearchHistoryItemQueryParamsSchema)

        Returns: UserSearchHistoryItemResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        user_search_history_item_query = _build_query(params=data).one()
        response = schema_resource.dump(user_search_history_item_query).data
        return response


def _helper_create(data):
    new_search_item = UserSearchHistoryItemModel(**data)
    try:
        db_session.add(new_search_item)
        db_session.commit()
        user_search_history_item_query = db_session.query(
            UserSearchHistoryItemModel,
        ).get(new_search_item.id)
        response = schema_resource.dump(user_search_history_item_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(
        UserSearchHistoryItemModel)
    if params.get('id'):
        q = q.filter_by(id=params.get('id'))
    if params.get('user_id'):
        q = q.filter_by(user_id=params.get('user_id'))
    if params.get('search_term'):
        q = q.filter_by(search_term=params.get('search_term'))
    if params.get('search_type'):
        q = q.filter_by(search_type=params.get('search_type'))
    return q
