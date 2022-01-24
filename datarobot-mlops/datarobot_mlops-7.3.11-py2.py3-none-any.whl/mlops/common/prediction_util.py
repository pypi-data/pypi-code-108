#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

import copy


def get_predictions(df, predictions, target_col, prediction_cols=None, class_names=None):
    if predictions is not None:
        # if we already have the predictions, just return them
        return predictions

    # If prediction_cols are provided, prefer those over the target because we want
    # to report prediction probabilities rather than just the target.
    if prediction_cols is not None and len(prediction_cols) > 0:
        if len(prediction_cols) == 1:
            # regression models will only have a single prediction
            predictions = df[target_col].tolist()
        else:
            predictions = []
            for index, row in df.iterrows():
                prediction = []
                for prediction_col in prediction_cols:
                    prediction.append(row[prediction_col])
                predictions.append(prediction)
        return predictions

    # if there are no prediction columns, fall back on using the target column.
    # Unfortunately, this relies on providing the class_names to determine the
    # model type.
    if class_names is None:
        # if no class names, assume this is regression.
        predictions = df[target_col].tolist()
    else:
        predictions = []
        for predicted_class in df[target_col].tolist():
            # Similar to 1 hot encoding - should work for multiclass too
            prediction = [
                1.0 if str(predicted_class) == class_name else 0.0
                for class_name in class_names
            ]
            predictions.append(copy.copy(prediction))

    return predictions
