import re
import dateutil
import pandas as pd

from datetime import datetime
from textblob.classifiers import NaiveBayesClassifier
from colorama import init, Fore, Style
from tabulate import tabulate


class BankClassify:

    def __init__(self, db, data="sql"):
        """Load in the previous data (by default from `data`) and initialise the classifier"""
        self.db = db

        # allows dynamic training data to be used (i.e many accounts in a loop)
        self.unprocessed_data = None
        self.processed_data = None
        self.categories = None

        if data == 'sql':

            # select all data from transactions joined with categories descriptions that have been assigned a
            # category to be used for/as training data - only data with a category is selected
            data = self.db.conn.cursor().execute("SELECT date, desc, amount, cat_desc FROM transactions "
                                                 "JOIN categories ON transactions.cat_id=categories.cat_id").fetchall()
            # create data frame from cursor selection with expected column names
            prev_df = pd.DataFrame(data, columns=['date', 'desc', 'amount', 'cat'])

            self.training_data = prev_df
        else:
            self.training_data = pd.DataFrame(columns=['date', 'desc', 'amount', 'cat'])

        self.classifier = NaiveBayesClassifier(self._get_training(self.training_data), self._extractor)

    def add_unprocessed_data(self):
        """Add new data and interactively classify it.
        Arguments:
         - filename: filename of Santander-format file
        """
        query = pd.read_sql_query("SELECT * FROM transactions "
                                  "WHERE cat_id IS NULL ORDER BY date asc", self.db.conn)
        unprocessed_df = pd.DataFrame(query, columns=self.db.schema['transactions'])

        self.unprocessed_data = unprocessed_df

        # update following section to add data back into transactions db

        # self.prev_data = pd.concat([self.prev_data, self.new_data])
        # # save data to the same file we loaded earlier
        # self.prev_data.to_csv(self.trainingDataFile, index=False)

    def _prep_for_analysis(self):
        """Prepare data for analysis in pandas, setting index types and subsetting"""
        self.training_data = self._make_date_index(self.training_data)

        self.training_data['cat'] = self.training_data['cat'].str.strip()

        self.inc = self.training_data[self.training_data.amount > 0]
        self.out = self.training_data[self.training_data.amount < 0]
        self.out.amount = self.out.amount.abs()

        self.inc_noignore = self.inc[self.inc.cat != 'Ignore']
        self.inc_noexpignore = self.inc[(self.inc.cat != 'Ignore') & (self.inc.cat != 'Expenses')]

        self.out_noignore = self.out[self.out.cat != 'Ignore']
        self.out_noexpignore = self.out[(self.out.cat != 'Ignore') & (self.out.cat != 'Expenses')]

    def _read_categories(self):
        """Read list of categories from categories.txt"""
        categories = {}

        with open('categories.txt') as f:
            for i, line in enumerate(f.readlines()):
                categories[i] = line.strip()

        return categories

    def _read_categories_sql(self):
        """Read list of categories from categories.txt
            categories in an enumerated dictionary!
            """
        categories_dict = {}
        categories = self.db.conn.cursor().execute("SELECT * FROM categories").fetchall()

        categories_dict = dict((x, y) for x, y in categories)

        return categories_dict

    def _add_new_category(self, categories, category):
        """Add a new category to categories.txt"""
        # with open('categories.txt', 'a') as f:
        #     f.write('\n' + category)
        if len(categories) != 0:
            max_key = max(list(categories.keys()))
            new_key = max_key + 1
            categories[new_key] = category
        else:
            categories[1] = category

        return categories

    def commit_categories(self, table='categories'):
        # move categories dictionary to dataframe to make sql transition easier
        if self.categories:
            categories_df = pd.DataFrame.from_dict(data=self.categories, orient="index")
            # replace because entire category is added when loaded, ignore is deal but not available
            categories_df.rename(columns={0: self.db.schema['categories'][1]}, inplace=True)
            categories_df.index.names = [self.db.schema['categories'][0],]
            # TODO cant replace table when there are foreign key constraints
            # TODO compare old and new categories OUTSIDE of database, then reindex and append without index to allow for autoincrement
            # self.db.drop_duplicates(table='categories', method='outside', new_data=categories_df)
            self.db.drop_duplicates(table='categories', condition='MIN', method='inside',
                                    filter_columns=['cat_desc'])

            # categories_df.to_sql(name='categories', con=self.db.conn, index=False, if_exists='append')

            self.db.conn.commit()

    def commit_data(self, table):
        if not self.processed_data.empty:
            # set processed column to 1 for processed columns
            self.processed_data['processed'] = 1
            self.processed_data.drop(columns=['trans_id'], inplace=True)
            self.processed_data.to_sql(name=table, con=self.db.conn, index=False, if_exists='append')

            self.db.drop_duplicates(table=table, condition='MAX', method='inside',
                                    filter_columns=['date', 'desc', 'amount', 'total_id'])
            self.db.conn.commit()

    # function to return key for any value
    def get_key(self, val):
        for key, value in self.categories.items():
            if val == value:
                return key

        return "key doesn't exist"

    def ask_with_guess(self):
        """Interactively guess categories for each transaction in df, asking each time if the guess
        is correct"""
        # Initialise colorama
        init()

        # new_data['cat'] = ""
        self.add_unprocessed_data()
        self.unprocessed_data.rename(columns={"description": "desc"}, inplace=True)
        self.processed_data = pd.DataFrame(columns=self.db.schema['transactions'])

        # categories returned as dictionary
        self.categories = self._read_categories_sql()
        if not self.categories:
            self.categories = dict()

        for index, row in self.unprocessed_data.iterrows():
            # Generate the category numbers table from the list of categories
            cats_list = [[idnum, cat] for idnum, cat in self.categories.items()]
            cats_table = tabulate(cats_list)

            stripped_text = self._strip_numbers(row['desc'])

            # Guess a category using the classifier (only if there is data in the classifier)
            if len(self.classifier.train_set) > 1:
                guess = self.classifier.classify(stripped_text)
            else:
                guess = ""

            # Print list of categories
            print(cats_table)
            print("\n")
            # Print transaction
            # print("On: %s\t %.2f\n%s" % (row['date'], row['amount'], row['desc']))
            # print(Fore.RED  + Style.BRIGHT + "My guess is: " + str(guess) + Fore.RESET)
            print(tabulate(self.unprocessed_data.loc[[index]], headers='keys'))
            print(Fore.RED + Style.BRIGHT + "My guess is: " + str(guess) + Fore.RESET)

            input_value = input("> ")
            category = ""
            if input_value.lower() == 'q':
                # If the input was 'q' then quit
                self.commit_categories()
                self.commit_data(table='transactions')
                return

            if input_value == "":
                # If the input was blank then our guess was right!
                # TODO need to put in category index not description or sql will be pissed
                # update data with category ID
                self.unprocessed_data.at[index, 'cat_id'] = self.get_key(guess)
                category_key = self.get_key(guess)
                # update classifier with category (guess)
                self.classifier.update([(stripped_text, guess)])

            else:
                # Otherwise, our guess was wrong
                if input_value in self.categories.values():
                    # if entered category is a categories dictionary value, convert ot integer id and update data
                    category = input_value
                    category_key = self.get_key(input_value)
                else:
                    try:
                        category_key = int(input_value)
                        if int(input_value) in self.categories.keys():
                            # if integer key entered for category use as is
                            category_key = input_value
                            category = self.categories[int(input_value)]

                    except ValueError:
                        # Otherwise, we've entered a new category, so add it to the list of
                        # categories
                        category = input_value
                        self._add_new_category(self.categories, input_value)
                        category_key = self.get_key(input_value)

            # Write correct answer
            self.unprocessed_data.at[index, 'cat_id'] = category_key
            self.processed_data = self.processed_data.append(self.unprocessed_data.loc[[index]])
            # Update classifier
            self.classifier.update([(stripped_text, category)])

            # if all transactions are processed
        self.commit_categories()
        self.commit_data(table='transactions')

        return

    def _make_date_index(self, df):
        """Make the index of df a Datetime index"""
        df.index = pd.DatetimeIndex(df.date.apply(dateutil.parser.parse, dayfirst=True))

        return df

    def _read_nationwide_file(self, filename):
        """Read a file in the csv file that Nationwide provides downloads in.
        Returns a pd.DataFrame with columns of 'date', 'desc' and 'amount'."""

        with open(filename) as f:
            lines = f.readlines()


        dates = []
        descs = []
        amounts = []

        for line in lines[5:]:

            line = "".join(i for i in line if ord(i)<128)
            if line.strip() == '':
                continue

            splits = line.split("\",\"")
            """
            0 = Date
            1 = Transaction type
            2 = Description
            3 = Paid Out
            4 = Paid In
            5 = Balance
            """
            date = splits[0].replace("\"", "").strip()
            date = datetime.strptime(date, '%d %b %Y').strftime('%d/%m/%Y')
            dates.append(date)

            # get spend/pay in amount
            if splits[3] != "": # paid out
                spend = float(re.sub("[^0-9\.-]", "", splits[3])) * -1
            else: # paid in
                spend = float(re.sub("[^0-9\.-]", "", splits[4]))

            amounts.append(spend)

            #Description
            descs.append(splits[2])

        df = pd.DataFrame({'date':dates, 'desc':descs, 'amount':amounts})

        df['amount'] = df.amount.astype(float)
        df['desc'] = df.desc.astype(str)
        df['date'] = df.date.astype(str)

        return df

    def _read_santander_file(self, filename):
        """Read a file in the plain text format that Santander provides downloads in.
        Returns a pd.DataFrame with columns of 'date', 'desc' and 'amount'."""
        with open(filename, errors='replace') as f:
            lines = f.readlines()

        dates = []
        descs = []
        amounts = []

        for line in lines[4:]:

            line = "".join(i for i in line if ord(i)<128)
            if line.strip() == '':
                continue

            splitted = line.split(":")

            category = splitted[0]
            data = ":".join(splitted[1:])

            if category == 'Date':
                dates.append(data.strip())
            elif category == 'Description':
                descs.append(data.strip())
            elif category == 'Amount':
                just_numbers = re.sub("[^0-9\.-]", "", data)
                amounts.append(just_numbers.strip())


        df = pd.DataFrame({'date':dates, 'desc':descs, 'amount':amounts})


        df['amount'] = df.amount.astype(float)
        df['desc'] = df.desc.astype(str)
        df['date'] = df.date.astype(str)

        return df

    def _read_lloyds_csv(self, filename):
        """Read a file in the CSV format that Lloyds Bank provides downloads in.
        Returns a pd.DataFrame with columns of 'date' 0 , 'desc'  4 and 'amount' 5 ."""

        df = pd.read_csv(filename, skiprows=0)

        """Rename columns """
        #df.columns = ['date', 'desc', 'amount']
        df.rename(
            columns={
                "Transaction Date" : 'date',
                "Transaction Description" : 'desc',
                "Debit Amount": 'amount',
                "Credit Amount": 'creditAmount'
            },
            inplace=True
        )

        # if its income we still want it in the amount col!
        # manually correct each using 2 cols to create 1 col with either + or - figure
        # lloyds outputs 2 cols, credit and debit, we want 1 col representing a +- figure
        for index, row in df.iterrows():
            if (row['amount'] > 0):
                # it's a negative amount because this is a spend
                df.at[index, 'amount'] = -row['amount']
            elif (row['creditAmount'] > 0):
                df.at[index, 'amount'] = row['creditAmount']

        # cast types to columns for math
        df = df.astype({"desc": str, "date": str, "amount": float})

        return df

    def _read_mint_csv(self, filename) -> pd.DataFrame:
        """Read a file in the CSV format that mint.intuit.com provides downloads in.
        Returns a pd.DataFrame with columns of 'date', 'desc', and 'amount'."""

        df = pd.read_csv(filename, skiprows=0)

        """Rename columns """
        # df.columns = ['date', 'desc', 'amount']
        df.rename(
            columns={
                "Date": 'date',
                "Original Description": 'desc',
                "Amount": 'amount',
                "Transaction Type": 'type'
            },
            inplace=True
        )

        # mint outputs 2 cols, amount and type, we want 1 col representing a +- figure
        # manually correct amount based on transaction type colum with either + or - figure
        df.loc[df['type'] == 'debit', 'amount'] = -df['amount']

        # cast types to columns for math
        df = df.astype({"desc": str, "date": str, "amount": float})
        df = df[['date', 'desc', 'amount']]

        return df

    def _read_barclays_csv(self, filename):
        """Read a file in the CSV format that Barclays Bank provides downloads in.
        Edge case: foreign txn's sometimes causes more cols than it should
        Returns a pd.DataFrame with columns of 'date' 1 , 'desc' (memo)  5 and 'amount' 3 ."""

        # Edge case: Barclays foreign transaction memo sometimes contains a comma, which is bad.
        # Use a work-around to read only fixed col count
        # https://stackoverflow.com/questions/20154303/pandas-read-csv-expects-wrong-number-of-columns-with-ragged-csv-file
        # Prevents an error where some rows have more cols than they should
        temp=pd.read_csv(filename,sep='^',header=None,prefix='X',skiprows=1)
        temp2=temp.X0.str.split(',',expand=True)
        del temp['X0']
        df = pd.concat([temp,temp2],axis=1)

        """Rename columns """
        df.rename(
            columns={
                1: 'date',
                5 : 'desc',
                3: 'amount'
            },
            inplace=True
        )

        # cast types to columns for math
        df = df.astype({"desc": str, "date": str, "amount": float})

        return df

    def _get_training(self, df):
        """Get training data for the classifier, consisting of tuples of
        (text, category)"""
        train = []
        subset = df[df['cat'] != '']
        for i in subset.index:
            row = subset.iloc[i]
            new_desc = self._strip_numbers(row['desc'])
            train.append((new_desc, row['cat']))

        return train

    def _extractor(self, doc):
        """Extract tokens from a given string"""
        # TODO: Extend to extract words within words
        # For example, MUSICROOM should give MUSIC and ROOM
        tokens = self._split_by_multiple_delims(doc, [' ', '/'])

        features = {}

        for token in tokens:
            if token == "":
                continue
            features[token] = True

        return features

    def _strip_numbers(self, s):
        """Strip numbers from the given string"""
        return re.sub("[^A-Z ]", "", s)

    def _split_by_multiple_delims(self, string, delims):
        """Split the given string by the list of delimiters given"""
        regexp = "|".join(delims)

        return re.split(regexp, string)