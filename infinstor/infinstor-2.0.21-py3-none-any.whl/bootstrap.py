import os
import urllib.parse
import builtins
import requests
from requests.exceptions import HTTPError

def _bootstrap_config_values_from_mlflow_rest_if_needed():
    ##########
    #  TODO: a copy exists in infinstor-mlflow/plugin/infinstor_mlflow_plugin/new_login.py and infinstor-jupyterlab/server-extention/jupyterlab_infinstor/cognito_utils.py.  Need to see how to share code between two pypi packages to eliminate this duplication
    #  when refactoring this code, also refactor the copies
    ############
    
    # if the configuration values have already been bootstrapped, return
    if getattr(builtins, 'mlflowserver', None): return
    
    # note that this code (server-extension code) runs in the jupyterlab server, where MLFLOW_TRACKING_URI was not set earlier.  Now it needs to be set correctly to the mlflow api hostname: mlflow.infinstor.com.  Note that 'mlflow' in the hostname is not hardcoded.. it can be a different subdomain name
    #
    muri = os.getenv('MLFLOW_TRACKING_URI')
    pmuri = urllib.parse.urlparse(muri)
    if (pmuri.scheme.lower() != 'infinstor'):
        raise Exception(f"environment variable MLFLOW_TRACKING_URI={muri} has an invalid value or the url scheme != infinstor.  Set the environment variable correctly and restart the process")
    cognito_domain = pmuri.hostname[pmuri.hostname.index('.')+1:]
    url = 'https://' + pmuri.hostname + '/api/2.0/mlflow/infinstor/get_version'
    
    headers = { 'Authorization': 'None' }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resp = response.json()
        builtins.clientid = resp['cognitoCliClientId']
        builtins.appclientid = resp['cognitoAppClientId']
        builtins.mlflowserver = resp['mlflowDnsName'] + '.' + cognito_domain
        builtins.mlflowuiserver = resp['mlflowuiDnsName'] + '.' + cognito_domain
        builtins.mlflowstaticserver = resp['mlflowstaticDnsName'] + '.' + cognito_domain
        builtins.apiserver = resp['apiDnsName'] + '.' + cognito_domain
        builtins.serviceserver = resp['serviceDnsName'] + '.' + cognito_domain
        builtins.service = cognito_domain
        builtins.region = resp['region']        
    except HTTPError as http_err:
        builtins.log.error(f"Caught Exception: {http_err}: {traceback.format_exc()}" )
        return None
    except Exception as err:
        builtins.log.error(f"Caught Exception: {err}: {traceback.format_exc()}" )
        return None


