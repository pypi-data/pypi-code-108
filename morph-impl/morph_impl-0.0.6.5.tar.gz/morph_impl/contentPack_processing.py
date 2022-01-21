import glob
import time
import yaml
import fnmatch
from configparser import ConfigParser
from os import environ
from . import group
from . import getBearerToken
from . import license
from . import role
from . import morph_log
from . import file_handler
from . import cypher
from . import input
from . import whitelabel
from . import file_ImportScript

def contentPack_implementation(contentPackSelection):
    """
    # Contentpack Implementation 

    ## Summary
    This function executes when the contentPackSelection finds the morpheusComponent as implementation.

    ### Inputs
    - contentPackSelection

    associated functions: user_select_contentPack
    """
    # Process config file
    configur = ConfigParser()
    configur.read(contentPackSelection+'/configs.ini')
    contentPack = contentPackSelection
    # Set Variables
    baseURL = configur.get('DEFAULT', 'BASE_URL')
    ADMIN_USERNAME = configur.get('DEFAULT', 'ADMIN_USERNAME')
    ADMIN_PASSWORD = configur.get('DEFAULT', 'ADMIN_PASSWORD')

    bearerToken = getBearerToken.bearerToken(baseURL, ADMIN_USERNAME, ADMIN_PASSWORD)
    # Logging 
    logger = morph_log.get_logger('cp_impl')

    # Process content pack yaml files.
    files_inContentPack = glob.glob(contentPackSelection+'/*')
    for file in files_inContentPack:
        if file.endswith('.yaml') and file != contentPackSelection+'/version.yaml':
            yaml_file = file
            logger.info('Current contentPack file processing: '+yaml_file)
            with open(yaml_file) as f: 
                result = yaml.safe_load(f)
                morpheusComponent = result['morpheusComponent']
                logger.info('Morpheus Component Detected: '+morpheusComponent)
                logger.info('Verifying Yaml: '+yaml_file)
                file_handler.verify_yaml_structure_helper(morpheusComponent, yaml_file)
                if morpheusComponent in ['groups', 'group']:
                    logger.info('Adding Groups')
                    group.createGroups(baseURL, bearerToken, yaml_file)
                    logger.info('Completed: Groups')
                #if morpheusComponent == 'license':
                #    print('Adding License')
                #    license.add_license(baseURL, bearerToken, yaml_file)
                #    print('Completed: License')
                if morpheusComponent in ['roles', 'role']:
                    logger.info('Adding Roles')
                    role.genericRoleCreate(baseURL, bearerToken, yaml_file)
                    logger.info('Completed: Roles')
                if morpheusComponent in ['cyphers', 'cypher']:
                    logger.info('Adding Cyphers')
                    cypher.cypherCreate(baseURL, bearerToken, yaml_file)
                    logger.info('Completed: Cyphers')
                if morpheusComponent in ['inputs', 'input']:
                    logger.info('Adding Input')
                    input.inputCreate(baseURL, bearerToken, yaml_file)
                    logger.info('Completed: Inputs')
                if morpheusComponent in ['whitelabel', 'whitelabels']:
                    logger.info('Updating Whitelabel')
                    whitelabel.updateWhiteLabel(baseURL, bearerToken, yaml_file)
                    logger.info('Completed: Update Whitelabel')
                if morpheusComponent in ['templates', 'template']:
                    logger.info('Adding Templates')
                    file_ImportScript.create_Template_fromCP(baseURL, bearerToken, yaml_file, contentPackSelection)
                    logger.info('Completed: Templates')
            
        if file.endswith('.png'):
            if fnmatch.fnmatch(file, '*header_logo*'):
                logoHeader = file_handler.imageResizer(file)
                whitelabel.updateLogoHeader(baseURL, bearerToken, logoHeader)
            if fnmatch.fnmatch(file, '*footer_logo*'):
                logoFooter = file_handler.imageResizer(file)
                whitelabel.updateLogoFooter(baseURL, bearerToken, logoFooter)
            if fnmatch.fnmatch(file, '*login_logo*'):
                logoLogin = file_handler.imageResizer(file)
                whitelabel.updateLogoLogin(baseURL, bearerToken, logoLogin)
        
def contentPack_file_processor(contentPackSelection):
    """
    # Content Pack file processor
    
    ## Summary
    This module - takes the contentpack selection and cycles through the version.yaml file to understand what type of contentpack it will be.

    Depending on the type: implementation, catalogItems, init, pov are currently supported - it will then process all the files and call the appropriate modules. 
    
    ### Inputs
    - contentPackSelection

    associated functions: contentPack_implementation
    """
    # Logging
    logger = morph_log.get_logger('cp_fpro')

    print('Starting File Processor')
    time.sleep(1)
    print('I am a processor.... checking files')
    time.sleep(5)
    with open(contentPackSelection+'/version.yaml') as f: 
        loaded_version_yaml = yaml.safe_load(f)
        logger.info('Loaded Version.yaml')
        type_of_contentPack = loaded_version_yaml['type']
    if type_of_contentPack == 'implementation':
        logger.info('Processing ContentPack Type Implementation')
        contentPack_implementation(contentPackSelection)
        logger.info('Completed: ContentPack')

        