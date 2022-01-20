from sklearn.model_selection import train_test_split
from kortical.storage.persistent_cloud_storage import PersistentCloudStorage
from module_placeholder.config import read_config

config = read_config('config.yml')

target = config['target']
not_automated_class = config['not_automated_class']
model_code = r"""
- ml_solution:
  - data_set:
    - target_column: OutcomeType
    - problem_type: classification
    - evaluation_metric: f1_score
    - fraction_of_data_set_to_use: 1
    - time_series:
      - date_time_index: DateTime
      - test_start_date_time: '2015-04-28 15:41:00'
      - test_end_date_time: '2015-08-24 19:54:00'
  - features:
    - numeric:
      - AgeuponOutcome:
        - preprocessing:
          - custom:
            - code: |
              @kortical.signature(input_columns=column_name, output_columns=[column_name, NUMERIC])
              def transform(column_name: str, input_columns: pd.DataFrame, fit_data):
                  age_multiplier_map = {
                          'year': 1,
                          'years': 1,
                          'month': 1/12,
                          'months': 1/12,
                          'week': 1/52,
                          'weeks': 1/52,
                          'day': 1/365,
                          'days': 1/365}
                  def convert_age(age_string):
                      if not isinstance(age_string, str):
                          return age_string
                      x = age_string.split()
                      age = float(x[0])
                      age *= age_multiplier_map[x[1]]
                      return age
                  column = input_columns[column_name].map(convert_age)
                  return {column_name: column}
            - remove_original_column: False
    - categorical:
      - AnimalType
      - SexuponOutcome
      - Breed
      - Color
      - Name_is_null
    - text:
      - Name:
        - preprocessing:
          - custom:
            - code: |
              @kortical.signature(input_columns=column_name, output_columns=[column_name + '_is_null', CATEGORICAL])
              def transform(column_name: str, input_columns: pd.DataFrame, fit_data):
                  column = input_columns[column_name].map(lambda x: pd.isna(x))
                  return {column_name + '_is_null': column}
              
            - remove_original_column: True
    - date:
      - DateTime
  - models:
    - one_of:
      - xgboost
      - linear
      - random_forest
      - extra_trees
      - decision_tree
      - deep_neural_network
      - lightgbm"""


storage = PersistentCloudStorage('automation-template')


def create_train_calibrate_and_test_datasets(df):
    df_train, calibrate_test = train_test_split(df, test_size=.33, random_state=1)
    df_calibrate, df_test = train_test_split(calibrate_test, test_size=.5, random_state=1)
    dataset_map = {
        'train': df_train,
        'calibrate': df_calibrate,
        'test': df_test
    }
    for k, v in dataset_map.items():
        print(f"Dataset {k}: {len(v)} rows")
    return df_train, df_calibrate, df_test


def get_calibration_data_storage_name(model_id):
    return f"calibration_data_{model_id}"


def preprocessing(df):
    # Do custom logic here
    for replace_class in ['Adoption', 'Euthanasia', 'Died']:
        df[target] = df[target].map(lambda x: x.replace(replace_class, not_automated_class))


def postprocessing(df):
    return df