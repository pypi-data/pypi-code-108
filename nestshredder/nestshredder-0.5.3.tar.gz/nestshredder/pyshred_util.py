import logging
import sys
import os

def check_arguments(target_folder_path,object_name,batch_ref=None):

    if os.path.exists(target_folder_path) == False:
        target_path_bad = 'Target Folder Path could not be found.'
        logging.error(target_path_bad)
        sys.exit()        

    # REMOVED TO ALLOW FILE OBJECTS ETC. TO BE PASSED.    
    # try:
    #     source_file_path.read()
    # except AttributeError:
    #     try:
    #         if os.path.exists(source_file_path) == False:
    #             source_path_bad = 'Source File Path could not be found.'
    #             logging.error(source_path_bad)
    #             sys.exit() 
    #     except:
    #         logging.error('Path or File Like Object Expected')
    #         raise 

    if object_name.find(" ")>0:
        whoops_obj_name = f"One word object names please. You provided:'{object_name}'. Hyphens and underscores are acceptable."
        logging.error(whoops_obj_name)
        sys.exit() 

    if batch_ref is not None:
        if batch_ref.find(" ")>0:
            whoops_batch_space = f"Invalid batch_ref argument. Alphanumeric character strings only. No spaces. You provided:'{batch_ref}'."
            logging.error(whoops_batch_space)
            sys.exit()
        elif batch_ref.isalnum() == False:
            whoops_batch_space = f"Invalid batch_ref argument. Alphanumeric character strings only. No spaces. You provided:'{batch_ref}'."
            logging.error(whoops_batch_space)
            sys.exit()