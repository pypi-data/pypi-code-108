import os
import pandas as pd


class DataReader:
    def __init__(self, path, delimiter=" "):
        self.path = path
        self.data = pd.read_table(path, header=None, delimiter=delimiter)


class DataCleaner:
    def __init__(
        self,
        data,
        merge_data=None,
        average_window=True,
        window_size=0,
        step=0,
        add_columns_dictionnary: dict = None,
        save_dataset=False,
        name_dataset="dataset",
        timestamp_column="Timestamp (seconds)",
        verbose=0,
    ):
        self.data_raw = data
        self.data_filtered = data.drop_duplicates(subset=[timestamp_column])
        self.average_window = average_window
        self.window_size = window_size
        self.step = step
        self.data_windowed = self.window_stepping(
            self.data_filtered,
            average_window=average_window,
            window_size=window_size,
            step=step,
            verbose=verbose,
        )
        if merge_data is not None:
            self.data_merged = self.dataframes_merging(
                self.data_windowed,
                merge_data,
                timestamp_column=timestamp_column,
                drop_duplicates=average_window,
                verbose=verbose,
            )
        else:
            self.data_merged = self.data_windowed
        self.data_interpolated = self.data_interpolating(
            self.data_merged, timestamp_columns=timestamp_column, verbose=verbose
        )
        self.dataset = self.removing_incomplete_raws(
            self.data_interpolated, verbose=verbose
        )
        if add_columns_dictionnary is not None:
            self.dataset = self.column_adding(
                self.dataset,
                add_columns_dictionnary=add_columns_dictionnary,
                verbose=verbose,
            )
        if save_dataset == True:
            NEW_PATH = "dataset"
            if not os.path.exists(NEW_PATH):
                os.makedirs(NEW_PATH)
            self.dataset.to_csv(f"{NEW_PATH}/{name_dataset}.csv", index=False)

    @staticmethod
    def window_stepping(data=[], window_size=0, step=0, average_window=True, verbose=1):
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

    @staticmethod
    def dataframes_merging(
        data=[],
        new_data=[],
        timestamp_column="Timestamp (seconds)",
        drop_duplicates=True,
        verbose=1,
    ):
        try:
            while data.dtypes[timestamp_column] != "int64":
                if verbose == 1:
                    print(
                        "\nWarning: data Timestamp type is: ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
                data = data.astype({timestamp_column: "int"})
                if verbose == 1:
                    print(
                        "data timestamp type changed to : ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
            while new_data.dtypes[timestamp_column] != "int64":
                if verbose == 1:
                    print(
                        "Warning: new_data Timestamp type is: ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
                new_data = new_data.astype({timestamp_column: "int"})
                if verbose == 1:
                    print(
                        "new_data timestamp type changed to : ",
                        new_data.dtypes[timestamp_column],
                        "\n",
                    )
            if drop_duplicates is True:
                data = data.drop_duplicates([timestamp_column])
                new_data = new_data.drop_duplicates([timestamp_column])
            data_merged = data.set_index(timestamp_column).join(
                new_data.set_index(timestamp_column)
            )
            data_merged = data_merged.reset_index()
            if verbose == 1:
                print(f"Shape of the megred data: {data_merged.shape}\n")
                print("\033[1m", "******* DATA SUCCESSFULLY MERGED *******", "\033[0m")
        except Exception:
            print(
                "ERROR: empty data entries or one data entry or both do not have Timestamp column, \nplease renter your two dataframes and check their columns before entry "
            )
            print("\nEmpty data returned")
            data_merged = []
        return data_merged

    @staticmethod
    def data_interpolating(
        data=[], timestamp_columns=["Timestamp (seconds)"], verbose=1
    ):
        try:
            if verbose == 1:
                print(
                    f"\n    State before interpolation    \nCOLUMNS                   NUMBER OF RAWS WITH MISSING DATA\n{data.isnull().sum()}\n"
                )
            if data.isnull().values.any() == True:
                if verbose == 1:
                    print("\n       Executing interpolation     \n")
                missing_values = data.drop(timestamp_columns, axis=1)
                missing_values = missing_values.interpolate(method="cubic", limit=3)
                data[missing_values.columns] = missing_values
                data_interpolated = data
                if verbose == 1:
                    print(
                        f"\n    State after interpolation    \nCOLUMNS                   NUMBER OF RAWS WITH MISSING DATA\n{data_interpolated.isnull().sum()}\n"
                    )
            else:
                data_interpolated = data
                if verbose == 1:
                    print("\n   Interpolation not needed    \n")
        except Exception:
            data_interpolated = []
            print(
                f"{data_interpolated}\nERROR: empty data entry or non dataframe type\nEmpty data returned"
            )
        return data_interpolated

    @staticmethod
    def removing_incomplete_raws(data=[], verbose=1):
        try:
            if verbose == 1:
                print(
                    f"\n    Data count before removing any rows :     \n{data.count()}"
                )
                print(
                    "\nis there any missing data values? :",
                    "\033[1m",
                    data.isnull().values.any(),
                    "\033[0m",
                )
            data = data.dropna()
            data = data.reset_index(drop=True)
            if verbose == 1:
                print(f"\n  Final Data count :     \n{data.count()}")
                print(
                    "\nis there any missing data values? :",
                    "\033[1m",
                    data.isnull().values.any(),
                    "\033[0m",
                )
        except Exception:
            print(
                "ERROR: empty data entry or non dataframe type, please enter your data dataframe\nEmpty data returned"
            )
            data = []
        return data

    @staticmethod
    def column_adding(
        data,
        column_name: str = None,
        value: str = None,
        add_columns_dictionnary: dict = None,
        verbose=0,
    ):
        if add_columns_dictionnary is None:
            if column_name is not None and value is not None:
                data[column_name] = value
            else:
                data = data
                if verbose == 1:
                    print("\n    No columns added    \n")
        else:
            for key in add_columns_dictionnary:
                try:
                    data[key] = add_columns_dictionnary[key]
                    if verbose == 1:
                        print(f"\nThe '{key}' column was added successfully   \n")
                except ValueError:
                    print(
                        f"\nAbort column adding operation : The '{key}' column length is {len(add_columns_dictionnary[key])}, while the data length {len(data)}\n"
                    )
                    break
        return data


if __name__ == "__main__":
    DATA_DIR_PATH = "/run/media/najem/34b207a8-0f0c-4398-bba2-f31339727706/home/stock/The_stock/dev & datasets/PhD/datasets/UAH-DRIVESET-v1/"
    my_dict = {
        "Timestamp (seconds)": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        "speed": [40, 45, 60, 62, 70, 75, 80, None, 72, 70],
        "loc": [3, 4, 7, 10, None, 15, 17, 20, 24, 27],
        "driver": ["D1", "D1", "D1", "D1", "D2", "D4", None, "D2", "D1", "D5"],
        "target": [
            "normal",
            "normal",
            "normal",
            "agressif",
            "agressif",
            "drowsy",
            "normal",
            "normal",
            "normal",
            "drowsy",
        ],
    }
    data = pd.DataFrame(my_dict)
    cleaning = DataCleaner(
        data,
        add_columns_dictionnary={"axis": [12, 4, 5, 7, 5, 8, 2, 5, 4]},
        verbose=1,
    )
    print(cleaning.data_raw)
    print(cleaning.dataset)
