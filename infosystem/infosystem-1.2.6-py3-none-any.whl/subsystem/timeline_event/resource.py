from sqlalchemy import orm
from infosystem.database import db
from infosystem.common.subsystem import entity


class TimelineEvent(entity.Entity, db.Model):

    LIMIT_SEARCH = 30

    attributes = ['domain_id', 'event_at', 'event_by', 'lat', 'lon',
                  'description', 'entity', 'entity_id']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    event_at = db.Column(db.DateTime, nullable=False, unique=False)
    event_by = db.Column(db.CHAR(32), nullable=False, unique=False)
    lat = db.Column(db.Numeric(14, 8), nullable=False, unique=False)
    lon = db.Column(db.Numeric(14, 8), nullable=False, unique=False)
    description = db.Column(db.String(500), nullable=False, unique=False)
    entity = db.Column(db.String(100), nullable=True, unique=False)
    entity_id = db.Column(db.CHAR(32), nullable=True, unique=False)
    users = orm.relationship(
        "TimelineEventUser", backref=orm.backref('timeline_event_user'),
        cascade='delete,delete-orphan,save-update')

    __tablename__ = 'timeline_event'

    def __init__(self, id, domain_id, event_at, event_by, lat, lon,
                 description, entity=None, entity_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.id = id
        self.domain_id = domain_id
        self.event_at = event_at
        self.event_by = event_by
        self.lat = lat
        self.lon = lon
        self.description = description
        self.entity = entity
        self.entity_id = entity_id,

    @classmethod
    def individual(cls):
        return 'timeline_event'

    @classmethod
    def embedded(cls):
        return ['users']


class TimelineEventUser(entity.Entity, db.Model):
    attributes = ['id', 'user_id']

    timeline_event_id = db.Column(
        db.CHAR(32), db.ForeignKey("timeline_event.id"), nullable=False)
    user_id = db.Column(
        db.CHAR(32), db.ForeignKey("user.id"), nullable=False)
    user = orm.relationship(
        'User', backref=orm.backref('timeline_event_user'))

    def __init__(self, id, timeline_event_id, user_id,
                 active=True, created_at=None,
                 created_by=None, updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.timeline_event_id = timeline_event_id
        self.user_id = user_id

    def is_stable(self):
        if self.user_id is not None and self.timeline_event_id is not None:
            return True
        return False
