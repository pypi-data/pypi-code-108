import pandas as pd
import json
import os
from gql import gql, Client#, AIOHTTPTransport, RequestsHTTPTransport # This is gql version 3
from gql.transport.requests import RequestsHTTPTransport
from loguru import logger

from .utils.ut_autprog import AutProgUtils
from .utils.ut import Utils

class Programming():

    def __init__(self, accessToken:str, endpoint:str) -> None:
            
        header = {
            'authorization': 'Bearer ' + accessToken
        }
        
        transport =  RequestsHTTPTransport(url=endpoint, headers=header, verify=True)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

        return

    def functions(self) -> pd.DataFrame:
        """ Get available programming service functions"""

        graphQLString = f'''query functions {{
            functions {{
                name
                functionId
                languageVersion
                }}
            }}
        '''
    
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pd.json_normalize(result['functions'])
        return df

    def createFunction(self, name:str, languageVersion:str, description:str=None, 
        files:list=None, deploy:bool=False, deploymentName:str=None, envVars:dict=None,
        memoryLimit:str='250M', cpuLimit:float=0.2) -> str:
        """ 
        Creates a function with possibility to commit files and deployment
        in one step. The function Id is returned.

        Parameters:
        ----------
        name : str
            The name of the function, which is also taken for deployment, if the option is 
            chosen. The deployment function name is converted to small letters. Special characters 
            will be removed.
        languageVersion : str
            Choose between a languange and its version, e.g. 'PYTHON_3_9' and 'CSHARP_NET_5_0'.
        description : str
            Additional description to the function.
        files : list
            A list of full file paths to be committed.
        deploy : bool
            If True, the function will be deployed. The files argument must not be 
            None in this case.
        deploymentName:
            The name of the deployed function. If left to default (None) the function name 
            will be used. Use small letters only and no special characters.
        envVars : dict
            A Dictionary of Environment variables provided to the deployment function. All values
            will be converted to string.

        Examples of a function for Python:
        ---------
        >>> createFunction('myfunction', 'PYTHON_3_9')
        >>> files = [path1, path2, path3]
            vars = {'var1': 42, 'var2': 'full_scale'}
            createFunction('myfunction', 'PYTHON_3_9', files=files, deploy=True, 
                envVars=vars)
        """

        graphQLString = f'''mutation createFunction {{
            createFunction(input:{{
                name: "{name}"
                languageVersion: {languageVersion}
                description: "{description}"

                }}) {{
                functionId
                errors {{
                    message
                    code
                    }}
                }}
            }}
        '''
    
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result['createFunction']['errors']:
            Utils._listGraphQlErrors(result, 'createInventory')
            return

        functionId = result['createFunction']['functionId']

        if files == None: 
            logger.info(f"Function with id {functionId} created. No files comitted")
            return functionId
        else:
            if type(files) != list:
                logger.error("Files must be of type list!")
            self.commitFunctionFiles(functionId, files)
            logger.info(f"Function with id {functionId} created.")
            if deploy == False:
                return functionId
            else:
                if deploymentName == None:
                    deploymentName = name.lower()
                self.deployFunction(functionId, deploymentName, envVars, memoryLimit, cpuLimit)
                return functionId

    def commitFunctionFiles(self, functionId:str, files:list=None, deploy:bool=False, 
        deploymentName:str=None, envVars:dict=None, memoryLimit:str='250M', cpuLimit:float=0.2) -> None:
        """
        Upload programming files to an existing function. 

        Parameters:
        ----------
        functionId : str
            Id of an existing function.
        files : list
            A list of full file paths to be committed.
        deploy : bool
            If True, the function will be deployed, after commintg the files. 
        deploymentName:
            The name of the deployed function. Use small letters only and no special characters.
        envVars : dict
            A Dictionary of Environment variables provided to the deployment function. All values
            will be converted to string.
        memoryLimit: str = '250M'
            The memory that is assigned for execution of this function. 
        cpuLimit: loat = 0.2
            The assigned amount of CPU capacity to this function: note, that a too high capacity
            might affect other services negatively.


        Example:
        --------
        >>> files = [path1, path2, path3]
            vars = {'var1': 42, 'var2': 'full_scale'}
            commitFunctionFiles('3dba276e3c8645838c2d598043cab057', files=files, deploy=True, 
                deploymentName='myfunction', envVars=vars)
        """

        fileList = AutProgUtils._upsetFiles(files)
        if fileList == None: return

        graphQLString = f'''mutation commitFunctionFiles {{
            commitFunctionFiles(input:{{
                functionId: "{functionId}"
                upsetFiles: [
                    {fileList}
                ]

                }}) {{
                errors {{
                    message
                    code
                    }}
                }}
            }}
        '''
    
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: 
            return
        else:
            logger.info(f"Committed files: {AutProgUtils._getFileNames(files)}")
            if deploy == False:
                return functionId
            else:
                if deploymentName == None:
                    logger.error(f"No deployment name was provided for deployment. Function id: {functionId}")
                self.deployFunction(functionId, deploymentName, envVars, memoryLimit, cpuLimit)

        return result

    def deployFunction(self, functionId:str, deploymentName:str, envVars:dict=None,
        memoryLimit:str='250M', cpuLimit:float=0.2):
        """
        Deploys a function to make it executable.

        Parameters:
        ----------
        functionId: str
            Id of an existing function.
        deploymentName:
            The name of the deployed function. Use small letters only and no special characters.
        envVars: dict = None
            A Dictionary of Environment variables provided to the deployment function. 
        memoryLimit: str = '250M'
            The memory that is assigned for execution of this function.   
        cpuLimit: loat = 0.2
            The assigned amount of CPU capacity to this function: note, that a too high capacity
            might affect other services negatively.

        Example:
        --------
        >>> vars = {'exec_timeout': '2m', 'read_timeout': '2m','write_timeout': '2m'}
            deployFunction('3dba276e3c8645838c2d598043cab057', deploymentName=myfunction, 
            automationTopic='autFunction', envVars=vars)
        """

        if envVars == None:
            _vars = ''
        else:
            _vars = AutProgUtils._varsToString(envVars, 'env')

        graphQLString = f'''mutation deployFunction {{
            deployFunction(
                input: {{
                functionId: "{functionId}"
                functionName: "{deploymentName}"
                memoryLimit: "{memoryLimit}"
                cpuLimit: "{str(cpuLimit)}"
                {_vars}
                }}
            ) {{
                deploymentId
                errors {{
                    code
                    message
                    }}
                }}
            }}
            '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: 
            return
        else:
            deploymentId = result['deployFunction']['deploymentId']
            logger.info(f"Deployed function with deploymentId {deploymentId}")
            return deploymentId

    def functionFiles(self, functionId:str, downloadPath:str=None) -> pd.DataFrame:
        """
        Shows files of a function.

        Parameters:
        ----------
        functionId : str
            Id of an existing function.

        Example:
        --------
        >>> functionFiles('3dba276e3c8645838c2d598043cab057')
        """

        if downloadPath == None:
            _contentBase64 = ''
        else:
            _contentBase64 = 'contentBase64'
            
        graphQLString = f''' query functionFiles {{
            functionFiles (functionId: "{functionId}") {{
                version
                files {{
                    fullname
                    {_contentBase64}
                    }}
                }}
            }}
        '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pd.json_normalize(result['functionFiles'], meta=['version'], record_path=['files'])

        if downloadPath != None:
            if os.path.exists(downloadPath) == False:
                logger.error(f"Download path '{downloadPath}' does not exist.")
            else:
                fileList = []
                for file in result['functionFiles']['files']:
                    AutProgUtils._downloadFunctionFile(downloadPath, file['fullname'], file['contentBase64'])
                    fileList.append(file['fullname'])
                logger.info(f"Downloaded {fileList} to {downloadPath}")
                del df['contentBase64']
        
        return df

    def executeFunction(self, deploymentId:str, inputVariables:dict=None) -> str:
        """
        Executes a function and returns its execution id
        
        Parameters:
        ----------
        deploymentId : str
            Id of a deployment. Can be retrieved by Programming.deployments().

        Example:
        --------
        >>> executeFunction('c877cc1b568a4c489aacdb4538b3f544')
        """

        if inputVariables == None:
            _vars = ''
        else:
            _vars = json.dumps(inputVariables)
            _vars = _vars.replace('"', '\\"')

        graphQLString = f''' mutation executeFunction {{
            executeFunction(
                input: {{ 
                    deploymentId: "{deploymentId}", 
                    input: "{_vars}"
                    }}
            ) {{
                executionId
                result {{
                    output
                    errorMessage
                    hasError
                }}
                errors {{
                    code
                    message
                    }}
                }}
            }}
        '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        return result

    def deleteFunction(self, functionId:str, force:bool=False) -> None:
        """
        Deletes a function.
        
        Parameters:
        ----------
        functionId : str
            Id of the function to be deleted.
        force : bool
            Use True to ignore confirmation.

        Example:
        --------
        >>> executeFunction('3dba276e3c8645838c2d598043cab057')
        """
        if force == False:
            confirm = input(f"Press 'y' to delete  function with id {functionId}")

        graphQLString = f''' mutation deleteFunction {{
            deleteFunction (input: {{
                functionId: "{functionId}"
            }}) {{
                errors {{
                    message
                }}
            }}
        }}
        '''
        if force == True: confirm = 'y'
        if confirm == 'y':
            result = Utils._executeGraphQL(self, graphQLString)
        else:
            return
        if result == None: return

        return result

    def deployments(self, functionId:str) -> pd.DataFrame:
        """
        Shows deployments of a function as a DataFrame.
        Parameters:
        ----------
        functionId : str
            Id of the function.

        Example:
        --------
        >>> deployments('3dba276e3c8645838c2d598043cab057')
        """

        graphQLString = f'''query deployments {{
            deployments(functionId:"{functionId}") {{
                functionAggregateId
                functionAggregateVersion
                deploymentId
                functionName
                log
                state
                }}
            }}
            '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pd.json_normalize(result['deployments'])
        del df['log']
        return df
