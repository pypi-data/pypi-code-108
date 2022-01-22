#!/usr/bin/env python
# coding: utf-8

# # import libraries
import pandas as pd
import numpy as np
import os
import time
import platform
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
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    roc_auc_score,
)
from keras.layers import (
    Dense,
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dropout,
    BatchNormalization,
    Input,
    Add,
    Activation,
)
from keras.models import Model, load_model, save_model
from sklearn.model_selection import train_test_split, ShuffleSplit
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from matplotlib import pyplot

# ## functions
# ### dataset loader function
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


# ### label encoder function
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


# ### data normalization function
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


# ### One hot encoder function
def One_hot_encoding(data, target="target", verbose=1):
    encoder = OneHotEncoder()
    try:
        if verbose == 1:
            print("One Hot Encoder target: ", data[target].unique())
        encoded = encoder.fit_transform(data[target].values.reshape(-1, 1)).toarray()
    except Exception:
        try:
            if verbose == 1:
                print("One Hot Encoder target: ", data.unique())
            encoded = encoder.fit_transform(data.values.reshape(-1, 1)).toarray()
        except Exception:
            if verbose == 1:
                print(
                    f"ERROR: target name '{target}' is not available in data\n",
                    f"no One hot encoding realized for '{target}'\n",
                )
            return data
    if verbose == 1:
        print("example of target after One Hot encoding : ", encoded[0])
    df = pd.DataFrame(encoded)
    return df


# ### create Deep RCN model function
def create_resnet_model(input_shape=(20, 1, 1), class_nb=3):
    inputs = Input(shape=input_shape, name="input")
    x = Conv2D(60, (4, 4), activation="relu", padding="same", name="conv1_60_4x4")(
        inputs
    )
    x = BatchNormalization(name="batch_norm1")(x)
    x = MaxPooling2D((2, 2), padding="same", name="Max_pool1_2x2")(x)
    x = Dropout(0.2, name="dropout1_0.2")(x)
    x = resnet_block(x, 60, 4)
    x = Conv2D(30, (4, 4), activation="relu", padding="same", name="conv2_30_4x4")(x)
    x = BatchNormalization(name="batch_norm2")(x)
    x = MaxPooling2D((2, 2), padding="same", name="Max_pool2_2x2")(x)
    x = Dropout(0.2, name="dropout2_0.2")(x)
    x = Conv2D(15, (4, 4), activation="relu", padding="same", name="conv3_15_4x4")(x)
    x = BatchNormalization(name="batch_norm3")(x)
    x = MaxPooling2D((2, 2), padding="same", name="Max_pool3_2x2")(x)
    x = Dropout(0.2, name="dropout3_0.2")(x)
    x = Conv2D(8, (4, 4), activation="relu", padding="same", name="conv4_8_4x4")(x)
    x = BatchNormalization(name="batch_norm4")(x)
    x = MaxPooling2D((1, 1), padding="same", name="Max_pool4_1x1")(x)
    x = Flatten(name="Flatten_layer")(x)
    x = Dense(units=224, input_dim=448, activation="relu", name="dense1_448x224")(x)
    x = BatchNormalization(name="batch_norm5")(x)
    outputs = Dense(units=class_nb, activation="softmax", name="dense2_224x10")(x)
    your_model = Model(inputs, outputs, name="your_Conv_model")
    return your_model


def resnet_block(input_data, filters, conv_size):
    x = Conv2D(
        filters, conv_size, activation="relu", padding="same", name="resnet_block1"
    )(input_data)
    x = BatchNormalization(name="resnet_block2")(x)
    x = Conv2D(
        filters, conv_size, activation=None, padding="same", name="resnet_block3"
    )(x)
    x = BatchNormalization(name="resnet_block4")(x)
    x = Dropout(0.2)(x)
    x = Add(name="resnet")([x, input_data])
    x = Activation("relu", name="resnet_activation")(x)
    return x


# ### preprocess the dataset function
def data_preprocessing(
    data, target_name="target", normalization="1", raw_data_entry=True, verbose=1
):
    if raw_data_entry == True:
        data_numeric = encoding_label(
            encoding_label(data, "target", verbose=verbose), "road", verbose=verbose
        ).drop("Timestamp (seconds)", axis=1)
        df, normalizer_name = sklearn_data_normalizer(
            data_numeric, [target_name], normalization, verbose=verbose
        )
    elif raw_data_entry == False:
        df = data
    X = df.drop(target_name, axis=1)
    Y = df[target_name]
    X = np.reshape(X.values, (len(X), X.shape[1], 1, 1))
    Y_origin = df["target"]
    target = df["target"]
    Y = One_hot_encoding(target)
    if verbose == 1:
        print(
            "X shape is :",
            X.shape,
            "\nY shape is :",
            Y.shape,
            "\nY_orgin shape is:",
            Y_origin.shape,
        )
    return X, Y, Y_origin


# ### learning rate custom stepping function
def step_adam(epoch, scheduler_threshold=480, initial_lrate=0.001, second_lrate=0.0001):
    lrate = 0.001
    if epoch > 480:
        lrate = 0.0001
        print("Change in the learning rate, the new learning rate is:", lrate)
    return lrate


# ### model training function
def train_model(
    X,
    Y,
    Y_origin,
    model,
    epochs=600,
    batch_size=60,
    callbacks="best model",
    test_size=0.3,
    opt="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"],
    learning_rate="scheduler",
    scheduler_threshold=480,
    verbose=1,
):
    if callbacks == "best model":
        mc = ModelCheckpoint(
            "best_model.h5", monitor="val_accuracy", save_best_only=True, verbose=2
        )
        if any(c.isdigit() for c in platform.node()) == True:
            mc = ModelCheckpoint(
                "/content/drive/MyDrive/best_model.h5",
                monitor="val_accuracy",
                save_best_only=True,
                verbose=2,
            )
        cb = [mc]
        if learning_rate == "scheduler":
            lrs = LearningRateScheduler(step_adam)
            cb = [mc, lrs]
    elif callbacks == None:
        cb = None
    model.compile(loss=loss, optimizer=opt, metrics=metrics)
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=test_size, random_state=10
    )
    _, _, Yo_train, Yo_test = train_test_split(
        X, Y_origin, test_size=test_size, random_state=10
    )
    start_time = time.time()
    history = model.fit(
        X_train,
        Y_train,
        validation_data=(X_test, Y_test),
        callbacks=cb,
        epochs=epochs,
        batch_size=batch_size,
        verbose=verbose,
    )
    end_time = time.time()
    training_history = history.history
    save_history = pd.DataFrame(training_history).to_csv(
        r"training_history.csv", index=False
    )
    if any(c.isdigit() for c in platform.node()) == True:
        save_history = pd.DataFrame(training_history).to_csv(
            r"/content/drive/MyDrive/training_history.csv", index=False
        )
    if callbacks == "best model":
        try:
            best_model = load_model("/content/drive/MyDrive/best_model.h5")
        except Exception:
            try:
                best_model = load_model("best_model.h5")
            except Exception:
                print(
                    "exception triggered, can't load the saved best model, the best model is the current one"
                )
                best_model = model
    pred = model.predict(X_test, batch_size=batch_size, verbose=1)
    predictions = np.argmax(pred, axis=1)
    train_eval = model.evaluate(X_train, Y_train, verbose=verbose)
    train_score = train_eval[1] * 100
    exec_time = str(format((end_time - start_time), ".2f")) + " (s)"
    acc_score = accuracy_score(Yo_test.values, predictions, normalize=True) * 100
    pres_score = precision_score(Yo_test.values, predictions, average="macro") * 100
    rec_score = recall_score(Yo_test.values, predictions, average="macro") * 100
    f1 = f1_score(Yo_test.values, predictions, average="macro") * 100
    cokap_score = cohen_kappa_score(Yo_test.values, predictions) * 100
    roc_auc = roc_auc_score(Y_test.values, pred) * 100
    scores = [
        "execution time: {}".format(exec_time),
        "train accuracy: %.4f%%" % train_score,
        "accuracy: %.4f%%" % acc_score,
        "precision: %.4f%%" % pres_score,
        "recall: %.4f%%" % rec_score,
        "F1 score: %.4f%%" % f1,
        "cohen kappa: %.4f%%" % cokap_score,
        "roc_auc_score: %.4f%%" % roc_auc,
    ]
    if verbose == 1:
        print(scores)
    return model, best_model, training_history, scores


# ### cros validation evaluation function
def cros_validation_evaluation(
    dataset_path,
    model_fn="create_resnet_model",
    normalization=0,
    target_name="target",
    nb_splits=5,
    epochs=600,
    batch_size=60,
    callbacks="best model",
    test_size=0.3,
    opt="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"],
    learning_rate="scheduler",
    scheduler_threshold=120,
    dataset=None,
    verbose=1,
):
    if type(model_fn) == str:
        model_fn = model_fn + "()"
    else:
        model_fn = str(model_fn) + "()"
    if dataset_path == "" or dataset_path == None:
        if dataset == None:
            print("Empty dataset path and empty dataset entry")
            return None
        data = dataset
    else:
        data = dataset_loader(dataset_path)
    data_numeric = encoding_label(
        encoding_label(data, "target", verbose=verbose), "road", verbose=verbose
    ).drop("Timestamp (seconds)", axis=1)
    df, normalizer_name = sklearn_data_normalizer(
        data_numeric, [target_name], normalization, verbose=verbose
    )
    X_origin = df.drop(target_name, axis=1)
    Y_origin = df[target_name]
    cv = ShuffleSplit(n_splits=nb_splits, test_size=test_size, random_state=10)
    (
        exec_time,
        train_acc_scores,
        acc_scores,
        pres_scores,
        rec_scores,
        f1,
        cokap_scores,
        roc_auc_scores,
    ) = ([], [], [], [], [], [], [], [])
    cv_scores = pd.DataFrame()
    for train, test in cv.split(X_origin, Y_origin):
        print(
            "\033[1m"
            + "\n"
            + "*******"
            + "begin cross validation in fold number:{}".format(
                len(train_acc_scores) + 1
            )
            + "*******"
            + "\033[0m"
        )
        X_train = np.reshape(
            X_origin.loc[train].values,
            (len(X_origin.loc[train]), X_origin.loc[train].shape[1], 1, 1),
        )
        X_test = np.reshape(
            X_origin.loc[test].values,
            (len(X_origin.loc[test]), X_origin.loc[test].shape[1], 1, 1),
        )
        Y_train = One_hot_encoding(Y_origin[train], verbose=0)
        Y_test = One_hot_encoding(Y_origin[test], verbose=verbose)
        if callbacks == "best model":
            mc = ModelCheckpoint(
                "cross_validation/cv_best_model.h5",
                monitor="val_accuracy",
                save_best_only=True,
                verbose=2,
            )
            cb = [mc]
            if learning_rate == "scheduler":
                lrs = LearningRateScheduler(step_adam)
                cb = [mc, lrs]
        elif callbacks == None:
            cb = None
        try:
            cv_model = eval(model_fn)
        except Exception:
            print(
                "Error: model function variable is bad entry, please pass the name of your model building function as string in the variable: model_fn"
            )
            return
        newpath = "cross_validation"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        cv_model.compile(loss=loss, optimizer=opt, metrics=metrics)
        start_time = time.time()
        history = cv_model.fit(
            X_train,
            Y_train,
            validation_data=(X_test, Y_test),
            callbacks=cb,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
        )
        end_time = time.time()
        training_history = history.history
        save_history = pd.DataFrame(training_history).to_csv(
            r"cross_validation/training_history{}.csv".format(
                len(train_acc_scores) + 1
            ),
            index=False,
        )
        if callbacks == "best model":
            try:
                best_model = load_model("cross_validation/cv_best_model.h5")
            except Exception:
                print(
                    "exception triggered, can't load the saved best model, the best model is the current one"
                )
                best_model = cv_model
        elif callbacks == None:
            best_model = cv_model
        save_model(
            best_model,
            "cross_validation/cv_best_model{}.h5".format(len(train_acc_scores) + 1),
        )
        pred = cv_model.predict(X_test, batch_size=batch_size, verbose=0)
        predictions = np.argmax(pred, axis=1)
        exec_time.append((end_time - start_time))
        train_acc_scores.append(
            cv_model.evaluate(X_train, Y_train, verbose=verbose)[1] * 100
        )
        acc_scores.append(
            accuracy_score(Y_origin[test].values, predictions, normalize=True) * 100
        )
        pres_scores.append(
            precision_score(Y_origin[test].values, predictions, average="macro") * 100
        )
        rec_scores.append(
            recall_score(Y_origin[test].values, predictions, average="macro") * 100
        )
        f1.append(f1_score(Y_origin[test].values, predictions, average="macro") * 100)
        cokap_scores.append(cohen_kappa_score(Y_origin[test].values, predictions) * 100)
        roc_auc_scores.append(roc_auc_score(Y_test.values, pred) * 100)
    scores = [
        "precision: %.4f%% (+/- %.4f%%)" % (np.mean(pres_scores), np.std(pres_scores)),
        "recall: %.4f%% (+/- %.4f%%)" % (np.mean(rec_scores), np.std(rec_scores)),
    ]
    cv_scores["metrics"] = [
        "preprocessing",
        "execution time",
        "training accuracy",
        "accuracy",
        "precision",
        "recall",
        "F1",
        "cohen_kappa",
        "roc_auc",
    ]
    _, model_name = model_fn.split("_", 1)
    cv_scores[model_name.replace("()", "")] = [
        normalizer_name,
        str(format(np.mean(exec_time), ".2f")) + " (s)",
        "%.4f%% (+/- %.4f%%)" % (np.mean(train_acc_scores), np.std(train_acc_scores)),
        "%.4f%% (+/- %.4f%%)" % (np.mean(acc_scores), np.std(acc_scores)),
        "%.4f%% (+/- %.4f%%)" % (np.mean(pres_scores), np.std(pres_scores)),
        "%.4f%% (+/- %.4f%%)" % (np.mean(rec_scores), np.std(rec_scores)),
        "%.4f%% (+/- %.4f%%)" % (np.mean(f1), np.std(f1)),
        "%.4f%% (+/- %.4f%%)" % (np.mean(cokap_scores), np.std(cokap_scores)),
        "%.4f%% (+/- %.4f%%)" % (np.mean(roc_auc_scores), np.std(roc_auc_scores)),
    ]
    cv_scores.to_csv(
        r"cross_validation/cross_validation_scores_{}.csv".format(normalizer_name),
        index=False,
    )
    return cv_scores


# ### learning rate visualization function
def plot_learning_rate(
    training_history, save=False, metric="accuracy", style="default"
):
    styles = [
        "seaborn-poster",
        "seaborn-bright",
        "Solarize_Light2",
        "seaborn-whitegrid",
        "_classic_test_patch",
        "seaborn-white",
        "fivethirtyeight",
        "seaborn-deep",
        "seaborn",
        "seaborn-dark-palette",
        "seaborn-paper",
        "seaborn-darkgrid",
        "seaborn-notebook",
        "grayscale",
        "seaborn-muted",
        "seaborn-dark",
        "seaborn-talk",
        "ggplot",
        "bmh",
        "dark_background",
        "fast",
        "seaborn-ticks",
        "seaborn-colorblind",
        "classic",
    ]
    if type(style) is int:
        try:
            style = styles[style]
        except Exception:
            print("back to default style, wrong style entry, choose style from 0 to 23")
            style = "default"
    if type(training_history) is pd.DataFrame:
        pass
    else:
        training_history = pd.DataFrame(training_history)
    pyplot.style.use(style)
    pyplot.figure(figsize=(20, 10))
    pyplot.title("{} ({} ephocs)".format(metric, len(training_history)))
    if metric == "all":
        for column in training_history.columns:
            if column != "Unnamed: 0":
                pyplot.plot(
                    [i for i in range(0, len(training_history))],
                    training_history[column],
                    label=str(column),
                )
                pyplot.legend()
                pyplot.grid(True)
                if save == True:
                    pyplot.savefig("plot.png")
    else:
        pyplot.plot(
            [i for i in range(0, len(training_history))],
            training_history["{}".format(metric)],
            label="train",
        )
        pyplot.plot(
            [i for i in range(0, len(training_history))],
            training_history["val_{}".format(metric)],
            label="test",
        )
        pyplot.legend()
        pyplot.grid(True)
        if save == True:
            pyplot.savefig("plot.png")
