from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class StructureDivision(Base):
    """
    Модель "Подразделение"
    """

    __tablename__ = 'univer_structure_division_1c'

    # Идентификатор
    id = Column('structure_division_id', Integer, primary_key=True)

    # Наименование
    name_kz = Column('structure_division_name_kz', String(500))
    name_ru = Column('structure_division_name_ru', String(500))
    name_en = Column('structure_division_name_en', String(500))

    # Родительское подразделение
    parent_id = Column('structure_division_ext', ForeignKey('univer_structure_division_1c.structure_division_id'))
    parent = relationship('StructureDivision', remote_side='StructureDivision.id')

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<StructureDivision {}>'.format(self)

    def __str__(self):
        return self.name_ru


class PersonnelStructureDivisionLink(Base):
    """
    Модель "Ссылка персонала с подразделением"
    """

    __tablename__ = 'univer_personal_struct_pos_link_1c'

    # Идентификатор
    id = Column('pers_struct_pos_link_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Сотрудник
    personnel_id = Column('personal_id', ForeignKey(
        'univer_personal.personal_id'))
    personnel = relationship('Personnel')

    # Подразделение
    structure_division_id = Column(ForeignKey(
        'univer_structure_division_1c.structure_division_id'))
    structure_division = relationship('StructureDivision')

    # Должность сотрудника
    personnel_position_id = Column('personal_position_id', ForeignKey(
        'univer_personal_position_1c.personal_position_id'))
    personnel_position = relationship('PersonnelPosition')

    def __repr__(self):
        return '<PersonnelStructureDivisionLink {}>'.format(self)

    def __str__(self):
        return '{} ({})'.format(self.personnel, self.structure_division)


class Faculty(Base):
    """
    Модель "Факультет"
    """

    __tablename__ = 'univer_faculty'

    id = Column('faculty_id', Integer, primary_key=True)
    status = Column(Integer)
    name_kz = Column('faculty_name_kz', String(200))
    name_ru = Column('faculty_name_ru', String(200))
    name_en = Column('faculty_name_en', String(200))

    def __repr__(self):
        return "<Faculty {}>".format(self)

    def __str__(self):
        return self.name_ru


class Chair(Base):
    """
    Модель "Кафедра"
    """

    __tablename__ = 'univer_chair'

    id = Column('chair_id', Integer, primary_key=True)
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')
    status = Column(Integer)
    name_kz = Column('chair_name_kz', String(200))
    name_ru = Column('chair_name_ru', String(200))
    name_en = Column('chair_name_en', String(200))
    structure_division_id = Column(ForeignKey(
        'univer_structure_division_1c.structure_division_id'))
    structure_division = relationship('StructureDivision')

    def __repr__(self):
        return '<Chair {}>'.format(self)

    def __str__(self):
        return self.name_ru


class PersonnelPosition(Base):
    """
    Модель "Должность сотрудника"
    """
    __tablename__ = 'univer_personal_position_1c'

    # Идентификатор
    id = Column('personal_position_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('personal_position_name_ru', String)
    name_kz = Column('personal_position_name_kz', String)
    name_en = Column('personal_position_name_en', String)

    def __repr__(self):
        return '<PersonnelPosition {}>'.format(self)

    def __str__(self):
        return self.name_ru
