import os
import pandas as pd
from module_placeholder.workflows import train, common
from module_placeholder.config import read_config

config = read_config("config.yml")
data_file_name = config['data_file_name']

if __name__ == "__main__":
    df = pd.read_csv(os.path.join("..", "data", data_file_name))
    df_train, df_calibrate, df_test = common.create_train_calibrate_and_test_datasets(df)
    train.train(df_train, df_calibrate, df_test)
