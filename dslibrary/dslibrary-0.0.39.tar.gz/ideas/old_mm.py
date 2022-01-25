"""
SNAPSHOT FROM https://innersource.accenture.com/projects/MSDOHEDCAIPDS/repos/model-management/browse/model-management-ds/src/main/mmlibraries/python/mmlibrary.py
"""

import glob
import json
import os
import sys
import uuid
import warnings

import requests
from bson.objectid import ObjectId
from gridfs import GridFSBucket
from pymongo import MongoClient

"""
Script that would parse the arguments passed from Model Manager
while executing any python job. Expected format of argument is as follows

python <scriptname.py> <job_id> secondary_id <?> model <model_file_absolute_path> input_file <input_data_file_abs_path> 
 -> KPI-START key1 95 key2 90 KPI-END PARAM-START param1 value1 param2 value2 PARAM-END

Date of creation: 8th March, 2017

Author: Model Management Dev Team
----------------------------------------------------------------------------------------------------------
Import libraries for downloading file from mongodb
"""

arguments = {}
kpi_dictionary = {}
param_dictionary = {}
input_file = {}
parsed_json_args = {}
env_config = {}
recipe_runtime = {}

__mm_arguments_parsed = False


def __custom_warning_format__(message, category, filename, lineno, file=None, line=None):
    sys.stdout.write(warnings.formatwarning(message, category, filename, lineno))


warnings.showwarning = __custom_warning_format__


def __evaluate_parse_arguments__():
    """
    Checks whether the <c>parse_arguments</c> function has already been called or not. If not then this function
    calls it making sure that the mmlibrary is properly initialized.
    """
    global __mm_arguments_parsed

    if __mm_arguments_parsed:
        return

    parse_arguments("")


def parseArguments(args=None):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use parse_arguments(args=None) instead.")
    return parse_arguments(args)


def parse_arguments(args=None):
    """
    Parse arguments from sys.argv, for use with get_argument(key).
    This is not intended to use by users and deprecated from users point of view.
    :param args:   Currently ignored.
    """
    global __mm_arguments_parsed

    if __mm_arguments_parsed:
        return
    __mm_arguments_parsed = True

    global kpi_dictionary
    global param_dictionary
    global input_file
    global parsed_json_args
    global arguments
    global env_config
    global recipe_runtime

    param = __build_args__()

    parsed_json_args = json.loads(param)
    arguments = parsed_json_args["args"]
    kpi_dictionary = arguments["kpi"]
    param_dictionary = arguments["params"]
    input_file = arguments["input_file"]
    env_config = arguments["env_config"]
    recipe_runtime = parsed_json_args["runtime"]


# Added below for getting jobId, which is outside args json of job request.
def __get_job_id__():
    global parsed_json_args
    return parsed_json_args["job_id"]


def about():
    print("Model Manager header library v${python_version} (id: ${buildNumber.commitsha}, "
          "built: ${buildNumber.timestamp})")


def __get_json_argument__(key):
    global arguments
    try:
        return arguments[key]
    except KeyError:
        __raise_value_error__("System does not have a value for the argument key = " + key)


def __all_files_in__(dir_):
    all_files = None
    try:
        all_files = os.listdir(dir_)
    except os.error:
        __raise_value_error__("__get_all_files_in__: unable to retrieve files from dir: " + dir_)

    return all_files


def __score_model_binary_path__():
    score_base_dir = __get_env_config__("mm_score_mbin_fpath")
    model_resource_id = __get_json_argument__("model_resource_id")

    score_model_binary_cached_dir = os.path.join(score_base_dir, model_resource_id)
    # find all files in scoring_model_path directory
    all_files = __all_files_in__(score_model_binary_cached_dir)
    return os.path.join(score_model_binary_cached_dir, all_files[0])


def getModel():
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_model() instead.")
    return get_model()


def get_model():
    """
    Access data for the current model's model binary.
    :return: Path to model binary or ``None`` if it is not found.
    :except: ``ValueError`` if it is called from step recipe.
    """
    __evaluate_parse_arguments__()

    model = None
    model_path = None
    val = __get_json_argument__("model")
    is_not_model = __get_json_argument__("adhocStep")

    if is_not_model:
        __raise_value_error__("get_model() can only be called from model's recipe")

    if val is None:
        __raise_value_error__("System does not have a value for model")

    if __is_scoring_run__():
        model_path = __score_model_binary_path__()
    else:
        try:
            model_binary = __get_resource__(val)
            # check model is not null
            if model_binary is not None:
                with open(__temp_file_in_the_working_directory__(), "w+b") as model:
                    model.write(model_binary)

        except:
            __raise_value_error__("get_model: unable to retrieve model")

        if model is not None:
            model_path = model.name
            model.close()

    return model_path


def __get_resource__(file_id):
    """
    Return resourceContent as a stream of bytes.
    :param file_id: The gridfs file id.
    :return: returned bytes
    """
    return __stream_file_data_as_binary__(file_id).read()


def getArgument(key):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_argument(key) instead.")
    return get_argument(key)


def get_argument(key):
    """
    Get the value of one of this model's supplied arguments.
    :param key: Name of argument.
    :return: Value of argument.
    :except: ``ValueError`` if the key is not contained by the dictionary.
    """
    global param_dictionary
    __evaluate_parse_arguments__()

    try:
        return param_dictionary[key]
    except KeyError:
        __raise_value_error__("System does not have a value for parameter key = " + key)


def newVersion(data, autoPublish=True):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use new_version(data, auto_publish=True) instead.")
    return new_version(data, autoPublish)


def new_version(data, auto_publish=True):
    """
    Create new version for trained binary data, i.e. save model binary.
    :param data:  A readable stream with the content to save, i.e. a file-like object with a ``read()`` method.
    :param auto_publish: Whether the new trained version should be auto-published. Please note, this parameter is just an intent, if the current version is not published this version won't be published either even if the autopublish is TRUE
    :except: ``ValueError`` in the following cases:
    * if data is not file-like object or string or
    * if the master node endpoint is not set or
    * if the request sent to the master node was unsuccessful.
    """

    __evaluate_parse_arguments__()

    if not (data and (hasattr(data, "read") or isinstance(data, (str, bytes)))):
        __raise_value_error__("data is not provided or is of the wrong type")

    mm_endpoint = __get_master_node_endpoint__()
    if mm_endpoint is None:
        __raise_value_error__("model manager endpoint is not available")

    model_binary_name = "trainedmodel"
    mm_rest_url = mm_endpoint + "models/newtrainedversion"
    fs_bucket = __get_grid_fs_bucket__()
    fs_bucket.upload_from_stream(model_binary_name, data,
                                 metadata={
                                     "jobId": __get_job_id__(),
                                     "name": model_binary_name,
                                     "modelBinary": "true"
                                 })

    r = requests.post(mm_rest_url,
                      data=json.dumps({
                          "jobId": __get_job_id__(),
                          "secondary_id": __get_json_argument__('secondary_id'),
                          "autoPublish": auto_publish
                      }),
                      headers={'content-type': 'application/json'})

    if r.status_code != 200 or r.json().get("model_id") is None:
        __raise_value_error__("Error while creating new version of the training model")


def save_kpi(kpi_name, kpi_value, model_name=None, model_version_id="latest"):
    """
    Save KPI result value - for KPI name, model and model version.
    :param kpi_name the kpi name
    :param kpi_value the kpi result value to store
    :param model_name the name of the model
    :param model_version_id the version id
    :except ``ValueError`` in the following case:
    * if the request sent to the master node wasn't successful.
    """

    __evaluate_parse_arguments__()

    is_step = __get_json_argument__("adhocStep")

    ids = list(__get_json_argument__('secondary_id').split("_"))
    run_id = ids[1]
    model_id = ""
    version_id = model_version_id

    if is_step:
        if model_name is None or version_id is None:
            __raise_value_error__("Save Kpi: method save_kpi(kpi_name, kpi_value) "
                                  "should be used within model only. "
                                  "Use method save_kpi(kpi_name, kpi_value, model_name, "
                                  "model_version_id) within step.")
    else:  # model
        if model_name is not None or version_id != "latest":
            __raise_value_error__("Save Kpi: method save_kpi(kpi_name, kpi_value, "
                                  "model_name, model_version_id) should be used within step only. "
                                  "Use method save_kpi(kpi_name, kpi_value) "
                                  "within a model.")
        else:
            model_id = ids[2]  # modelId
            version_id = ids[3]  # versionId

    mm_endpoint = __get_master_node_endpoint__()
    mm_rest_url = mm_endpoint + "kpiresults"

    r = requests.post(mm_rest_url,
                      data=json.dumps({"kpi_result_value": kpi_value,
                                       "kpi_name": kpi_name,
                                       "model_id": model_id,
                                       "model_name": model_name,
                                       "model_version_id": version_id,
                                       "project": get_project(),
                                       "run_id": run_id}),
                      headers={'content-type': 'application/json'})

    if r.status_code != 200:
        json_response = r.json()
        if len(json_response) > 0:
            __raise_value_error__("Save Kpi: " + json_response[0]["ValidationError"])
        __raise_value_error__("Save Kpi: Unable to save KPI result")


def saveKpiResult(kpiName, referenceDate, kpiResultValue, modelName=None, versionId=None):
    """
    Save KPI result value - for KPI name, reference date, model and model version.
    :param kpiName the kpi name
    :param referenceDate the reference date by the ``getKpiResult`` function can retrieve result.
    IGNORED since 5.2 release, the creation date of the KpiResult will be used instead of!
    :param kpiResultValue the kpi result value to store
    :param modelName the name of the model
    :param versionId the version id
    :except ``ValueError`` in the following cases:
    * if the reference date is given and it is not in the expected format or
    * if the request sent to the master node wasn't successful.
    """

    warnings.warn("Deprecated function, it may be removed in future releases.")

    __evaluate_parse_arguments__()

    is_step = __get_json_argument__("adhocStep")

    # extract additional parameters
    ids = list(__get_json_argument__('secondary_id').split("_"))
    run_id = ids[1]  # runId
    model_id = ""
    model_version_id = versionId
    if is_step:
        if modelName is None or versionId is None:
            __raise_value_error__("saveKpiResult: method saveKpiResult(kpiName, referenceDate, kpiResultValue) "
                                  "should be used within model only. "
                                  "Use method saveKpiResult(kpiName, referenceDate, kpiResultValue, modelName, "
                                  "versionId) within step.")
    else:  # model
        if modelName is not None or versionId is not None:
            __raise_value_error__("saveKpiResult: method saveKpiResult(kpiName, referenceDate, kpiResultValue, "
                                  "modelName, versionId) should be used within step only. "
                                  "Use method saveKpiResult(kpiName, referenceDate, kpiResultValue) "
                                  "within a model.")
        else:
            model_id = ids[2]  # modelId
            model_version_id = ids[3]  # versionId

    mm_endpoint = __get_master_node_endpoint__()
    mm_rest_url = mm_endpoint + "kpiresults"
    r = requests.post(mm_rest_url,
                      data=json.dumps({"kpi_result_value": kpiResultValue,
                                       "kpi_name": kpiName,
                                       "model_id": model_id,
                                       "model_name": modelName,
                                       "model_version_id": model_version_id,
                                       "project": get_project(),
                                       "run_id": run_id}),
                      headers={'content-type': 'application/json'})

    if r.status_code != 200:
        json_response = r.json()
        if len(json_response) > 0:
            __raise_value_error__("saveKpiResult: " + json_response[0]["ValidationError"])
        __raise_value_error__("saveKpiResult: Unable to save KPI result")


def get_last_kpi(kpi_name, model_name, model_version_id="all"):
    """
    Get the value of the latest KPI.
    :param kpi_name The kpi name criteria.
    :param model_name The model name criteria.
    :param model_version_id The version id criteria. It can be "all", "latest" or numeric.
    :return With a dictionary containing the kpi result and timestamp retrieved by the criteria or
            ``None`` if not found any.
    :except ``ValueError`` if the request sent to the master node was unsuccessful.
    """
    __evaluate_parse_arguments__()

    mm_endpoint = __get_master_node_endpoint__()
    mm_rest_url = mm_endpoint + "kpiresults/last"
    project = get_project()
    response = requests.get(mm_rest_url,
                            params={
                                'model_name': model_name,
                                'version_id': model_version_id,
                                'kpi_name': kpi_name,
                                'project': project
                            })

    json_response = response.json()
    if response.status_code != 200:
        if len(json_response) > 0:
            __raise_value_error__("get_last_kpi: " + json_response[0]["ValidationError"])
        __raise_value_error__("get_last_kpi: Error while get KPI result")

    if (json_response is None or
            json_response.get("kpi_result_value") is None or
            json_response.get("created") is None):
        return None

    return {
        "value": json_response.get("kpi_result_value"),
        "timestamp": json_response.get("created")
    }


def getKpiResult(kpiName, modelName, versionId, referenceDate):
    """
    Get the value of a KPI.
    :param kpiName The kpi name criteria.
    :param modelName The model name criteria.
    :param versionId The version id criteria.
    :param referenceDate The reference date criteria. IGNORED since 5.2 release!
    :return With the kpi result retrieved by the criteria or ``None`` if not found any.
    :except ``ValueError`` if the ``referenceDate`` is not given in the expected format or
    the request sent to the master node was unsuccessful.
    """

    warnings.warn("Deprecated function, it may be removed in future releases. The <referenceDate> field is ignored.")

    return get_last_kpi(kpiName, modelName, versionId)


def getBinaryFromResource(resourceName):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_binary_from_resource(resource_name) instead.")
    return get_binary_from_resource(resourceName)


def get_binary_from_resource(resource_name):
    """
    Download the entire content of the given resource from mongodb.
    :param resource_name:  Name of resource to download.
    :returns:  Binary content.
    :except: ``ValueError`` if the resource requested by name doesn't exist or its content couldn't be retrieved.
    """
    # input_file is Json array
    __evaluate_parse_arguments__()

    file_id = __get_resource_file_id__(resource_name)
    # Download the file content to a local file and then pass the file name to the caller
    content = __get_resource__(file_id)
    if content is None:
        __raise_value_error__("get_binary_from_resource: unable to retrieve data from resource: <" + resource_name + ">")
    return content


def saveBinaryToResource(resourceName, data):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use save_binary_to_resource(resource_name, data) instead.")
    return save_binary_to_resource(resourceName, data)


def save_binary_to_resource(resource_name, data):
    """
    Upload binary resource file to mongodb.
    :param resource_name:  Name of resource.
    :param data: A file-like object with a ``read()`` method or ``string``.
    :except: ``ValueError`` in the following cases:
    * if the ``resourceName`` parameter is not provided or ``None`` or
    * if the ``data`` parameter is neither file-like object nor ``string``.
    """
    __evaluate_parse_arguments__()

    if not resource_name:
        __raise_value_error__("resource name is not provided")

    if not data or not (hasattr(data, "read") or isinstance(data, (str, bytes))):
        __raise_value_error__("data is not provided or is of the wrong type")

    fs_bucket = __get_grid_fs_bucket__()

    # output_file is Json array
    fs_bucket.upload_from_stream(resource_name,
                                 data.encode('utf-8') if isinstance(data, str) else data,
                                 metadata={'jobId': __get_job_id__(),
                                           'name': resource_name})


def saveTemporaryData(run_data):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use save_temporary_data(run_data) instead.")
    return save_temporary_data(run_data)


def save_temporary_data(run_data):
    """
    Uploads transient resource file to mongodb for given run.
    :param run_data: A file-like object with a ``read()`` method or ``string``.
    :type run_data: str or bytes or file-like object using either in binary or text mode
    :except: ``ValueError`` in the following cases:
    * if the ``run_data`` parameter is neither file-like object nor ``string``,
    * if the ``transient_resource_id`` is ``None``,
    * if the ``run_data`` couldn't be uploaded through the Resource API.
    """
    __evaluate_parse_arguments__()

    if not run_data or not (hasattr(run_data, "read") or isinstance(run_data, (str, bytes))):
        __raise_value_error__("run_data is not provided or is of the wrong type")

    transient_resource_id = __get_transient_resource_id__()
    if transient_resource_id is None:
        __raise_value_error__("The transient_resource_id is missing.")

    save_transient_resource_url = \
        __get_master_node_endpoint__() + "resources/transient_resource/" + transient_resource_id

    if isinstance(run_data, (str, bytes)):
        file_data = ("transient_resource_data_file_name",
                     run_data.encode() if isinstance(run_data, str) else run_data)
    else:
        file_data = run_data

    response = requests.post(url=save_transient_resource_url, files={'fileData': file_data})

    if response.status_code == 400:
        __raise_value_error__("save_temporary_data: " + response.json()[0]["ValidationError"])
    elif response.status_code != 200:
        __raise_value_error__("save_temporary_data: transient resource data couldn't be uploaded.")


def __get_response_data__(response):
    content = b''
    for chunk in response.iter_content(chunk_size=128):
        content += chunk

    return content


def getTemporaryData():
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_temporary_data() instead.")
    return get_temporary_data()


def get_temporary_data():
    """
    Downloads transient resource file from mongodb for given run.
    :returns The content of the downloaded temporary data.
    :rtype bytes
    """
    __evaluate_parse_arguments__()

    transient_resource_id = __get_transient_resource_id__()
    if transient_resource_id is None:
        __raise_value_error__("The transient_resource_id is missing.")

    download_transient_resource_url = \
        __get_master_node_endpoint__() + "resources/" + transient_resource_id + "/download"

    response = requests.get(download_transient_resource_url, stream=True)

    if response.status_code != 200:
        json_response = response.json()
        if len(json_response) > 0:
            __raise_value_error__("get_temporary_data: " + json_response[0]["ValidationError"])
        __raise_value_error__("get_temporary_data: transient resource data couldn't be downloaded.")

    return __get_response_data__(response)


# ---- Private methods --------------
def __get_grid_fs_bucket__():
    db = __get_model_manager_db__()
    return GridFSBucket(db, bucket_name="mm.fs")


def __get_resource_file_id__(resource_name):
    """
    Determine the resource file id
    """
    global input_file
    # input_file is Json array
    file_id = None
    for file in input_file:
        if file['name'] == resource_name:
            file_id = file['value']
    if file_id is None:
        __raise_value_error__("System does not have a value for input file key = " + resource_name +
                              ", please check the uploaded resource(s) name(s)")
    return file_id


def __stream_file_data_as_binary__(file_id):
    fs_bucket = __get_grid_fs_bucket__()
    return fs_bucket.open_download_stream(ObjectId(file_id))


def __build_args__():
    arg = ""
    for index in range(len(sys.argv) - 1):
        arg = arg + " " + sys.argv[index + 1]
    return arg


class MmLibraryValidationWarning(UserWarning):
    pass


def evaluationResult(message):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use evaluation_result(message) instead.")
    return evaluation_result(message)


def evaluation_result(message):
    """
    It is used to indicate evaluation failure scenarios.
    :param message: optional. The message to use in the printed warning.
    """
    __evaluate_parse_arguments__()

    if message is not None:
        warnings.warn("mmlibrary evaluation error: " + message, MmLibraryValidationWarning, stacklevel=2)
    else:
        warnings.warn("mmlibrary evaluation error: ", MmLibraryValidationWarning, stacklevel=2)


def getDBConnection(jdbc_connection_name, create_connection=None):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_db_connection(jdbc_connection_name, create_connection=None) instead.")
    return get_db_connection(jdbc_connection_name, create_connection)


def get_db_connection(jdbc_connection_name, create_connection=None):
    """
    Get a connection to a database.
    :param jdbc_connection_name:   Name associated with connection details.
    :param create_connection: An optional callable object, so it can be function or lambda expression, too. The callable
    object must have at least 3 parameters if it is provided. The first where the connection url, the second where the
    user name and the third where the password will be passed.
    If this callable object is provided then its return value will be used as a connection to the database. Otherwise
    the get_db_connection function will create a connection to it.
    If a connection name provided as first parameter which refers to a JDBC connection then this parameter will be
    ignored.
    :return:   A standard python database connection object. The user's responsibility is to close the database connection.
    :except: * ``ValueError`` either if the db configuration cannot be retrieved or
    connection attempt to the database was unsuccessful or
    the database connection name refers to a non-JDBC connection where the connection type is ``postgresql`` and the
    ``psycopg2`` library is not available/installed.
    * ``KeyError`` if the user refers to DB connection details which doesn't exist in the system.
    """

    __evaluate_parse_arguments__()

    db_connection_details = __get_db_connection_details__(jdbc_connection_name, get_project())

    if db_connection_details["custom"] and create_connection is None:
        print("Detected custom connection without connection_creation function")
        __raise_value_error__("A custom db connection requires the use of the connection_creation function")

    if __connection_url_type_is_jdbc__(db_connection_details["url"]):
        print("Detected JDBC connection -- checking requirements")
        return __jaydebeapi_connection__(db_connection_details, jdbc_connection_name)

    if create_connection is not None:
        print("Detected custom connection creation function -- checking requirements")
        return __custom_db_connection__(create_connection, db_connection_details)

    if db_connection_details["type"] == "postgresql":
        print("Detected native PostgreSQL connection -- checking requirements")
        if __is_psycopg2_importable__():
            return __psycopg2_connection__(db_connection_details, jdbc_connection_name)
        else:
            __raise_mmlibrary_error__("MMLIB_ERR_POSTGRESQL_DRIVER_MISSING",
                                      "psycopg2 library is not installed in the used Python environment.",
                                      "Install the psycopg2 library. E.g. pip install psycopg2-binary")

    if db_connection_details["type"] == "teradata":
        print("Detected native Teradata Database connection -- checking requirements")
        if __is_teradata_sql_importable__():
            return __teradata_connection__(db_connection_details, jdbc_connection_name)
        else:
            __raise_mmlibrary_error__("MMLIB_ERR_TERADATA_DRIVER_MISSING",
                                      "teradatasql library is not installed in the used Python environment.",
                                      "Install the teradatasql library. E.g. pip install teradatasql")


def __get_runtime__():
    return recipe_runtime


def __get_db_connection_details__(db_connection_name, project):
    db_data = __get_db_data__()
    db_connection_details = None
    try:
        db_connection_details = db_data[project][db_connection_name]
    except KeyError:
        __raise_value_error__("System does not have a DB connection with the given connection name = " +
                              db_connection_name + " and project = " + project)

    return db_connection_details


def __get_db_config_details__(db_type):
    db = __get_model_manager_db__()
    runtime = __get_python_runtime__()
    db_details = db["mm.dbconfigdetails"].find({'runtime': runtime})
    if db_details is None:
        __raise_value_error__("No connection found for runtime = " + runtime)

    jar_list = list()
    data_base_details = [None, None]
    for db_detail in db_details:
        if db_detail["drv_jar_location"] is not None:
            jar_list.extend(glob.glob(db_detail["drv_jar_location"] + "/*.jar"))
        if db_type == db_detail["type"]:
            data_base_details[0] = db_detail["driver_class"]

    data_base_details[1] = ":".join(jar_list)
    return data_base_details


def __get_model_manager_db__():
    mongo_db_uri = __get_mongo_db_uri__()
    client = MongoClient(mongo_db_uri)
    return client.get_default_database()


def __get_db_data__():
    db_data = __get_env_config__("db_data")

    if not isinstance(db_data, dict):
        db_data = json.loads(db_data)

    return db_data


def __get_mongo_db_uri__():
    return __get_env_config__("mongoURI")


def __get_env_config__(key):
    global env_config
    try:
        return env_config[key]
    except KeyError:
        __raise_value_error__("System does not have a value for parameter key = " + key)


def __get_python_runtime__():
    """
    Determine python runtime
    :return: 'container' for containerized environment, 'python' for 'python 3'
    """
    runtime = __get_runtime__()
    if runtime == "container":
        return 'container'
    return 'python'


def __custom_db_connection__(create_connection, db_connection_details):
    print("Creating custom connection.")

    import inspect
    if not inspect.isfunction(create_connection):
        __raise_value_error__("The create_connection parameter must be a callable object. But it is " +
                              str(type(create_connection)) + ".")

    parameter_number = len(inspect.signature(create_connection).parameters)
    if parameter_number < 3:
        __raise_value_error__("The create_connection parameter must be a callable object whose has at least 3 " +
                              "parameters but it has only " + str(parameter_number) + ".")

    connection = create_connection(db_connection_details["url"],
                                   db_connection_details["user_name"],
                                   db_connection_details["password"])
    if connection is None:
        print("Warning: the created custom connection is seems to be not a valid one.")
    else:
        print("...done.")

    return connection


def __connection_url_type_is_jdbc__(connection_url):
    return connection_url.startswith("jdbc:")


def __is_psycopg2_importable__():
    try:
        import psycopg2
        return True
    except ImportError:
        return False


def __psycopg2_connection__(db_connection_details, db_connection_name):
    print("Creating native connection to PostgreSQL Database.")

    import psycopg2
    try:
        connection = psycopg2.connect(db_connection_details["url"],
                                      user=db_connection_details["user_name"],
                                      password=db_connection_details["password"])
        print("...done.")
        return connection
    except psycopg2.Error as error:
        __raise_value_error__("Cannot connect to " + db_connection_name + ". " + str(error))


def __is_teradata_sql_importable__():
    try:
        import teradatasql
        return True
    except ImportError:
        return False


def __teradata_connection__(db_connection_details, db_connection_name):
    print("Creating native connection to Teradata Database.")

    url_components = __connection_url_components__(db_connection_details["url"])
    json_connection_string = __json_connection_string__(db_connection_details, url_components)

    import teradatasql
    try:
        connection = teradatasql.connect(json_connection_string)
        print("...done.")
        return connection
    except teradatasql.Error as error:
        __raise_value_error__("Cannot connect to " + db_connection_name + ". " + str(error))


def __connection_url_components__(url):
    import urllib.parse
    url_components = urllib.parse.urlsplit(url)

    query_string = url_components.query.split("&") if len(url_components.query) > 0 else []
    query = list(map(lambda query_element: query_element.split("="), query_string))

    return {
        "host": url_components.hostname,
        "dbs_port": str(url_components.port),
        "database": url_components.path.lstrip("/") if url_components.path.startswith("/") else url_components.path,
        "query": query
    }


def __json_connection_string__(db_connection_details, url_components):
    joined_key_value_pairs = __query_part__(url_components["query"])

    return ('{"host": "' + url_components["host"] + '",' +
            ' "dbs_port": "' + url_components["dbs_port"] + '",' +
            ' "database": "' + url_components["database"] + '",' +
            ' "user": "' + db_connection_details["user_name"] + '",' +
            ' "password": "' + db_connection_details["password"] + '"' +
            joined_key_value_pairs +
            '}')


def __query_part__(query_list):
    if len(query_list) == 0:
        return ''

    query_filter = filter(lambda list_element: len(list_element) == 2 and len(list_element[1]) > 0,
                          query_list)
    key_value_pairs = map(lambda query_key_value: '"' + query_key_value[0] + '": "' + query_key_value[1] + '"',
                          query_filter)

    from functools import reduce
    return reduce(lambda first, second: first + ", " + second, key_value_pairs, '')


def __jaydebeapi_connection__(db_connection_details, db_connection_name):
    print("Creating JDBC connection.")

    db_details = __get_db_config_details__(db_connection_details["type"])
    if db_details is None:
        __raise_value_error__("Cannot get Db config details.")

    import jaydebeapi
    try:
        connection = jaydebeapi.connect(jclassname=db_details[0],
                                        url=db_connection_details["url"],
                                        driver_args=[db_connection_details["user_name"],
                                                     db_connection_details["password"]],
                                        jars=db_details[1])
        print("...done.")
        return connection
    except:
        __raise_value_error__("Cannot connect to " + db_connection_name)


def getProject():
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_project() instead.")
    return get_project()


def get_project():
    """
    Get the ID of the associated project.
    :except: ``ValueError`` if the project name can not be found.
    """
    __evaluate_parse_arguments__()

    project = __get_json_argument__("project")
    if project is None:
        __raise_value_error__("System does not know the project")
    return project


def __get_master_node_endpoint__():
    """
    Gives back the master node endpoint.
    :except ``ValueError`` if the master node endpoint value is not stored in the ``env_config`` dictionary.
    """
    return __get_env_config__("mm_master_node_endpoint")


def returnScore(score):
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use return_score(score) instead.")
    return return_score(score)


def return_score(score):
    """
    Returns the score result.
    :param score: the value to store in the output file.
    :except ``ValueError`` if this function called from not a scoring recipe.
    """
    __evaluate_parse_arguments__()

    if not __is_scoring_run__():
        __raise_value_error__("return_score: function can only be called inside scoring recipe")

    score_json = __get_score_json__(score)

    with open(__temp_file_in_the_working_directory__(file_name="scoreresult.txt"), "w+") as f:
        f.write(score_json)
        f.close()

    return score_json


def __get_transient_resource_id__():
    return __get_json_argument__("transient_resource_id")


def __get_score_json__(score):
    score_type = 'object'
    if __is_primitive__(score):
        score_type = 'primitive'
    score_info = {'type': score_type, 'value': score}
    return json.dumps(score_info)


def __is_primitive__(result_type):
    if isinstance(result_type, int):
        return True
    if isinstance(result_type, str):
        return True
    if isinstance(result_type, bool):
        return True
    if isinstance(result_type, float):
        return True
    if result_type is None:
        return True
    return False


def getrunid():
    warnings.warn("Function has been renamed according to pep-0008 standard. "
                  "Please use get_run_id() instead.")
    return get_run_id()


def get_run_id():
    """
    Returns the run id associated with the particular step/model run.
    :except ``ValueError`` if it is called from a scoring recipe or ``secondary_id`` is not stored.
    """
    __evaluate_parse_arguments__()

    if __is_scoring_run__():
        __raise_value_error__("get_run_id: function can not be called inside scoring recipe")

    # extract additional parameters
    ids = list(__get_json_argument__('secondary_id').split("_"))
    run_id = ids[1]  # runId
    return run_id


def __is_scoring_run__():
    """
    Determine whether the current run is a scoring run.
    :return: True if it is scoring otherwise false.
    """
    step_number = __get_json_argument__("stepNumber")
    entity_number = __get_json_argument__("entityNumber")

    return step_number is None and entity_number is None


def __get_script_tmp_location__():
    """
    Returning the script location
    :return: the directory name of the script
    """
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def __temp_file_in_the_working_directory__(file_name=None):
    """
    Creating a temporary file that will be cleaned up upon a process exit
    :return: a temporary file
    """
    temp_file_name = file_name
    if temp_file_name is None:
        temp_file_name = str(uuid.uuid4())
    return os.path.join(__get_script_tmp_location__(), temp_file_name)


def __raise_value_error__(error_string):
    e = ValueError("mmlibrary: " + error_string)
    print(e)
    raise e


def __raise_mmlibrary_error__(code, description, advice):
    raise ValueError(__syntax__(
        [
            "__MMLIBRARY_ERROR_BEGINS__",
            json.dumps({
                "code": code,
                "description": description,
                "advice": advice
            }),
            "__MMLIBRARY_ERROR_ENDS__"
        ]
    ))


def __syntax__(iterable):
    return "\n".join(iterable)


if __name__ == '__main__':
    print("Executing header/installer python script")