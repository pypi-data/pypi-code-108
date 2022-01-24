import uuid
from typing import Any, Type

from infosystem.common import exception
from sqlalchemy import func
from sqlalchemy.orm import exc
from sqlalchemy.sql import text


class Driver(object):

    def __init__(self, resource: Type[Any]) -> None:
        self.resource = resource

    def removeId(self, entity_aux):
        new_id = uuid.uuid4().hex

        if entity_aux.get('id') is not None:
            new_id = entity_aux.pop('id')

        return new_id

    def instantiate(self, **kwargs):
        try:
            embedded = {}
            for attr in self.resource.embedded():
                if attr not in kwargs:
                    raise Exception()
                embedded.update({attr: kwargs.pop(attr)})

            instance = self.resource(**kwargs)

            for attr in embedded:
                value = embedded[attr]
                var = getattr(self.resource, attr)
                # TODO(samueldmq): is this good enough? should we discover it?
                mapped_attr = {self.resource.individual() + '_id': instance.id}
                if isinstance(value, list):
                    setattr(instance, attr, [var.property.mapper.class_(
                        id=self.removeId(ref), **dict(ref, **mapped_attr))
                        for ref in value])
                else:
                    # TODO(samueldmq): id is inserted here. it is in the
                    # manager for the entities. do it all in the resource
                    # contructor
                    setattr(instance, attr, var.property.mapper.class_(
                        id=uuid.uuid4().hex, **dict(value, **mapped_attr)))
        except Exception as exec:
            # TODO(samueldmq): replace with specific exception
            message = ''.join(exec.args)
            raise exception.BadRequest(message)

        return instance

    def create(self, entity, session):
        if not entity.is_stable():
            raise exception.PreconditionFailed()
        session.add(entity)
        session.flush()

    def update(self, entity, data, session):
        # try:
        #     entity = self.get(id, session)
        # except exc.NoResultFound:
        #     raise exception.NotFound()

        for attr in self.resource.embedded():
            if attr in data:
                value = data.pop(attr)
                var = getattr(self.resource, attr)
                # TODO(samueldmq): is this good enough? should we discover it?
                mapped_attr = {self.resource.individual() + '_id': id}
                if isinstance(value, list):
                    setattr(entity, attr, [var.property.mapper.class_(
                        id=self.removeId(ref), **dict(ref, **mapped_attr))
                        for ref in value])
                else:
                    # TODO(samueldmq): id is inserted here. it is in the
                    # manager for the entities. do it all in the resource
                    # contructor
                    setattr(entity, attr, var.property.mapper.class_(
                        id=uuid.uuid4().hex, **dict(value, **mapped_attr)))

        for key, value in data.items():
            if hasattr(entity, key):
                try:
                    setattr(entity, key, value)
                except AttributeError:
                    raise exception.BadRequest(
                        f'Error! The attribute {key} is read only')
            else:
                raise exception.BadRequest(
                    f'Error! The attribute {key} not exists')

        if not entity.is_stable():
            raise exception.PreconditionFailed()
        session.flush()
        return entity

    def delete(self, entity, session):
        session.delete(entity)
        session.flush()

    def get(self, id, session):
        try:
            query = session.query(self.resource).filter_by(id=id)
            result = query.one()
        except exc.NoResultFound:
            raise exception.NotFound()

        return result

    def list(self, session, **kwargs):
        query = session.query(self.resource)

        try:
            page = kwargs.pop('page', None)
            page = int(page) if page is not None else None
            page_size = kwargs.pop('page_size', None)
            page_size = int(page_size) if page_size is not None else None
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        for k, v in kwargs.items():
            if hasattr(self.resource, k):
                if isinstance(v, str) and '%' in v:
                    normalize = func.infosystem_normalize
                    query = query.filter(normalize(getattr(self.resource, k))
                                         .ilike(normalize(v)))
                else:
                    query = query.filter(getattr(self.resource, k) == v)

        name_pagination_column = 'pagination_column'
        order_by = None
        if hasattr(self.resource, name_pagination_column):
            order_by = getattr(self.resource, name_pagination_column)
        if order_by is not None:
            query = query.order_by(text(order_by))

        if page_size is not None:
            query = query.limit(page_size)
            if page is not None:
                query = query.offset(page * page_size)

        result = query.all()
        return result

    def count(self, session, **kwargs):
        try:
            rows = session.query(self.resource.id).filter_by(**kwargs).count()
            result = rows
        except exc.NoResultFound:
            raise exception.NotFound()

        return result
