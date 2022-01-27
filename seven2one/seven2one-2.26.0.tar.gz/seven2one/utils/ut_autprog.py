import base64
from loguru import logger
import os

class AutProgUtils():

    def _upsetFiles(filePaths:list) -> str:
        """Converts a list of files to Base64 provides the upsetFiles graphQL format"""
        
        _files = ''

        for path in filePaths:
            if not os.path.exists(path):
                logger.error(f"Path {path} does not exist.")
                return None
            else: 
                fileName = os.path.split(path)[-1]
                contentBase64 = AutProgUtils._encodeBase64(path)
                _files += f'{{fullName: "{fileName}", contentBase64: "{contentBase64}"}},\n'

        return _files

    def _getFileNames(filePaths:list) -> str:
        """Returns file names from a file path"""
        return [os.path.split(path)[-1] for path in filePaths]


    def _encodeBase64(file:str):
        with open(file) as file:
            content = file.read()
            content = base64.b64encode(content.encode('ascii'))
            return content.decode('UTF8')

    def _varsToString(vars:dict, type) -> str:
        """Transforms a dict of function variables to a string. All values will be 
            converted to string.
        """
        if type == 'input': type = 'inputVariables'
        elif type == 'env': type = 'environmentVariables'
        else:
            return ''

        _vars = f'{type}: [\n'
        for key, value in vars.items():
            _vars += f'{{key: "{key}", value: "{str(value)}"}}\n'
        
        _vars += '\n]'

        return _vars

    def _downloadFunctionFile(path, fileName, content):
        with open(path+fileName, 'w') as f:
            f.write(base64.b64decode(content).decode('UTF8'))




