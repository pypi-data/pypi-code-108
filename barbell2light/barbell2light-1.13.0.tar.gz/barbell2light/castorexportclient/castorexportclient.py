import json
import pandas as pd
import numpy as np


class CastorExportClient:

    def __init__(self, show_params=True):
        """
        Constructs instance of this class.
        :param show_params: Whether to print parameters or not (default True)
        """
        self.params = {
            'sheet_name_data': 'Study results',                 # with spaces
            'sheet_name_data_dict': 'Study variable list',      # ''
            'sheet_name_data_options': 'Field options',         # ''
            'data_dict_crf_name': 'Step_name',                  # without spaces because column names are updated
            'data_dict_var_name': 'Variable_name',              # ''
            'data_dict_field_type': 'Field_type',               # ''
            'data_dict_field_label': 'Field_label',             # ''
            'data_dict_option_group_name': 'Optiongroup_name',  # ''
            'data_options_group_name': 'Option_group_name',     # ''
            'data_options_name': 'Option_name',                 # ''
            'data_options_value': 'Option_value',               # ''
            'data_cols_ignore': [
                'Record_Id',                                    # without spaces because column names are updated
                'Institute_Abbreviation',                       # ''
                'Record_Creation_Date',                         # ''
            ],
            'patient_id_field_name': 'dpca_idcode',
            'surgery_date_field_name': 'dpca_datok',
            'data_miss_float': [999, 9999, 99999, 999.0, 9999.0],
            'data_miss_date': ['09-09-1809'],
            'to_pandas': {
                'dropdown': 'Int64',
                'radio': 'Int64',
                'string': 'object',
                'textarea': 'object',
                'remark': 'object',
                'date': 'datetime64[ns]',
                'year': 'Int64',
                'numeric': 'float64',
            }
        }

        if show_params:
            print(json.dumps(self.params, indent=4))

        self.data = None
        self.data_dict = {}
        self.data_options = {}

    @staticmethod
    def remove_spaces(value):
        """
        Removes spaces from given value and replaces them with underscores.
        :param value: Value to process
        :return: Processed value
        """
        return value.replace(' ', '_')

    def to_pandas_type(self, field_type):
        """
        Lookup Pandas data type for given Castor field type.
        :param field_type: Castor field type name
        :return: Corresponding Pandas data type or None if not found
        """
        if field_type in list(self.params['to_pandas'].keys()):
            return self.params['to_pandas'][field_type]
        return None

    def load_data(self, file_path, verbose=False):
        """
        Loads Castor export Excel file containing the data, data dictionary and field options.
        :param file_path: Path to Excel file
        :param verbose: Verbose
        :return: Tuple of data, data dictionary and options
        """
        # Load data dictionary first and remove spaces from columns
        df_data_dict = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data_dict'], dtype='object')
        df_data_dict.columns = map(self.remove_spaces, df_data_dict.columns)

        # Fill missing values with np.nan
        for column in df_data_dict.columns:
            df_data_dict[column] = df_data_dict[column].fillna(np.nan)

        data_dict = {}

        # Add columns to ignore to data dictionary
        for column in self.params['data_cols_ignore']:
            data_dict[column] = {
                'crf_name': '',
                'field_label': column,
                'field_type': 'string',
                'pandas_type': 'object',
                'option_group_name': None,
            }

        # Store field definitions in data dictionary
        for idx, row in df_data_dict.iterrows():
            var_name = row[self.params['data_dict_var_name']]
            if var_name is None or var_name == '' or pd.isna(var_name):
                continue
            data_dict[var_name] = {
                'crf_name': row[self.params['data_dict_crf_name']],
                'field_label': row[self.params['data_dict_field_label']],
                'field_type': row[self.params['data_dict_field_type']],
                'pandas_type': self.to_pandas_type(row[self.params['data_dict_field_type']]),
                'option_group_name': row[self.params['data_dict_option_group_name']],
            }

        self.data_dict = data_dict

        # Load data and remove spaces from columns
        df_data = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data'])
        df_data.columns = map(self.remove_spaces, df_data.columns)

        for column in df_data.columns:

            if column not in self.data_dict.keys():
                continue

            # Check Pandas type
            pandas_type = self.to_pandas_type(self.data_dict[column]['field_type'])

            # Fill with NaN values and create new series according to Pandas type
            df_data[column] = df_data[column].fillna(np.nan)
            df_data[column] = pd.Series(data=df_data[column], dtype=pandas_type)

            # Missing values for floats en dates are specific to Castor data. Let's
            # replace these with either np.nan or pd.NaT
            if pandas_type == 'float64':
                for mv in self.params['data_miss_float']:
                    df_data.loc[df_data[column] == mv, column] = np.nan
            elif pandas_type == 'datetime64[ns]':
                for mv in self.params['data_miss_date']:
                    df_data.loc[df_data[column] == mv, column] = pd.NaT
            else:
                pass

            if verbose:
                print('Processed column {}'.format(column))

        self.data = df_data

        # Load options and remove spaces from columns
        df_data_options = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data_options'], dtype='object')
        df_data_options.columns = map(self.remove_spaces, df_data_options.columns)

        # Fill in missing values
        for column in df_data_options.columns:
            df_data_options[column] = df_data_options[column].fillna(np.nan)

        data_options = {}

        for idx, row in df_data_options.iterrows():

            # Store options in option dictionary
            option_group = row[self.params['data_options_group_name']]
            if option_group not in list(data_options.keys()):
                data_options[option_group] = []
            data_options[option_group].append(
                (int(row[self.params['data_options_value']]), row[self.params['data_options_name']]))

        self.data_options = data_options

        return self.data, self.data_dict, self.data_options

    def find_option_group(self, text=''):
        """
        Finds option groups and corresponding option values for the given (partial) text.
        :param text: (Part of) option name or group name (default='' returns all options groups)
        """
        option_groups = {}
        for option_group, options in self.data_options.items():
            if text.lower() in option_group.lower():
                option_groups[option_group] = options
                continue
            for option in options:
                if text.lower() in option[1].lower():
                    option_groups[option_group] = options
        return option_groups

    def find_variable(self, keys):
        """
        Finds variable definitions that contain <text> in either the name or label. Info returned
        contains: CRF name, field label, field type, Pandas type and option group name (if applicable).
        :param keys: Key or list of keys
        :return: List of variable definitions matching given keys
        """
        if isinstance(keys, str):
            keys = [keys]
        if not isinstance(keys, list):
            print('Keys must be string or list of strings')
        definitions = []
        for name, definition in self.data_dict.items():
            found = False
            for key in keys:
                if key.lower() in name.lower():
                    found = True
                elif key.lower() in definition['field_label'].lower():
                    found = True
                elif key.lower() in definition['crf_name'].lower():
                    found = True
                else:
                    pass
                if found:
                    if not pd.isna(definition['option_group_name']):
                        option_group = self.find_option_group(definition['option_group_name'])
                        definition['options'] = option_group[definition['option_group_name']]
                    definitions.append((name, definition))
        return definitions

    def find_values(self, var_name):
        """
        Finds values for given <var_name>.
        :param var_name: Variable (column) to display values for.
        :return: Pandas series with values
        """
        return self.data[var_name]

    def find_missing(self, in_column, show_columns):
        """
        Finds records with missing values in column <in_column>. Each record is displayed as indicated
        by <show_columns>
        :param in_column: Column that is searched for missing values.
        :param show_columns: List of column names to show when displaying records with missing values.
        :return:
        """
        if isinstance(show_columns, str):
            if not show_columns in self.data.columns:
                print('Column {} not found'.format(show_columns))
                return None
        elif isinstance(show_columns, list) or isinstance(show_columns, tuple):
            for column in show_columns:
                if not column in self.data.columns:
                    print('Column {} not found'.format(show_columns))
                    return None
        else:
            print('Wrong type for show_columns, must be string, list or tuple')
            return None
        missing = self.data[in_column].isnull()
        return self.data.loc[missing == True, show_columns]

    def find_duplicate_records(self, columns):
        """
        Finds duplicate records in the export file based on the given key columns, e.g., you can
        call this function as find_duplicate_records(['dpca_idcode', 'dpca_datok'] to find all
        records that have the same combination of SAP number and surgery date.
        :return: Dictionary with keys that contain more than 1 record.
        """
        for column in columns:
            if not column in self.data.columns:
                print('Could not find column {}'.format(column))
                return {}
        record_counts = {}
        for idx, row in self.data.iterrows():
            key = []
            for column in columns:
                key_item = row[column]
                if self.data[column].dtype == 'datetime64[ns]':
                    key_item = '{}-{}-{}'.format(key_item.year, key_item.month, key_item.day)
                key.append(key_item)
            key = tuple(key)
            if key not in record_counts.keys():
                record_counts[key] = 0
            record_counts[key] += 1
        duplicates = {}
        for key, count in record_counts.items():
            if count > 1:
                duplicates[key] = count
        return duplicates

    def query(self, query_string):
        """
        Run the given query on the Pandas dataframe. If query fails with a value error we try again,
        using the 'python' engine. This seems only to happen when running the query from within
        a Jupyter notebook.

        Example queries:
        ----------------
        Given the column (variable) names 'dob' and 'gender', select all records where dob is earlier than
        01-01-1945 and gender is male. Note: you must lookup the option value for 'male' using the find_option_group
        function, e.g., find_option_group('gender')

            client.query('dob < "01-01-1945" & gender == 1')

        Common query variables:
        -----------------------

        DPCA:
        - dpca_gebdat       Birth date
        - dpca_gebjaar      Year of birth
        - dpca_geslacht     Gender (1: male, 2: female)
        - dpca_typok        Type of surgery procedure
        - dpca_comorb       Comorbidities (0: no, 1: yes)
        - dpca_ovl          Deceased (0: no, 1: yes)
        - dpca_datovl       Date of death
        - dpca_afwijking    Most recent disease diagnosis

        DHBA:
        - dhba_diagnose     Most recent disease diagnosis

        :param query_string: Query string
        :return: Result data frame
        """
        try:
            return self.data.query(query_string)
        except ValueError:
            return self.data.query(query_string, engine='python')


if __name__ == '__main__':
    CastorExportClient()
