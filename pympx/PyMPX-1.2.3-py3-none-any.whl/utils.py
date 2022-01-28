#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation
'''Common Empower Functionality

/****************************************************************************/
/* Metapraxis Limited                                                       */
/*                                                                          */
/* Copyright (©) Metapraxis Ltd, 1991 - 2017, all rights reserved.          */
/****************************************************************************/
/* NOTICE:  All information contained herein is, and remains the property   */
/* of Metapraxis Limited and its suppliers, if any.                         */
/* The intellectual and technical concepts contained herein are proprietary */
/* to Metapraxis Limited and its suppliers and may be covered by UK and     */
/* Foreign Patents, patents in process, and are protected by trade secret   */
/* or copyright law.  Dissemination of this information or reproduction of  */
/* this material is strictly forbidden unless prior written permission is   */
/* obtained from Metapraxis Limited.                                        */
/*                                                                          */
/* This file is subject to the terms and conditions defined in              */
/* file "license.txt", which is part of this source code package.           */
/****************************************************************************/

.. todo::
    create_and_run_ebat_file: allow creation of a temporary file, put default Empower Executable
    create_and_run_ebat_file: try piping the commands in - removing the need for a batch file!
    
    
'''

#.. hardcode::
#    The hardcoding in this module is restricted to Empower return values and internal constants.
#    
#    * EMPOWER_BATCH_SUCCESS=1
#    * EMPOWER_IMPORTER_SUCCESS=0
#    * EMPOWER_CALCULATION_SETTER_SUCCESS=0
#    * EMPOWER_MONTH_CONSTANT=3
#    * EMPOWER_WEEK_CONSTANT=4    

import os
import csv

from pympx import queuing as mpq
from pympx import exceptions as mpex
from pympx import low_level_utilities as llu
from pympx import pympx

EMPOWER_BATCH_SUCCESS               = llu.EMPOWER_BATCH_SUCCESS
EMPOWER_IMPORTER_SUCCESS            = llu.EMPOWER_IMPORTER_SUCCESS
EMPOWER_CALCULATION_SETTER_SUCCESS  = llu.EMPOWER_CALCULATION_SETTER_SUCCESS
EMPOWER_MONTH_CONSTANT              = llu.EMPOWER_MONTH_CONSTANT
EMPOWER_WEEK_CONSTANT               = llu.EMPOWER_WEEK_CONSTANT    


EMPOWER_ROOT                = llu.EMPOWER_ROOT
EMPOWER_BATCH_EXECUTABLE    = llu.EMPOWER_BATCH_EXECUTABLE   
EMPOWER_IMPORTER_EXECUTABLE = llu.EMPOWER_IMPORTER_EXECUTABLE
EMPOWER_CALCSET_EXECUTABLE  = llu.EMPOWER_CALCSET_EXECUTABLE 

#Import datetime so we can put generation information into the EBAT file
import datetime
from dateutil import relativedelta
#import calendar

#We need pkg_resources to find the Import scripts we've included with the package
import pkg_resources

from pympx import logconfig
log=logconfig.get_logger()
CompletelyLoggedError=mpex.CompletelyLoggedError

DAY  = llu.DAY
YEAR = llu.YEAR


#In order not to break the API, we include original utils functions that are now in the low_level_utils as simple monkeypatches
    
read_source_locations_file_into_dictionary = llu.read_source_locations_file_into_dictionary  
check_files_that_must_exist_do_exist       = llu.check_files_that_must_exist_do_exist
check_dirs_that_must_exist_do_exist        = llu.check_dirs_that_must_exist_do_exist    

Element             =   pympx.Element
TimeElement         =   pympx.TimeElement
Structure           =   pympx.Structure
StructureElement    =   pympx.StructureElement
 
# The best way to convert dates is to get unique values, run strptime over the unique values and then join the strings/dates lookup table with the original data to get the translated dates. The code here uses a dictionary lookup to reduce the strptime, but Kostas says that we really want to be avoiding the .apply() function
date_lookups={}
def format_dates(date_str,date_lookups,style):
    '''Convert the string, integers and dates we get from the excel or csv read into a proper datetime.datetime
    
    :param date_str: a string containing a date separated with forward slashes, or a date intenger as returned by excel, or a datetime.datetime. Any instance of datetime.datetime is returned as entered.
    :param date_lookups: a dictionary of previously successful date lookups. This dictionary seriously increases performance, as doing a lookup is much, much faster than parsing a date string
    :param style: One of two strings 'mdy' or 'dmy' for the order of the dates. In the calling code, each style is tried on the entire data set at once, ensuring all dates in the same file are translated in the same way
    
    :return: converted datetime.datetime
    
    >>> format_dates('06/01/2013',{},'mdy',open('mylog.txt','w'),2)
        datetime.datetime(2013,6,1)
    >>> format_dates('06/01/2013',{},'dmy',open('mylog.txt','w'),2)
        datetime.datetime(2013,1,6)
    >>> format_dates('06/01/2013',{},'dmy',open('mylog.txt','w'),2)
        datetime.datetime(2013,1,6)    
    >>> format_dates(40000,{},'dmy',open('mylog.txt','w'),2)
        datetime.datetime(2009,7,6)    
    >>> format_dates(datetime.datetime(2017,9,2),{},'dmy',open('mylog.txt','w'),2)
        datetime.datetime(2017,9,2)    
    '''
    return llu.format_dates(date_str,date_lookups,style)

try_convert_to_string_via_int   = llu.try_convert_to_string_via_int
replace_bad_unicode             = llu.replace_bad_unicode

def insert_new_time_elements_into_empower(empower_site_file, empower_user, empower_pwd, empower_importer_executable, target_file_path, start_date=None, end_date=None, date_period='day', long_name_date_format='%Y-%m-%d'):
    '''Create and insert new time elements into an Empower Site
    '''
    #Export current time dimension elements from Empower
    
    #Generate new necessary elements
    
    #Compare the generated elements with the elements in the site, and
    #get only new elements which are not already in the site
    
    #Load the new elements into the site
    
    
    pass
        
    
generate_date_dimension_elements_file = llu.generate_date_dimension_elements_file
 
lookup_empower_columns                  = llu.lookup_empower_columns 
create_empower_lookup_dataframe         = llu.create_empower_lookup_dataframe
generate_simple_empower_mapping_file    = llu.generate_simple_empower_mapping_file
physid_to_empower_file_suffix           = llu.physid_to_empower_file_suffix       
empower_file_suffix_to_physid           = llu.empower_file_suffix_to_physid       
create_and_run_ebat_file                = llu.create_and_run_ebat_file            
delete_cache_files_for_site             = llu.delete_cache_files_for_site         
run_empower_importer_script             = llu.run_empower_importer_script             
export_empower_dimensions               = llu.export_empower_dimensions          
 
four_bytes_to_int                       = llu.four_bytes_to_int
int_to_four_bytes                       = llu.int_to_four_bytes

#TODO - reroute via Site and Dimension classes    

create_empower_dimension_element_list           = pympx._create_empower_dimension_element_list  
create_empower_dimension_shortname_element_dict = pympx._create_empower_dimension_shortname_element_dict
#create_empower_dimension_physid_element_dict    = pympx._create_empower_dimension_physid_element_dict  
#create_empower_dimension_longname_element_dict  = pympx._create_empower_dimension_longname_element_dict
#create_empower_dimension_field_element_dict     = pympx._create_empower_dimension_field_element_dict
    
import_empower_commentary               = llu.import_empower_commentary               
msgsink__run_single_dim0_empower_load   = llu.msgsink__run_single_dim0_empower_load   
run_single_dim0_empower_load            = llu.run_single_dim0_empower_load            
generate_cache_instructions             = llu.generate_cache_instructions             
shard_files_in_list_by_storage_dim      = llu.shard_files_in_list_by_storage_dim          
msgsink__shard_files_by_storage_dim     = llu.msgsink__shard_files_by_storage_dim     
load_empower_from_shards                = llu.load_empower_from_shards                
msgsink__process_empower_import_metrics = llu.msgsink__process_empower_import_metrics
cumulate_dataframe_for_empower_import   = llu.cumulate_dataframe_for_empower_import  
cumulate_dataframe_for_empower_bulkload = llu.cumulate_dataframe_for_empower_bulkload
process_one_metric_for_empower_import   = llu.process_one_metric_for_empower_import  
create_exploded_bulkload_files          = llu.create_exploded_bulkload_files         
create_exploded_shortname_files         = llu.create_exploded_shortname_files        
create_na_bulk_load_file                = llu.create_na_bulk_load_file               
create_overwrite_bulk_load_file         = llu.create_overwrite_bulk_load_file        
export_empower_shortname_tuples         = llu.export_empower_shortname_tuples        
                                     
set_calculation                         = llu.set_calculation                                     
                                     
get_simple_translation_df               = llu.get_simple_translation_df              
translate_dim                           = llu.translate_dim   
                      
zip_file                                = llu.zip_file                               
unzip_file                              = llu.unzip_file                             
concatenate_files                       = llu.concatenate_files                      
sort_file                               = llu.sort_file                              

read_structure_from_site                = pympx._read_structure_from_site
#add_new_elements_to_site                = pympx._add_new_elements_to_site
#write_structure_to_file                 = pympx._write_structure_to_file
 

write_structure_file_to_site    = llu.write_structure_file_to_site

#write_structure_to_site                 = pympx._write_structure_to_site                                    

#update_dimension_structure              =pympx._update_dimension_structure
    

