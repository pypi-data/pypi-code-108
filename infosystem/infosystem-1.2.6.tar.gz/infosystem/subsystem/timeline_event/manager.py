import flask
import uuid

from datetime import datetime
from sqlalchemy import func
from infosystem.common import exception
from infosystem.common.subsystem import operation, manager
from infosystem.subsystem.timeline_event.resource \
    import TimelineEvent, TimelineEventUser


class Create(operation.Create):

    def pre(self, session, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4().hex
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()
        if flask.has_request_context():
            token_id = flask.request.headers.get('token')
            if token_id is not None:
                self.token = self.manager.api.tokens().get(id=token_id)
                kwargs['created_by'] = self.token.user_id
                kwargs['event_by'] = self.token.user_id
        else:
            kwargs['event_by'] = kwargs['created_by']

        kwargs['lat'] = kwargs.get('lat', '0')
        kwargs['lon'] = kwargs.get('lon', '0')
        kwargs['event_at'] = kwargs.get('event_at', datetime.now())

        self.entity = self.driver.instantiate(**kwargs)

        return self.entity.is_stable()


class List(operation.List):

    # TODO passar para o driver do infosystem
    def __filter_params(self, resource, query, **kwargs):
        for k, v in kwargs.items():
            if hasattr(resource, k):
                if isinstance(v, str) and '%' in v:
                    normalize = func.infosystem_normalize
                    query = query.filter(normalize(getattr(resource, k))
                                         .ilike(normalize(v)))
                else:
                    query = query.filter(getattr(resource, k) == v)
        return query

    def pre(self, **kwargs):
        self.user_id = kwargs.get('user_id', None)
        if not self.user_id:
            raise exception.BadRequest('Erro! user_id is empty')
        return super().pre(**kwargs)

    def do(self, session, **kwargs):
        timeline_events = []

        timeline_events_query = session. \
            query(TimelineEvent). \
            join(TimelineEventUser,
                 TimelineEventUser.timeline_event_id == TimelineEvent.id). \
            filter(TimelineEventUser.user_id == self.user_id)

        timeline_events_query = self.__filter_params(
            TimelineEvent, timeline_events_query, **kwargs)

        timeline_events = timeline_events_query.distinct(). \
            order_by(TimelineEvent.created_at.desc()). \
            limit(TimelineEvent.LIMIT_SEARCH). \
            all()

        return timeline_events


class Manager(manager.Manager):

    def __init__(self, driver) -> None:
        super().__init__(driver)
        self.create = Create(self)
        self.list = List(self)
