#!/usr/bin/python

# SQLMorph API CLI Tool is licensed under the following terms:
#
#    Copyright 2020, phData, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import sys
import getopt
import argparse
import urllib.request as request
import urllib.parse as parse
import json
import time
import re
import traceback
from pathlib import Path
from schema_crawler import schema_crawler_oracle
from configparser import ConfigParser
import json

DEFAULT_API_URL = "https://toolkit.phdata.io/sqlmorph/"
# Represents a single file to be translated
class SQLInput(object):
    def __init__(self, path, contents, number, outputPath):
        self.path = path
        self.contents = contents
        self.number = number
        self.output = _calculate_output_file(path, outputPath)

def _calculate_output_file(inputPath, outputPath):
    inputPath = Path(inputPath)
    outputPath = Path(outputPath).resolve()
    absoluteInputPath = inputPath.resolve()
    if outputPath == absoluteInputPath:
        raise Exception("Output '{}' and input '{}' paths are the same".format(outputPath, absoluteInputPath))
    # if both paths are absolute, find the common prefix and remove that from the input path then join
    # the remaining portions of the input path with the output path to get the resulting output file
    # otherwise just add the relative portions of the input to the output and call it a day
    if inputPath.is_absolute():
        inputPath = inputPath.resolve() # resolve any symlinks
        commonPrefix = os.path.commonpath([outputPath, inputPath])
        prefixLen = len(commonPrefix)
        if not commonPrefix.endswith(os.sep):
          prefixLen += 1
        return outputPath.joinpath(str(inputPath)[prefixLen:])
    else:
        return outputPath.joinpath(inputPath)

def __read_directory(path, outputPath):
    results = []
    count = 1
    totalCount = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            totalCount += 1
    for root, dirs, files in os.walk(path):
        for f in files:
            path = os.path.join(root, f)
            with open(path, "r") as fh:
                contents = fh.read()
            results.append(SQLInput(path, contents, "%s/%s" % (count, totalCount), outputPath))
            count += 1
    return results

def __make_requests(baseUrl, inputs, source, target, authentication, outputPath, serverOptions, debug):
    requests = []
    for sql in inputs:
        if os.path.isfile(sql.output) and os.path.getsize(sql.output) > 0:
            sys.stderr.write("Skipping file due to existing output: %s (%s)\n" % (sql.path, sql.number))
            continue

        sys.stderr.write("Queueing file: %s (%s)\n" % (sql.path, sql.number))
        body = {
            "source": source,
            "target": target,
            "statement": sql.contents,
            "options": serverOptions
        }
        auth_header = "BEARER %s" % authentication
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = json.dumps(body).encode('utf-8')
        if debug:
            sys.stderr.write("Request: %s\n" % (data))

        myRequest = request.Request(baseUrl + "/api/v3/convert", data=data, headers=headers)
        requests.append({"input": sql, "request": myRequest})

    responses = __handle_request_queue(requests)
    return responses

def __handle_request_queue(requests):
    localRequests = requests
    responses = []

    while localRequests:
        myRequest = localRequests.pop(0)
        sqlInput = myRequest["input"]
        sys.stderr.write("Sending request to server for file: %s (%s)\n" % (sqlInput.path, sqlInput.number))
        try:
            response = request.urlopen(myRequest["request"])
            id = response.read().decode('utf-8')
            responses.append({"input": sqlInput, "id": id})
        except Exception as e:
            if 'HTTP Error 401' in str(e):
                print("Invalid Auth Token")
                sys.exit(2)
            else:
                sys.stderr.write("%s\n" % e)
                time.sleep(0.25)
            localRequests.append(myRequest)
            continue
    return responses

def __handle_responses(baseUrl, responses, authentication, target, outputPath, debug):
    responsesToProcess = responses
    allErrors = []
    while responsesToProcess:
        responseToProcess = responsesToProcess.pop(0)
        auth_header = "BEARER %s" % authentication
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        myRequest = request.Request(baseUrl + "/api/v3/convert/" + responseToProcess['id'], headers=headers)
        try:
            response = request.urlopen(myRequest)
        except Exception as e:
            if 'HTTP Error 401' in str(e):
                print("Invalid Auth Token")
                sys.exit(2)
            else:
                sys.stderr.write("%s\n" % e)
                responsesToProcess.append(responseToProcess)
                time.sleep(0.25)
            continue
        code = response.getcode()

        # if the sql hasn't finished processing, go to the next one and put back in list
        if code == 202:
            responsesToProcess.append(responseToProcess)
            continue

        #decode response and write to file
        responseRaw = response.read().decode('utf-8')
        if debug:
            sys.stderr.write("Response: %s\n" % (responseRaw))
        responseData = json.loads(responseRaw)
        sqlInput = responseToProcess["input"]
        queries = []
        queryErrors = []
        for data in responseData:
            # Validation error
            if data["translateCompilation"]["error"] is not None:
                sys.stderr.write("ERROR in file: %s\n" % sqlInput.path)
                sys.stderr.write("%s\n" % data["translateCompilation"]["error"])
                queryErrors.append(data["translateCompilation"]["error"])
            # Translation error
            if data['errors'] or data['fatals']:
                for err in data['fatals'] + data['errors']:
                    msg = err.get('message')
                    sys.stderr.write("ERROR in file: %s\n" % sqlInput.path)
                    if msg is not None:
                        sys.stderr.write("%s\n" % msg)
                        queryErrors.append(msg)
            if data["targetStmt"]:
                queries.append(data["targetStmt"])
        sys.stderr.write("Finished processing file: %s (%s)\n" % (sqlInput.path, sqlInput.number))
        sqlInput.output.parent.mkdir(parents=True, exist_ok=True)
        with sqlInput.output.open('wb') as fh:
            sys.stderr.write('Writing results to: %s\n' % (sqlInput.output))
            fh.write('\n'.join(queries).encode())
        if queryErrors:
            errorsPath = sqlInput.output.with_name(sqlInput.output.stem + '-errors.txt')
            with errorsPath.open('wb') as fh:
                sys.stderr.write('Writing errors to: %s\n' % (errorsPath))
                for queryError in queryErrors:
                    fh.write(("ERROR: %s\n\n" % queryError).encode())
        for queryError in queryErrors:
            allErrors.append({"input": sqlInput.path, "error": queryError})
    return allErrors

def __print_errors(errors):
    if errors:
        for error in errors:
            print("Error in file: %s\nReason: %s\n" % (error["input"], error["error"]))

def __collect_inputs(inputPath, outputPath):
    results = []
    if os.path.isdir(inputPath):
        results += __read_directory(inputPath, outputPath)
    elif os.path.isfile(inputPath):
        with open(inputPath, "r") as fh:
            contents = fh.read()
        results.append(SQLInput(inputPath, contents, "1/1", outputPath))
    else:
        raise Exception("Input is neither a directory or a file.")
    return results


# Read a flat properties file
def __read_property_file(path):
    # https://stackoverflow.com/questions/3595363/properties-file-in-python-similar-to-java-properties
    config = ConfigParser()
    with open(path, 'r') as fh:
        s_config= fh.read()
    s_config="[ini]\n%s" % s_config
    config.read_string(s_config)
    items=config.items('ini')
    itemDict={}
    for key,value in items:
        itemDict[key]=value
    return itemDict

def fetchSourceTarget():
    dict ={}
    prodURl= DEFAULT_API_URL + "api/v1/sourcetargetmapping"
    myRequest = request.Request(prodURl)
    response = request.urlopen(myRequest)
    responseDict = json.loads(response.read().decode('utf-8'))
    sources = set()
    targets= set()
    for source in responseDict:
        sources.add(source)
        for target in responseDict.get(source):
            targets.add(target)
    dict.update({"source":sorted(sources)})
    dict.update({"target":sorted(targets)})
    return dict

def runner(runnerArgs):
    startApp = time.time()
    sourceTarget =  fetchSourceTarget();
    parser = argparse.ArgumentParser(prog='sqlmorph_api.py', description="Utility for scripting access to the SQLMorph Api")
    parser.add_argument('--url', required=False, type=str, help="SQLMorph API Url", dest="url", default=DEFAULT_API_URL)
    parser.add_argument('--debug', help="Run the CLI in debug mode", dest="debug", action="store_true")
    requiredParams = parser.add_argument_group("required arguments")
    requiredParams.add_argument('--source', required=True, type=str, help="Source dialect", choices=sourceTarget.get("source"), dest="source")
    requiredParams.add_argument('--target', required=True, type=str, help="Target dialect", choices=sourceTarget.get("target"), dest="target")
    requiredParams.add_argument('--auth-token', required=True, type=str, help="Okta Access Token", dest="auth")
    requiredParams.add_argument('--input', required=False, type=str, help="File or directory to translate", dest="input")
    requiredParams.add_argument('--output', required=True, type=Path, help="Output directory path", dest="output")
    dbConnParams = parser.add_argument_group("database arguments")
    dbConnParams.add_argument('--db-url', type=str, help="Database connection to translate directly from a database. The string is in Oracle EZConnect format USER/PASSWORD@//hostname:port/service_name", dest="db_url")
    dbConnParams.add_argument('--db-schema', type=str, help="Schema in database to interrogate. Wildcards can be post-fixed with %%", dest="db_schema")
    dbConnParams.add_argument('--db-table', type=str, help="Table in database to interrogate. Wildcards can be post-fixed with %%", dest="db_table")
    dbConnParams.add_argument('--db-view', type=str, help="View in database to interrogate. Wildcards can be post-fixed with %%", dest="db_view")

    configOptions = parser.add_argument_group("server configuration options")
    configOptions.add_argument('--server-config', type=Path, help="Property file of server configuration options", dest="server_config")

    args = parser.parse_args(runnerArgs)
    serverOptions = {
      'format': 'true'
    }
    try:
        sys.stderr.write('\n')
        baseUrl = args.url.strip("/")
        outputPath = args.output.joinpath(args.target)

        if args.server_config:
            serverOptions.update(__read_property_file(args.server_config))
        # NOTE: I didn't find a way to make all db-* args required if input=db but that would be nicer than the post validation I do below.
        startCollectingInput = time.time()
        if args.db_url or args.db_schema or args.db_table or args.db_view:
            if args.source != 'oracle':
                raise Exception("Input is database but unsupported db type specified %s as source." % (args.db_type))
            elif not (args.db_url and args.db_schema and (args.db_table is  not None or  args.db_view is not None)):
                raise Exception("Input is database but at least one of db-url, db-schema, db-table or db-view not specified.")
            elif not schema_crawler_oracle.CX_ORACLE_IMPORT_SUCCESS:
                raise Exception("Input type of db requested but wasn't able to import cx_Oracle, try `pip install wheel cx_Oracle'")
            elif args.input:
                raise Exception("Cannot use both file/directory input and a database: --input and --db-* cannot both be specified.")
            inputPath = args.output.joinpath(args.source)
            schema_crawler_oracle.oracle_collect_sql(args.db_url, args.db_schema, args.db_table, args.db_view, inputPath) # inputPath is this functions outputPath
            inputs = __collect_inputs(inputPath, outputPath)
        else:
            inputs = __collect_inputs(args.input, outputPath)
        endCollectingInput = time.time()

        startRequests = time.time()
        responses = __make_requests(baseUrl, inputs, args.source, args.target, args.auth, outputPath, serverOptions, args.debug)
        endRequests = time.time()
        startResponses = time.time()
        errors = __handle_responses(baseUrl, responses, args.auth, args.target, outputPath, args.debug)
        endResponses = time.time()

        endApp = time.time()
        __print_errors(errors)
        sys.stderr.write("\nTotal files: %d\n" % len(inputs))
        sys.stderr.write("Total script run time: %.2fs\n" % (endApp-startApp))
        sys.stderr.write("Total input collection time: %.2fs\n" % (endCollectingInput-startCollectingInput))
        sys.stderr.write("Total request time: %.2fs\n" % (endRequests-startRequests))
        sys.stderr.write("Total response retrieval time: %.2fs\n" % (endResponses-startResponses))
    except Exception as e:
        if args.debug:
            traceback.print_exc(file=sys.stderr)
            sys.stderr.write('\n')
        sys.stderr.write("ERROR: {}\n".format(e))

def main():
    runner(sys.argv[1:])

if __name__ == "__main__":
    main()
