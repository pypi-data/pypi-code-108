#!/usr/bin/python3

# DIDIS - Desy ITk Database Interaction Script -- DESY's very own framework for interacting with the ITk Production Database
# Based on itkdb: https://gitlab.cern.ch/atlas-itk/sw/db/itkdb
# Created: 2021/11/17, Updated: 2021/11/19
# Written by Maximilian Felix Caspar, DESY HH


from loguru import logger
import argh
import os
import json
import itkdb
import mimetypes


def authenticate():
    "Check the DB login for this session."
    try:
        # Get the Pixel project contents to show that there is a connection
        client = itkdb.Client()
        client.get('listComponents', json={
            'project': 'P', 'pageInfo': {'pageSize': 32}})
        logger.info("Authentification successful")
    except itkdb.exceptions.ResponseException as e:
        logger.error("Wrong or missing login credentials")
        logger.info(
            "Set environment variables ITKDB_ACCESS_CODE1 and ITKDB_ACCESS_CODE2")


@argh.arg('-v', '--value', nargs='+', type=str)
def lookup(project: "ATLAS Subproject" = 'S',
           lookupKey: "Key that corresponds to VALUE" = 'serialNumber',
           value: "Values to look up (can be a list)" = None,
           componentType: "Type of component" = 'BT',
           returnResults: "Return lookup results (useful if not used from CLI)" = False,
           printJSON: "PrettyPrint the component JSON" = False):
    "Look up a component or list of components in the DB."
    try:
        if value is None:
            value = []
        client = itkdb.Client()
        components = client.get('listComponents', json={
                                'project': project, "componentType": componentType})
        results = {}
        logger.info(f"Looking up {lookupKey} = {value}")
        for i, comp in enumerate(components):
            if value != []:
                # If no input is given, show all components of this type
                if comp[lookupKey] in value:
                    logger.info(
                        f"Found {lookupKey} = {comp[lookupKey]}: {comp['code']}")
                    results[comp[lookupKey]] = comp
            else:
                # Search for the ones that fit the criteria
                logger.info(
                    f"Found {lookupKey} = {comp[lookupKey]}: {comp['code']}")
                results[str(comp[lookupKey])] = comp
        print("I'm here...")
        if printJSON:
            for k in results:
                print(json.dumps(results[k], indent=1))
        if returnResults or __name__ != '__main__':
            return results
    except:
        logger.error("Error while trying to get connection to DB")
        logger.info(
            "Are environment variables ITKDB_ACCESS_CODE1 and ITKDB_ACCESS_CODE2 set?")


def attach(file: "Path of the file to upload",
           component: "Component code (NOT the ATLAS SN, use lookup for that)",
           title: "Title of the file" = "",
           description: "A file description" = "",
           filetype: "File MIME type (sript can usually guess this)" = None):
    "Attach a file to a component in the DB."
    try:
        client = itkdb.Client()
        if filetype is None:
            # If you can't be bothered to look up the MIME type,
            # we'll look it up for you :)
            filetype = mimetypes.guess_type(file)
        data = {
            'component': component,
            'title': title,
            'description': description,
            'type': 'file',
            'url': file,
        }
        # Get attachment data
        attachment = {'data': (os.path.basename(
            file), open(file, 'rb'), filetype)}

        client.post('createComponentAttachment',
                    data=data, files=attachment)
        logger.info(f"Attached file {file} to {component}")
    except:
        logger.error("Error while trying to get connection to DB")
        logger.info(
            "Are environment variables ITKDB_ACCESS_CODE1 and ITKDB_ACCESS_CODE2 set?")


def register(component: "Component to register (path to .json file or dict)"):
    "Register a new component"
    if isinstance(component, str) and os.path.isfile(component):
        logger.info(f"Loading component definition from file {component}")
        with open(component) as jsonFile:
            component = json.load(jsonFile)
            jsonFile.close()
    elif isinstance(component, dict):
        logger.info("Component definition was passed as a dict")
    else:
        logger.error(f"Unrecognised input {component}")
        return
    try:
        client = itkdb.Client()
        client.post('registerComponent', json=component)
        logger.info(f"Registered new component")
    except:
        logger.error(
            f"Unable to register component in the DB, is the format correct?")


def tests(componentType: "Type of component" = "BT",
          project: "ATLAS Subproject" = 'S',
          returnResults: "Return available tests (useful if not used from CLI)" = False):
    "Get a list of available tests for a component."
    logger.info(f"Polling for test types for {componentType}")
    try:
        client = itkdb.Client()
        out = client.get("listTestTypes", json={
            'project': project, "componentType": componentType})
        logger.info("Test type and required results:")
        result = {}
        for i, test in enumerate(out):
            result[test['code']] = test
            if not returnResults:
                print(test['code'], ":", test['name'])
                for p in test['parameters']:
                    print("  ", p['code'], ":", p['name'])
        if returnResults or __name__ != '__main__':
            return result
    except:
        logger.error("Error while trying to get connection to DB")
        logger.info(
            "Are environment variables ITKDB_ACCESS_CODE1 and ITKDB_ACCESS_CODE2 set?")


def stage(lookupValue: "Value to look up (must be unique in the DB!)",
          stage: "Production stage to set",
          project: "ATLAS Subproject" = 'S',
          lookupKey: "Key that corresponds to VALUE" = 'serialNumber',
          componentType: "Type of component" = 'BT',
          comment: "Reason for production stage change" = ""):
    "Set or look up production stage for a component."
    logger.info(f"Getting component from the DB")
    component = lookup(project=project, lookupKey=lookupKey, value=[
                       lookupValue], componentType=componentType, returnResults=True)
    if len(component) == 0:
        logger.error(
            "No components that match the criteria were found in the DB")
        raise LookupError
    elif len(component) > 1:
        logger.error(
            "More than 1 component that match the criteria was found")
        raise LookupError
    component = component[lookupValue]
    if stage == "":
        logger.info(
            f"Current production stage: {component['currentStage']['code']}")
        return
    client = itkdb.Client()
    data = {
        'component': component['code'],
        'stage': stage,
    }
    if comment != "":
        data['comment'] = comment
    try:
        client.post('setComponentStage', data=data)
        logger.info(f"Set stage to {stage}")
    except:
        logger.error(
            f"DB error, is {stage} a valid stage for {componentType}?")


def skeleton(test: "Type of test",
             componentType: "Type of component" = "BT",
             project: "ATLAS Subproject" = 'S',
             returnResults: "Return available tests (useful if not used from CLI)" = False):
    "Genereate a test skeleton for a given test. Otput is either as JSON to the CLI or as a dict as a return value."
    allTests = tests(componentType=componentType,
                     project=project, returnResults=True)
    if not test in allTests:
        logger.error(f"Unable to find {test} for {componentType}")
    skeleton = {
        'runNumber': '0-0',
        'component': None,
        'results':
        {
        },
        'properties':
        {
        },
        'passed': False,
        'problems': False,
        'testType': test,
        'institution': None
    }

    for v in allTests[test]["properties"]:
        skeleton["properties"][v["code"]] = None
    for v in allTests[test]["parameters"]:
        skeleton["results"][v["code"]] = None

    if returnResults or __name__ != '__main__':
        return skeleton
    else:
        print(json.dumps(allTests[test], indent=1))


def upload(result: "Results from the test (path to .json file or dict)"):
    "Upload a test result to the DB."
    if isinstance(result, str) and os.path.isfile(result):
        logger.info(f"Loading test result from file {result}")
        with open(result) as jsonFile:
            result = json.load(jsonFile)
            jsonFile.close()
    elif isinstance(result, dict):
        logger.info("Test result was passed as a dict")
    else:
        logger.error(f"Unrecognised input {result}")
        return
    try:
        client = itkdb.Client()
        client.post('uploadTestRunResults', json=result)
        logger.info(
            f"Uploaded {result['testType']} results for {result['component']} to the DB")
    except:
        logger.error(f"Unable to upload result to DB, is the format correct?")

def testruns(cid: "Component ID",
             returnResults: "Return lookup results (useful if not used from CLI)" = False,
             printJSON: "PrettyPrint the component JSON" = False):
    "Look up all test results associated with a component ID."
    try:
        logger.info(f"Looking up tests in CID = {cid}")
        client = itkdb.Client()
        runs = client.get('listTestRunsByComponent', json={'component' : cid})
        results = {}
        for i, testres in enumerate(runs):
            logger.info(f"Found {testres['testType']['name']} with ID = {testres['id']}")
            results[testres['id']] = testres
        if printJSON:
            for k in results:
                print(json.dumps(results[k], indent=1))
        if returnResults or __name__ != '__main__':
            return results
    except:
        logger.error("Error while trying to get connection to DB")
        logger.info(
            "Are environment variables ITKDB_ACCESS_CODE1 and ITKDB_ACCESS_CODE2 set?")



def main():
    parser = argh.ArghParser()
    parser.add_commands([authenticate, register, lookup,
                        attach, tests, stage, skeleton, upload, testruns])
    parser.dispatch()


if __name__ == '__main__':
    main()
