"""
База данных для клиентской стороны мессенджера.
БД содержит следующие таблицы:
a) список всех пользователей;
b) список контактов;
c) история сообщений.
Использует SQLite базу данных, реализован с помощью
SQLAlchemy ORM с использованием декларативного подхода.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


class ClientStorage:
    """
    Класс-оболочка для клиентской базы данных.
    """
    Base = declarative_base()

    class AllUsers(Base):
        """
        Таблица "Все пользователеи"
        """
        __tablename__ = 'all_users'

        id = Column(Integer, primary_key=True)
        user_name = Column(String, unique=True)

        def __init__(self, name):
            self.user_name = name

    class ContactList(Base):
        """
        Таблица "Список контактов"
        """
        __tablename__ = 'contact_list'

        id = Column(Integer, primary_key=True)
        user_name = Column(String, unique=True)

        def __init__(self, name):
            self.user_name = name

    class MessageHistory(Base):
        """
        Таблица "История сообщений"
        """
        __tablename__ = 'message_history'

        id = Column(Integer, primary_key=True)
        sender = Column(String)
        recipient = Column(String)
        msg_text = Column(String)
        msg_time = Column(DateTime)

        def __init__(self, sender, recipient, msg_text):
            self.sender = sender
            self.recipient = recipient
            self.msg_text = msg_text
            self.msg_time = datetime.now()

    def __init__(self, name):
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.db3'
        self.engine = create_engine(f'sqlite:///{os.path.join(path, filename)}',
                                    echo=False,
                                    pool_recycle=7200,
                                    connect_args={'check_same_thread': False})

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(self.engine)
        self.session = Session()

        self.session.query(self.ContactList).delete()
        self.session.commit()

    def save_message(self, sender, recipient, msg_text):
        """
        Функция сохраниения сообщений.
        """
        self.session.add(self.MessageHistory(sender, recipient, msg_text))
        self.session.commit()

    def get_message_history(self, name=None):
        """
        Получает историю сообщений с пользователем или всю историю сообщений
        """
        history = self.session.query(self.MessageHistory)
        if name:
            history = history.filter(or_(self.MessageHistory.sender == name,
                                         self.MessageHistory.recipient == name))

        result = [(row.sender, row.recipient, row.msg_time, row.msg_text) for row in history]
        return result

    def add_all_users(self, user_list):
        """
        Добавляет в базу список пользователей, полученный с сервера.
        """
        self.session.query(self.AllUsers).delete()
        for user in user_list:
            user_row = self.AllUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def get_users(self):
        """
        Возвращает список известных пользователей.
        """
        return [user[0] for user in self.session.query(self.AllUsers.user_name).all()]

    def check_user(self, user):
        """
        Проверяющяя наличие пользователя в известных.
        """
        if self.session.query(self.AllUsers).filter_by(user_name=user).count():
            return True
        else:
            return False

    def add_contacts(self, contact_list):
        """
        Обновляет список контактов.
        """
        self.session.query(self.ContactList).delete()
        for user in contact_list:
            self.session.add(self.ContactList(user))
        self.session.commit()

    def add_contact(self, name):
        """
        Добавляет контакт в список контактов
        """
        if not self.session.query(self.ContactList).filter_by(user_name=name).count():
            self.session.add(self.ContactList(name))
            self.session.commit()

    def del_contact(self, name):
        """
        Удаляет контакт из списка контактов
        """
        self.session.query(self.ContactList).filter_by(user_name=name).delete()
        self.session.commit()

    def get_contacts(self):
        """
        Возвращает список контактов пользователя
        """
        return [contact[0] for contact in self.session.query(self.ContactList.user_name).all()]

    def check_contact(self, contact):
        """
        Проверяет наличие пользователя в списке контактов
        """
        if self.session.query(self.ContactList).filter_by(user_name=contact).count():
            return True
        else:
            return False


if __name__ == '__main__':
    test_db = ClientStorage('test1')
    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)

    test_db.add_contact('test4')

    test_db.add_contacts(['test1', 'test2', 'test3', 'test4', 'test5'])

    test_db.save_message('test1', 'test2', 'тестовое сообщение')
    test_db.save_message('test2', 'test1', 'другое тестовое сообщение')
    print(test_db.get_contacts())

    print(test_db.check_contact('test1'))
    print(test_db.check_contact('test10'))

    for msg in test_db.get_message_history('test2'):
        print(f'От {msg[0]} для {msg[1]} в {msg[2]}\n'
              f'{msg[3]}')

    for msg in test_db.get_message_history():
        print(f'От {msg[0]} для {msg[1]} в {msg[2]}\n'
              f'{msg[3]}')

    test_db.del_contact('test4')
    print(test_db.get_contacts())
