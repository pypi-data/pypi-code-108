import pandas as pd

class InvestmentManagement:
    def __init__(self):
        self.__user_id_number = 0
        self.__users = dict()
        self.__backup_table = pd.DataFrame(columns=['ID', 'USERID', 'PORTPOLIO'])

    def __iter__(self):
        return self

    def __next__(self):
        self.__user_id_number += 1
        return self.__user_id_number

    def user(self, user_id):
        ID = self.__backup_table.loc[lambda x: x.USERID == user_id, 'ID'].item()
        return self.users[ID]

    @property
    def users(self):
        return self.__users
    
    @users.setter
    def users(self, user_id):
        ID = next(self)
        self.__users[ID] = User(ID, user_id)
        backup_table = pd.DataFrame([[ID, user_id, None]], columns=self.__backup_table.columns)
        self.__backup_table = self.__backup_table.append(backup_table)

    def _regulation_check(self, user_id):
        return user_id

    def _duplication_check(self, user_id):
        if self.__backup_table.loc[lambda x: x.USERID == user_id].shape[0] == 0:
            duplication = False
        else:
            duplication = True

        if not duplication:
            return user_id
        else:
            raise Exception('ID Duplication Error')

    def enroll(self, user_id):
        user_id = self._duplication_check(user_id)
        user_id = self._regulation_check(user_id)
        self.users = user_id

    
class User:
    def __init__(self, id_number, user_id):
        self.id_number = id_number
        self.user_id = user_id

    def portfolio_selector(self, baskets):
        self.baskets = baskets

    def expected_earning_rate(self):
        pass

    def profit(self):
        pass

    def risk(self):
        pass


IM = InvestmentManagement()
IM.enroll('si0001')
IM.enroll('kang4053')

def IMQuery(user_id):
    return IM.user(user_id)
