from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class Speciality(Base):
    """
    Модель "Специальность"
    """

    __tablename__ = 'univer_speciality'

    id = Column('speciality_id', Integer, primary_key=True)
    status = Column(Integer)
    faculty_id = Column(ForeignKey('univer_faculty.faculty_id'))
    faculty = relationship('Faculty')
    stage_id = Column(ForeignKey('univer_stage.stage_id'))
    stage = relationship('Stage')
    name_kz = Column('speciality_name_kz', String(200))
    name_ru = Column('speciality_name_ru', String(200))
    name_en = Column('speciality_name_en', String(200))
    code = Column('speciality_okpd', String(10))
    description_kz = Column('speciality_discription_kz', String)
    description_ru = Column('speciality_discription_ru', String)
    description_en = Column('speciality_discription_en', String)
    result_ru = Column(String)
    result_kz = Column(String)
    result_en = Column(String)
    type = Column(Integer)

    def __repr__(self):
        return "<Speciality {}>".format(self)

    def __str__(self):
        return "{} - {}".format(self.code, self.name_ru)


class SpecialityChair(Base):
    """
    Модель отношений "Специальность-Кафедра"
    """

    __tablename__ = 'univer_speciality_chair'

    speciality_id = Column(ForeignKey(
        'univer_speciality.speciality_id'), primary_key=True)
    speciality = relationship('Speciality')
    chair_id = Column(ForeignKey('univer_chair.chair_id'), primary_key=True)
    chair = relationship('Chair')

    def __repr__(self):
        return '<SpecialityChair {}>'.format(self)

    def __str__(self):
        return '{} - {}'.format(self.chair, self.speciality)


class Subject(Base):
    """
    Модель "Дисциплина"
    """

    __tablename__ = 'univer_subject'

    id = Column('subject_id', Integer, primary_key=True)
    name_kz = Column('subject_name_kz', String(500))
    name_ru = Column('subject_name_ru', String(500))
    name_en = Column('subject_name_en', String(500))
    description_kz = Column('subject_description_kz', String)
    description_ru = Column('subject_description_ru', String)
    description_en = Column('subject_description_en', String)
    status = Column(Integer)

    def __repr__(self):
        return '<Subject {}>'.format(self.name_ru)

    def __str__(self):
        return self.name_ru


class EducType(Base):
    __tablename__ = 'univer_educ_type'

    id = Column('educ_type_id', Integer, primary_key=True)
    name_ru = Column('educ_type_name_ru', String(100))

    def __repr__(self):
        return '<EducType {}>'.format(self.name_ru)

    def __str__(self):
        return self.name_ru


class LangDivision(Base):
    """
    Модель "Языковый отдел"
    """

    __tablename__ = 'univer_lang_division'

    id = Column('lang_division_id', Integer, primary_key=True)
    name_ru = Column('lang_division_name_ru', String(100))

    def __repr__(self):
        return '<LangDivision {}>'.format(self.name_ru)

    def __str__(self):
        return self.name_ru


class DocumentIdentity(Base):
    """
    Модель "Тип документа"
    Статус: Выполнено
    """

    __tablename__ = 'univer_document_identity'

    id = Column('document_identity_type', Integer, primary_key=True)
    name_ru = Column('document_name_ru', String(100))
    name_kz = Column('document_name_kz', String(100))
    name_en = Column('document_name_en', String(100))

    def __repr__(self):
        return '<DocumentIdentity {} (id={})'.format(self, self.id)

    def __str__(self):
        return self.name_ru


class Institution(Base):
    """
    Модель "Учебное заведение"
    Статус: Выполняется
    """

    __tablename__ = 'univer_edu_institutions'

    id = Column('edu_institution_id', Integer, primary_key=True)
    name_kz = Column('edu_institution_name_kz', String)
    name_ru = Column('edu_institution_name_ru', String)
    name_en = Column('edu_institution_name_en', String)

    def __repr__(self):
        return '<Institution {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name_ru


class GraduateDocType(Base):
    """
    Тип документа об окончании учебного заведения перед поступлением в университет
    Статус: Выполняется
    """

    __tablename__ = 'univer_graduate_doctypes'

    id = Column('graduate_doctype_id', Integer, primary_key=True)
    name_ru = Column('graduate_doctype_name_ru', String)
    name_kz = Column('graduate_doctype_name_kz', String)
    name_en = Column('graduate_doctype_name_en', String)

    def __repr__(self):
        return '<GraduateDocType {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name_ru


class GraduateInfo(Base):
    """
    Данные об окончании учебного заведения перед поступлением в университет
    Статус: Выполняется
    """

    __tablename__ = 'univer_graduate_info'

    id = Column('graduate_info_id', Integer, primary_key=True)
    date = Column('graduate_info_date', DateTime)
    institution_name = Column('graduate_info_institution_name', String)
    series = Column('graduate_info_series', String)
    number = Column('graduate_info_number', String)
    graduate_doctype_id = Column(ForeignKey(
        'univer_graduate_doctypes.graduate_doctype_id'))
    graduate_doctype = relationship('GraduateDocType')
    institution_id = Column('edu_institution_id', ForeignKey(
        'univer_edu_institutions.edu_institution_id'))
    institution = relationship('Institution')

    def __repr__(self):
        return '<Graduate {} (id={})>'.format(self, self.id)

    def __str__(self):
        return '{} {}'.format(self.series, self.number)


class Contract(Base):
    """
    Модель "Договор студента"
    Статус: Выполняется
    """

    __tablename__ = 'univer_contract'

    id = Column('contract_id', Integer, primary_key=True)
    number = Column('contract_number', String)
    date_received = Column('contract_date_recieved', DateTime)
    status = Column(Integer)
    student_id = Column('students_id', ForeignKey(
        'univer_students.students_id'))
    student = relationship('Student')

    def __repr__(self):
        return '<Contract {} (id={})>'.format(self, self.id)

    def __str__(self):
        '{} ({})'.format(self.student, self.number)


class AcademCalendar(Base):
    """
    Модель "Академический календарь"
    """

    __tablename__ = 'univer_academ_calendar_pos'

    id = Column('acpos_id', Integer, primary_key=True)
    educ_plan_id = Column(ForeignKey('univer_educ_plan.educ_plan_id'))
    educ_plan = relationship('EducPlan')
    acpos_semester = Column(Integer)
    acpos_module = Column(Integer)
    controll_id = Column('control_id', ForeignKey('univer_control.control_id'))
    controll = relationship('Controll')
    acpos_weeks = Column(Integer)
    acpos_date_start = Column(DateTime)
    acpos_date_end = Column(DateTime)

    def __repr__(self):
        return '<AcademCalendar {}>'.format(self)

    def __str__(self):
        return '{}'.format(self.id)


class EducPlan(Base):
    """
    Модель "Учебный план"
    """
    __tablename__ = 'univer_educ_plan'

    # Идентификатор
    id = Column('educ_plan_id', Integer, primary_key=True)

    # Специальность
    speciality_id = Column('speciality_id', ForeignKey(
        'univer_speciality.speciality_id'))
    speciality = relationship('Speciality')

    # Форма обучения
    education_form_id = Column(ForeignKey(
        'univer_education_form.education_form_id'))
    education_form = relationship('EducationForm')

    # Уровень образования
    edu_level_id = Column(ForeignKey('univer_edu_levels.edu_level_id'))
    edu_level = relationship('EduLevel')

    # Учебный год
    year = Column('educ_plan_adm_year', Integer)

    # Количество семестров в учебном плане
    semesters = Column('educ_plan_number_of_semestr', Integer)

    # Количество обязательных кредитов
    min_cred_total = Column('educ_plan_min_cred_total', Integer)

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return "<EducPlan {} {}>".format(self.speciality, self.year)

    def __str__(self):
        return "{} {}".format(self.speciality, self.year)


class EducPlanPos(Base):
    """
    Модель "Позиция учебного плана"
    """
    __tablename__ = 'univer_educ_plan_pos'

    # Идентификатор
    id = Column('educ_plan_pos_id', Integer, primary_key=True)

    # Учебный план
    educ_plan_id = Column('educ_plan_id', ForeignKey(
        'univer_educ_plan.educ_plan_id'))
    educ_plan = relationship('EducPlan')

    # Код дисциплины
    code = Column('rup_ru', String(50))

    # Дисциплина
    subject_id = Column('subject_id', ForeignKey('univer_subject.subject_id'))
    subject = relationship('Subject')

    # Тип контроля
    controll_type_id = Column(ForeignKey(
        'univer_controll_type.controll_type_id'))
    controll_type = relationship('ControllType')

    # Кредит
    credit = Column('educ_plan_pos_credit', Integer)

    # Семестр
    semester = Column('educ_plan_pos_semestr', Integer)

    # Цикл
    cycle_id = Column(ForeignKey('univer_cycles.cycle_id'))
    cycle = relationship('Cycle')

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return "<EducPlanPos {}: {} ({} семестр)>".format(self.educ_plan, self.subject, self.semester)

    def __str__(self):
        return "{}: {} ({} семестр)".format(self.educ_plan, self.subject, self.semester)


class Cycle(Base):
    """
    Модель "Цикл"
    """
    __tablename__ = 'univer_cycles'

    # Идентификатор
    id = Column('cycle_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('cycle_name_ru', String)
    name_kz = Column('cycle_name_kz', String)
    name_en = Column('cycle_name_en', String)

    def __repr__(self):
        return '<Cycle {}>'.format(self)

    def __str__(self):
        return self.name_ru


class Attendance(Base):
    """
    Модель "Журнал посещаемости"
    """

    __tablename__ = 'univer_attendance'

    date = Column('att_date', Date, primary_key=True)
    grade = Column('ball', Float)
    was = Column(Boolean)
    student_id = Column(ForeignKey(
        'univer_students.students_id'), primary_key=True)
    student = relationship('Student')
    group_id = Column(ForeignKey('univer_group.group_id'), primary_key=True)
    group = relationship('Group')

    def __repr__(self):
        return '<Attendance {}: {} балл ({})>'.format(self.student, self.grade, self.date)

    def __str__(self):
        return '{}: {} балл ({})'.format(self.student, self.grade, self.date)


class Group(Base):
    """
    Модель "Группа"
    Статус: Выполняется
    """

    __tablename__ = 'univer_group'

    id = Column('group_id', Integer, primary_key=True)
    educ_plan_pos_id = Column('educ_plan_pos_id', ForeignKey(
        'univer_educ_plan_pos.educ_plan_pos_id'))
    educ_plan_pos = relationship('EducPlanPos', backref='groups')
    teacher_id = Column('teacher_id', ForeignKey('univer_teacher.teacher_id'))
    teacher = relationship('Teacher')
    year = Column('group_year', Float)
    semester = Column('group_semestr', Integer)
    acpos_module = Column('acpos_module', Integer)
    educ_type_id = Column('educ_type_id', ForeignKey(
        'univer_educ_type.educ_type_id'))
    educ_type = relationship('EducType')
    lang_division_id = Column('lang_division_id', ForeignKey(
        'univer_lang_division.lang_division_id'))
    lang_division = relationship('LangDivision')

    # Семестр повторного обучения
    retake_semester = Column('group_retake_semestr', Integer)

    def __repr__(self):
        return '<Group {} (id={} educ_plan_pos_id={} teacher_id={})>'.format(self, self.id, self.educ_plan_pos_id, self.teacher_id)

    def __str__(self):
        return '{} ({} год)'.format(self.educ_plan_pos.educ_plan.speciality, self.educ_plan_pos.educ_plan.year)


class GroupStudent(Base):
    """
    Модель "Студент в группе"
    """

    __tablename__ = 'univer_group_student'

    id = Column('group_student_id', Integer, primary_key=True)
    group_id = Column(ForeignKey('univer_group.group_id'))
    group = relationship('Group', backref='group_students')
    student_id = Column(ForeignKey('univer_students.students_id'))
    student = relationship('Student')


class Controll(Base):
    """
    Модель "Контроль"
    """

    __tablename__ = 'univer_control'

    # Идентификатор
    id = Column('control_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('control_name_ru', String(100))

    def __repr__(self):
        return '<Controll {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name_ru


class ControllType(Base):
    """
    Модель "Тип контроля"
    """

    __tablename__ = 'univer_controll_type'

    # Идентификатор
    id = Column('controll_type_id', Integer, primary_key=True)

    # Наименование
    name_kz = Column('controll_type_name_kz', String(100))
    name_ru = Column('controll_type_name_ru', String(100))
    name_en = Column('controll_type_name_en', String(100))

    def __repr__(self):
        return '<ControllType {}>'.format(self)

    def __str__(self):
        return self.name_ru


class ControllTypeControllLink(Base):
    """
    Модель "Связь между Controll и ControllType
    Статус: Выполняется
    """

    __tablename__ = 'univer_controll_type_control_link'

    # Тип контроля
    controll_type_id = Column(ForeignKey(
        'univer_controll_type.controll_type_id'), primary_key=True)
    controll_type = relationship('ControllType')

    # Контроль
    controll_id = Column('control_id', ForeignKey(
        'univer_control.control_id'), primary_key=True)
    controll = relationship('Controll')

    # Тип ведомости
    sheet_type_id = Column(ForeignKey(
        'univer_sheet_type.sheet_type_id'), primary_key=True)
    sheet_type = relationship('SheetType')

    def __repr__(self):
        return '<ControllTypeControllLink {} (controll_type_id={} controll_id={} sheet_type_id={}>'.format(self, self.controll_type_id, self.controll_id, self.sheet_type_id)

    def __str__(self):
        return '{}-{}'.format(self.controll_type, self.controll)


class MarkType(Base):
    """
    Модель "Тип оценки"
    """

    __tablename__ = 'univer_mark_type'

    # Идентификатор
    id = Column('mark_type_id', Integer, primary_key=True)

    # Символ оценки
    symbol = Column('mark_type_symbol', String(10))

    # Минимальное значение
    min_val = Column('mark_type_minval', Integer)

    # Максимальное значение
    max_val = Column('mark_type_maxval', Integer)

    # GPA
    gpa = Column('mark_type_gpa', Float)

    def __repr__(self):
        return '<MarkType {}>'.format(self)

    def __str__(self):
        return '{} ({})'.format(self.symbol, self.gpa)


class Progress(Base):
    """
    Модель "Прогресс студента"
    """

    __tablename__ = 'univer_progress'

    # Идентификатор
    id = Column('progress_id', Integer, primary_key=True)

    # Академический год
    academ_year = Column(Integer)

    # Академический семестр
    academ_semester = Column('semestr', Integer)

    # Студент
    student_id = Column(ForeignKey('univer_students.students_id'))
    student = relationship('Student')

    # Дисциплина
    subject_id = Column(ForeignKey('univer_subject.subject_id'))
    subject = relationship('Subject')

    # Наименование дисциплины
    subject_name_ru = Column(String(500))
    subject_name_kz = Column(String(500))
    subject_name_en = Column(String(500))

    # Тип оценки
    mark_type_id = Column(ForeignKey('univer_mark_type.mark_type_id'))
    mark_type = relationship('MarkType')

    # Кредит
    credit = Column('progress_credit', Integer)

    # Оценки
    result_rk1 = Column('progress_result_rk1', Integer)
    result_rk2 = Column('progress_result_rk2', Integer)
    result = Column('progress_result', Integer)

    # Семестры
    semester = Column('n_seme', Integer)

    # Тип контроля
    controll_type_id = Column(ForeignKey(
        'univer_controll_type.controll_type_id'))
    controll_type = relationship('ControllType')

    # Часы
    hours = Column('progress_hours', Integer)

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<Progress {}>'.format(self)

    def __str__(self):
        return '{} - {}'.format(self.student, self.subject)


class Country(Base):
    __tablename__ = 'univer_country'

    id = Column('country_id', Integer, primary_key=True)
    status = Column(Integer)
    name_ru = Column('country_name_ru', String(500))
    name_kz = Column('country_name_kz', String(500))
    name_en = Column('country_name_en', String(500))
    code = Column('country_code', Integer)
    current = Column('country_current', Integer)
    letter_code = Column('country_letter_code', String(10))
    alfa3_code = Column(String(5))

    def __repr__(self):
        return '<Country {}>'.format(self)

    def __str__(self):
        return self.name_ru
