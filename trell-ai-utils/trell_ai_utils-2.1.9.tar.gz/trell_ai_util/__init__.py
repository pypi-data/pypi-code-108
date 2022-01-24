import logging
import warnings
import dotenv

message = "\nThis version of trell-ai-utils has been deprecated.\nPlease use trell-ai-utils>=2.0.0 now ownwards.\nLink for latest pip package documentation : https://pypi.org/project/trell-ai-utils/"
warnings.warn(message, DeprecationWarning)
logging.warning(message)

dotenv_path = dotenv.find_dotenv('trell.env')
if dotenv_path:
    dotenv.load_dotenv(dotenv_path)
    print("-------------- Environment Variables Loaded Successfully ---------------")
