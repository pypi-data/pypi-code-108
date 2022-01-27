import base64
from loguru import logger
import os

class ProgrammingUtils():

    def _upsetFiles(filePaths:list) -> str:
        """Converts a list of files to Base64 provides the upsetFiles graphQL format"""
        
        _files = ''

        for path in filePaths:
            if not os.path.exists(path):
                logger.error(f"Path {path} does not exist.")
                return None
            else: 
                fileName = os.path.split(path)[-1]
                contentBase64 = ProgrammingUtils._encodeBase64(path)
                _files += f'{{fullName: "{fileName}", contentBase64: "{contentBase64}"}},\n'

        return _files

    def _encodeBase64(file:str):
        with open(file) as file:
            content = file.read()
            content = base64.b64encode(content.encode('ascii'))
            return content.decode('UTF8')



