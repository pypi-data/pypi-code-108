from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class User(Base):
    """
    Модель "Пользователи"
    Статус: Выполняется
    """

    __tablename__ = 'univer_users'

    # Идентификатор
    id = Column('user_id', Integer, primary_key=True)

    # Логин
    username = Column('user_login', String(50))

    # Пароль
    password = Column('user_password', String(128))

    # Временный пароль
    temppass = Column('user_temppass', String(50))

    # Права доступа пользователя
    access = Column('user_access', Integer, default=0)

    def __repr__(self):
        return '<User {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.username


class Student(Base):
    """
    Модель "Студенты"
    Статус: Выполняется
    """

    __tablename__ = 'univer_students'
    __table_args__ = {
        'implicit_returning': False
    }

    # Идентификатор
    id = Column('students_id', Integer, primary_key=True)

    # Пользователь
    user_id = Column('user_id', ForeignKey('univer_users.user_id'))
    user = relationship('User')

    # Статус
    status = Column('status', Integer)

    # Дата регистрации
    reg_date = Column('student_reg_date', DateTime)

    # Ступень обучения
    stage_id = Column(ForeignKey('univer_stage.stage_id'))
    stage = relationship('Stage')

    # Уровень обучения
    edu_level_id = Column('edu_levels_id', ForeignKey(
        'univer_edu_levels.edu_level_id'))
    edu_level = relationship('EduLevel')

    # Форма обучения
    education_form_id = Column(ForeignKey(
        'univer_education_form.education_form_id'))
    education_form = relationship('EducationForm')

    # Тип поступления
    enrollment_type_id = Column(ForeignKey(
        'univer_enrollment_type.enrollment_type_id'))
    enrollment_type = relationship('EnrollmentType')

    # Тип оплаты
    payment_form_id = Column('payment_forms_id', ForeignKey(
        'univer_payment_forms.payment_form_id'))
    payment_form = relationship('PaymentForm')

    country_id = Column(ForeignKey('univer_country.country_id'))
    country = relationship('Country')

    # Пол
    sex = Column('students_sex', Integer)

    marital_status = Column('students_marital_status', Integer)

    # Дата рождения
    birth_date = Column('students_birth_date', DateTime)

    # ФИО студента
    last_name = Column('students_sname', String(100))
    first_name = Column('students_name', String(100))
    middle_name = Column('students_father_name', String(100))

    # ФИО студента в дательном падеже (На русском языке)
    dative_last_name_ru = Column('students_dative_sname_ru', String(100))
    dative_first_name_ru = Column('students_dative_name_ru', String(100))
    dative_middle_name_ru = Column(
        'students_dative_father_name_ru', String(100))

    # ФИО студента в дательном падеже (На казахском языке)
    dative_last_name_kz = Column('students_dative_sname_kz', String(100))
    dative_first_name_kz = Column('students_dative_name_kz', String(100))
    dative_middle_name_kz = Column(
        'students_dative_father_name_kz', String(100))

    # ФИО студента в дательном падеже (На английском языке)
    dative_last_name_en = Column('students_dative_sname_en', String(100))
    dative_first_name_en = Column('students_dative_name_en', String(100))
    dative_middle_name_en = Column(
        'students_dative_father_name_en', String(100))

    # Фамилия и Имя студента транслитом
    last_name_translit = Column('students_sname_intern', String(100))
    first_name_translit = Column('students_name_intern', String(100))

    # Электронная почта
    email = Column('students_email', String(25))

    # Курс
    course = Column('students_curce_number', Integer)

    # Документ
    document_identity_type_id = Column('students_document_identity_type', ForeignKey(
        'univer_document_identity.document_identity_type'))
    document_identity_type = relationship('DocumentIdentity')
    document_identity_number = Column(
        'students_document_identity_number', String(50))
    document_identity_date = Column(
        'students_document_identity_date', DateTime)
    document_identity_issued = Column(
        'students_document_identity_issued', String(100))

    # ИИН студента
    identify_code = Column('students_identify_code', String(50))

    # Данные об окончании учебного заведения перед поступлением в университет
    graduate_info_id = Column(ForeignKey(
        'univer_graduate_info.graduate_info_id'))
    graduate_info = relationship('GraduateInfo')

    # Факультет
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')

    # ОП
    speciality_id = Column(ForeignKey('univer_speciality.speciality_id'))
    speciality = relationship('Speciality')

    # Год начала действия учебного плана
    educ_plan_adm_year = Column(Integer)

    # Языковое отделение
    lang_division_id = Column(ForeignKey(
        'univer_lang_division.lang_division_id'))
    lang_division = relationship('LangDivision')

    # Нуждается в общежитии
    need_hostel = Column('students_need_hostel', Integer)

    @property
    def payment_info_ru(self):
        if self.payment_form_id == 2:
            return 'на платной основе'
        elif self.payment_form_id == 5:
            return 'на основе государственного образовательного гранта'

    @property
    def payment_info_kz(self):
        if self.payment_form_id == 2:
            return 'ақылы негізде'
        elif self.payment_form_id == 5:
            return 'мемлекеттік білім беру гранты негізінде'

    @property
    def edu_level_info_ru(self):
        if self.edu_level_id == 1:
            return '(бакалавриат, 4 года)'
        elif self.edu_level_id == 3:
            return 'по сокращенной образовательной программе на базе среднего профессионального образования'
        elif self.edu_level_id == 2:
            return 'по сокращенной образовательной программе на базе высшего образования'

    @property
    def edu_level_info_kz(self):
        if self.edu_level_id == 1:
            return '(бакалавриат, 4 жыл)'
        elif self.edu_level_id == 3:
            return 'орта кәсіптік білім негізінде қысқартылған білім беру бағдарламасы бойынша күндізгі білім беру нысаны'
        elif self.edu_level_id == 2:
            return 'жоғары білім негізінде қысқартылған білім беру бағдарламасы бойынша күндізгі білім беру нысаны'

    @property
    def dative_full_name_ru(self):
        dative_last_name_ru = self.dative_last_name_ru if self.dative_last_name_ru else self.last_name
        dative_first_name_ru = self.dative_first_name_ru if self.dative_first_name_ru else self.first_name
        dative_middle_name_ru = self.dative_middle_name_ru if self.dative_middle_name_ru else self.middle_name

        return ' '.join(filter(None, [dative_last_name_ru, dative_first_name_ru, dative_middle_name_ru]))

    @property
    def dative_full_name_kz(self):
        dative_last_name_kz = self.dative_last_name_kz if self.dative_last_name_kz else self.last_name
        dative_first_name_kz = self.dative_first_name_kz if self.dative_first_name_kz else self.first_name
        dative_middle_name_kz = self.dative_middle_name_kz if self.dative_middle_name_kz else self.middle_name

        return ' '.join(filter(None, [dative_last_name_kz, dative_first_name_kz, dative_middle_name_kz]))

    @property
    def dative_full_name_en(self):
        return ' '.join(filter(None, [self.dative_last_name_en, self.dative_first_name_en, self.dative_middle_name_en]))

    def __repr__(self):
        return '<Student {} (id={} user={} status={})>'.format(self, self.id, self.user_id, self.status)

    def __str__(self):
        return ' '.join(filter(None, [self.last_name, self.first_name, self.middle_name]))


class Personnel(Base):
    """
    Модель "Сотрудники"
    Статус: Выполняется
    """

    __tablename__ = 'univer_personal'

    # Идентификатор
    id = Column('personal_id', Integer, primary_key=True)

    # Пользователь
    user_id = Column('user_id', ForeignKey('univer_users.user_id'))
    user = relationship('User')

    # Статус
    status = Column('status', Integer)

    # ФИО персонала
    last_name = Column('personal_sname', String(200))
    first_name = Column('personal_name', String(100))
    middle_name = Column('personal_father_name', String(100))

    # Фамилия и Имя персонала транслитом
    last_name_translit = Column('personal_translit_sname', String(100))
    first_name_translit = Column('personal_translit_name', String(100))

    # Электронная почта
    work_email = Column('personal_work_email', String(50))

    # ИИН сотрудника
    identify_code = Column('personal_identification_number', String(150))

    def __repr__(self):
        return '<Personnel {} (id={} user={} status={})>'.format(self, self.user_id, self.status)

    def __str__(self):
        return ' '.join(filter(None, [self.last_name, self.first_name, self.middle_name]))


class Teacher(Base):
    """
    Модель "Преподаватели"
    Статус: Выполняется
    """

    __tablename__ = 'univer_teacher'

    # Идентификатор
    id = Column('teacher_id', Integer, primary_key=True)

    # Сотрудник
    personnel_id = Column('personal_id', ForeignKey(
        'univer_personal.personal_id'))
    personnel = relationship('Personnel')

    # Статус
    status = Column('status', Integer)

    def __repr__(self):
        return '<Teacher {} (id={} personnel={} status={})>'.format(self, self.id, self.personnel_id, self.status)

    def __str__(self):
        return str(self.personnel)


class OfficeRegistrator(Base):
    """
    Модель "Сотрудник Офис-Регистратора"
    """

    __tablename__ = 'univer_office_registrator'

    # Идентификатор
    id = Column('office_registrator_id', Integer, primary_key=True)

    # Сотрудник
    personnel_id = Column('personal_id', ForeignKey(
        'univer_personal.personal_id'))
    personnel = relationship('Personnel')

    # Факультет
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')

    # Статус
    status = Column(Integer)

    # Тип
    type = Column(Integer)

    def __repr__(self):
        return '<OfficeRegistrator {} (id={})>'.format(self, self.id)

    def __str__(self):
        return str(self.personnel)


class OfficeRegistratorFacultyLink(Base):
    """
    Связь между Специалистом ОР и Факультетом
    """
    __tablename__ = 'univer_office_registrator_faculty_link'

    # Специалист ОР
    office_registrator_id = Column(ForeignKey(
        'univer_office_registrator.office_registrator_id'), primary_key=True)
    office_registrator = relationship('OfficeRegistrator', backref='faculties')

    # Факультет
    faculty_id = Column(ForeignKey(
        'univer_faculty.faculty_id'), primary_key=True)
    faculty = relationship('Faculty')

    def __repr__(self):
        return '<OfficeRegistratorFacultyLink {}>'.format(self)

    def __str__(self):
        return f'{self.office_registrator}: {self.faculty}'


class Dean(Base):
    """
    Модель "Декан"
    """
    __tablename__ = 'univer_dekan'

    # Идентификатор
    id = Column('dekan_id', Integer, primary_key=True)

    # Сотрудник
    personnel_id = Column('personal_id', ForeignKey(
        'univer_personal.personal_id'))
    personnel = relationship('Personnel')

    # Факультет
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')

    # Дата начала
    start_date = Column('dekan_start_date', DateTime)

    # Дата окончания
    end_date = Column('dekan_end_date', DateTime)

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<Dean {} (id={})>'.format(self, self.id)

    def __str__(self):
        return str(self.personnel)


class TeacherChairLink(Base):
    """
    Модель отношение между Teacher (Преподаватель) и Chair (Кафедра)
    """
    __tablename__ = 'univer_teacher_chair_link'

    # Преподаватель
    teacher_id = Column(ForeignKey(
        'univer_teacher.teacher_id'), primary_key=True)
    teacher = relationship('Teacher')

    # Кафедра
    chair_id = Column(ForeignKey('univer_chair.chair_id'), primary_key=True)
    chair = relationship('Chair')

    # Ставка
    rate = Column('stavka', Integer)

    def __repr__(self):
        return '<TeacherChairLink {}>'.format(self)

    def __str__(self):
        return f'{self.chair}: {self.teacher}'
