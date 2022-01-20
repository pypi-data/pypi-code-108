import json
import yaml
import requests
from . import morph_log
import glob
from os import path
import os



def updateWhiteLabel (baseURL, bearerToken, yaml_file):
    logger = morph_log.get_logger('uwhlabel')
    headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
    files = glob.glob(yaml_file)
    url = baseURL+'/api/whitelabel-settings'
    for file in files:
        yaml_file = file
        logger.info('Current file: '+yaml_file)
        with open(yaml_file) as f:
            try:
                result = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                logger.error(exc)
                logger.error('Was unable to load the yaml file.')
        enabled = result['enabled']
        applianceName = result['applianceName']
        headerBgColor = result['headerBgColor']
        footerBgColor = result['footerBgColor']
        loginBgColor = result['loginBgColor']
        disableSupportMenu = result['disableSupportMenu']

        payload = json.dumps({"whitelabelSettings": {
                                "enabled": enabled,
                                "applianceName": applianceName,
                                "disableSupportMenu": disableSupportMenu,
                                "headerBgColor": headerBgColor,
                                "footerBgColor": footerBgColor,
                                "loginBgColor": loginBgColor}})
        whitelabelStatus = requests.request('PUT', url, verify=False, headers=headers, data=payload)
        print(whitelabelStatus.text)

def updateLogoHeader(baseURL, bearerToken, logoHeader):
    logger = morph_log.get_logger('ulogohead')
    headers = {'Authorization': 'Bearer ' +bearerToken}
    url = baseURL+'/api/whitelabel-settings/images'
    files = {'headerLogo.file' : open(logoHeader, 'rb')}
    payload = {}
    result = requests.request('POST', url, verify=False, headers=headers, files=files, data=payload)
    logger.info(result.text)
def updateLogoFooter(baseURL, bearerToken, logoFooter):
    logger = morph_log.get_logger('ulogofoot')
    headers = {'Authorization': 'Bearer ' +bearerToken}
    url = baseURL+'/api/whitelabel-settings/images'
    files = {'footerLogo.file' : open(logoFooter, 'rb')}
    payload = {}
    result = requests.request('POST', url, verify=False, headers=headers, files=files, data=payload)
    logger.info(result.text)

def updateLogoLogin(baseURL, bearerToken, logoLogin):
    logger = morph_log.get_logger('ulogolog')
    headers = {'Authorization': 'Bearer ' +bearerToken}
    url = baseURL+'/api/whitelabel-settings/images'
    files = {'loginLogo.file' : open(logoLogin, 'rb')}
    payload = {}
    result = requests.request('POST', url, verify=False, headers=headers, files=files, data=payload)
    logger.info(result.text)




#    curl -XPOST "$serverUrl/api/whitelabel-settings/images" \
#  -H "Authorization: BEARER access_token" \
##  -F 'headerLogo.file=@filename.png;type=image/png' \
##  -F 'footerLogo.file=@filename.png;type=image/png' \
#  -F 'loginLogo.file=@filename.png;type=image/png' \
#  -F 'favicon.file=@filename.ico;type=image/ico'