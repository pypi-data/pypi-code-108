import random
import uuid
import re


class UuidTools:
    """
    Tools to update uuid consistently, maybe this should not be a class but a module...
    """

    def __init__(self, salt='', seed=None):
        # maybe salt should be in the function instead... but maybe is ok to keep consistency
        self.salt = salt
        self.seed = seed
        self.Uuid_string = r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        self.regex_pat = re.compile(self.Uuid_string, flags=re.IGNORECASE)

    def replace_id(self, seed):
        """
        generates new from another uuid adds a seed and a salt to avoid collisions,
        """
        if seed:
            rd = random.Random()
            # when coping a config two times we need to put salt
            seed = seed + self.salt
            rd.seed(seed)
            return str(uuid.UUID(int=rd.getrandbits(128), version=4)).upper()

    def get_uuid(self, number: int = 1):
        """
        generates new ids,
        """
        if self.seed:
            print(f"Generated with seed: {self.seed}")
            rd = random.Random()
            rd.seed(self.seed)
            return [str(uuid.UUID(int=rd.getrandbits(128), version=4)).upper() for i in range(number)]
        else:
            return [str(uuid.uuid4()).upper() for i in range(number)]

    def consistent_id_change(self, series):
        """
        Changes an id to another one where the same input will give always same output

        Need to apply this in some places
        """
        # series = series.copy()
        return series.apply(self.replace_id)

    def permute_id_by_dict(self, series, replace_dictionary):
        """Permute uuid given a dictionary"""
        # series = series.copy()
        return series.str.replace(self.regex_pat, lambda x: replace_dictionary[x[0]], regex=True)

    def permute_in_text_rows(self, series):
        """Permute when uuid are somewhere in a string """
        # series = series.copy()
        return series.str.replace(self.regex_pat, lambda x: self.replace_id(x[0]), regex=True)

    def make_uuid_upper(self, series):
        return series.str.replace(self.regex_pat, lambda x: x[0].upper(), regex=True)

    def apply_to_regex_uuid(self, series, fun):  # delete?
        return series.str.replace(self.regex_pat, lambda x: fun(x[0]), regex=True)

    def permute_id_for_keys(self, df, keys_to_permute, row_keys_to_permute, inplace=True):
        """
        Permute Ids in a table keys to permute are clean keys, row_keys when the ids are in
        a calculation or in a text for example
        """
        if inplace:
            table = df
        else:
            table = df.copy()

        keys_to_permute = table.keys()[table.keys().isin(keys_to_permute)]
        row_keys_to_permute = table.keys()[table.keys().isin(row_keys_to_permute)]
        for key in keys_to_permute:
            table.loc[table.index, key] = self.consistent_id_change(table[key])
        for key in row_keys_to_permute:
            table.loc[table.index, key] = self.permute_in_text_rows(table[key])
        return table

    @staticmethod
    def format_uuid(uuid_str):
        """Given a hex number with the proper size transforms it in a uuid"""
        return f"{uuid_str[:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-{uuid_str[20:]}".upper()

    @staticmethod
    def join_uuid(uuid_string):
        return ''.join(uuid_string.split('-'))

    def get_uuid_set(self, series):
        """
        Gets a series of uuid sets contained in a series
        """
        series = series.copy()
        uuid_sets = series.str.extractall(self.regex_pat)
        uuid_sets.columns = ['key']
        uuid_sets = uuid_sets.groupby(level=0)['key'].apply(set)
        series.loc[:] = None
        series.loc[uuid_sets.index] = uuid_sets
        return series

    def get_set_of_sets(self, series):
        series = self.get_uuid_set(series)
        return set().union(*series)

    def fill_ids(self, df_in, key='ID'):
        df = df_in.copy()
        df.loc[df.ID.isna(), key] = self.get_uuid(len(df[df.ID.isna()]))
        return df
