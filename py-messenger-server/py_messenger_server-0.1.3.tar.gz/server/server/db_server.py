import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ServerStorage:
    """ Класс - оболочка для работы с базой данных сервера. Использует SQLite базу данных, реализован с помощью
        SQLAlchemy ORM и используется декларотивный подход.

    """
    Base = declarative_base()

    class AllUsers(Base):
        """ Класс таблица всех пользователей.

        """
        __tablename__ = 'Users'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        last_login = Column(DateTime)
        passwd_hash = Column(String)
        pubkey = Column(String)

        def __init__(self, username, passwd_hash):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None
            self.id = None

        def __repr__(self):
            return f'<User({self.id}, {self.name}, {self.last_login})>'

    # Активные пользователи:
    class ActiveUsers(Base):
        """ Класс таблица активных пользователей.

        """
        __tablename__ = 'Active_users'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('Users.id'), unique=True)
        ip_address = Column(String)
        port = Column(Integer)
        login_time = Column(DateTime)

        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

        def __repr__(self):
            return f'<User({self.user}, {self.ip_address}, {self.port}, {self.login_time})>'

    class LoginHistory(Base):
        """ Класс таблица истории входов.

        """
        __tablename__ = 'Login_history'
        id = Column(Integer, primary_key=True)
        name = Column(ForeignKey('Users.id'))
        date_time = Column(DateTime)
        ip = Column(String)
        port = Column(Integer)

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

        def __repr__(self):
            return f'<User({self.name}, {self.ip}, {self.port}, {self.date_time})>'

    class UsersContacts(Base):
        """ Класс таблица контактов пользователей.

        """
        __tablename__ = 'Contacts'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('Users.id'))
        contact = Column(ForeignKey('Users.id'))

        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

        def __repr__(self):
            return f'<User({self.id}, {self.user}, {self.contact})>'

    class UsersHistory(Base):
        """ Класс таблица истории действий.

        """
        __tablename__ = 'History'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('Users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

        def __repr__(self):
            return f'<User({self.id}, {self.user}, {self.sent}, {self.accepted})>'

    def __init__(self, path):
        # Создаём движок базы данных
        # SERVER_DATABASE - sqlite:///server_base.db3
        # echo=False - отключает вывод на экран sql-запросов)
        # pool_recycle - по умолчанию соединение с БД через 8 часов простоя обрывается
        # Чтобы этого не случилось необходимо добавить pool_recycle=7200 (переустановка
        # соединения через каждые 2 часа)

        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})
        self.Base.metadata.create_all(self.database_engine)
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()
        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        # Когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port, key):
        """ Метод выполняющийся при входе пользователя, записывает в базу факт входа
            Обновляет открытый ключ пользователя при его изменении.

        """
        result = self.session.query(self.AllUsers).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        # и проверяем корректность ключа. Если клиент прислал новый ключ,
        # сохраняем его.
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        # Если нет, то создаём нового пользователя
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        self.session.commit()

    def add_user(self, name, passwd_hash):
        """ Метод регистрации пользователя. Принимает имя и хэш пароля, создаёт запись в таблице статистики.

        """
        user_row = self.AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        """ Метод удаляющий пользователя из базы.

        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(
            self.UsersContacts).filter_by(
            contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        """ Метод получения хэша пароля пользователя.

        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        """ Метод получения публичного ключа пользователя.

        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        """ Метод проверяющий существование пользователя.

        """
        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, username):
        """ Метод, выполняющийся при отключении пользователя. Пользователь удаляется из таблицы Active_users

        """
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        """ Метод возвращающий список известных пользователей со временем последнего входа.

        """
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login)
        return query.all()

    def active_users_list(self):
        """ Метод возвращающий список активных пользователей.

        """
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        """ Метод, возвращающий историю входов по конкретному пользователю, если пользователь не задан, то по всем

        """
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def process_message(self, sender, recipient):
        """ Метод записывающий в таблицу статистики факт передачи сообщения.

        """
        # Получаем ID отправителя и получателя
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        """ Метод добавления контакта для пользователя.

        """
        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что не дубль и что контакт может существовать
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        """ Метод удаления контакта пользователя.

        """
        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что контакт может существовать
        if not contact:
            return

        # Удаляем требуемое
        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    def message_history(self):
        """ Метод возвращающий статистику сообщений.

        """
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        # Возвращаем список кортежей
        return query.all()

    def get_contacts(self, username):
        """ Метод возвращающий список контактов пользователя.

        """
        user = self.session.query(self.AllUsers).filter_by(name=username).one()
        query = self.session.query(self.UsersContacts, self.AllUsers.name).filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in query.all()]
