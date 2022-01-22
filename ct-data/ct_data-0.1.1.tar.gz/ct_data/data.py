from pathlib import Path
from web3 import Web3

import pandas as pd
import os
import sqlite3
import tabulate
import copy

# internal
from db_utility import Query
from questrade_2 import QTrade
from crypto import Crypto

fipy_fp = Path(__file__).absolute().parent


class dbView():
    def __init__(self, db, query, data=None):
        self.db = db
        self.query = query
        self.header = self.get_header()
        if not data:
            self.data = pd.read_sql(self.query.build_select(), self.db.conn)
        else:
            self.data = data
        self.tabulated = tabulate.tabulate(self.data, headers=self.header)

    def get_header(self,):
        """ gets proper header for data if tabulated given columns as string

        args:
            db:             db object from finance_db
            table:          string table name to query
            columns:        select columns as list of strings toi be filtered in query
        """

        header = []
        columns = self.query.s_cols
        if not columns or '*' in columns:
            header = self.db.schema[self.query.table]
        else:
            for column in columns:
                if column in self.db.schema[self.query.table]:
                    header.append(column)

        return header

    # def show_tabulated_sql(self, db, query, data=None):
    #     """ pass db object and query object to show tabulated sql data
    #
    #     args:
    #         db:             db object from finance_db
    #         query:          query object from graph.py
    #         data:           iterable data as list of tuples or dataframe
    #
    #     """
    #     # passed query is used to get data if no data is passed
    #     if not data:
    #         data = self.db.conn.cursor().execute(self.query.build_select()).fetchall()
    #
    #     header = self.get_header()
    #     print("")
    #     print(tabulate.tabulate(data, headers=header))
    #     print("")

    # def view(self):
    #
    #     """ process requests to view db data - not great right now
    #         Args:
    #         table:          table name as string
    #         columns:        list of column names as string to be displayed DEFAULT: "*" (all columns)
    #         where_cols:     list of columns to compare to where_vals
    #
    #         pass options in *args
    #         pass args ofr options in **kwargs
    #
    #     """
    #
    #     data = pd.read_sql(self.query.build_select(), self.db.conn)
    #     if 'amount' in data.columns:
    #         data.loc['Total', 'amount'] = data['amount'].sum()
    #
    #     header = self.get_header()
    #
    #     return tabulate.tabulate(data, headers=header)


class dbInput():
    def __init__(self, query, db, drop_cond=None, drop_method=None, comp_columns=None, drop_id_col=None):
        self.query = query
        self.db = db
        self.item_type = None
        self.drop_cond = drop_cond
        self.drop_method = drop_method
        self.comp_cols = comp_columns
        self.drop_id_col = drop_id_col

    def create_item(self, item_type):
        if item_type == 'account':
            self.create_acc()
        elif item_type == 'crypto_holding':
            self.create_holding()

        self.db.conn.cursor().execute(self.query.build_insert())

        if self.drop_cond and self.drop_method:
            # delete duplicates and keep minimum id value (original entry)
            self.db.drop_duplicates(table=self.query.table, condition=self.drop_cond, method=self.drop_method,
                                    filter_columns=self.comp_cols,
                                    id_col=self.drop_id_col)
            self.db.conn.commit()

        # show new table entry
        # show_tabulated_sql(db, query)
        view = dbView(db=self.db, query=self.query)
        print(view.tabulated)

        print(item_type + " created successfully!")

    def create_acc(self,):
        """ Modify query object per the requirements of account creation
        Args:
            query:          Query object from finance_db library

        """

        # assign file path to accounts file within source parent
        filepath = None
        number = None
        for i in range(0, len(self.query.in_cols)):
            if self.query.in_cols[i] == 'num':
                filepath = str(fipy_fp.joinpath('accounts').joinpath(self.query.in_vals[i]))
                number = self.query.in_vals[i]

        for i in range(0, len(self.query.in_cols)):
            if self.query.in_cols[i] == 'filepath':
                self.query.in_vals[i] = filepath
                self.query.build_str()

        source = None
        for i in range(0, len(self.query.in_cols)):
            if self.query.in_cols[i] == 'source':
                source = self.query.in_vals[i]

        # create directory for saving transaction data to be imported if file is source
        if source == 'file':
            os.makedirs(fipy_fp.joinpath('accounts'), exist_ok=True)
            os.makedirs(fipy_fp.joinpath('accounts').joinpath(number), exist_ok=True)

    def create_holding(self,):
        # convert chain address to checksum before storage
        for i in range(0, len(self.query.in_cols)):
            if self.query.in_cols[i] == 'chain_address':
                self.query.in_vals[i] = Web3.toChecksumAddress(self.query.in_vals[i])
                self.query.build_str()

        return


class dbUpdate():
    def __init__(self, db):
        self.db = db

    def td_csv2df(self, new_data, filepath, acc_id):
        """ converts ALL TD type csv files in the account folder to appropriate dataframe for importing to sql and
            interfacing with other functions

            Args:
            account         account number or description as string
            new_data        blank dataframe with columns [date, description, amount , account id]
            db              FinanceDB object
        """

        # for each file dumped in the account folder, csv is read and appended to data
        for file in filepath:
            # if file.suffix == ".csv":
            td_statement = file

            # read from csv to df, move withdrawl column into deposit columns and reverse sign, drop withdrawl column
            statement_df = pd.read_csv(td_statement, header=None)
            statement_df[3].fillna(statement_df[2]*-1, inplace=True)

            # drop withdrawls column and total column from csv
            statement_df.drop(columns=[2], inplace=True)
            statement_df.columns = ['date', 'desc', 'amount', 'total_id']
            statement_df['acc_id'] = acc_id
            statement_df['date'] = pd.to_datetime(statement_df['date'])  # format dates and datetime objects
            if new_data.empty:
                new_data = statement_df
            else:

                new_data = pd.concat([new_data, statement_df], ignore_index=True, )
                new_data.drop_duplicates(inplace=True)

        return new_data

    def update_account(self, account):

        try:
            # get list of account info: acc_id, num, institution, desc, filepath, source if account identifier input can
            # be matched to either the account number or description
            account_info = self.db.conn.cursor().execute("SELECT * FROM accounts WHERE acc_id=? OR num=? OR desc=?",
                                                    (account, account, account)).fetchall()
            # define account information to be used later more discretely
            acc_filepath = Path(account_info[0][4]).rglob('*.csv')
            acc_source = account_info[0][5]
            acc_id = account_info[0][0]
            acc_insti = account_info[0][2]

        except sqlite3.OperationalError:
            print("Could not find Account")
            return

        # if the account source is file
        if acc_source == 'file':
            new_data = pd.DataFrame(columns=['date', 'desc', 'amount', 'acc_id', 'total'])  # date, desc, amount
            new_data['date'] = pd.to_datetime(new_data['date'])  # convert date column to datetime object
            # if account institution is TD, use TD function to convert expected csv
            if acc_insti == 'TD':
                table = 'transactions'
                new_data = self.td_csv2df(new_data, acc_filepath, acc_id)
                new_data.to_sql(name=table, index=False, con=self.db.conn, if_exists='append')
                self.db.drop_duplicates(table=table, condition='MIN', method='inside', filter_columns=['date', 'desc', 'amount', 'total_id'])

                # delete any transactions in the splits table form transactions to prevent duplication
                self.db.conn.cursor().execute("DELETE FROM transactions WHERE trans_id IN "
                                              "(SELECT transactions.trans_id FROM transactions "
                                              "LEFT JOIN splits ON splits.total_id = transactions.total_id "
                                              "WHERE splits.date = transactions.date "
                                              "AND splits.desc = transactions.desc "
                                              "AND splits.amount = transactions.amount "
                                              "AND splits.total_id = transactions.total_id)")

        elif acc_source == 'api':
            if acc_insti == 'QT':
                account_id = self.db.conn.cursor().execute("SELECT num FROM accounts WHERE institution='QT'").fetchall()[0][0]
                qt = QTrade(db=self.db)
                qt.update_qpositions(account_id=account_id)
            if acc_insti == 'crypto':
                crypto = Crypto(db=self.db)
                crypto.update_holdings()

        self.db.conn.commit()

    def split_transaction(self, query, percentage=50, amount=None):
        """ Split a transaction into multiple and edit the resulting transaction
        Args:
            db:                 FinanceDB object from finance_db lib
            query:              Query object from finance_db lib
            percentage:         percentage by which to split transaction amount, split amount is existing * percentage
                                default = 50
            amount:             amount of split portion of transaction as str, if none defaults to percentage
            """

        # get existing transaction - can only split one transaction at a time
        existing_entry = self.db.conn.cursor().execute(query.build_select()).fetchall()[0]

        # map existing entry to dictionary with columns as keys for easy handling
        existing_dict = dict()
        for i in range(0, len(existing_entry)):
            existing_dict[self.db.schema[query.table][i]] = existing_entry[i]

        # create matching new_dict to set up inserting new values
        new_dict = copy.deepcopy(existing_dict)
        new_query = copy.deepcopy(query)

        # insert existing transaction into splits table
        # splits_query = copy.deepcopy(query) # use same query but swap table
        query.table = 'splits'
        query.in_cols = ['trans_id', 'date', 'desc', 'amount', 'total_id']
        query.in_vals = []
        for column in query.in_cols:
            query.in_vals.append(str(existing_dict[column]))

        query.build_str()
        self.db.conn.cursor().execute(query.build_insert())

        # get updated amount for split transaction
        new_amount = 0
        if amount:
            if not isinstance(amount, int):
                amount = float(amount)

            if new_amount <= abs(existing_dict['amount']):
                # set updated amounts and totals (total_id)
                # new value entered is value of new transaction created by split
                new_amount = amount
            else:
                print('New split transaction amount cannot exceed original')

        elif percentage:
            if not isinstance(percentage, int):
                percentage = int(percentage)
            if int(percentage) >= 1:
                percentage = percentage/100

            # percentage is applied to total to get new amount
            new_amount = existing_dict['amount']*percentage

        # transactions are only recorded in 2 decimal places in typical transaction
        new_amount = round(new_amount, 2)

        # set new amounts for both new and existing transactions
        # set total_id for existing and split transacitons - total_id + amount = total_id prior to transaction
        original_total_id = existing_dict['total_id'] + existing_dict['amount']
        existing_dict['amount'] = existing_dict['amount'] - new_amount
        new_dict['amount'] = new_amount

        existing_dict['total_id'] = original_total_id + existing_dict['amount']
        # adding the split amount should bring the total back up to the original
        new_dict['total_id'] = original_total_id

        # edit existing transaction
        # important to note updates do not apply to the existing transaction - therefore up_cols is initialized empty
        query.up_cols = []
        query.up_cols.append('amount')
        query.up_cols.append('total_id')

        # important to note updates do not apply to the existing transaction - therefore up_vals is initialized empty
        query.up_vals = []
        query.up_vals.append(str(existing_dict['amount']))
        query.up_vals.append(str(existing_dict['total_id']))

        query.build_str()

        self.edit(query=query)

        # insert new split transaction with edits
        # insert updates into new_dict
        if new_query.up_cols and new_query.up_vals:
            for i in range(0, len(new_query.up_cols)):
                new_dict[new_query.up_cols[i]] = new_query.up_vals[i]

        # remove original trans_id so new is auto generated
        new_dict['trans_id'] = 'NULL'

        # map new_dict to new_query insert properties
        new_query.in_cols = []
        new_query.in_vals = []
        for key in new_dict.keys():
            new_query.in_cols.append(key)
            new_query.in_vals.append(str(new_dict[key]))
        new_query.build_str()

        self.db.conn.cursor().execute(new_query.build_insert())
        self.db.conn.commit()

        return

    def edit(self, query):
        """ edit selection in query using provided up_vals and diplay change to user"""

        # copy query object but erase select columns to get all data for display
        query_all = copy.deepcopy(query)
        query_all.select_str = '*'

        # get pre-update data
        original_data = self.db.conn.cursor().execute(query_all.build_select()).fetchall()

        # update the data
        self.db.conn.cursor().execute(query.build_update())
        self.db.conn.commit()

        # get updated data
        updated_data = self.db.conn.cursor().execute(query_all.build_select()).fetchall()

        # display change to user
        print('Pre-Update:')
        # print(tabulate.tabulate(original_data, headers=header))
        # show_tabulated_sql(db, query_all, data=original_data)
        view = dbView(db=self.db, query=query, data=original_data)
        print(view.tabulated)
        print("Post Update:")
        # print(tabulate.tabulate(updated_data, headers=header))
        # show_tabulated_sql(db, query, data=updated_data)
        view = dbView(db=self.db, query=query, data=updated_data)
        print(view.tabulated)

    def tag_entry(self, tagged_query, tag_param):
        # TODO drop duplicates in tags_links instead of unique constraint
        """
        tag selections in tagged_query as tags in tag_query
        tagged query can be multiple items in selection but tag_query must only select single tage at a time

        args:
            db:                 FinanceDB object from finance_db lib
            tagged_query:       Query object with selection to be tagged
            tag_param:          tag_id or tag_desc to select tag to tag tagged_query selection
        """

        # identify items to be tagged from transactions given user inputs

        # check if id column of data to be tagged is also in tags-links, otherwise table does not support tagging
        if self.db.schema[tagged_query.table][0] not in self.db.schema['tags_links']:
            print(" Table does not support tagging ")
            return

        # tag param can be either tag_id or tag_desc
        # tag query contains query to find tag to tag items passed in query or to create tag if not exists
        tags_table = 'tags'
        in_vals = [None, tag_param]
        w_cols = self.db.schema[tags_table]
        w_conds = ['=', '=']
        w_vals = [tag_param, tag_param]
        w_joins = ['OR', None]

        tag_query = Query(db=self.db, table=tags_table, in_vals=in_vals,
                          w_cols=w_cols, w_conds=w_conds, w_vals=w_vals, w_joins=w_joins)

        # need full data point to filtered columns and up_vals are cancelled out, only for when update and tag are
        # done simultaneously
        tagged_query.build_str()
        to_tag = self.db.conn.cursor().execute(tagged_query.build_select()).fetchall()

        # check if tag exists, create if not and get tag_data
        tag_data = self.db.conn.cursor().execute(tag_query.build_select()).fetchall()
        if len(tag_data) == 0:
            # tag does not exist
            tag = dbInput(query=tag_query, db=self.db)
            tag.create_item(item_type='tag')
            tag_data = self.db.conn.cursor().execute(tag_query.build_select()).fetchall()[0]
            tag_id = str(tag_data[0])
        else:
            tag_id = str(tag_data[0][0])

        for transaction in to_tag:
            # tag transaction
            table = 'tags_links'
            query_tags_transactions = Query(db=self.db, table=table, in_cols=self.db.schema[table],
                                            in_vals=[str(transaction[0]), tag_id])
            self.db.conn.cursor().execute(query_tags_transactions.build_insert())

        # show_tabulated_sql(db=db, query=tagged_query)
        view = dbView(db=self.db, query=tagged_query)
        print(view.tabulated)
        print("Tagged above transactions with tags below!")
        # show_tabulated_sql(db=db, query=tag_query)
        view = dbView(db=self.db, query=tag_query)
        print(view.tabulated)

        return
