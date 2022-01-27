'''
This module contains the statements of creating and
processing clients database storage.

Databasese creats for each registered on server users.
'''

import os
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, \
                       String, Text, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ClientDatabaseStorage:
    '''Class for processing work with database object'''

    class AllKnownUsers:
        def __init__(self, username):
            self.id = None
            self.username = username

    class ClientContacts:
        def __init__(self, contact):
            self.id = None
            self.username = contact

    class ClientActivityHistory:
        def __init__(self, sender, addressee, message):
            self.id = None
            self.sender = sender
            self.addressee = addressee
            self.message = message
            self.date = datetime.now()

    def __init__(self, client_name):
        path = os.path.dirname(os.path.realpath(__file__))
        file_name = f'client_{client_name}.db3'
        self.database_engine = create_engine(
            f'sqlite:///{os.path.join(path, "databases", file_name)}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )

        self.metadata = MetaData()

        all_known_users_table = Table(
            'All_known_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String)
        )

        client_contacts_table = Table(
            'Client_contacts', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String)
        )

        client_activity_history_table = Table(
            'Client_activity_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('sender', String),
            Column('addressee', String),
            Column('message', Text),
            Column('date', DateTime)
        )

        self.metadata.create_all(self.database_engine)

        mapper(self.AllKnownUsers, all_known_users_table)
        mapper(self.ClientContacts, client_contacts_table)
        mapper(self.ClientActivityHistory, client_activity_history_table)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ClientContacts).delete()
        self.session.commit()

    def add_contact(self, contact: str):
        if not self.session.query(self.ClientContacts).filter_by(username=contact).count():
            contact_object = self.ClientContacts(contact)
            self.session.add(contact_object)
            self.session.commit()

    def contacts_clear(self):
        self.session.query(self.ClientContacts).delete()
        self.session.commit()

    def del_contact(self, contact: str):
        self.session.query(self.ClientContacts).filter_by(username=contact).delete()
        self.session.commit()

    def add_known_users(self, users: list):
        self.session.query(self.AllKnownUsers).delete()
        for user in users:
            user_object = self.AllKnownUsers(user)
            self.session.add(user_object)
        self.session.commit()

    def save_message(self, sender, addressee, message):
        message_object = self.ClientActivityHistory(sender, addressee, message)
        self.session.add(message_object)
        self.session.commit()

    def get_all_client_contacts(self):
        return [contact[0] for contact in self.session.query(self.ClientContacts.username).all()]

    def get_all_known_users(self):
        return [user[0] for user in self.session.query(self.AllKnownUsers.username).all()]

    def check_user_presence_in_known_users(self, username: str):
        if self.session.query(self.AllKnownUsers).filter_by(username=username).count():
            return True
        return False

    def check_user_presence_in_client_contacts(self, contact: str):
        if self.session.query(self.ClientContacts).filter_by(username=contact).count():
            return True
        return False

    def get_client_activity_history(self, sender):
        query = self.session.query(self.ClientActivityHistory).filter_by(sender=sender)
        return [(history_object.sender,
                 history_object.addressee,
                 history_object.message,
                 history_object.date) for history_object in query.all()]


if __name__ == '__main__':
    test_db = ClientDatabaseStorage('client_1')

    for obj in ['client_2', 'client_3', 'client_4']:
        test_db.add_contact(obj)

    test_db.add_contact('client_3')
    test_db.add_known_users(['client_1', 'client_2', 'client_3', 'client_4'])
    test_db.save_message('client_1', 'client_2', 'Hello! My name is client_1.')
    test_db.save_message('client_2', 'client_1', 'Hello! My name is clinet_2.')

    print('--- All contacts ---')
    print(test_db.get_all_client_contacts())
    print('--- All known  users ---')
    print(test_db.get_all_known_users())
    print('--- Users in known users list ---')
    print(test_db.check_user_presence_in_known_users('client_4'))
    print('--- Users in client contacts ---')
    print(test_db.check_user_presence_in_client_contacts('client_3'))
    print('--- Client history ---')
    print(test_db.get_client_activity_history(sender='client_1'))
    test_db.del_contact('client_3')
    print('--- All contacts after deleting client_3 ---')
    print(test_db.get_all_client_contacts())

