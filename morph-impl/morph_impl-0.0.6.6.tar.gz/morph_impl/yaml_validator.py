import os
import yaml
import time
from . import morph_log
from cerberus import Validator

def validate(configfile, schema_file):
    logger = morph_log.get_logger('validator')
    with open(configfile, 'r') as stream:
        try:
            result = yaml.load(stream, Loader=yaml.FullLoader)
            logger.info("Loaded config: "+configfile)
        except yaml.YAMLError as exception:
            raise exception
    logger.info('... Validating ...')
    time.sleep(2)     
    schema = eval(open(schema_file, 'r').read())
    v = Validator(schema)
    validation = v.validate(result, schema)
    if validation is False:
        logger.error(v.errors)
        exit()
    else: 
        logger.info('Config Validated: '+configfile)