from kortical.anonymization import _anonymization


def process_df(df, tokenize_columns=None, numeric_columns=None, categorical_columns=None, scramble_column_names=False,
               allow_lower_case_names=True, tokenize_organizations=True, tokenize_time=False, tokenize_locations=True,
               tokenize_numbers=True, normalize_numeric_columns=False):
    # Set default values
    if tokenize_columns is None:
        tokenize_columns = []
    if numeric_columns is None:
        numeric_columns = []
    if categorical_columns is None:
        categorical_columns = []

    return _anonymization.process_df(df, tokenize_columns, numeric_columns, categorical_columns, scramble_column_names,
                                     allow_lower_case_names, tokenize_organizations, tokenize_time, tokenize_locations,
                                     tokenize_numbers, normalize_numeric_columns)


def tokenize(df, columns, allow_lower_case_names=True, tokenize_organizations=True, tokenize_time=False, tokenize_locations=True, tokenize_numbers=True):
    return _anonymization.tokenize(df, columns, allow_lower_case_names, tokenize_organizations, tokenize_time, tokenize_locations, tokenize_numbers)


def normalize(df, columns):
    return _anonymization.normalize(df, columns)


def add_noise(df, columns, percentage=0.02):
    return _anonymization.add_noise(df, columns, percentage)


def jitter(df, columns, percentage_of_population_to_jitter=0.2, percentage_of_standard_deviation=0.1):
    return _anonymization.jitter(df, columns, percentage_of_population_to_jitter, percentage_of_standard_deviation)


def scramble_column_names(df, columns):
    return _anonymization.scramble_column_names(df, columns)