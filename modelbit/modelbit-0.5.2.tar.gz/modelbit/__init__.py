__version__ = "0.5.2"
__author__ = 'Modelbit'

from ._Globals import rememberSession
from ._MbDatasets import _MbDatasets
from ._MbWarehouses import _MbWarehouses
from .Deployment import Deployment
from ._Utils import _Utils
class __Modelbit:

  _API_HOST = 'https://app.modelbit.com/'
  _LOGIN_HOST = _API_HOST
  _API_URL = None
  _MAX_DATA_LEN = 10000000
  _state = {
    "notebookEnv": {
      "userEmail": "",
      "signedToken": "",
      "uuid": "",
      "authenticated": False,
      "workspaceName": "",
      "mostReventVersion": ""
    }
  }
    
  def __init__(self):
    import os
    if os.getenv('MB_JUPYTER_API_HOST'):
      self._API_HOST = os.getenv('MB_JUPYTER_API_HOST')
    if os.getenv('MB_JUPYTER_LOGIN_HOST'):
      self._LOGIN_HOST = os.getenv('MB_JUPYTER_LOGIN_HOST')
    self._API_URL = f'{self._API_HOST}api/'

  def _isAuthenticated(self, testRemote=True):
    if testRemote and not self._isAuthenticated(False):
      data = self._getJson("jupyter/v1/login")
      if 'error' in data:
        _Utils._printError(data["error"])
        return False
      self._state["notebookEnv"] = data["notebookEnv"]
      return self._isAuthenticated(False)
    return self._state["notebookEnv"]["authenticated"]


  def _getJson(self, path, body = {}):
    import requests, json
    try:
      data = {
        "requestToken": self._state["notebookEnv"]["signedToken"],
        "version": __version__
      }
      data.update(body)
      dataLen = len(json.dumps(data))
      if (dataLen > self._MAX_DATA_LEN):
        return {"error": f'API Error: Request is too large. (Request is {_Utils._sizeof_fmt(dataLen)} Limit is {_Utils._sizeof_fmt(self._MAX_DATA_LEN)})'}
      with requests.post(f'{self._API_URL}{path}', json=data) as url:
        json = url.json()
        self._state["notebookEnv"] = json["notebookEnv"]
        return json
    except BaseException as err:
      return {"error": f'Unable to reach Modelbit. ({err})'}

  def _getJsonOrPrintError(self, path, body = {}):
    data = self._getJson(path, body)
    if not self._isAuthenticated():
      self._login()
      return False
    if 'error' in data:
      _Utils._printError(data["error"])
      return False
    return data

  def _maybePrintUpgradeMessage(self):
    latestVer = self._state["notebookEnv"]["mostRecentVersion"]
    nbVer = __version__
    if latestVer and latestVer.split('.') > nbVer.split('.'):
      pipCmd = '<span style="color:#E7699A; font-family: monospace;">pip install --upgrade modelbit</span>'
      _Utils._printMk(f'Please run {pipCmd} to upgrade to the latest version. ' + 
        f'(Installed: <span style="font-family: monospace">{nbVer}</span>. ' + 
        f' Latest: <span style="font-family: monospace">{latestVer}</span>)')

  def _printAuthenticatedMsg(self):
    connectedTag = '<span style="color:green; font-weight: bold;">connected</span>'
    email = self._state["notebookEnv"]["userEmail"]
    workspace = self._state["notebookEnv"]["workspaceName"]
    
    _Utils._printMk(f'You\'re {connectedTag} to Modelbit as {email} in the \'{workspace}\' workspace.')
    self._maybePrintUpgradeMessage()

  def _login(self):
    if self._isAuthenticated(True):
      self._printAuthenticatedMsg()
      return

    displayUrl = f'modelbit.com/t/{self._state["notebookEnv"]["uuid"]}'
    linkUrl = f'{self._LOGIN_HOST}/t/{self._state["notebookEnv"]["uuid"]}'
    aTag = f'<a style="text-decoration:none;" href="{linkUrl}" target="_blank">{displayUrl}</a>'
    helpTag = '<a style="text-decoration:none;" href="https://doc.modelbit.com/getting-started.html" target="_blank">Learn more.</a>'
    _Utils._printMk('**Connect to Modelbit**<br/>' +
      f'Open {aTag} to authenticate this kernel, then re-run this cell. {helpTag}')
    self._maybePrintUpgradeMessage()

  # Public APIs
  def datasets(self): return _MbDatasets(self)
  def get_dataset(self, dataset_name): return _MbDatasets(self).get(dataset_name)
  def warehouses(self): return _MbWarehouses(self)
  def Deployment(self, name = None, deploy_function = None, python_version = None):
    return Deployment(name, deploy_function, python_version)

  def deploy(self, deployment, name = None, python_version = None):
    if not self._isAuthenticated():
      self._login()
      return
    if callable(deployment):
      dep = Deployment(name, deployment, python_version)
      return dep._deploy(self)
    else:
      return deployment._deploy(self)

def login():
  _modelbit = __Modelbit()
  _modelbit._login()
  rememberSession(_modelbit)
  return _modelbit
