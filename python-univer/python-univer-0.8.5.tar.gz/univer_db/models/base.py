from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class PaymentForm(Base):
    """
    Модель "Форма оплаты"
    Статус: Выполняется
    """

    __tablename__ = 'univer_payment_forms'

    # Идентификатор
    id = Column('payment_form_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('payment_form_name_ru', String(100))
    name_kz = Column('payment_form_name_kz', String(100))
    name_en = Column('payment_form_name_en', String(100))

    # Краткое наименование
    short_name_ru = Column('payment_form_short_name_ru', String(100))
    short_name_kz = Column('payment_form_short_name_kz', String(100))
    short_name_en = Column('payment_form_short_name_en', String(100))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<PaymentForm {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class Stage(Base):
    """
    Модель "Ступень обучения"
    Статус: Выполняется
    """

    __tablename__ = 'univer_stage'

    # Идентификатор
    id = Column('stage_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Наименование
    name_kz = Column('stage_name_kz', String(200))
    name_ru = Column('stage_name_ru', String(200))
    name_en = Column('stage_name_en', String(200))

    def __repr__(self):
        return "<Stage {} (id={} status={})>".format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class EducationForm(Base):
    """
    Модель "Форма обучения"
    Статус: Выполняется
    """

    __tablename__ = 'univer_education_form'

    # Идентификатор
    id = Column('education_form_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Наименование
    name_kz = Column('education_form_name_kz', String(200))
    name_ru = Column('education_form_name_ru', String(200))
    name_en = Column('education_form_name_en', String(200))

    def __repr__(self):
        return "<EducationForm {} (id={} status={})>".format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class EduLevel(Base):
    """
    Модель "Уровень обучения"
    Статус: Выполняется
    """

    __tablename__ = 'univer_edu_levels'

    # Идентификатор
    id = Column('edu_level_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('edu_level_name_ru', String(100))
    name_kz = Column('edu_level_name_kz', String(100))
    name_en = Column('edu_level_name_en', String(100))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<EduLevel {} (id={} status={})'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class EnrollmentType(Base):
    """
    Модель "Тип поступления"
    Статус: Выполняется
    """

    __tablename__ = 'univer_enrollment_type'

    # Идентификатор
    id = Column('enrollment_type_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('enrollment_type_name_ru', String(100))
    name_kz = Column('enrollment_type_name_kz', String(100))
    name_en = Column('enrollment_type_name_en', String(100))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<EnrollmentType {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class Audience(Base):
    """
    Модель: Аудитория
    """

    __tablename__ = 'univer_audience'

    # Идентификатор
    id = Column('audience_id', Integer, primary_key=True)

    # Номер аудитории (На русском)
    number_ru = Column('audience_number_ru', String)

    # Номер аудитории (На казахском)
    number_kz = Column('audience_number_kz', String)

    # Номер аудитории (На английском))
    number_en = Column('audience_number_en', String)
