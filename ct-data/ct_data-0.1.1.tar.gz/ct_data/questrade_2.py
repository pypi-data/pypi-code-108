from qtrade import Questrade
import pathlib

# internal
from db_utility import Query


class QTrade():
    def __init__(self, db):
        self.fipy_fp = pathlib.Path(__file__).absolute().parent.parent
        self.src_path = self.fipy_fp.joinpath('ct_data')
        self.yaml_path = self.src_path.joinpath('access_token.yml')
        self.db = db
        self.qtrade_table = 'qtrade'
        print(self.yaml_path)

    def qtrade_connect(self,):
        try:
            # access_code = 'hJxEWwStLWDPAx397CYGXc93AtQEeAa10'
            # qtrade = Questrade(access_code=access_code)
            qtrade = Questrade(token_yaml=self.yaml_path)
            qtrade.refresh_access_token(from_yaml=True)
        except:
            # qtrade = Questrade(token_yaml=yaml_path)
            # qtrade.refresh_access_token(from_yaml=True)
            access_code = input("please input Questrade API Access token ")
            qtrade = Questrade(access_code=access_code)

        return qtrade

    def update_qpositions(self, account_id):

        qtrade = self.qtrade_connect()
        positions = qtrade.get_account_positions(account_id=account_id)
        for pos in positions:
            update = {key: None for key in self.db.schema['qtrade']}
            for key in update.keys():
                # db table column names are same as default dictionary names for properties in position
                # need to eliminate params that are in positions dictionaries but not in db qtrade table
                if key in pos.keys():
                    update[key] = pos[key]

            update.pop('date')
            update_cols = list(update.keys())
            update_vals = list(update.values())

            query = Query(db=self.db, table=self.qtrade_table,
                          in_vals=update_vals, in_cols=update_cols, )

            # query = db.insert(table='qtrade', columns=update_cols, values=update_vals)
            self.db.conn.cursor().execute(query.build_insert())
            self.db.conn.commit()
