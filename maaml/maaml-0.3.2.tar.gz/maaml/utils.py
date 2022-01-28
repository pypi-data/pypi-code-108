import os
import pandas as pd
import time


def save_csv(df, path, name, verbose=0, prompt=None):
    """saves a csv file from pandas DataFrame to the given path with the given name,
    if the entry is not a pandas DataFrame, it gets transformed to a pandas
    DataFrame before saving it

    Args:
        df (pandas.DataFrame or array or numpy.array): A pandas.DataFrame or an array or a numpy.array
        path (str): A string of the path where the file is going to bes saved
        name (str): A string of the name of the saved file with or without the .csv extention
        verbose (int, optional): An integer of the verbosity of the function can be 0 or 1. Defaults to 0.
        prompt (str, optional): A string of a custom prompt that is going to be displayed instead of the default
            generated prompt in case of verbosity set to 1. Defaults to None.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    if not path.endswith("/"):
        path = path + "/"
    if not name.endswith(".csv"):
        name = name + ".csv"
    if not os.path.exists(path):
        os.makedirs(path)
    df.to_csv(f"{path}/{name}", index=False)
    if verbose == 1:
        if prompt is None:
            print(
                f"\n\033[1mThe file {name}.csv was saved in the path :\n{os.getcwd()}/{path} \033[0m\n"
            )
        else:
            print(prompt)


def save_parquet(df, path, name, verbose=0, prompt=None):
    """saves a parquet file from pandas DataFrame to the given path with the given name,
    if the entry is not a pandas DataFrame, it gets transformed to a pandas
    DataFrame before saving it

    Args:
        df (pandas.DataFrame or array or numpy.array): A pandas.DataFrame or an array or a numpy.array
        path (str): A string of the path where the file is going to bes saved
        name (str): A string of the name of the saved file with or without the .parquet extention
        verbose (int, optional): An integer of the verbosity of the function can be 0 or 1. Defaults to 0.
        prompt (str, optional): A string of a custom prompt that is going to be displayed instead of the default
            generated prompt in case of verbosity set to 1. Defaults to None.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    if not path.endswith("/"):
        path = path + "/"
    if not name.endswith(".parquet"):
        name = name + ".parquet"
    if not os.path.exists(path):
        os.makedirs(path)
    df.to_parquet(f"{path}/{name}", index=False)
    if verbose == 1:
        if prompt is None:
            print(
                f"\n\033[1mThe file {name}.parquet was saved in the path :\n{os.getcwd()}/{path} \033[0m\n"
            )
        else:
            print(prompt)


def read_csv(path, delimiter=" ", header=None, verbose=0, prompt=None):
    df_csv = pd.read_table(path, header=header, delimiter=delimiter)
    if verbose == 1:
        if prompt is None:
            print(
                f"\n\033[1mLoading dataframe from csv file from:\n{os.getcwd()}/{path} \033[0m\n"
            )
        else:
            print(prompt)
    return df_csv


def read_parquet(path, verbose=0, prompt=None):
    df_parquet = pd.read_parquet(path)
    if verbose == 1:
        if prompt is None:
            print(
                f"\n\033[1mLoading dataframe from parquet file from:\n{os.getcwd()}/{path} \033[0m\n"
            )
        else:
            print(prompt)
    return df_parquet


def dict_transpose(dictionary):
    """A fucntion that transposes a dictionary,
    it simply uses the first key and it's values as the new keys and then
     maps the rest of the keys and their values to the newly created keys in the same order of apperance
        Args:
            dictionary (dict): A python dictionary

        Returns:
            dict: A transposed python dictionary
        Exemple:
            >>> d = {
                "classifier": ["SVM","LR","MLP"],
                "scaler": ["Standard", "Standard", "Standard"],
                "exec time": ["75.88(s)", "4.78(s)", "94.89(s)"],
                "accuracy": ["78.5%","53.6%","88.6%"],
                "F1": ["78.6%","53.0%","88.6%"],
                }
            >>> d_transposed = dict_transpose(d)
            >>> d_transposed
                {
                "classifier": ["scaler","exec time","accuracy","F1"],
                "SVM": ["Standard","75.88(s)","78.5%","78.6%"],
                "LR": ["Standard","4.78(s)","53.6%","53.0%"],
                "MLP": ["Standard","94.89(s)","88.6%","88.6%"],
                }
    """
    keys_list = list(dictionary)
    values_list = list(dictionary.values())
    new_dict = {keys_list[0]: keys_list[1:]}
    new_keys = values_list[0]
    for key in new_keys:
        new_dict[key] = []
    for values in values_list[1:]:
        for key, v in zip(new_keys, values):
            new_dict[key].append(v)
    return new_dict


class FileScraper:
    def __init__(self, path, search_list, verbose=0) -> None:
        start_time = time.perf_counter()
        self.parent_path = path
        self.search_list = search_list
        self.searched_list = search_list.copy()
        self.file_scraping(self.parent_path, self.search_list, verbose=verbose)
        self.found_files_count = len(self.path_list)
        self.all_files_count = len(self.all_files)
        end_time = time.perf_counter()
        self.time = f"{end_time-start_time} (s)"
        print(f"Finished searching in {self.time}")
        print(
            f"Total of {self.found_files_count} found from total of {self.all_files_count} existant files"
        )
        if self.searched_list != []:
            print(f"These elements are not found: {self.searched_list}\n")
        else:
            print("*******All search_list elements were found successfully*******\n")

    def __call__(self):
        return self.path_list

    def file_scraping(self, path, search_list, verbose=0):
        files = []
        for text in os.listdir(path):
            if os.path.isdir(os.path.join(path, text)):
                if verbose == 2:
                    print(f"Changing directory to subdirectory: '{text}'")
                dir = os.path.join(path, text)
                localfiles = self.file_scraping(dir, self.search_list, verbose=verbose)
                if verbose == 2:
                    if localfiles != []:
                        print(f"'{text}' files :{localfiles}")
                if localfiles == []:
                    localfiles, dir = files, path
                    if verbose == 2:
                        if localfiles == []:
                            print(f"No files found in the '{text}' directory")
                        else:
                            print(f"Changing directory to main directory:")
                            print(f"'{dir}'\nfiles :{localfiles}")
                for file in localfiles:
                    file_path = os.path.join(dir, file)
                    try:
                        if file not in self.all_files:
                            self.all_files.append(file_path)
                    except AttributeError:
                        self.all_files = [file_path]
                    for picked_file in self.search_list:
                        if file == picked_file:
                            if picked_file in self.searched_list:
                                self.searched_list.remove(picked_file)
                            try:
                                if file_path not in self.path_list:
                                    self.path_list.append(file_path)
                                    if verbose == 1:
                                        print(f"file '{file}' found in: \n{dir}")
                                        print(
                                            "**File path added to the path_list successfully**\n"
                                        )
                            except AttributeError:
                                self.path_list = [file_path]
                                if verbose == 1:
                                    print(f"file '{file}' found in: \n{dir}")
                                    print(
                                        "**Initalization of the path_list with the file path is successful**\n"
                                    )

            elif os.path.isfile(os.path.join(path, text)):
                files.append(text)
        return files


if __name__ == "__main__":
    DATA_DIR_PATH = "/run/media/najem/34b207a8-0f0c-4398-bba2-f31339727706/home/stock/The_stock/dev & datasets/PhD/datasets/UAH-DRIVESET-v1"
    # 'RAW_ACCELEROMETERS.txt' "RAW_GPS.txt",
    file_list = FileScraper(
        DATA_DIR_PATH,
        search_list=["RAW_ACCELEROMETERS.txt", "RAW_GPS.txt", "try"],
        verbose=0,
    )
    print(file_list())
