import pandas as pd
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    MaxAbsScaler,
    RobustScaler,
    QuantileTransformer,
    PowerTransformer,
    Normalizer,
)
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# #  dataset loader function
def dataset_loader(path="", full=True, specific="", verbose=1):
    if path == "":
        print("\nset path to default:", "\ndataset build/UAHdataset.csv\n")
        data = pd.read_csv("dataset build/UAHdataset.csv")
    else:
        try:
            data = pd.read_csv(path)
        except Exception:
            print("\nERROR: bad path entry", "\nReturn empty data")
            print("\nNote: pandas must be imported as pd")
            data = []
            return data
    while full == True:
        data_name = "full data loaded"
        return data
    specific = str(specific)
    if specific == "secondary road" or specific == "":
        data = data.loc[data["road"] == "secondary"]
        data = data.drop("road", axis=1)
        data_name = "secondary road data loaded"
    elif specific == "motorway road" or specific == "0":
        data = data.loc[data["road"] == "motorway"]
        data = data.drop("road", axis=1)
        data_name = "motorway road data loaded"
    elif int(specific) < 7:
        data = data.loc[data["driver"] == int(specific)]
        data = data.drop("driver", axis=1)
        data_name = "driver specific data loaded" + "\ndriver number:" + specific + "\n"
    else:
        print(
            "ERROR: wrong specific entry or specific entry does not exist",
            "\nEmpty data returned ",
        )
        print(
            'Note: Pandas library needed for this function to work and must be loaded as "pd"'
        )
        data = []
    if verbose == 1:
        print(data_name)
    return data


# # label encoding function
def encoding_label(data, target, verbose=1):
    encoder = LabelEncoder()
    df = pd.DataFrame(data)
    try:
        if verbose == 1:
            print("label encoder target: ", data[target].unique())
        df[target] = encoder.fit_transform(data[target])
        if verbose == 1:
            print("target after label encoding : ", df[target].unique())
    except Exception:
        if verbose == 1:
            print(
                f"ERROR: target name '{target}' is not available in data\n",
                f"no label encoding realized for '{target}'\n",
            )
        return data
    return df


# # data normalization function
def sklearn_data_normalizer(data, excluded_axis=[], scaler="minmax", verbose=1):
    normalized = data
    for i in excluded_axis:
        normalized = normalized.drop(i, axis=1)
    reserved_columns = normalized.columns
    scaler = str(scaler)
    if scaler == "0" or scaler == "raw_data":
        normalizer_name = "RawData (no scaling)"
        normalized = pd.DataFrame()
        for column in data.columns:
            normalized[column] = data[column].astype("float")
            normalized = normalized.reset_index(drop=True)
        normalized = normalized.fillna(0)
        if verbose == 1:
            print("data is not normalized, returned:", normalizer_name)
        return normalized, normalizer_name
    elif scaler == "1" or scaler == "minmax":
        scalerfunction = MinMaxScaler()
        normalizer_name = "MinMaxscaler"
    elif scaler == "2" or scaler == "standard":
        scalerfunction = StandardScaler()
        normalizer_name = "Standardscaler"
    elif scaler == "3" or scaler == "maxabs":
        scalerfunction = MaxAbsScaler()
        normalizer_name = "MaxAbsScaler"
    elif scaler == "4" or scaler == "robust":
        scalerfunction = RobustScaler()
        normalizer_name = "RobustScaler"
    elif scaler == "5" or scaler == "quantile_normal":
        scalerfunction = QuantileTransformer(output_distribution="normal")
        normalizer_name = "QuantileTransformer using normal distribution"
    elif scaler == "6" or scaler == "quantile_uniform":
        scalerfunction = QuantileTransformer(output_distribution="uniform")
        normalizer_name = "QuantileTransformer using uniform distribution"
    elif scaler == "7" or scaler == "power_transform":
        scalerfunction = PowerTransformer(method="yeo-johnson")
        normalizer_name = "PowerTransformer using method yeo-johnson"
    elif scaler == "8" or scaler == "normalizer":
        scalerfunction = Normalizer()
        normalizer_name = " sklearn Normalizer"
    else:
        print("\nERROR: wrong entry or wrong scaler type")
        print("\nreturned input data")
        return data
    if verbose == 1:
        print("data normalized with the", normalizer_name)
    normalized = scalerfunction.fit_transform(normalized)
    normalized = pd.DataFrame(normalized, columns=reserved_columns)
    for i in excluded_axis:
        normalized[i] = data[i]
    normalized = normalized.fillna(0)
    return normalized, normalizer_name


# # One hot encoder function
def One_hot_encoder(data, target="target", verbose=1):
    encoder = OneHotEncoder()
    try:
        if verbose == 1:
            print("One Hot Encoder target: ", data[target].unique())
        encoded = encoder.fit_transform(data[target].values.reshape(-1, 1)).toarray()
        if verbose == 1:
            print("example of target after One Hot encoding : ", encoded[0])
    except Exception:
        try:
            print("One Hot Encoder target: ", data.unique())
            encoded = encoder.fit_transform(data.values.reshape(-1, 1)).toarray()
            if verbose == 1:
                print("example of target after One Hot encoding : ", encoded[0])
        except Exception:
            if verbose == 1:
                print(
                    f"ERROR: target name '{target}' is not available in data\n",
                    f"no One hot encoding realized for '{target}'\n",
                )
            return data
    df = pd.DataFrame(encoded)
    return df
