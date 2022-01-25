import json
import boto3
import logging
import pandas as pd
import numpy as np
import math
from io import BytesIO
from datetime import datetime
import statistics
from botocore.exceptions import ClientError


def days_diff(d1, d2):
    """
    Returns days between dates:  d2 - d1

    :param d1:
    :param d2:
    :return:
    """
    print("days_diff: formatting dates")
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    print("days_diff: subtracting dates")
    return (d2 - d1).days


def accuracyMetric(target, reported):
    """return Absolute error"""
    return abs(target - reported)


def accuracy_metrics(vals, truth_val, expected_dt):
    """

    :param vals:
    :param expected_dt:
    :param truth_val:
    :return: dict
    """
    accs = [accuracyMetric(truth_val, val) for val in vals[vals.notna()]]

    orig_acc = None
    avg = None
    std = None
    final_acc = None
    normalized_acc = None

    if len(accs) > 1:
        std = statistics.stdev(accs)
        avg = sum(accs) / len(accs)
        orig_acc = accs[0]
        final_acc = accs[-1]
    elif len(accs) == 1:
        avg = accs[0]
        orig_acc = accs[0]
        final_acc = accs[0]

    if truth_val != 0:
        normalized_acc = (1 / len(accs)) * (sum([1 - (acc / truth_val) for acc in accs]))

    return {
        "OriginalAccuracy": orig_acc,
        "AverageAccuracy": avg,
        "AccuracySTDev": std,
        "FinalAccuracy": final_acc,
        "NormalizedAccuracy": normalized_acc
    }


def completeness_metric(series, truth_df, expected_df, *args, **kwargs):
    """
    Returns percent of an update that includes previous values

    :param vals:
    :param expected_dt:
    :param truth_val:
    :return:
    """
    # check that there is an update for all the expected less than or equal to this
    expected_vals = expected_df[expected_df.iloc[:, 0] < series.name].index
    not_na = series[series.notna()]
    num_missing = len([each for each in expected_vals if each not in not_na.index])
    if len(expected_vals) > 0:
        return {"Completeness": 1 - (num_missing / len(expected_vals))}
    else:
        return {"Completeness": None}


def time_till_metrics(vals, truth_val, expected_dt):
    """

    :param vals: pandas Series object
    :param expected_dt:
    :param truth_val:
    :return:
    """
    # to accommodate not updated dates
    vals_not_na = vals[vals.notna()]

    # ------Time Till Reported------- #
    # first date updated
    first_reported = vals_not_na.index[0]

    # ------Time Till Accurate------- #
    # Else the final value was correct, and we need to find the last date for which it changed

    # changes between updates; [NaN, val1-val0, ...]
    diffs = [each for each in vals_not_na.diff()]

    # Find the dates at which the value changed
    change_dates = [ind for ind, dff in zip(vals_not_na.index, diffs) if dff != 0]
    time_till_accurate = days_diff(expected_dt, change_dates[-1])

    # If final value was not correct
    if truth_val != vals_not_na[-1]:
        time_till_accurate = 2 * days_diff(expected_dt,
                                           vals.index[-1])  # should this be something like more days than have elapsed?
    return {
        "TimeTillReported": days_diff(expected_dt, first_reported),
        "TimeTillAccurate": time_till_accurate
    }


def validity_nondecreasing_step(series, truth_df, expected_df, *args, **kwargs):
    truth_max = truth_df[expected_df.index < series.name].iloc[:, 0].max()
    num_expected_updates = len(expected_df[expected_df.index < series.name].iloc[:, 0].unique())
    coef = -1 / (min(num_expected_updates, truth_max) / 5)
    num_increasing_updates = len(series[series.diff() > 0])

    return -1 + 2 / (1 + math.exp(coef * num_increasing_updates))


def validity_nondecreasing_smoothness(series, truth_df, expected_df, *args, **kwargs):
    """
    Assumes series is of nondecreasing observations by increasing dates

    :param series:
    :param truth_df:
    :param expected_df:
    :param args:
    :param kwargs:
    :return:
    """
    orig_diffs = series.diff()  # nan, 2
    rises = [abs(diff) for diff in orig_diffs if diff > 0]  # 2
    inds = [ind for ind, diff in enumerate(orig_diffs) if diff > 0]  # 2020-03-28

    if len(inds) == 0:
        return 0

    runs = [inds[0]]  # 2020-03-28
    if len(inds) > 1:
        runs = runs + [abs(ind2 - ind1) for ind1, ind2 in zip(inds[:-1], inds[1:])]

    # last observation updated (max dt not na)
    obsvs = series[series.notna()]
    # max_date = obsvs.index[-1]
    max_val = obsvs.iloc[-1]  # 6
    num_expected_dates = expected_df[expected_df.iloc[:, 0] < series.name].shape[0]  # 2
    total_area = max_val * num_expected_dates  # 6x2
    covered_area = sum([rise * run for rise, run in zip(rises, runs)])  # sum([]
    if total_area > 0:
        return 1 - (covered_area / total_area)
    else:
        return None


def validity_nondecreasing(series, *args, **kwargs):
    """Percent of sequential reported dates that decrease"""
    num_decreasing_updates = len([each for each in series[series.notna()].diff() if each < 0])
    num_updates = len([each for each in series[series.notna()].diff() if each != 0])
    if num_updates > 2:
        return 1 - (num_decreasing_updates / (num_updates - 1))
    else:
        return 1


def consistency_nondecreasing_percent_restatement(series, truth_df, expected_df, *args, **kwargs):
    # |sum of increases| / |sum of absolute changes|
    increases = sum([diff for diff in series.diff().dropna() if diff > 0])
    changes = sum([abs(diff) for diff in series.diff().dropna()])
    if changes > 0:
        return increases / changes
    else:
        return None


def consistency_between_updates(data_df, truth_df, expected_df):
    updates = data_df.columns
    dct = {}
    last_non_null = None

    for prior, post in zip(updates[:-1], updates[1:]):

        if len(data_df[prior].notna()) > 0:
            last_non_null = data_df[prior]
        post_nonnulls = data_df[post].notna()
        diff = data_df[post][post_nonnulls] - last_non_null[post_nonnulls]

        if len(diff) > 0:
            dct[post] = {"ConsistencyPercentUpdated": len(diff[diff > 0]) / len(diff)}
        else:
            dct[post] = None

    return pd.DataFrame.from_dict(dct)


# ----------------------------------------------#
# -------- Data Quality Dimensions--------------#
# ----------------------------------------------#

def apply_to_observations(func):
    """

    :param func:
    :return: func
    """

    def over_observations(data_df, truth_df, expected_df, *args, **kwargs):
        dct = {}

        for obsv, vals in data_df.iterrows():

            not_na = vals[vals.notna()]
            if len(not_na) == 0:
                dct[obsv] = {}

            else:
                truth_val = truth_df.loc[obsv][0]
                expected_dt = expected_df.loc[obsv][0]

                dct[obsv] = func(vals, truth_val, expected_dt, *args, **kwargs)

        return pd.DataFrame.from_dict(dct, orient='index')

    return over_observations


def apply_to_updates(func):
    """

    :param func:
    :return: func
    """

    def over_updates(data_df, truth_df, expected_df, *args, **kwargs):
        dct = {}

        for update, series in data_df.iteritems():

            not_na = series[series.notna()]
            if len(not_na) == 0:
                dct[update] = None

            else:
                dct[update] = func(series, truth_df, expected_df, *args, **kwargs)

        return pd.DataFrame.from_dict(dct, orient='columns')

    return over_updates


def timeliness(data_df, truth_df, expected_df):
    """

    :param data_df:
    :param truth_df:
    :param expected_df:
    :return:
    """
    func = apply_to_observations(time_till_metrics)
    return func(data_df, truth_df, expected_df)


def accuracy(data_df, truth_df, expected_df):
    """

    :type data_df: object
    :param data_df:
    :param truth_df:
    :param expected_df:
    :return:pandas dataframe
    """

    func = apply_to_observations(accuracy_metrics)
    return func(data_df, truth_df, expected_df)


def validity(data_df, truth_df, expected_df):
    def validity_metrics(series, truth_df, expected_df):
        return {
            "ValidityNondecreasingSmoothness":
                validity_nondecreasing_smoothness(series, truth_df, expected_df),
            "ValidityNondecreasingUpdates":
                validity_nondecreasing(series, truth_df, expected_df),
            "ValidityNondecreasingStep":
                validity_nondecreasing_step(series, truth_df, expected_df),
        }

    func = apply_to_updates(validity_metrics)
    return func(data_df, truth_df, expected_df)


def consistency(data_df, truth_df, expected_df):
    def consistency_metrics(series, truth_df, expected_df):
        return {
            "ConsistencyNondecreasingPercentRestatement":
                consistency_nondecreasing_percent_restatement(series, truth_df, expected_df)
        }

    func = apply_to_updates(consistency_metrics)
    df1 = func(data_df, truth_df, expected_df)
    print(type(df1))
    print(df1.shape)
    df2 = consistency_between_updates(data_df, truth_df, expected_df)
    print(type(df2))
    print(df2.shape)
    return pd.concat([df1, df2])


def completeness(data_df, truth_df, expected_df):
    func = apply_to_updates(completeness_metric)
    return func(data_df, truth_df, expected_df)


def basic_stats(data_df, truth_df, expected_df):
    desc = truth_df.describe().T
    desc.columns = [f'truth_{each}' for each in desc.columns]
    return desc

# ----------------------------------------------#
# -------------- AWS Management-----------------#
# ----------------------------------------------#

def df_from_s3_csv(bucket, key):
    """

    :param s3_client: a boto3 client object for s3
    :param bucket: str
    :param key: str
    :return: pandas dataframe
    """
    s3_client = boto3.client('s3')
    logging.info(f'Attempting to read S3 object {key}')
    print(f'Attempting to read S3 object {key} in {bucket}')
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    print(f'Successfully read S3 object {key} in {bucket}')
    logging.info(f'Successfully read S3 object {key}')
    df = pd.read_csv(obj['Body'], sep=',', index_col=0)
    return df


def df_to_s3_csv(bucket, key, df):
    """

    :param s3_client: boto3 client object for s3
    :param bucket: str
    :param key: str
    :param df: pandas dataframe
    :return: True
    """
    print("Connecting to S3")
    s3_client = boto3.client('s3')

    print("Writing BytesIO")
    with BytesIO() as csv_buffer:
        df.to_csv(csv_buffer)
        print(f'Attempting to put object to bucket {bucket} at key {key}')
        response = s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    return status


def send_sqs_message(to_sqs_url, msg_body, region_name):
    """

    :param to_sqs_url: str
    :param msg_body: dictionary
    :param region_name: str
    :return:
    """
    sqs_client = boto3.client('sqs', region_name=region_name)

    try:
        msg = sqs_client.send_message(QueueUrl=to_sqs_url,
                                      MessageBody=json.dumps(msg_body))
        return msg

    except ClientError as e:
        logging.error(e)
        return None


def metric_node(
        event,
        context,
        to_sqs_url,
        region_name,
        to_bucket,
        to_key,
        func="accuracy"
):
    """
        The structure of a processing station: receive, load, do, save, send

    Load a pandas dataframe from the buck/key referenced in the triggering event
    Execute func on the dataframe which must return a df
    Put the df into to_bucket/key
    Send message to to_sqs_url

    :param event:
    :param context:
    :param to_sqs_url: str
    :param region_name: str
    :param to_bucket: str
    :param to_key: str
    :param func: func(data_df, truth_df, expected_df) returns a pandas df
    :return:
    """
    funcs_mapping = {
        "stats": basic_stats,
        "accuracy": accuracy,
        "timeliness": timeliness,
        "validity": validity,
        "consistency": consistency,
        "completeness": completeness
    }

    logging.getLogger().setLevel(logging.INFO)
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)s: %(asctime)s: %(message)s')

    body = event["Records"][0]["body"]
    if isinstance(body, str):
        body = json.loads(body)

    from_bucket = body['bucket']
    path, data_file, truth_file, expected_file = "", "data.csv", "truth.csv", "expected_update.csv"
    if 'path' in body:
        path = body['path']
    if 'data_file' in body:
        data_file = body['data_file']
    if 'truth_file' in body:
        truth_file = body['truth_file']
    if 'expected_file' in body:
        expected_file = body['expected_file']

    def make_key(file):
        if path == "":
            return file
        else:
            return "/".join([path, file])

    completed_stations = [each for each in body['completed_stations']]

    data_df = df_from_s3_csv(from_bucket, make_key(data_file))
    truth_df = df_from_s3_csv(from_bucket, make_key(truth_file))
    expected_df = df_from_s3_csv(from_bucket, make_key(expected_file))

    finished_df = funcs_mapping[func](data_df, truth_df, expected_df)

    status = df_to_s3_csv(bucket=to_bucket, key=make_key(to_key), df=finished_df)

    if status == 200:
        logging.info(f'Successful S3 put_object response')

    else:
        logging.info(f'Unsuccessful S3 put_object response - {status}')

    completed_stations.append(context.function_name)

    message = {
        'bucket': from_bucket,
        'path': path,
        'data_file': data_file,
        'truth_file': truth_file,
        'expected_file': expected_file,
        'completed_stations': completed_stations
    }

    msg = send_sqs_message(to_sqs_url, message, region_name)

    if msg is not None:
        logging.info(f'Sent SQS message ID: {msg["MessageId"]}')

    return {
        'statusCode': status,
        'body': message
    }


def summary_node(
        event,
        context,
        to_sqs_url,
        region_name,
        from_bucket,
        to_bucket,
        to_key
):
    """
     Summarize the Data Quality Dimensions

    Load a pandas dataframe from the buck/key referenced in the triggering event
    Execute func on the dataframe which must return a df
    Put the df into to_bucket/key
    Send message to to_sqs_url


    """
    logging.getLogger().setLevel(logging.INFO)
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)s: %(asctime)s: %(message)s')
    dims_files = [
        "timeliness.csv",
        "accuracy.csv",
        "validity.csv",
        "completeness.csv",
        "consistency.csv"
    ]

    body = event["Records"][0]["body"]
    if isinstance(body, str):
        body = json.loads(body)

    path, data_file, truth_file, expected_file = "", "data.csv", "truth.csv", "expected_update.csv"
    if 'path' in body:
        path = body['path']
    if 'data_file' in body:
        data_file = body['data_file']
    if 'truth_file' in body:
        truth_file = body['truth_file']
    if 'expected_file' in body:
        expected_file = body['expected_file']

    # from_bucket = body['bucket']  # unless completed edits the event, this is prepared-data

    def make_key(file):
        if path == "":
            return file
        else:
            return "/".join([path, file])

    completed_stations = [each for each in body['completed_stations']]

    dfs = []
    transpose = ["validity.csv", "consistency.csv", "completeness.csv"]

    for from_key in dims_files:
        df = df_from_s3_csv(from_bucket, make_key(from_key))

        if from_key in transpose:
            df = df.T

        desc_cols = ['mean', '50%', 'std']
        df_desc = df.describe()
        df_desc = df_desc.loc[desc_cols]
        df_desc.index = ['mean', 'median', 'std']
        df_desc = df_desc.T
        df_desc["coef_var"] = df_desc['std'] / df_desc['mean']
        kurtosis = df.kurtosis()
        df_desc = pd.concat([df_desc, kurtosis], axis=1)
        df_desc.rename({0: "kurtosis"}, inplace=True, axis=1)
        dfs.append(df_desc)

    finished_df = pd.concat(dfs)

    status = df_to_s3_csv(bucket=to_bucket, key=make_key(to_key), df=finished_df)

    flattened = finished_df.unstack().to_frame().sort_index(level=1).T
    flattened.columns = flattened.columns.map('_'.join)

    stats = df_from_s3_csv(from_bucket, make_key("stats.csv"))
    flattened = pd.concat([stats, flattened], axis=1)
    # concat flattened to stats

    status = df_to_s3_csv(bucket=to_bucket, key=make_key(f'flattened_{to_key}'), df=flattened)

    completed_stations.append(context.function_name)

    message = {
        'bucket': from_bucket,
        'path': path,
        'data_file': data_file,
        'truth_file': truth_file,
        'expected_file': expected_file,
        'summary_file': to_key,
        'completed_stations': completed_stations
    }

    msg = send_sqs_message(to_sqs_url, message, region_name)

    if msg is not None:
        logging.info(f'Sent SQS message ID: {msg["MessageId"]}')

    return {
        'statusCode': status,
        'body': message
    }
