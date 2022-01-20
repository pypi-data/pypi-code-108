from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, Time
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class ScheduleTimeType(Base):
    """
    Модель "Тип времени расписания"
    """
    __tablename__ = 'univer_schedule_time_type'

    # Идентификтор
    id = Column('schedule_time_type_id', Integer, primary_key=True)

    # Наименование (на казахском)
    name_kz = Column('schedule_time_type_name_kz', String)

    # Наименование (на русском)
    name_ru = Column('schedule_time_type_name_ru', String)

    # Наименование (на английском)
    name_en = Column('schedule_time_type_name_en', String)

    def __repr__(self):
        return '<ScheduleTimeType {}>'.format(self)

    def __str__(self):
        return str(self.id)


class ScheduleTime(Base):
    """
    Модель "Время расписания
    """
    __tablename__ = 'univer_schedule_time'

    # Идентификатор
    id = Column('schedule_time_id', Integer, primary_key=True)

    # Время начало
    begin = Column('schedule_time_begin', Time)

    # Время окончания
    end = Column('schedule_time_end', Time)

    # Статус
    status = Column(Integer)

    # Тип времени расписания
    type_id = Column('schedule_time_type_id', ForeignKey(
        'univer_schedule_time_type.schedule_time_type_id'))
    type = relationship('ScheduleTimeType')

    def __repr__(self):
        return '<ScheduleTime {}>'.format(self)

    def __str__(self):
        return str(self.id)


class Schedule(Base):
    """
    Модель "Расписание"
    """
    __tablename__ = 'univer_schedule'

    # Идентификатор
    id = Column('schedule_id', Integer, primary_key=True)

    # Группа
    group_id = Column(ForeignKey('univer_group.group_id'))
    group = relationship('Group')

    # Время расписаниея
    time_id = Column('schedule_time_id', ForeignKey(
        'univer_schedule_time.schedule_time_id'))
    time = relationship('ScheduleTime')

    # День недели
    week_day = Column('schedule_week_day', Integer)

    # Аудитория
    audience_id = Column(ForeignKey('univer_audience.audience_id'))
    audience = relationship('Audience')

    def __repr__(self):
        return '<Schedule {}>'.format(self)

    def __str__(self):
        return str(self.id)


class ExamSchedule(Base):
    """
    Модель "Расписание экзамена"
    """
    __tablename__ = 'univer_exam_schedule'

    # Идентификатор
    id = Column('exam_schedule_id', Integer, primary_key=True)

    # Группа
    group_id = Column(ForeignKey('univer_group.group_id'))
    group = relationship('Group')

    # Экзаменатор
    examiner_id = Column('examiner_teacher_id',
                         ForeignKey('univer_teacher.teacher_id'))
    examiner = relationship('Teacher')

    # Аудитория
    audience_id = Column(ForeignKey('univer_audience.audience_id'))
    audience = relationship('Audience')

    # Дата и время экзамена
    exam_time = Column(DateTime)

    # Время экзамена
    time_id = Column('schedule_time_id', ForeignKey(
        'univer_exam_schedule_time.exam_schedule_time_id'))
    time = relationship('ExamScheduleTime')

    def __repr__(self):
        return '<ExamSchedule {}>'.format(self)

    def __str__(self):
        return str(self.id)


class ExamScheduleTime(Base):
    """
    Модель "Время расписания экзамена"
    """
    __tablename__ = 'univer_exam_schedule_time'

    # Идентификатор
    id = Column('exam_schedule_time_id', Integer, primary_key=True)

    # Время начала экзамена
    begin = Column(Time)

    # Тип (?)
    type = Column(Integer)

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<ExamScheduleTime {}>'.format(self)

    def __str__(self):
        return str(self.id)
