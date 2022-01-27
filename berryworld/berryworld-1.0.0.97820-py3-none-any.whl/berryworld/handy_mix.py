import numpy as np
import pandas as pd
import traceback
import heapq
from difflib import SequenceMatcher
import re


class HandyMix:
    """Class containing several static methods (standalone methods) useful to solve different problems"""

    def flatten_nested_list(self, nested_list):
        """ Converts a nested list to a flat list
        ------------------------------------------
        list_sample = [[1], [2, 3]]
        flatten_nested_list(list_sample)
        ------------------------------------------
        :param nested_list: Nested list to flatten
        :return: Flattened list
        """
        flat_list = []
        # Iterate over all the elements in given list
        for elem in nested_list:
            # Check if type of element is list
            if isinstance(elem, list):
                # Extend the flat list by adding contents of this element (list)
                flat_list.extend(self.flatten_nested_list(elem))
            else:
                # Append the element to the list
                flat_list.append(elem)
        return flat_list

    @staticmethod
    def sql_groupby(data, by_cols, method_agg='sum()', as_index=False):
        """
        This method replicates a SQL Server group by. It avoids pandas.groupby getting rid of rows
        containing null values. This is basically a wrapper to pandas.groupby which creates dummy
        values for those rows so that we can ensure its behaviour is equivalent to the one in SQL Server.
        ------------------------------------------
        df = pd.DataFrame({'col1': ['a', 'b'], 'col2': [1, 2]})
        by_cols = 'col1'
        method_agg = 'count()'

        sql_groupby(df, by_cols, method_agg)
        ------------------------------------------
        :param data: DataFrame to aggregate
        :param by_cols: List of columns to apply the aggregation
        :param method_agg: Aggregation method to use (It must be a string type but it can be any of the
        aggregation methods available for groupby)
        :param as_index: Indicate whether the grouped columns are to become the index of the DataFrame or not
        :return: Aggregated DataFrame
        """
        res = data.copy(deep=True)
        if not isinstance(by_cols, list):
            by_cols = [by_cols]
        typ = []
        for col in by_cols:
            typ.append(type(res[col].iloc[0]))
            res[col] = res[col].astype(str)
        result = eval('res.groupby(by_cols, as_index=' + str(as_index) + ').' + method_agg)
        k = 0
        for col in by_cols:
            result[col] = result[col].astype(typ[k])
            k += 1
        return result

    @staticmethod
    def likely_match(srs, match_str, n_res=1, threshold=False):
        """ Look for the more similar element in a Series to the one provided in match_str. If there is a draw,
        It will pick the first matching elements. Threshold only consider the elements if their likelihood is
        greater than that threshold variable
        ------------------------------------------
        df = pd.DataFrame({'col1': ['bird', 'bire', 'bear'], 'col2': ['blurr', 'blind', 'bill']},)
        srs = df['col1']
        match_str = 'bir'

        mask = likely_match(srs, match_str, threshold=0.8)
        srs.loc[mask].values[0]
        ------------------------------------------
        :param srs: DataFrame column having the elements to match
        :param match_str: String to check against srs
        :param n_res: Number of fuzzy matches to retrieve
        :param threshold: Indicate a minimum threshold to consider an element of srs likely to match match_str
        :return: Boolean mask indicating the more likely element
        """
        comp = []
        for element in srs:
            aux = SequenceMatcher(None, element, match_str)
            comp.append(aux.ratio())

        def grab_n_elem(n, comp):
            max_list = heapq.nlargest(n, comp)
            like_matches = np.array([elem in max_list for elem in comp]).sum()
            if like_matches > n:
                list_ = [elem in max_list for elem in comp]
                k = 0
                for elem in list_:
                    if (elem is True) & (k > n - 1):
                        list_[k] = False
                    k = + 1
                return list_
            else:
                return [elem in max_list for elem in comp]

        if threshold:
            # Return n elements above the threshold
            if any(elem >= threshold for elem in comp):
                return grab_n_elem(n_res, comp)
            else:
                return [False] * comp.__len__()
        else:
            # Return n elements likely to match
            return grab_n_elem(n_res, comp)

    @staticmethod
    def remove_line_chars(input_text, remove_duplicate_white_spaces=False):
        """
        Function to remove \r and \n from a string
        ------------------------------------------
        text_str = "This is a line \n This is another line"
        remove_line_chars(text_str)
        ------------------------------------------
        :param input_text: string to remove \r or \n
        :param remove_duplicate_white_spaces: bool to indicate if duplicates white spaces
        should be remove from input text
        :return: String without the special characters
        """
        text = input_text.splitlines()
        output_text = ''
        for x in text:
            output_text = output_text + str(x)
        output_text = output_text.rstrip().lstrip()

        if remove_duplicate_white_spaces:
            output_text = re.sub(' +', ' ', output_text)

        return output_text

    @staticmethod
    def coalesce(df, col_list=None, col_multipliers=None, col_to_multiply=None):
        """
        Method to apply the COALESCE function as you would do in SQL
        -----------------------------
        a_list = [(10.00, None, None, None),
            (20.00, None, None, None),
            (30.00, None, None, None),
            (40.00, None, None, None),
            (None, 10000.00, None, None),
            (None, 20000.00, None, None),
            (None, 30000.00, None, None),
            (None, 40000.00, None, None),
            (None, None, 15000, 3),
            (None, None, 25000, 2),
            (None, None, 20000, 6),
            (None, None, 14000, 4)]

        df = pd.DataFrame(a_list, columns=['hourly_wage', 'salary', 'commission', 'num_sales'])

        coalesce(df,
                 col_list = ['hourly_wage', 'salary', 'commission', 'num_sales'],
                 col_multipliers = [40 * 52, 1, 1, 1],
                 col_to_multiply = [['num_sales', 'commission']])
        -----------------------------
        :param df: DataFrame to apply the logic
        :param col_list: List of column names in which the method will be applied
        :param col_multipliers: List of numbers indicating which is the
        :param col_to_multiply: List of lists of the columns to multiply
        :return: DataFrame with the function applied
        """

        try:
            aux = df.copy(deep=True)

            if col_list is not None:

                if col_multipliers is not None:

                    if col_to_multiply is not None:
                        aux[col_list] = aux[col_list] * col_multipliers

                        for col in col_to_multiply:
                            aux[str(col)] = aux[col].prod(axis=1, skipna=False)

                        col_flatten = list(set([item for sublist in col_to_multiply for item in sublist]))
                        aux.drop(col_flatten, axis=1, inplace=True)
                        [col_list.remove(col_) for col_ in col_flatten]
                        col_list = aux.columns.tolist()

                        res_col = aux[col_list].sum(axis=1)
                    else:
                        aux[col_list] = aux[col_list] * col_multipliers

                        res_col = aux[col_list].sum(axis=1)
                else:
                    res_col = aux[col_list].sum(axis=1)
            else:
                res_col = aux.sum(axis=1)

            return res_col

        except Exception:
            raise Exception(traceback.format_exc())

    @staticmethod
    def bools2bits(data):
        """
        Method to translate boolean columns to Bits to be inserted in SQL
        ------------------------------------------
        :param data: DataFrame to transform its boolean columns to bit
        :return: DataFrame with its columns translated to bits
        """
        boolean_cols = data.columns[data.dtypes == 'bool']
        for boolean in data.columns:
            if pd.api.types.is_bool_dtype(np.array(data[boolean].dropna().tolist())):
                data[boolean] = data[boolean].apply(lambda x: 1 if x is True else 0)
            if boolean in boolean_cols:
                data[boolean] = data[boolean].apply(lambda x: 1 if x is True else 0)

        return data
