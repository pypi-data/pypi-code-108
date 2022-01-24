from sqlalchemy import UniqueConstraint

from infosystem.database import db
from infosystem.common.subsystem import entity


class DomainSequence(entity.Entity, db.Model):

    attributes = ['domain_id', 'name', 'value']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Numeric(10), default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'name',
            'domain_id',
            name='domain_sequence_name_domain_id_uk'),)

    def __init__(self, id, domain_id, name, value,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.name = name
        self.value = value

    @classmethod
    def individual(cls):
        return 'domain_sequence'

    def is_stable(self):
        domain_id_stable = self.domain_id is not None
        name_stable = self.name is not None
        value_stable = self.value is not None and self.value >= 0

        return domain_id_stable and name_stable and value_stable
