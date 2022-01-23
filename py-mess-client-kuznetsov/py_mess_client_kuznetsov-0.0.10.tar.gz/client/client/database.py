import os
import sys
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
sys.path.append('../')
from common.variables import *
import datetime


class ClientDatabase:
    """
    Wrapper class for working with the client database.
    Uses SQLite database, implemented with
    SQLAlchemy ORM and the classical approach is used.
    """
    class KnownUsers:
        """
        Class - display for the table of all users.
        """
        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageStat:
        '''
        Class - display for the statistics table of transmitted messages.
        '''
        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        '''
        Class - mapping for the contact table.
        '''
        def __init__(self, contact):
            self.id = None
            self.name = contact

    # Class Constructor:
    def __init__(self, name):
        # Creating a database engine, since several are allowed
        # clients at the same time, everyone should have their own database
        # Since the client is multithreaded, it is necessary to disable
        # checking for connections from different threads,
        # # otherwise sqlite3.Programming Error
        self.database_engine = create_engine(f'sqlite:///client/database/client_{name}.db3', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        # Creating a MetaData object
        self.metadata = MetaData()

        # Creating a table of famous users
        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )

        # Creating a message history table
        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('contact', String),
                        Column('direction', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )

        # Creating a contact table
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )

        # Creating tables
        self.metadata.create_all(self.database_engine)

        # Creating mappings
        mapper(self.KnownUsers, users)
        mapper(self.MessageStat, history)
        mapper(self.Contacts, contacts)

        # Creating a session
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # It is necessary to clear the contact table, because at startup they are
        # loaded from the server.
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """ A method that adds a contact to the database. """
        if not self.session.query(
                self.Contacts).filter_by(
                name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        """ A method that clears a table with a list of contacts. """
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def del_contact(self, contact):
        """ A method that deletes a specific contact. """
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def add_users(self, users_list):
        """ A method that fills in a table of known users. """
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """ The method that stores the message in the database. """
        message_row = self.MessageStat(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """ Method that returns a list of all contacts. """
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """ Method that returns a list of all known users. """
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """ A method that checks whether a user exists. """
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """ A method that checks whether a contact exists. """
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        """ A method that returns the history of messages with a specific user. """
        query = self.session.query(
            self.MessageStat).filter_by(
            contact=contact)
        return [(history_row.contact,
                 history_row.direction,
                 history_row.message,
                 history_row.date) for history_row in query.all()]


# отладка
if __name__ == '__main__':
    test_db = ClientDatabase('test1')
    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message('test2', 'in', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('test2', 'out', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(sorted(test_db.get_history('test2'), key=lambda item: item[3]))
    test_db.del_contact('test4')
    print(test_db.get_contacts())
