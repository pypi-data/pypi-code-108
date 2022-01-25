from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class Dormitory(Base):
    """
    Модель "Общежитие"
    """
    __tablename__ = 'platonus_univer_dormitories'

    id = Column('dormitoryID', Integer, primary_key=True)  # Идентификатор
    address = Column(String(256))  # Адрес общежития
    status = Column(Integer)  # Статус

    def __repr__(self):
        return '<Dormitory (id={} address={} status={})>'.format(
            self.id, self.address, self.status
        )
    
    def __str__(self):
        return self.address


class DormitoryRoom(Base):
    """
    Модель "Комната общежития"
    """
    __tablename__ = 'univer_dormitory_rooms'

    id = Column('dormitory_room_id', Integer, primary_key=True)  # Идентификатор
    dormitory_id = Column(ForeignKey('platonus_univer_dormitories.dormitoryID'))
    dormitory = relationship('Dormitory')  # Общежитие
    floor = Column('dormitory_room_floor', Integer)  # Этаж
    size = Column('dormitory_room_size', Integer)  # Вместимость
    number_ru = Column('dormitory_room_number_ru', String(30))  # Наименование комнаты (на русском)
    number_kz = Column('dormitory_room_number_kz', String(30))  # Наименование комнаты (на казахском)
    number_en = Column('dormitory_room_number_en', String(30))  # Наименование комнаты (на английском)
    status = Column(Integer)  # Статус

    def __repr__(self):
        return '<DormitoryRoom {} (id={} dormitory_id={} floor={} size={} status={}>'.format(self, self.id, self.dormitory_id, self.floor, self.size, self.status)
    
    def __str__(self):
        return self.number_ru


class DormitoryApplicant(Base):
    """
    Модель "Заявление общежития"
    """
    __tablename__ = 'univer_dormitory_applicant'

    id = Column('dormitory_applicant_id', Integer, primary_key=True)  # Идентификатор
    applicant_create = Column('dormitory_applicant_create', DateTime)  # Дата и время создания заявления
    applicant_initiator = Column('dormitory_applicant_initiator', Integer)  # Инициатор заявки
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')  # Факультет
    dormitory_id = Column(ForeignKey('platonus_univer_dormitories.dormitoryID'))
    dormitory = relationship('Dormitory')  # Общежитие
    applicant_status = Column('dormitory_applicant_status', Integer)  # Статус заявки
    status = Column(Integer)  # Статус
    year = Column(Integer)  # Год

    def __repr__(self):
        return '<DormitoryApplicant (id={}, applicant_create={}, dormitory_id={}, applicant_status={}, year={})>'.format(
            self.id, self.applicant_create, self.dormitory_id, self.applicant_status, self.year
        )


class DormitoryApplicantStudent(Base):
    """
    Модель "Студент в заявке общежития"
    """
    __tablename__ = 'univer_dormitory_applicant_students'

    applicant_id = Column('dormitory_applicant_id', ForeignKey('univer_dormitory_applicant.dormitory_applicant_id'), primary_key=True)
    applicant = relationship('DormitoryApplicant')  # Заявление общежития
    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')  # Студент
    student_status = Column('dormitory_applicant_student_status', Integer)  # Статус студента в заявке общежития
    date_begin = Column('dormitory_student_date_begin', DateTime)  # Дата и время начала
    date_end = Column('dormitory_student_date_end', DateTime)  # Дата и время окончания
    created_at = Column('dormitory_applicant_student_create', DateTime)  # Дата и время создания
    updated_at = Column('dormitory_applicant_student_update', DateTime)  # Дата и время обновления
    status = Column(Integer)  # Статус

    def __repr__(self):
        return '<DormitoryApplicantStudent (dormitory_applicant_id={} student_id={} student_status={})>'.format(
            self.applicant_id, self.student_id, self.student_status
        )


class StudentDormitoryRoomLink(Base):
    """
    Модель "Связь между студентом и комнатой"
    """
    __tablename__ = 'univer_student_dormitory_room_link'

    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')  # Студент
    dormitory_room_id = Column(ForeignKey('univer_dormitory_rooms.dormitory_room_id'), primary_key=True)
    dormitory_room = relationship('DormitoryRoom')  # Комната общежития
    year = Column(Integer)  # Год
    created_at = Column('created', DateTime)  # Дата и время создания
    applicant_id = Column('dormitory_applicant_id', ForeignKey('univer_dormitory_applicant.dormitory_applicant_id'))
    applicant = relationship('DormitoryApplicant')  # Заявления общежития

    def __repr__(self):
        return '<StudentDormitoryRoomLink (student_id={} dormitory_room_id={} year={} applicant_id={})>'.format(
            self.student_id, self.dormitory_room_id, self.year, self.applicant_id
        )


class StudentDormitoryRoomSettleHistory(Base):
    """
    Модель "История проживания в комнате общежития студентом"
    """
    __tablename__ = 'univer_student_dormitory_room_settle_history'

    id = Column('history_id', Integer, primary_key=True)  # Идентификатор
    student_id = Column(ForeignKey('univer_students.students_id'))
    student = relationship('Student')  # Студент
    dormitory_room_id = Column(ForeignKey('univer_dormitory_rooms.dormitory_room_id'))
    dormitory_room = relationship('DormitoryRoom')  # Комната общежития
    date = Column('history_date', DateTime)  # Дата и время
    user_id = Column(ForeignKey('univer_users.user_id'))
    user = relationship('User')  # Пользователь
    personnel_id = Column('personal_id', ForeignKey('univer_personal.personal_id'))
    personnel = relationship('Personnel')  # Сотрудник
    applicant_id = Column('dormitory_applicant_id', ForeignKey('univer_dormitory_applicant.dormitory_applicant_id'))
    applicant = relationship('DormitoryApplicant')  # Заявления общежития
    dormitory_id = Column(ForeignKey('platonus_univer_dormitories.dormitoryID'))
    dormitory = relationship('Dormitory')  # Общежитие
    order_type = Column(Integer)  # Тип приказа
    order_date = Column(DateTime)  # Дата и время приказа
    order_status = Column(Integer)  # Статус приказа
    dormitory_room_size = Column('dormitory_room_size', Integer)  # Размер комнаты общежития

    def __repr__(self):
        return '<StudentDormitoryRoomSettleHistory (id={} student_id={} dormitory_room_id={} date={} applicant_id={} order_type={}'.format(
            self.id,
            self.student_id,
            self.dormitory_room_id,
            self.date,
            self.applicant_id,
            self.order_type
        )


class DormitoryStudentAccess(Base):
    """
    Модель "Доступ студента к общежитию"
    """
    __tablename__ = 'univer_dormitory_student_access'

    student_id = Column(ForeignKey('univer_students.students_id'), primary_key=True)
    student = relationship('Student')  # Студент
    status = Column('access_status', Integer)  # Статус доступа
    year = Column(Integer)  # Год

    def __repr__(self):
        return '<DormitoryStudentAccess (student_id={}, status={}, year={})>'.format(
            self.student_id,
            self.status,
            self.year
        )