import copy
import pandas as pd
import pandas_profiling
import json
import os
import string
import itertools

from fuzzywuzzy import fuzz

from inspec._analytics import telemetry_service


class CategoryCleaner:
    def __init__(self, df: pd.DataFrame, pandas_profiling_report: dict=None):
        """

        :param df: pd.DataFrame containing the data to be cleaned. Assumes that df has column headers
        :param pandas_profiling_report: [OPTIONAL] the pandas profiling report associated with the df. If not provided, will be generated.
        """
        self.df = df

        if pandas_profiling_report:
            self.pandas_profiling_report = pandas_profiling_report
        else:
            self.pandas_profiling_report = self.get_pandas_profiling_report()


    def get_pandas_profiling_report(self) -> dict:
        """
        Generates a pandas profiling report for the pd.DataFrame given as input to the class

        :return: dict, containing the report's results
        """
        profile = pandas_profiling.ProfileReport(self.df, title="Pandas Profiling Report", explorative=True)
        return json.loads(profile.to_json())


    def get_string_categorical_features(self) -> list:
        """
        Finds the features that are categorical and of dtypes "object" to find string categorical features

        :return: list, containing strings. Each value is the name of a feature identified as categorical with string values.
        """
        # get categorical features
        categorical_features = []
        for feat in self.pandas_profiling_report["variables"]:
            if self.pandas_profiling_report["variables"][feat]["type"] == 'Categorical':
                categorical_features.append(feat)

        # get features with only strings (object) type
        types = self.df.dtypes
        object_type = list(types[types == "object"].index)

        string_categorical_features=[]
        # clean each string categorical feature
        for feat in categorical_features:
            if feat in object_type:
                string_categorical_features.append(feat)

        return string_categorical_features


    def get_unique_values(self, col:pd.Series) -> pd.Series:
        """
        Finds unique values contained in "col". Ignores NaN and empty strings as unique values

        :param col: pd.Series. The data to check the unique values in. It is assumed that col contains strings.
        :return: pd.Series. Contains the unique values found in col
        """
        values = pd.Series(col.dropna().unique())
        values = values[values != ""]
        return values


    def get_cleaned_values(self, unique_values:pd.Series) -> pd.Series:
        """
        Performs some cleaning operations on values in "unique_values". Assumes that "unique_values" contains strings.

        :param unique_values: pd.Series. Usually a column with the unique values of another column. Assumed to be strings.
        :return: pd.Series. The cleaned version of "unique_values"
        """

        # BASIC PRE-PROCESSING OF THE UNIQUE VALUES
        # remove whitespaces at the end and beginning
        clean_values = unique_values.str.strip()

        # replace multiple white spaces with single whitespace
        clean_values = clean_values.str.replace(r" +", r" ", regex=True)

        # only lower case
        clean_values = clean_values.str.lower()

        # remove punctuation
        clean_values = clean_values.str.replace(r"[{}]".format(string.punctuation), r"", regex=True)

        # remove digits
        clean_values = clean_values.str.replace(r"\d+", r"", regex=True)

        return clean_values


    def get_basic_groupings(self, col:pd.Series) -> list:
        """
        Gets groupings of values contained in "col" that can be easily identified as similar.

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :return: list. Each element is a tuple of two strings. Each tuple represents the name of columns that could be grouped.
        """
        unique_values = self.get_unique_values(col)
        clean_unique_values = self.get_cleaned_values(unique_values)

        values_count = clean_unique_values.value_counts()

        # find the ones occuring more than once
        duplicated_values = list(values_count[values_count > 1].index)

        # go back into lower_values to find index of duplicata and their original value
        all_to_group = []
        for duplicata in duplicated_values:
            to_group = unique_values[clean_unique_values == duplicata]
            all_to_group.append(tuple(to_group))

        return all_to_group


    def get_groupings_acronym(self, col:pd.Series) -> list:
        """
        Gets groupings of values contained un "col" that are identified as being acronyms for one another. E.g. "hs" and "high school"

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :return: list. Each element is a tuple of two strings. Each tuple represents the name of columns that could be grouped.
        """
        value = self.get_unique_values(col)
        value_lower = self.get_cleaned_values(value)
        df_info = pd.DataFrame({"value": value, "value_lower": value_lower})
        df_info["value_initial"] = df_info["value"].apply(lambda x: ''.join(i[0] for i in x.split()))
        df_info["value_initial_lower"] = df_info["value_lower"].apply(lambda x: ''.join(i[0] for i in x.split()))


        # find initials that could only come from one value
        init_lower_count = df_info["value_initial_lower"].value_counts()
        init_not_shared = list(init_lower_count[init_lower_count == 1].index)
        df_not_shared = df_info[df_info["value_initial_lower"].isin(init_not_shared)]

        # look into the values if the not shared intials are in it
        to_group = []
        for index, not_shared in df_not_shared.iterrows():
            for index_2, row in df_info.iterrows():
                if not_shared["value_initial_lower"] == row["value_lower"]:
                    to_group.append((row["value"], not_shared["value"]))

        return to_group


    def get_groupings_first_letter_of_another_value(self, col: pd.Series) -> list:
        """
        Gets groupings of values contained un "col" that are identified as being the first letter of another. E.g. "f" and "female"

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :return: list. Each element is a tuple of two strings. Each tuple represents the name of columns that could be grouped.
        """
        values = self.get_unique_values(col)
        unique_clean_values = list(self.get_cleaned_values(values))

        # find values that are a single letter
        just_one_letter = []
        for value in unique_clean_values:
            if len(value) == 1:
                just_one_letter.append(value)

        starts_with = {k: [] for k in just_one_letter}

        # find the other values that start with those single letter
        for letter in just_one_letter:
            for value in unique_clean_values:
                if value[0] == letter and value != letter:
                    starts_with[letter].append(value)

        # if there is only one other value that starts with that letter, clearly someone was lazy and simply type "m" instead of "male"
        # otherwise (more than one value with this start letter) we cannot conclude
        to_group = []
        for letter in starts_with.keys():
            if len(starts_with[letter]) == 1:
                to_group.append((letter, starts_with[letter][0]))

        return to_group


    def get_levenshtein_close_values(self, col: pd.Series, threshold=85) -> list:
        """
        Gets groupings of values contained un "col" that are identified as being close to one another. E.g. "Montreal" and "Montrea"

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :param threshold: int. Must be between 0 and 100. Threshold from which it is decided if two values are "similar" or not.
        :return: list. Each element is a tuple of two strings. Each tuple represents the name of columns that could be grouped.
        """
        values = self.get_unique_values(col)

        pairs_of_values = list(itertools.combinations(values, 2))
        high_score_pairs = []
        for pair in pairs_of_values:
            # .lower() could be replace by any pre-processing. Ideally, a copy of the pre-processed and original values should be kept everywhere
            # would allow to have access to pre-processed values for comparison, WHILE always knowing it was associated with what original value
            # Hence, can always know when something similar is found what original value it maps to.
            this_score = fuzz.ratio(pair[0].lower(), pair[1].lower())
            if this_score >= threshold:
                high_score_pairs.append(pair)
        return high_score_pairs


    # to apply only on values with more than one word
    # not optimized, but we can always repeat it
    # other way of doing levenhstein distance comparaison could be:
    # 1. you just compare with values "after" you in the list
    # 2. once you are tagged as "similar to someone", you are not comparing yourself afterwards (you are known and have been attributed to a group, that's it, it's over for you)
    def get_partial_levenshtein_close_values(self, col: pd.Series, threshold: int=85) -> list:
        """
        Gets groupings of values contained un "col" that are identified as being close to one another, with partial Levenshtein metric.
        E.g. "Toronto Raptors" and "Raptors". Any string fully contained in another string will be flagged as 100 similar with partial levenshtein metric.

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :param threshold: int. Must be between 0 and 100. Threshold from which it is decided if two values are "similar" or not.
        :return: list. Each element is a tuple of two strings. Each tuple represents the name of columns that could be grouped.
        """
        values = self.get_unique_values(col)
        values_with_more_than_one_letter = values[values.str.len() > 1]
        values_with_more_than_one_word = values[values.str.contains(r" ")]

        # making sure that partial is only applied when multiple words
        # otherwise, something like "female" and "male" would get a score of 100 and be merged
        if values_with_more_than_one_word.empty:
            return []

        pairs_of_values = list(itertools.combinations(values_with_more_than_one_letter, 2))
        high_score_pairs = []
        for pair in pairs_of_values:

            this_score = fuzz.partial_ratio(pair[0].lower(), pair[1].lower())

            if this_score >= threshold:
                high_score_pairs.append(pair)

        return high_score_pairs


    def group_values_max_length(self, col: pd.Series, values_to_group: list=[] ) -> pd.Series:
        """
        Groups values passed into a single new value. E.g., if values_to_group is ["f", "female"], all "f" in "col" will be replaced by "female".
        Chooses the longest value in "values_to_group" as the value for all values mentioned in "values_to_group"

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :param values_to_group: list. Each element is a tuple, containing values that needs to be grouped under the same value.
        :return: pd.Series. Column where all values mentioned in "values_to_group" now have the same value.
        """
        new_col = copy.deepcopy(col)
        if values_to_group:
            # let's use the value with the most letters as the umbrella name (heuristic for the moment, intent is to avoid losing too much info)
            # (deciding that new name in a smart way is a problem to solve on
            for group in values_to_group:
                new_name = max(group, key=len).lower()
                new_col.loc[col.isin(group)] = new_name
                print("values " + str(group) + "have been grouped under the value \'"+ str(new_name) + "\' for column '"+ str(col.name) + "'")
        return new_col


    def group_values_min_length(self, col: pd.Series, values_to_group: list) -> pd.Series:
        """
        Currently not used by any other method from the class.
        Groups values passed into a single new value. E.g., if values_to_group is ["f", "female"], all "f" in "col" will be replaced by "f".
        Chooses the smallest value in "values_to_group" as the value for all values mentioned in "values_to_group"

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :param values_to_group: list. Each element is a tuple, containing values that needs to be grouped under the same value.
        :return: pd.Series. Column where all values mentioned in "values_to_group" now have the same value.
        """
        if values_to_group:
            # let's use the value with the most letters as the umbrella name (heuristic for the moment, intent is to avoid losing too much info)
            # (deciding that new name in a smart way is a problem to solve on
            new_col = copy.deepcopy(col)
            for group in values_to_group:
                new_name = min(group, key=len).lower()
                new_col.loc[col.isin(group)] = new_name
            return new_col


    def group_values_max_frequency(self, col: pd.Series, values_to_group: list) -> pd.Series:
        #TODO, most likely how tableau prep chooses their new name
        """
        Currently not used by any other method from the class.
        Groups values passed into a single new value. E.g., if "col" is ["f", "female", "female", "male"].
        and "values_to_group" is [("f", "female")], all "f" in "col" will be replaced by "female."
        Chooses the most frequent value in "values_to_group" as the value for all values mentioned in "values_to_group".
        """
        return None


    def get_cleaned_column(self, col:pd.Series) -> pd.Series:
        """
        Groups all values that are similar in "col" into a single value. Applies many different rules to identify similar values.

        :param col: pd.Series. A single column (feature). Assumed to contain strings.
        :return: pd.Series. Identical to "col", to the exception that all similar values as been grouped in a single value.
        """
        # basic
        basic_groupings = self.get_basic_groupings(col)
        col = self.group_values_max_length(col, basic_groupings)

        # levenshtein complete string
        values = col.unique()
        condition = True
        while condition:
            leven_groupings = self.get_levenshtein_close_values(col)
            col = self.group_values_max_length(col, leven_groupings)
            new_values = col.unique()

            if set(new_values) == set(values):
                condition = False
            else:
                values = new_values

        # levenshtein partial/substrings
        values = col.unique()
        condition = True
        while condition:
            leven_partial_groupings = self.get_partial_levenshtein_close_values(col)
            col = self.group_values_max_length(col, leven_partial_groupings)
            new_values = col.unique()

            if set(new_values) == set(values):
                condition = False
            else:
                values = new_values

        # acronym groupings
        acronym_groupings = self.get_groupings_acronym(col)
        col = self.group_values_max_length(col, acronym_groupings)

        # edge case of acronym
        # TO APPLY LAST BECAUSE MUST HAVE ONLY ONE STARTING WITH THIS LETTER
        # will group "f" and "female" if no other value starts with "f" other than "female"
        first_letter_groupings = self.get_groupings_first_letter_of_another_value(col)
        col = self.group_values_max_length(col, first_letter_groupings)

        return col

    @telemetry_service.track_function_executed("get_cleaned_df")
    def get_cleaned_df(self) -> pd.DataFrame:
        """
        For each column identified as categorical with strings, will group similar values under a single value.
        Uses self.df as the original DataFrame that needs cleaning.

        :return: pd.DataFrame. A DataFrame based on self.df where similar values are be grouped under a single value.
        """
        new_df = copy.deepcopy(self.df)
        features = self.get_string_categorical_features()
        for feat in features:
            new_df[feat] = self.get_cleaned_column(self.df[feat])

        return new_df
