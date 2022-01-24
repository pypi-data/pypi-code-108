import json
import yaml
import requests
import os
import glob
from . import morph_log
from .classes import MorphConfig

def cypherCreate(baseURL, yaml_file):
    logger = morph_log.get_logger('crCypher')
    morphApi= MorphConfig()
    #url = morphApi.searchGroupsName()
    header = morphApi.header_appJson()
    verifySSL = morphApi.verify()
    #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
    files = glob.glob(yaml_file)
    for file in files:
        yaml_file = file
        logger.info('Current file: '+yaml_file)
        with open(yaml_file) as f:
            try:
                result=yaml.safe_load(f)
            except yaml.YAMLError as exc:
                logger.error(exc)
                logger.error("Was unable to load the yaml file.")
        for k, v in result['cypher'].items():
            name = result['cypher'][k]['name']
            secret = result['cypher'][k]['secret']
            checkCypher = baseURL+"/api/cypher/v1/secret/"+name
            checkCypher = requests.request("GET", checkCypher, verify=False, headers=header)
            checkCypherResult = json.loads(checkCypher.text)
            cypherPasswordStatus = checkCypherResult["success"]
            if cypherPasswordStatus == True:
                logger.info("Cypher "+name+" Already Exists Skipping...")
                cypherPassword = json.loads(checkCypher.text)
                cypherPassword = cypherPassword["data"]
            else:
                logger.info("Cypher "+name+" Not Found Creating")
                url = baseURL+'/api/cypher/v1/secret/'+name+'?type=string&ttl=0'
                payload=json.dumps({'value': secret})
                cypherPasswordCreate = requests.request("POST", url, verify=verifySSL, headers=header, data=payload)