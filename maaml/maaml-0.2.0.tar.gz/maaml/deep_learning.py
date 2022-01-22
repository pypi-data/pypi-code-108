from keras.layers import (
    Input,
    Conv2D,
    BatchNormalization,
    MaxPooling2D,
    Dropout,
    Flatten,
    Dense,
    Add,
    Activation,
)
from keras.models import Model, load_model, save_model
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from sklearn.model_selection import train_test_split, ShuffleSplit
from maaml.machine_learning import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    roc_auc_score,
    classification_report,
)
import numpy as np
import pandas as pd
import time
import platform
import os


class DeepRCNModel:
    """[summary]
    a class for the DeepRCNModel, that allow you to
    access the layers as attributes by the ordinal numbers names from first_layer .. to the eighteenth_layer,
     except for the attributes of the resnet_block that has it's unique method and the input_layer and output_layer attributes
    """

    def __init__(self, input_shape=(20, 1, 1), class_nb=3):
        self.input_shape = input_shape
        self.input_layer = Input(shape=self.input_shape, name="input")
        self.first_layer = Conv2D(
            60, (4, 4), activation="relu", padding="same", name="conv1_60_4x4"
        )(self.input_layer)
        self.second_layer = BatchNormalization(name="batch_norm1")(self.first_layer)
        self.third_layer = MaxPooling2D((2, 2), padding="same", name="Max_pool1_2x2")(
            self.second_layer
        )
        self.fourth_layer = Dropout(0.2, name="dropout1_0.2")(self.third_layer)
        self.resnet_block = self.resnet_block_creating(self.fourth_layer, 60, 4)
        self.fifth_layer = Conv2D(
            30, (4, 4), activation="relu", padding="same", name="conv2_30_4x4"
        )(self.resnet_block)
        self.sixth_layer = BatchNormalization(name="batch_norm2")(self.fifth_layer)
        self.seventh_layer = MaxPooling2D((2, 2), padding="same", name="Max_pool2_2x2")(
            self.sixth_layer
        )
        self.eighth_layer = Dropout(0.2, name="dropout2_0.2")(self.seventh_layer)
        self.ninth_layer = Conv2D(
            15, (4, 4), activation="relu", padding="same", name="conv3_15_4x4"
        )(self.eighth_layer)
        self.tenth_layer = BatchNormalization(name="batch_norm3")(self.ninth_layer)
        self.eleventh_layer = MaxPooling2D(
            (2, 2), padding="same", name="Max_pool3_2x2"
        )(self.tenth_layer)
        self.twelfth_layer = Dropout(0.2, name="dropout3_0.2")(self.eleventh_layer)
        self.thirdteenth_layer = Conv2D(
            8, (4, 4), activation="relu", padding="same", name="conv4_8_4x4"
        )(self.twelfth_layer)
        self.fourteenth_layer = BatchNormalization(name="batch_norm4")(
            self.thirdteenth_layer
        )
        self.fifteenth_layer = MaxPooling2D(
            (1, 1), padding="same", name="Max_pool4_1x1"
        )(self.fourteenth_layer)
        self.sixteenth_layer = Flatten(name="Flatten_layer")(self.fifteenth_layer)
        self.seventeenth_layer = Dense(
            units=224, input_dim=448, activation="relu", name="dense1_448x224"
        )(self.sixteenth_layer)
        self.eighteenth_layer = BatchNormalization(name="batch_norm5")(
            self.seventeenth_layer
        )
        self.output_layer = Dense(
            units=class_nb, activation="softmax", name="dense2_224x10"
        )(self.eighteenth_layer)
        self.model = Model(self.input_layer, self.output_layer, name="DeepRCNModel")

    @staticmethod
    def resnet_block_creating(input_data, filters, conv_size):
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

    def show(self):
        self.model.summary()


class Evaluator:
    def __init__(
        self,
        model,
        dataset=None,
        features=None,
        target_column=None,
        target=None,
        target_name="target",
        model_name: str = None,
        preprocessing_alias=None,
        input_shape=None,
        cross_eval=True,
        nb_splits=5,
        test_size=0.3,
        callbacks="best model",
        learning_rate="scheduler",
        opt="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
        epochs=600,
        batch_size=60,
        verbose=1,
    ):
        self.model = model
        self.model_name = model_name if model_name is not None else model.name
        target_name = [target_name]
        self.target_list = []
        if dataset is not None:
            for column_name in dataset.columns:
                for keyname in target_name:
                    if keyname in column_name:
                        self.target_list.append(column_name)
        if cross_eval is True:
            self.cross_evaluation = self.cross_validating(
                model=self.model,
                dataset=dataset,
                features=features,
                target_column=target_column,
                target=target,
                target_names=self.target_list,
                model_name=self.model_name,
                preprocessing_alias=preprocessing_alias,
                input_shape=input_shape,
                callbacks=callbacks,
                learning_rate=learning_rate,
                nb_splits=nb_splits,
                test_size=test_size,
                opt=opt,
                loss=loss,
                metrics=metrics,
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose,
            )
        elif cross_eval is not True:
            (
                self.trained_model,
                self.best_model,
                self.training_history,
                self.evaluation,
            ) = self.model_training(
                model=self.model,
                dataset=dataset,
                features=features,
                target_column=target_column,
                target=target,
                target_names=self.target_list,
                model_name=self.model_name,
                input_shape=input_shape,
                callbacks=callbacks,
                learning_rate=learning_rate,
                test_size=test_size,
                opt=opt,
                loss=loss,
                metrics=metrics,
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose,
            )

    def model_training(
        self,
        model,
        dataset,
        features,
        target_column,
        target,
        target_names,
        input_shape,
        callbacks="best model",
        learning_rate="scheduler",
        test_size=0.3,
        opt="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
        epochs=600,
        batch_size=60,
        verbose=1,
    ):
        start_time = time.perf_counter()
        if dataset is not None:
            X, Y, Y_ohe = (
                dataset.drop(target_names, axis=1),
                dataset[target_names[0]],
                dataset[target_names[1:]],
            )
        elif features is not None and target is not None:
            X, Y, Y_ohe = features, target_column, target
        X = np.reshape(X.values, (len(X), *input_shape))
        if callbacks == "best model":
            if any(c.isdigit() for c in platform.node()) == True:
                mc = ModelCheckpoint(
                    "/content/drive/MyDrive/best_model.h5",
                    monitor="val_accuracy",
                    save_best_only=True,
                    verbose=2,
                )
            else:
                mc = ModelCheckpoint(
                    "best_model.h5",
                    monitor="val_accuracy",
                    save_best_only=True,
                    verbose=2,
                )
            cb = [mc]
            if learning_rate == "scheduler":
                lrs = LearningRateScheduler(self.learning_rate_sheduling)
                cb.append(lrs)
        elif callbacks == None:
            cb = None
        model.compile(loss=loss, optimizer=opt, metrics=metrics)
        X_train, X_test, Y_ohe_train, Y_ohe_test = train_test_split(
            X, Y_ohe, test_size=test_size, random_state=10
        )
        _, _, _, Y_test = train_test_split(X, Y, test_size=test_size, random_state=10)
        history = model.fit(
            X_train,
            Y_ohe_train,
            validation_data=(X_test, Y_ohe_test),
            callbacks=cb,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
        )
        end_time = time.perf_counter()
        training_history = history.history
        if any(c.isdigit() for c in platform.node()) == True:
            pd.DataFrame(training_history).to_csv(
                r"/content/drive/MyDrive/training_history.csv", index=False
            )
        else:
            pd.DataFrame(training_history).to_csv(r"training_history.csv", index=False)
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
        pred = best_model.predict(X_test, batch_size=batch_size, verbose=1)
        predictions = np.argmax(pred, axis=1)
        train_eval = best_model.evaluate(X_train, Y_ohe_train, verbose=verbose)
        train_score = train_eval[1] * 100
        exec_time = f"{(end_time - start_time): .2f} (s)"
        acc_score = accuracy_score(Y_test.values, predictions, normalize=True) * 100
        pres_score = precision_score(Y_test.values, predictions, average="macro") * 100
        rec_score = recall_score(Y_test.values, predictions, average="macro") * 100
        f1 = f1_score(Y_test.values, predictions, average="macro") * 100
        cokap_score = cohen_kappa_score(Y_test.values, predictions) * 100
        roc_auc = roc_auc_score(Y_ohe_test.values, pred) * 100
        scores = [
            f"execution time: {exec_time}",
            f"train accuracy: {train_score: .4f}% ",
            f"accuracy: {acc_score: .4f}%",
            f"precision: {pres_score: .4f}%",
            f"recall: {rec_score: .4f}%",
            f"F1 score: {f1: .4f}%",
            f"cohen kappa: {cokap_score: .4f}%",
            f"roc_auc_score: {roc_auc: .4f}%",
        ]
        if verbose == 1:
            print(scores)
        return model, best_model, training_history, scores

    def cross_validating(
        self,
        model,
        dataset,
        features,
        target_column,
        target,
        target_names,
        model_name,
        preprocessing_alias,
        input_shape,
        callbacks="best model",
        learning_rate="scheduler",
        nb_splits=5,
        test_size=0.3,
        opt="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
        epochs=600,
        batch_size=60,
        verbose=0,
    ):
        start_time = time.perf_counter()
        if dataset is not None:
            X, Y, Y_ohe = (
                dataset.drop(target_names, axis=1),
                dataset[target_names[0]],
                dataset[target_names[1:]],
            )
        elif features is not None and target is not None:
            X, Y, Y_ohe = features, target_column, target
        X = np.reshape(X.values, (len(X), *input_shape))
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
        for train, test in cv.split(X, Y, Y_ohe):
            print(
                f"\033[1m\n*******begin cross validation in fold number:{len(train_acc_scores) + 1}*******\033[0m"
            )
            newpath = "cross_validation"
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            if callbacks == "best model":
                if any(c.isdigit() for c in platform.node()) == True:
                    mc = ModelCheckpoint(
                        "/content/drive/MyDrive/best_model.h5",
                        monitor="val_accuracy",
                        save_best_only=True,
                        verbose=2,
                    )
                else:
                    mc = ModelCheckpoint(
                        f"{newpath}/cv_best_model.h5",
                        monitor="val_accuracy",
                        save_best_only=True,
                        verbose=2,
                    )
                cb = [mc]
                if learning_rate == "scheduler":
                    lrs = LearningRateScheduler(self.learning_rate_sheduling)
                    cb.append(lrs)
            elif callbacks == None:
                cb = None
            model.compile(loss=loss, optimizer=opt, metrics=metrics)
            history = model.fit(
                X[train],
                Y_ohe.loc[train],
                validation_data=(X[test], Y_ohe.loc[test]),
                callbacks=cb,
                epochs=epochs,
                batch_size=batch_size,
                verbose=verbose,
            )
            end_time = time.perf_counter()
            training_history = history.history
            if any(c.isdigit() for c in platform.node()) == True:
                pd.DataFrame(training_history).to_csv(
                    r"/content/drive/MyDrive/training_history.csv", index=False
                )
            else:
                pd.DataFrame(training_history).to_csv(
                    f"{newpath}/training_history.csv", index=False
                )
            if callbacks == "best model":
                try:
                    best_model = load_model(f"{newpath}/cv_best_model.h5")
                except Exception:
                    print(
                        "exception triggered, can't load the saved best model, the best model is the current one"
                    )
                    best_model = model
            elif callbacks == None:
                best_model = model
            save_model(
                best_model,
                f"{newpath}/cv_best_model{len(train_acc_scores) + 1}.h5",
            )
            pred = best_model.predict(X[test], batch_size=batch_size, verbose=0)
            predictions = np.argmax(pred, axis=1)
            exec_time.append((end_time - start_time))
            train_acc_scores.append(
                best_model.evaluate(X[train], Y_ohe.loc[train], verbose=verbose)[1]
                * 100
            )
            acc_scores.append(
                accuracy_score(Y[test].values, predictions, normalize=True) * 100
            )
            pres_scores.append(
                precision_score(Y[test].values, predictions, average="macro") * 100
            )
            rec_scores.append(
                recall_score(Y[test].values, predictions, average="macro") * 100
            )
            f1.append(f1_score(Y[test].values, predictions, average="macro") * 100)
            cokap_scores.append(cohen_kappa_score(Y[test].values, predictions) * 100)
            roc_auc_scores.append(roc_auc_score(Y_ohe.loc[test].values, pred) * 100)
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
        cv_scores[model_name] = [
            preprocessing_alias,
            f"{np.mean(exec_time): .2f} (s)",
            f"{np.mean(train_acc_scores):.4f}% (+/- {np.std(train_acc_scores):.4f}%)",
            f"{np.mean(acc_scores):.4f}% (+/- {np.std(acc_scores):.4f}%)",
            f"{np.mean(pres_scores):.4f}% (+/- {np.std(pres_scores):.4f}%)",
            f"{np.mean(rec_scores):.4f}% (+/- {np.std(rec_scores):.4f}%)",
            f"{np.mean(f1):.4f}% (+/- {np.std(f1):.4f}%)",
            f"{np.mean(cokap_scores):.4f}% (+/- {np.std(cokap_scores):.4f}%)",
            f"{np.mean(roc_auc_scores):.4f}% (+/- {np.std(roc_auc_scores):.4f}%)",
        ]
        cv_scores.to_csv(
            f"{newpath}/cross_validation_scores_{preprocessing_alias}.csv", index=False
        )
        return cv_scores

    @staticmethod
    def learning_rate_sheduling(
        epoch, scheduler_threshold=480, initial_lrate=0.001, second_lrate=0.0001
    ):
        lrate = initial_lrate
        if epoch > 480:
            lrate = second_lrate
            print("Change in the learning rate, the new learning rate is:", lrate)
        return lrate


def main():
    from maaml.preprocessing import DataPreprocessor as dp

    processed = dp(dataset="UAHdataset", scaler=2)
    uahdataset = processed.preprocessed_dataset
    alias = processed.scaler_name
    features = processed.features
    target_column = processed.target_column
    target = processed.target
    model_build = DeepRCNModel()
    model_build.show()
    evaluation = Evaluator(
        model_build.model,
        dataset=uahdataset,
        target_name="target",
        preprocessing_alias=alias,
        input_shape=model_build.input_shape,
        cross_eval=True,
        epochs=2,
        verbose=1,
    )
    print("cross validation results: \n", evaluation.cross_evaluation)
    print("model name :", evaluation.model_name)


if __name__ == "__main__":
    main()
