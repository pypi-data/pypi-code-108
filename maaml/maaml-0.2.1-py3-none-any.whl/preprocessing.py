import pkg_resources
import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    MaxAbsScaler,
    RobustScaler,
    QuantileTransformer,
    PowerTransformer,
    Normalizer,
)


class DataPreprocessor:
    """[summary]
    A class for Data preprocessing specialized in time series data analysis from dataframes
    """

    def __init__(
        self,
        data_path="",
        specific_data=None,
        target_name="target",
        dataset=None,
        scaler="0",
        droped_columns=["Timestamp (seconds)"],
        no_encoding_columns=[],
        no_scaling_columns=["target"],
        window_size=0,
        step=0,
        average_window=False,
        from_csv=True,
        save_dataset=False,
        name_saved_dataset="Dataset",
        verbose=0,
    ):
        if dataset is None or isinstance(dataset, str):
            if from_csv is True:
                if dataset in [
                    "UAHdataset",
                    "uahdataset",
                    "UAHDataset",
                    "UAHDATASET",
                    "uah",
                    "UAH",
                ]:
                    self.raw_dataset = self.uahdataset_loading(
                        data_path, specific=specific_data, verbose=verbose
                    )
                else:
                    try:
                        self.raw_dataset = pd.read_csv(data_path)
                        if verbose == 1:
                            print(
                                "Reading data from provided path to the data csv file"
                            )
                    except Exception:
                        print("\nError reading data, verify the provided path")
        else:
            self.raw_dataset = dataset
            if verbose == 1:
                print("Reading from the dataset argement the provided dataframe")
        self.filtered_dataset = self.raw_dataset.drop(labels=droped_columns, axis=1)
        self.numeric_dataset = self.filtered_dataset.copy(deep=True)
        for column in self.numeric_dataset.columns:
            if (
                self.numeric_dataset.dtypes[column] != float
                and self.numeric_dataset.dtypes[column] != int
            ):
                if column in no_encoding_columns:
                    if verbose == 1:
                        print(
                            f"skipping \033[1m{column}\033[0m label encoding for being in the no_encoding_columns"
                        )
                else:
                    self.numeric_dataset = self.label_encoding(
                        self.numeric_dataset, target=column, verbose=verbose
                    )
        self.scaled_dataset, self.scaler_name = self.data_scaling(
            self.numeric_dataset,
            excluded_axis=no_scaling_columns,
            scaler=scaler,
            verbose=verbose,
        )
        self.ml_dataset = self.scaled_dataset
        self.features = self.ml_dataset.drop(target_name, axis=1)
        self.target_column = self.ml_dataset[target_name]
        self.target = self.one_hot_encoding(
            self.ml_dataset, target=target_name, verbose=verbose
        )
        self.preprocessed_dataset = self.ml_dataset.copy(deep=True)
        for i in self.target.columns:
            column_name = f"target {i}"
            self.preprocessed_dataset[column_name] = self.target[i]
        if window_size > 0:
            if verbose == 1:
                print(
                    "\n\033[1mThe window steeping can take some time depending on the dataset (for UAHDataset, it is between 1 to 5 minutes)\033[0m"
                )
            self.windowed_dataset = self.ml_dataset.copy(deep=True)
            self.windowed_dataset = self.window_stepping(
                self.windowed_dataset,
                window_size=window_size,
                step=step,
                average_window=average_window,
                verbose=verbose,
            )
            self.windowed_ml_dataset = self.windowed_dataset
            self.windowed_features = self.windowed_ml_dataset.drop(target_name, axis=1)
            self.windowed_target_column = self.windowed_ml_dataset[target_name]
            self.windowed_target = self.one_hot_encoding(
                self.windowed_ml_dataset, target=target_name, verbose=verbose
            )
            self.windowed_preprocessed_dataset = self.windowed_ml_dataset.copy(
                deep=True
            )
            for i in self.windowed_target.columns:
                column_name = f"target {i}"
                self.windowed_preprocessed_dataset[column_name] = self.windowed_target[
                    i
                ]
        if save_dataset == True:
            NEW_PATH = "preprocessed_dataset"
            if not os.path.exists(NEW_PATH):
                os.makedirs(NEW_PATH)
            self.ml_dataset.to_csv(
                f"{NEW_PATH}/Preprocessed_ml_{name_saved_dataset}.csv",
                index=False,
            )
            self.preprocessed_dataset.to_csv(
                f"{NEW_PATH}/Preprocessed_{name_saved_dataset}.csv", index=False
            )
            if window_size > 0:
                self.windowed_ml_dataset.to_csv(
                    f"{NEW_PATH}/Windowed_preprocessed_ml_{name_saved_dataset}.csv",
                    index=False,
                )
                self.windowed_preprocessed_dataset.to_csv(
                    f"{NEW_PATH}/Windowed_preprocessed_{name_saved_dataset}.csv",
                    index=False,
                )
            if verbose == 1:
                print(
                    f"\n\033[1mPREPROCESSED DATASETS ARE SAVED IN THIS DIRECTORY : {os.getcwd()}/{NEW_PATH}/ \nWith the name similar to: Preprocessed_{name_saved_dataset}.csv  \033[0m\n"
                )

    @staticmethod
    def uahdataset_loading(path="", specific=None, verbose=1):
        if path == "":
            DATA_PATH = pkg_resources.resource_filename(
                __name__, "Datasets/UAH_dataset/dataset/UAHDataset.csv"
            )
            print(f"\nloading the internal \033[1mUAHDataset\033[0m from maaml\n")
            data = pd.read_csv(DATA_PATH)
        else:
            try:
                data = pd.read_csv(path)
                if verbose == 1:
                    print("\nUAHDataset read successfully\n")
            except Exception:
                print("\nERROR: bad path entry\nEmpty data variable returned")
                data = []
                return data
        if specific is None:
            data_info = "full data loaded successfully\n"
        elif str(specific) == "secondary road" or str(specific) == "":
            data = data.loc[data["road"] == "secondary"]
            data = data.drop("road", axis=1)
            data_info = "data of secondary road loaded successfully"
        elif str(specific) == "motorway road" or str(specific) == "0":
            data = data.loc[data["road"] == "motorway"]
            data = data.drop("road", axis=1)
            data_info = "data of motorway road loaded successfully"
        elif int(specific) < 7:
            data = data.loc[data["driver"] == int(specific)]
            data = data.drop("driver", axis=1)
            data_info = f"data of driver number {int(specific)} loaded successfully \n"
        else:
            print(
                "ERROR: wrong specific entry or specific entry does not exist\nEmpty data returned "
            )
            data = []
        if verbose == 1:
            print(data_info)
        return data

    @staticmethod
    def label_encoding(data, target, verbose=1):
        encoder = LabelEncoder()
        df = pd.DataFrame(data)
        try:
            if verbose == 1:
                print(
                    f"encoding the \033[1m{target}\033[0m column. The target labels are: {data[target].unique()} "
                )
            df[target] = encoder.fit_transform(data[target])
            if verbose == 1:
                print(f"The target labels after encoding : {df[target].unique()}")
        except Exception:
            print(
                f"ERROR: the column name '{target}' is not available in data\nno label encoding realized for this target\n"
            )
        return data

    @staticmethod
    def data_scaling(data, excluded_axis=[], scaler="minmax", verbose=1):
        scaled_df = data
        scaled_df = scaled_df.drop(excluded_axis, axis=1)
        columns_names_list = scaled_df.columns
        scaler = str(scaler)
        if scaler == "0" or scaler == "raw_data":
            scaler_name = "RawData (no scaling)"
            scaled_df = pd.DataFrame()
            for column in data.columns:
                scaled_df[column] = data[column].astype("float")
                scaled_df = scaled_df.reset_index(drop=True)
            scaled_df = scaled_df.fillna(0)
            if verbose == 1:
                print(f"data was not scaled, returned: {scaler_name}")
            return scaled_df, scaler_name
        elif scaler == "1" or scaler == "minmax":
            scalerfunction = MinMaxScaler()
            scaler_name = "MinMaxscaler"
        elif scaler == "2" or scaler == "standard":
            scalerfunction = StandardScaler()
            scaler_name = "Standardscaler"
        elif scaler == "3" or scaler == "maxabs":
            scalerfunction = MaxAbsScaler()
            scaler_name = "MaxAbsScaler"
        elif scaler == "4" or scaler == "robust":
            scalerfunction = RobustScaler()
            scaler_name = "RobustScaler"
        elif scaler == "5" or scaler == "quantile_normal":
            scalerfunction = QuantileTransformer(output_distribution="normal")
            scaler_name = "QuantileTransformer using normal distribution"
        elif scaler == "6" or scaler == "quantile_uniform":
            scalerfunction = QuantileTransformer(output_distribution="uniform")
            scaler_name = "QuantileTransformer using uniform distribution"
        elif scaler == "7" or scaler == "power_transform":
            scalerfunction = PowerTransformer(method="yeo-johnson")
            scaler_name = "PowerTransformer using the yeo-johnson method"
        elif scaler == "8" or scaler == "normalizer":
            scalerfunction = Normalizer()
            scaler_name = "Normalizer"
        else:
            print("\nERROR: wrong data entry or wrong scaler type\ninput data returned")
            scaler_name = "Worning : No scaling (something went wrong)"
            return data, scaler_name
        scaled_df = scalerfunction.fit_transform(scaled_df)
        scaled_df = pd.DataFrame(scaled_df, columns=columns_names_list)
        for i in excluded_axis:
            scaled_df[i] = data[i]
        scaled_df = scaled_df.fillna(0)
        if verbose == 1:
            print(f"data scaled with the {scaler_name}")
        return scaled_df, scaler_name

    @staticmethod
    def one_hot_encoding(data, target="target", verbose=1):
        encoder = OneHotEncoder()
        try:
            if verbose == 1:
                print(f"One Hot Encoder target: {data[target].unique()}")
            encoded = encoder.fit_transform(
                data[target].values.reshape(-1, 1)
            ).toarray()
        except Exception:
            try:
                if verbose == 1:
                    print(f"One Hot Encoder target: {data.unique()}")
                encoded = encoder.fit_transform(data.values.reshape(-1, 1)).toarray()
            except Exception:
                if verbose == 1:
                    print(
                        f"ERROR: target name '{target}' is not available in data\nNo One hot encoding realized"
                    )
                return data
        if verbose == 1:
            print(f"example of the target after One Hot encoding : {encoded[0]}")
        df = pd.DataFrame(encoded)
        return df

    @staticmethod
    def window_stepping(
        data=[], window_size=0, step=0, average_window=False, verbose=1
    ):
        segment = []
        final_data = pd.DataFrame()
        if len(data) != 0:
            if window_size == 0:
                final_data = data
                if verbose == 1:
                    print("\nATTENTION: Entry data returned without window stepping")
                return final_data
            else:
                if average_window is True:
                    if verbose == 1:
                        print("\nAverage window applied")
                    for i in range(0, len(data) - 1, step):
                        segment = data[i : i + window_size]
                        row = segment.mean()
                        final_data = final_data.append(row, ignore_index=True)
                else:
                    for i in range(0, len(data) - 1, step):
                        window = data[i : i + window_size]
                        final_data = final_data.append(window, ignore_index=True)
                    if verbose == 1:
                        print(
                            f"\nwindow stepping applied with window size: {window_size} and step : {step}"
                        )
        else:
            final_data = []
            print("ERROR: Empty data entry")
        return final_data


if __name__ == "__main__":
    preprocessor = DataPreprocessor(
        dataset="UAHdataset",
        no_encoding_columns=[],
        scaler=2,
        window_size=60,
        step=10,
        verbose=1,
        save_dataset=False,
    )
    print(f"\nthe raw dataset is: \n{preprocessor.raw_dataset}")
    print(f"\nthe dataset(after dropping columns) is\n{preprocessor.filtered_dataset}")
    print(f"the label encoded dataset: \n{preprocessor.numeric_dataset}")
    print(f"The used scaler is: {preprocessor.scaler_name}")
    print(f"\nthe scaled dataset is: \n{preprocessor.scaled_dataset}")
    print(f"\nthe dataset features are: \n{preprocessor.features}")
    print(f"\nthe dataset target column is: \n{preprocessor.target_column}")
    print(f"\nthe dataset one hot encoded target is: \n{preprocessor.target}")
    print(f"\nthe full preprocessed dataset is: \n{preprocessor.preprocessed_dataset}")
    print("\n ******* windowed data ******* \n")
    print(f"\nthe dataset windowed features are: \n{preprocessor.windowed_features}")
    print(
        f"\nthe dataset windowed target column is: \n{preprocessor.windowed_target_column}"
    )
    print(
        f"\nthe dataset windowed one hot encoded target is: \n{preprocessor.windowed_target}"
    )
    print(
        f"\nthe full windowed preprocessed dataset is: \n{preprocessor.windowed_preprocessed_dataset}"
    )
