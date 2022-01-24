import os
import pandas as pd


def save_csv(df, path, name, verbose=0, prompt=None):
    """saves a pandas DataFrame to a specific given path with a given name,
    if the entry is not a pandas DataFrame, it gets transformed to a pandas
    DataFrame before saving it

    Args:
        df (pandas.DataFrame or array or numpy.array): A pandas.DataFrame or an array or a numpy.array
        path (str): A string of the path where the file is going to bes saved
        name (str): A string of the name of the saved file without the .csv extention
        verbose (int, optional): An integer of the verbosity of the function can be 0 or 1. Defaults to 0.
        prompt (str, optional): A string of a custom prompt that is going to be displayed instead of the default
            generated prompt in case of verbosity set to 1. Defaults to None.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    if not path.endswith("/"):
        path = path + "/"
    if not os.path.exists(path):
        os.makedirs(path)
    df.to_csv(f"{path}/{name}.csv", index=False)
    if verbose == 1:
        if prompt is None:
            print(
                f"\n\033[1mThe file {name}.csv was saved in the path :\n{os.getcwd()}/{path} \033[0m\n"
            )
        else:
            print(prompt)


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
