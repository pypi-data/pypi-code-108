from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class ControllTypeMarkTypeLink(Base):
    """
    Связь между ControllType и MarkType
    """

    __tablename__ = 'univer_controll_type_mark_type_link'

    # Тип контроля
    controll_type_id = Column(ForeignKey('univer_controll_type.controll_type_id'), primary_key=True)
    controll_type = relationship('ControllType')

    # Тип оценки
    mark_type_id = Column(ForeignKey('univer_mark_type.mark_type_id'), primary_key=True)
    mark_type = relationship('MarkType')

    def __repr__(self):
        return '<ControllTypeMarkTypeLink {} (controll_type_id={} mark_type_id={})>'.format(self, self.controll_type_id, self.mark_type_id)
    
    def __str__(self):
        return '{} - {}'.format(self.controll_type, self.mark_type)