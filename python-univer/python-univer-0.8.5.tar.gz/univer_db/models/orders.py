from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class Order(Base):
    """
    Модель "Приказы"
    Статус: Выполняется
    """

    __tablename__ = 'univer_order'

    # Идентификатор
    id = Column('order_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Тип приказа
    order_type_id = Column(ForeignKey('univer_order_type.order_type_id'))
    order_type = relationship('OrderType')

    # Номер приказа
    number = Column('order_number', String(20))

    # Дата приказа
    date = Column('order_date', DateTime)

    # Ступень обучения
    stage_id = Column(ForeignKey('univer_stage.stage_id'))
    stage = relationship('Stage')

    # Форма обучения
    education_form_id = Column(ForeignKey('univer_education_form.education_form_id'))
    education_form = relationship('EducationForm')

    # Тип оплаты
    payment_form_id = Column(ForeignKey('univer_payment_forms.payment_form_id'))
    payment_form = relationship('PaymentForm')

    # Уровень обучения
    edu_level_id = Column(ForeignKey('univer_edu_levels.edu_level_id'))
    edu_level = relationship('EduLevel')

    def __repr__(self):
        return '<Order {} (id={} status={} order_type={} stage={} education_form={} payment_form={} edu_level={}'.format(
            self,
            self.id,
            self.status,
            self.order_type_id,
            self.stage_id,
            self.education_form_id,
            self.payment_form_id,
            self.edu_level_id
        )
    
    def __str__(self):
        return '{} - {}'.format(self.number, self.date)


class OrderType(Base):
    """
    Модель "Типы приказов"
    Статус: Выполняется
    """

    __tablename__ = 'univer_order_type'

    # Идентификатор
    id = Column('order_type_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Наименование
    name_ru = Column('order_type_name_ru', String(300))
    name_kz = Column('order_type_name_kz', String(300))
    name_en = Column('order_type_name_en', String(300))

    def __repr__(self):
        return '<OrderType {} (id={} status={})>'.format(self, self.id, self.status)
    
    def __str__(self):
        return self.name_ru


class OrderStudentLink(Base):
    """
    Связи между приказами и студентами
    Статус: Выполняется
    """

    __tablename__ = 'univer_order_student_link'

    # Приказ
    order_id = Column(ForeignKey('univer_order.order_id'), primary_key=True)
    order = relationship('Order')

    # Студент
    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')

    def __repr__(self):
        return '<OrderStudentLink {} (order={} student={})>'.format(self, self.order_id, self.student_id)
    
    def __str__(self):
        return '{} ({})'.format(self.student, self.order)