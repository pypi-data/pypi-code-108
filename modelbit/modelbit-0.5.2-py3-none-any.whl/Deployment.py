from ._Utils import _Utils
from ._Globals import anyAuthenticatedSession

class Deployment:
  _requirementsTxt = None
  _deployName = None
  _deployFunc = None
  _pythonVersion = '3.9' # Default version

  STATUS_DEPLOYABLE = 'Ready to Deploy'
  STATUS_NOT_DEPLOYABLE = 'Not Ready to Deploy'

  ALLOWED_PY_VERSIONS = ['3.6', '3.7', '3.8', '3.9']
  CODE_STYLE = "font-family: monospace; font-size: 0.95em; font-weight: medium; color: #714488;"

  MAX_REQUIREMENTS_TXT = 20_000

  # Keep these kwargs in sync with __init__.py/.Deployment(...)
  def __init__(self, name = None, deploy_function = None, python_version = None):
    if name != None: self.set_name(name)
    if deploy_function != None: self.set_deploy_function(deploy_function)
    if python_version != None: self.set_python_version(python_version)

  def _repr_markdown_(self):
    return self._describe()

  def set_name(self, name):
    import re
    if not re.match('^[a-zA-Z0-9_]+$', name):
      raise Exception("Deployment names should be alphanumeric with underscores.")
    self._deployName = name
    return self

  def set_python_version(self, version):
    if version not in self.ALLOWED_PY_VERSIONS:
      return self._selfError(f'Python version should be one of {self.ALLOWED_PY_VERSIONS}.')
    self._pythonVersion = version
    return self

  def set_requirements_txt(self):
    from ipywidgets import FileUpload
    from IPython.display import display, clear_output
    import re
    upload = FileUpload(accept='.txt', multiple=False)
    display(upload)
    def onUploadChange(change):
        clear_output(wait=True)
        for k,v in change['new'].items():
          content = v['content'].decode('utf-8')
          if len(content) < self.MAX_REQUIREMENTS_TXT:
            self._requirementsTxt = content
            session = anyAuthenticatedSession()
            if session:
              session._getJson("jupyter/v1/deployments/prep_environment", {
                "environment": {
                  "requirementsTxt": self._requirementsTxt,
                  "pythonVersion": self._pythonVersion
                }
              })
          else:
            _Utils._printError("The requirements.txt file is too large.")
        _Utils._printMk(self._describe())
    upload.observe(onUploadChange, names=['value'])
    return None

  def set_deploy_function(self, func):
    self._deployFunc = func
    if callable(func) and self._deployName == None: self.set_name(func.__name__)
    return self

  def _deploy(self, mbMain):
    status = self._getStatus()
    if status['status'] != self.STATUS_DEPLOYABLE:
      _Utils._printError('Unable to deploy.')
      return self
    resp = mbMain._getJsonOrPrintError("jupyter/v1/deployments/create", {
      "deployment": {
        "name": self._deployName,
        "pyState": {
          **self._getFuncProps(self._deployFunc),
          "requirementsTxt": self._requirementsTxt,
          "pythonVersion": self._pythonVersion
        }}})
    if resp and "deployOverviewUrl" in resp:
      if "message" in resp: _Utils._printMk(resp["message"])
      _Utils._printMk(f'<a href="{resp["deployOverviewUrl"]}" target="_blank">View status and integration options.</a>')
    elif resp:
      _Utils._printMk(f'Error while deploying. ({resp})')
    return None

  def _selfError(self, txt):
    _Utils._printError(txt)
    return None

  def _describe(self):
    nonStr = '(None)'
    def codeWrap(txt):
      if txt == nonStr: return nonStr
      return self._wrapStyle(txt, self.CODE_STYLE)

    status = self._getStatus()
    statusWithStyle = self._wrapStyle(status["status"], status["style"])
    md = ""
    if self._deployName != None: md += f'**{self._deployName}**: '
    md += f'{statusWithStyle}\n\n'
    statusList = "\n".join([f'* {n}' for n in status["notes"]])
    if len(statusList) > 0: md += statusList + "\n\n"

    md += "| Property | Value |\n" + "|:-|:-|\n"
    funcProps = self._getFuncProps(self._deployFunc)
    funcSig = nonStr
    argsDesc = nonStr
    nsFuncs = nonStr
    nsVars = nonStr
    nsImports = nonStr
    if funcProps != None:
      if 'name' in funcProps and 'argNames' in funcProps:
        funcSig = f"{funcProps['name']}({', '.join(funcProps['argNames'])})"
      if 'namespaceFunctions' in funcProps and len(funcProps['namespaceFunctions']) > 0:
        nsFuncs = "<br/>".join([k for k,_ in funcProps['namespaceFunctions'].items()])
      if 'namespaceVarsDesc' in funcProps and len(funcProps['namespaceVarsDesc']) > 0:
        nsVars = "<br/>".join([f'{k}: {v}' for k,v in funcProps['namespaceVarsDesc'].items()])
      if 'namespaceImports' in funcProps and len(funcProps['namespaceImports']) > 0:
        nsImports = "<br/>".join([f'{v} as {k}' for k,v in funcProps['namespaceImports'].items()])
    md += f"| Function | {codeWrap(funcSig)} |\n"
    if nsFuncs != nonStr: md += f"| Helpers | {codeWrap(nsFuncs)} |\n"
    if nsVars != nonStr: md += f"| Values | {codeWrap(nsVars)} |\n"
    if nsImports != nonStr: md += f"| Imports | {codeWrap(nsImports)} |\n"
    md += f"| Python Version | {codeWrap(self._pythonVersion or nonStr)} |\n"

    deps = nonStr
    if self._requirementsTxt and len(self._requirementsTxt) > 0:
      depsList = self._requirementsTxt.splitlines()
      maxDepsShown = 7
      if len(depsList) > maxDepsShown:
        deps = "<br/>".join([d for d in depsList[:maxDepsShown]])
        numLeft = len(depsList) - maxDepsShown
        deps += f'<br/><span style="font-style: italic;">...and {numLeft} more.</span>'
      else:
        deps = "<br/>".join([d for d in depsList])
    md += f"| requirements.txt | {codeWrap(deps)} |\n"
    return md

  def _getFuncProps(self, func):
    import inspect
    errors = []
    props = {}
    if not callable(func):
      errors.append('The deploy_function parameter does not appear to be a function.')
    else:
      props['name'] = func.__name__
      props['source'] = inspect.getsource(func)
      props['argNames'] = list(func.__code__.co_varnames[:func.__code__.co_argcount] or [])
      props['argTypes'] = self._annotationsToTypeStr(func.__annotations__)
      nsCollection = { "functions": {}, "vars": {}, "imports": {} }
      self._collectNamespaceDeps(func, nsCollection)
      props['namespaceFunctions'] = nsCollection["functions"]
      props['namespaceVars'] = self._pickleValues(nsCollection["vars"])
      props['namespaceVarsDesc'] = self._strValues(nsCollection["vars"])
      props['namespaceImports'] = nsCollection["imports"]
    if len(errors) > 0: props['errors'] = errors
    return props

  def _annotationsToTypeStr(self, annotations):
    annoStrs = {}
    for name, tClass in annotations.items():
      annoStrs[name] = tClass.__name__
    return annoStrs

  def _collectNamespaceDeps(self, func, collection):
    import inspect
    if not callable(func): return collection
    globalsDict = func.__globals__
    for maybeFuncVarName in func.__code__.co_names:
      if maybeFuncVarName in globalsDict:
        maybeFuncVar = globalsDict[maybeFuncVarName]
        if str(maybeFuncVar).startswith('<function'):
          argNames = list(maybeFuncVar.__code__.co_varnames or [])
          funcSig = f"{maybeFuncVar.__name__}({', '.join(argNames)})"
          if funcSig not in collection["functions"]:
            collection["functions"][funcSig] = inspect.getsource(maybeFuncVar)
            self._collectNamespaceDeps(maybeFuncVar, collection)
        elif str(maybeFuncVar).startswith('<module'):
          collection["imports"][maybeFuncVarName] = maybeFuncVar.__name__
        else:
          collection["vars"][maybeFuncVarName] = maybeFuncVar

  def _getStatus(self):
    notes = []
    if not self._deployName:
      cmd = self._wrapStyle(".set_name('name')", self.CODE_STYLE)
      notes.append(f'Run {cmd} to specify the deployment\'s name.')
    if not self._deployFunc:
      cmd = self._wrapStyle(".set_deploy_function(func, args = {\"arg1\": value1, ...})", self.CODE_STYLE)
      notes.append(f'Run {cmd} to specify the deployment\'s runtime.')
    else:
      funcProps = self._getFuncProps(self._deployFunc)
      if 'errors' in funcProps: notes.extend(funcProps['errors'])
    if not self._pythonVersion:
      cmd = self._wrapStyle(".set_python_version('version')", self.CODE_STYLE)
      notes.append(f'Run {cmd} to set the python version to one of {self.ALLOWED_PY_VERSIONS}.')
    if len(notes) > 0:
      return { "status": self.STATUS_NOT_DEPLOYABLE, "style": "color:gray; font-weight: bold;", "notes": notes }
    else:
      cmd = self._wrapStyle("mb.deploy(dep)", self.CODE_STYLE)
      notes.append(f'Run {cmd} to deploy this function to Modelbit.')
      return { "status": self.STATUS_DEPLOYABLE, "style": "color:green; font-weight: bold;", "notes": notes }

  def _wrapStyle(self, text, style):
    return f'<span style="{style}">{text}</span>'

  def _pickleValues(self, args):
    import pickle, codecs
    newDict = {}
    for k, v in args.items():
      newDict[k] = codecs.encode(pickle.dumps(v), "base64").decode()
    return newDict

  def _strValues(self, args):
    newDict = {}
    for k, v in args.items():
      newDict[k] = str(v)
    return newDict
