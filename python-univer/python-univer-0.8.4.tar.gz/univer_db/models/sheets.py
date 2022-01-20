from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class Sheet(Base):
    """
    Модель "Ведомость"
    """

    __tablename__ = 'univer_sheet'

    # Идентификатор
    id = Column('sheet_id', Integer, primary_key=True)

    # Тип ведомости
    sheet_type_id = Column(ForeignKey('univer_sheet_type.sheet_type_id'))
    sheet_type = relationship('SheetType')

    # Дата и время закрытия
    date_keep = Column(DateTime)

    # Группа
    group_id = Column(ForeignKey('univer_group.group_id'))
    group = relationship('Group')

    # Дата и время изменения
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<Sheet {}>'.format(self)
    
    def __str__(self):
        return str(self.id)


class SheetType(Base):
    """
    Модель "Тип ведомости"
    """

    __tablename__ = 'univer_sheet_type'

    # Идентификатор
    id = Column('sheet_type_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('sheet_type_name_ru', String(200))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<SheetType {} (id={} status={})>'.format(self, self.id, self.status)
    
    def __str__(self):
        return self.name_ru


class SheetResult(Base):
    """
    Модель "Результаты ведомости"
    """

    __tablename__ = 'univer_sheet_result'

    sheet_id = Column(ForeignKey('univer_sheet.sheet_id'), primary_key=True)
    sheet = relationship('Sheet')
    subject_id = Column(ForeignKey('univer_subject.subject_id'))
    subject = relationship('Subject')
    teacher_id = Column(ForeignKey('univer_teacher.teacher_id'))
    teacher = relationship('Teacher')
    academ_year = Column(Integer)
    semester = Column('semestr', Integer)
    control = Column(Integer, primary_key=True)
    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')
    result = Column(Float)
    date_keep = Column(DateTime)
    P_P = Column(Integer)
    n_seme = Column(Integer)
    mark_sheet_result = Column(Integer)
    retake_type = Column(Integer)

    def __repr__(self):
        return '<SheetResult {} (sheet_id={})>'.format(self, self.sheet_id)
    
    def __str__(self):
        return str(self.sheet_id)