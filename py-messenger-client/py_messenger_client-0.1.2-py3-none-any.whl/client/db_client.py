import os
import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class ClientStorage:
    """ Класс - оболочка для работы с базой данных клиента. Использует SQLite базу данных, реализован с помощью
        SQLAlchemy ORM и используется декларативный подход.

    """
    Base = declarative_base()

    class KnownUsers(Base):
        """ Класс таблица всех известных пользователей

        """
        __tablename__ = 'known_users'
        id = Column(Integer, primary_key=True)
        username = Column(String)

        def __init__(self, user):
            self.id = None
            self.username = user

        def __repr__(self):
            return f'<User({self.id}, {self.username})>'

    class MessageHistory(Base):
        """ Класс таблица статистики сообщений

        """
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        from_user = Column(String)
        to_user = Column(String)
        message = Column(Text)
        date = Column(DateTime)

        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()

        def __repr__(self):
            return f'<User({self.id}, {self.from_user}, {self.to_user}, {self.message}, {self.date})>'

    class Contacts(Base):
        """ Класс таблица контактов

        """
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

        def __init__(self, contact):
            self.id = None
            self.name = contact

        def __repr__(self):
            return f'<User({self.id}, {self.name})>'

    def __init__(self, name):
        # Создаём движок базы данных, поскольку разрешено несколько клиентов одновременно, каждый должен иметь свою БД
        # Поскольку клиент мультипоточный необходимо отключить проверки на подключения с разных потоков,
        # иначе sqlite3.ProgrammingError
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.db3'
        self.database_engine = create_engine(f'sqlite:///{os.path.join(path, filename)}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})
        self.Base.metadata.create_all(self.database_engine)
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()
        # Необходимо очистить таблицу контактов, т.к. при запуске они подгружаются с сервера.
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """ Метод добавляющий контакт в базу данных.

        """
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        """ Метод, очищающий таблицу со списком контактов. """
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def del_contact(self, contact):
        """ Метод удаляющий определённый контакт.

        """
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def add_users(self, users_list):
        """ Функция добавления известных пользователей. Пользователи получаются только с сервера,
            поэтому таблица очищается.

        """
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        """ Метод сохраняющий сообщение в базе данных.

        """
        message_row = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """ Метод возвращающий список всех контактов.

        """
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """ Метод возвращающий список всех известных пользователей.

        """
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """ Метод проверяющий существует ли пользователь.

        """
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """ Метод проверяющий существует ли контакт.

        """
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        """ Метод, возвращающий историю сообщений с определённым пользователем.

        """
        query = self.session.query(
            self.MessageHistory).filter_by(
            from_user=contact)
        return [(history_row.from_user,
                 history_row.to_user,
                 history_row.message,
                 history_row.date) for history_row in query.all()]
