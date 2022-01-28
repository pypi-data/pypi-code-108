'''

/****************************************************************************/
/* Metapraxis Limited                                                       */
/*                                                                          */
/* Copyright (©) Metapraxis Ltd, 1991 - present, all rights reserved.       */
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

'''


#For some reason the success return value from Empower Batch is 1 (!) Therefore we set a constant here to compare to, to check if the batch load worked or not.
#Note, we no longer call Empower Batch, we call all batch commands via Empower Importer instead
EMPOWER_BATCH_SUCCESS=1
#Richard B. changed the Empower Importer return value to 0 for successful batches in 9.1
#Just in case we use an older version of importer define the return code of a successful job here 
EMPOWER_IMPORTER_SUCCESS=0
EMPOWER_CALCULATION_SETTER_SUCCESS=0
# 3 is the Empower period number for month
EMPOWER_YEAR_CONSTANT=0
EMPOWER_HALFYEAR_CONSTANT=1  
EMPOWER_QUARTER_CONSTANT=2
EMPOWER_MONTH_CONSTANT=3
EMPOWER_WEEK_CONSTANT=4
EMPOWER_DAY_CONSTANT=5   

import sys
import os
import shutil
import win32file, win32pipe
import time

from pympx import queuing as mpq
from pympx import exceptions as mpex
from pympx import logconfig 
import zipfile
from cryptography.fernet import Fernet
import pickle
import getpass

log=logconfig.get_logger()

empower_debug=False
empower_encoder_usr=None

def set_empower_root():
    global empower_debug
    cwd=os.getcwd()
    empower=r"C:\Program Files\Metapraxis"
    dlist=os.listdir(empower)
    root=''
    fversion=0.0
    version_string=None
    if len(dlist)>=1:
        for s in dlist:
            slist=s.split(' ')
            if len(slist)==2: #this condition will be met if no error occur is installation location string
                fver=float(slist[1])
                if fver>fversion: 
                    fversion=fver
                    root=s
                    version_string=slist[1]
            else:
                root=max(root,s) #go here only if error occurs in Empower installation location string
    
    empower_root=os.path.join(empower,root)   
    rootfile=os.path.join(cwd,'empower_options')
    if os.path.isfile(rootfile):
        fd=open(rootfile,'r')
        ss=fd.read()
        ss=ss.strip('\n')
        slist=ss.split('\n')
        for ss in slist:
            if len(ss)<7: continue
            klist=ss.split('=')
            if len(klist) !=2: continue
            key=klist[0]
            value=klist[1]
            if key=='empower_root': 
                empower_root=value
                slist=empower_root.split(' ')
                if len(slist)>1: version_string=slist[-1]
                if version_string=='Unicode':version_string = slist[-2]
                
                continue
            if key=='empower_debug':
                if value=='true' or value=='True':
                    empower_debug=True
                elif value=='false' or value=='False':
                    empower_debug=False
                continue
            if key=='empower_encoder':
                empower_encoder_usr=value
                continue
            if key=='empower_version':
                version_string=value
                continue
            
                    
    if not version_string: version_string=empower_root[-3:]
                
    return empower_root,version_string
    
EMPOWER_ROOT, EMPOWER_VERSION =  set_empower_root()
if  empower_debug:
    print('root,version', EMPOWER_ROOT,',', EMPOWER_VERSION)
    
if  not EMPOWER_ROOT:
    EMPOWER_ROOT = r"C:\Program Files\Metapraxis"

try:
    fversion=float(EMPOWER_VERSION)
except:
    fversion=9.7    
    log.info('incorrect version number detected. empower_root may be set incorrectly')
    if empower_debug:
        print('incorrect version number detected. empower_root may be set incorrectly')
 
EMPOWER_BATCH_EXECUTABLE   =os.path.join(EMPOWER_ROOT,"Empower Batch.exe")
EMPOWER_IMPORTER_EXECUTABLE=os.path.join(EMPOWER_ROOT,"Empower Importer Console.exe")
EMPOWER_CALCSET_EXECUTABLE =os.path.join(EMPOWER_ROOT,"Empower Calculation Setter.exe")

empower_encoder='utf-8-sig'
if fversion<9.8: 
    empower_encoder='cp1252'
if  empower_encoder_usr:
    empower_encoder=empower_encoder_usr
    
#subprocess allows us to call command line programs - such as Empower Batch 
import subprocess

#multiprocessing is used as a 'threading' tool
import multiprocessing
import queue as qq
#unix style wildcard matching
import fnmatch


#Import datetime so we can put generation information into the EBAT file
import datetime
from dateutil import relativedelta
#import calendar

#We need pkg_resources to find the Importer scripts we've included with the package
import pkg_resources

# Avoid the annoying NUMEXPR warning
import os
os.environ['NUMEXPR_MAX_THREADS'] = '8'

import numpy as np
import pandas as pd
#pandas uses constants from the csv module when reading and saving
import csv

#itertools is used to expand out all of the different hierarchies
import itertools 

#The Garbage Collector
import gc



#The done message is set as a constant
DONE=mpq.DONE
FAILED=mpq.FAILED

DAY=relativedelta.relativedelta(days=1)
YEAR=relativedelta.relativedelta(years=1)

import multiprocessing
from multiprocessing import queues


CTX=multiprocessing.get_context()

msg="Empower Importer is not available at the default location. Empower must be installed,\n\
or an alternative location provided, for pympx to work correctly. An alternative location can be set\n\
in the empower_options file which should be at the working directory. e.g. in .\empower_options, set the following:\n\
empower_root=D:\Program Files\Metapraxis\Empower 9.7" 

if EMPOWER_ROOT == r"C:\Program Files\Metapraxis": log.info(msg)

# New addition: Zips up contents of site folder, places in a named, dated zip file in the data load folder. PYM-59
def zip_site(site_folder,include_site_files = True, additional_folders = [], target_folder = None ):
    """
	Zips up contents of site folder, places in a named, dated zip file in the data load folder.
    site_folder: path to the Empower site to be zipped.
	EKS / Site file and 'Metadata Files' are included unless specified otherwise
	Specify other folders to include, and each file from that folder will be added.
	Sub folders need to be specified separately; e.g. to include an 'Archive' folder within the 'Dashboards Folder', specify ['Dashboards', 'Dashboards\Archive']
		
	Parameters:
		* include_site_files: Optional, default True; states whether the metadata files folder and eks file of the site should be included in the zip
		* additional_folders: Optional, default []; list of folders and subfolders within the site folder to include in the zip file
		* target_folder: Optional, default None; sub-folder within the data sub folder to place the zip file
    """
	# Name the output with autozip, site name, date
    cwd = os.getcwd()
    
    date_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    site_name = os.path.basename(site_folder)
    zip_name = 'autozip_' + site_name + '_' + date_str + '.zip'
    zip_name = zip_name.replace(' ','-')
    # Get full list of folders to zip; force it to include Metadata Files unless specified otherwise
    default_folders = ['Metadata Files'] if include_site_files else []
    if len(additional_folders)==0:
        dname=site_folder
        items=os.listdir(dname)
        for item in items:
            path=os.path.join(dname,item)
            if os.path.isdir(path): additional_folders.append(item)
            
    folders = set(default_folders + additional_folders)
    log.info('Creating zip archive of: {} ...'.format(', '.join(folders)))
        
    # Get a zip file that we can start adding things to
    with zipfile.ZipFile(os.path.join(cwd, target_folder or '', zip_name), 'w') as output_zip:
        # Add the eks / site file
        if include_site_files:
            dname=site_folder
            items=os.listdir(dname)
            for item in items:
                path=os.path.join(dname,item)
                if os.path.isfile(path):                  
                    try: output_zip.write(path)
                    except Exception as e: 
                        log.info('Error: could not write file',str(e))
            
        # Work through each required folder
        for folder in folders:
            try:
                # Get the full path of the folder, and the items inside it
                root = os.path.join(site_folder, folder)
                items = os.listdir(root)
                # Get all of the files inside the folder (items that aren't folders)
                files = [os.path.join(root, i) for i in items if not os.path.isdir(os.path.join(root, i))]
                log.info('Adding "{}" to archive...'.format(folder)) 
				# Add each file to the zip
                for file in files: output_zip.write(file)
                log.info('"{}" added successfully.'.format(folder)) 
            except exception as e: 
                log.info('error in zip:'+folder+';'+str(e))
                continue
    log.info('Zip archive "{}" created.'.format(zip_name))



def read_source_locations_file_into_dictionary(source_locations_file,separator=','):
    '''Read and parse a file of comma separated source lcoations names, and source location paths
    
    For example if my_source_locations.csv contains lines:
    
    my_file1,     C:\MyDirectory\file.txt
    my_location2, C:\MyOtherDirectory
    
    then:
    
    >>> sloc=read_source_locations_file_into_dictionary('my_source_locations.csv')
    >>> sloc
        {'my_file1':r'C:\MyDirectory\file.txt','my_location2', r'C:\MyOtherDirectory'}
    >>> sloc['my_file1']
        r'C:\MyDirectory\file.txt'
    
    This dictionary can be used to pass around file paths that vary from ebvironmnet to environment
    
    
    :param source_locations_file: path to a csv file containing name, path pairs
    :param separator: character that separates the csv file - by default a comma, but could be a tab or pipe character. Note this function does not parse embedded separators well
    '''
    sloc={}
    #read source_locations.txt
    with open(source_locations_file) as source_locations:
        for line in source_locations:
            if len(line.strip()) > 1:
                name_loc=line.split(separator)
                name=name_loc[0].strip()
                loc=name_loc[1].strip()
                #Remove double quotes from file paths
                loc=loc.replace('"','')
            
            sloc[name]=loc
    return sloc        

def check_files_that_must_exist_do_exist(locations_list=[],source_locations={},locations_file_name='not specified'):
    '''Check for existence of files refered to in locations_list and raise and error if they don't exist.
    
    :param locations_list: a list of file paths that we will check for existence
    :param source_locations: the dictionary of source locations, originally read from the source_locations file
    :param locations_file_name: the file name from which we read the source_locations dictionary - only used to make any error message more informative
    '''
    sloc=source_locations
    
    for loc in locations_list:
        try:
            path=sloc[loc]
        except KeyError:
            msg='Location '+loc+' is not recorded in the source locations file '+locations_file_name+'. Please add this location lookup to the file'
            log.error(msg)
            raise mpex.CompletelyLoggedError(msg)
    
        if not os.path.isfile(path):
            #Open the missing file to provoke a useful error
            with open(path):
                pass

def check_dirs_that_must_exist_do_exist(directories_list=[],source_locations={},locations_file_name='not specified'):
    '''Check for existence of directories refered to in directories_list and raise and error if they don't exist
    
    :param directories_list: a list of directories that we will check for existence
    :param source_locations: the dictionary of source locations, originally read from the source_locations file
    :param locations_file_name: the file name from which we read the source_locations dictionary - only used to make any error message more informative
    '''
    
    sloc=source_locations

    for loc in directories_list:
        try:
            path=sloc[loc]
        except KeyError:
            msg='Location '+loc+' is not recorded in the source locations file '+locations_file_name+'. Please add this location lookup to the file'
            log.error(msg)
            raise mpex.CompletelyLoggedError(msg)
        if not os.path.isdir(path):
            msg='Location '+path+' as referred to in source locations file '+locations_file_name+' as "'+loc+'" does not exist'
            log.error(msg)
            raise mpex.CompletelyLoggedError(msg)
 
def _get_standard_empower_encoding_from_importer_path(importer_path):
    utf8sig = 'utf-8-sig'
    utf8 = 'utf8'
    default_encoding = utf8sig
    cp1252 = 'cp1252'
    
    ret = default_encoding
    
    final_path = os.path.basename(os.path.dirname(importer_path));
    if not final_path:
        ret = default_encoding
    else:
        empower_and_version = final_path.split(" ")
        try:
            version = empower_and_version[1]
        except IndexError:
            # Default to 9.7
            version = '9.9'
        
        try:
            # Lookup the version and return it
            ret = {'9.6':cp1252
            ,'9.7':cp1252
            ,'9.8':utf8sig
            ,'9.9':utf8sig
            }[version]
        except KeyError:
            ret = default_encoding

    return ret
    
 
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
    
    #The input may already be a datetime
    if isinstance(date_str,datetime.datetime):
        return date_str
        
    try:
        dt=date_lookups[date_str]
    except KeyError:
    
        #There are two styles - mdy and dmy
        #each file should have all dates as mdy or dmy - they should all transform correctly
        if style=='mdy':
            try:
                mdy=date_str.split('/')
                #the third i.e. [2] part of month-day-year is the year. If it less than 100 it is a 2 digit year - add 2000 to make it a 4 digit year
                if int(mdy[2]) < 100:
                    year=2000+int(mdy[2])
                else:
                    year=int(mdy[2])
                    
                dt=datetime.datetime(year,int(mdy[0]),int(mdy[1]))
            except (TypeError,ValueError,AttributeError):
                try:
                    dt=datetime.datetime.strptime(date_str,'%m/%d/%Y')
                except (TypeError,ValueError):
                    try:
                        dt=datetime.datetime.strptime(date_str,'%Y-%m-%d 00:00:00')
                    except (TypeError,ValueError):
                        try:
                            #Why take 2?
                            #I don't know - taking one makes sense since the excel 1900/1/1 date translates to 1, but testing shows we need to take 2. I am flummoxed. 
                            #Actually I was flummoxed, now I'm not - Excel, bless its heart, thinks that 1900/2/29 exists, because it has flaky leap year logic
                            dt=datetime.datetime(1900,1,1,0,0,0)+datetime.timedelta(days=int(date_str)-2)
                        except ValueError as e:
                            log.error('Erroneous date: '+date_str)
                            #Not yet fully logged - needs some traceback
                            raise e
        else:
            try:
                dmy=date_str.split('/')
                if int(dmy[2]) < 100:
                    #the third i.e. [2] part of month-day-year is the year. If it less than 100 it is a 2 digit year - add 2000 to make it a 4 digit year
                    year=2000+int(dmy[2])
                else:
                    year=int(dmy[2])
            
                dt=datetime.datetime(year,int(dmy[1]),int(dmy[0]))
            except (TypeError,ValueError,AttributeError):
                try:
                    dt=datetime.datetime.strptime(date_str,'%d/%m/%Y')
                except (TypeError,ValueError):
                    try:
                        dt=datetime.datetime.strptime(date_str,'%Y-%m-%d 00:00:00')
                    except (TypeError,ValueError):
                        try:
                            #Why take 2?
                            #I don't know - taking one makes sense since the excel 1900/1/1 date translates to 1, but testing shows we need to take 2. I am flummoxed. 
                            #Actually I was flummoxed, now I'm not - Excel, bless its heart, thinks that 1900/2/29 exists, because it has flaky leap year logic
                            dt=datetime.datetime(1900,1,1,0,0,0)+datetime.timedelta(days=int(date_str)-2)
                        except ValueError as e:
                            log.error('Erroneous date: '+date_str)
                            #Not yet fully logged - needs traceback
                            raise e
        
                        
        date_lookups[date_str]=dt
    
    return dt

def try_convert_to_string_via_int(something):

    '''Try to convert something to a string, if that something represents a numeric value
    
    Strings read in via pandas may in fact be integers. Try to convert to a string which represents an integer - if the string is not an integer just return what came in
    This function is useful if panda read a code such as 3995 and converted it to the float 3995.0 
    
    Directly converting the float to a string ('3995.0') for the purposes of a lookup would fail, so convert it to an integer first

    It is better to convert the data on the way in using the read_csv parameter converters={column_name,function}, which avoids leading zero issues
    
    >>> try_convert_to_string_via_int('Spam')
    'Spam'
    >>> try_convert_to_string_via_int(3995.0)
    '3995'
    >>> try_convert_to_string_via_int(3995.1)
    '3995'
    >>> try_convert_to_string_via_int('3995')
    '3995'
    >>> try_convert_to_string_via_int('3995.0')
    '3995'
    >>> try_convert_to_string_via_int('3995.3995')
    '3995'
    >>> try_convert_to_string_via_int('03995.0')
    '3995'
    >>> try_convert_to_string_via_int(datetime.datetime(0000,12,25))
    datetime.datetime(0000,12,25)
    
    :param something: any object
    :return: The input, converted to an integer if possible, or just the input if it could not be converted 
    '''
    
    try:
        return str(int(float(something)))
    except Exception:
        return something
        
def replace_bad_unicode(s,original_encoding='utf-8'):
    '''Replace unicode characters that will cause issues with Empower imports with a question mark
    
    :param s: The string which will have the difficult characters removed
    :param original_encoding: The original encoding of the string
    
    :return: string encoded as us-ascii
    
    >>> replace_bad_unicode('École')
    '?cole'
    >>> replace_bad_unicode('School')
    'School'
    '''
    return str(s).encode('ascii','replace').decode(original_encoding)


def insert_new_time_elements_into_empower(empower_site_file, empower_user, empower_pwd, empower_importer_executable, target_file_path, start_date=None, end_date=None, date_period='day', long_name_date_format='%Y-%m-%d'):
    '''Create and insert new time elements into an Empower Site
    '''
    #Export current time dimension elements from Empower
    
    #Generate new necessary elements
    
    #Compare the generated elements with the elements in the site, and
    #get only new elements which are not already in the site
    
    #Load the new elements into the site
    
    
    pass
        
    
def generate_date_dimension_elements_file(target_file_path, start_date=None, end_date=None, date_period='day', long_name_date_format='%Y-%m-%d'):
    '''Generate a file with Empower time elements in tab delimited format. This file can then be loaded as a set of time elements into empower
    
    :param target_file_path: Full file path of file to write date elements to   
    :param start_date: date to start generating elements for. Defaults to start of last year.
    :param end_date: date to stop generating dates for. Defaults to end of next year.
    :param date_period: type of period to create time elements for - allowed periods are 'day'
    :param long_name_date_format: c-format string of date to write
    '''
    
    #TODO - vbreak this into a generator an a file write, so we can test the generator
    with open(target_file_path,'w') as target_file:
        _generate_date_dimension_elements(start_date,end_date,date_period,long_name_date_format,open_writable_file=target_file)

def _generate_date_dimension_elements(start_date,end_date,date_period,long_name_date_format,open_writable_file):
    '''Write to an open file like, Empower time elements in tab delimited format. This file can then be loaded as a set of time elements into empower
    
    :param start_date: date to start generating elements for. Defaults to start of last year.
    :param end_date: date to stop generating dates for. Defaults to end of next year.
    :param date_period: type of period to create time elements for - allowed periods are 'day'
    :param long_name_date_format: c-format string of date to write
    :param open_writable_file: An open, writable file like object to write the dates to
    
    #TODo examples using string.io object
    '''
    if start_date is None:
        #Default to the start of last year, which is 1st of January
        start_date= datetime.datetime.now()-YEAR
        start_date= datetime.datetime(start_date.year,1,1)

    if end_date is None:
        end_date= datetime.datetime.now()+ YEAR
        #Initialise the end_date to end of next year ,which is 31st December)
        end_date=datetime.datetime(end_date.year,12,31)
        
    if date_period=='day':
        delta=DAY
        empower_period_type='5' # 5 means 'day'
    else:
        msg="Only date_period 'day' can be specified. If you require a different increment, please contact Metapraxis TSD"
        log.error(msg)
        raise mpex.CompletelyLoggedError(msg)

    working_date=start_date   
    while working_date <= end_date:
        
        #e.g. 
        #2015-01-01 2015 1 1 5
        element_line=_generate_single_date_dimension_element(working_date,long_name_date_format,empower_period_type)
        
        open_writable_file.write(element_line)
        open_writable_file.write('\n')   
        
        working_date+=delta
        
def _generate_single_date_dimension_element(working_date,long_name_date_format,empower_period_type):
    #e.g. 
    #2015-01-01 2015 1 1 5
    
    #TODo, brteakdown to test error messages for bad format string and so on
            
    return datetime.datetime.strftime(working_date,long_name_date_format)+'\t'+ \
            str(working_date.year)+'\t'+ \
            str(working_date.month)+'\t'+ \
            str(working_date.day)+'\t'+ \
            str(empower_period_type)
 
 
def lookup_empower_columns(df,columns,site_abbreviation,mapping_file_df,exported_dim_df):
    '''Add columns with Empower Ids to the dataframe
    
    :param df: Dataframe to append columns to
    :param columns: Listlike of columns in the original dataframe that need the Empower Ids looked up for them
    :param site_abbreviation: abbreviation for the site that the Empower Ids have come from - this distinguishes Ids from different sites
    :param mapping_file_df: a DataFrame containing the mappings that do the job of the EAS-IAS. Columns Should be ['Dimension String','Empower Short Code']
    :param exported_dim_df: a DataFrame containing the dimension as exported from Empower columns should include ['ID','Short Name']
    '''
    #Do a bit of magic, adding in the Empower Shortnames and Phys IDs for the various columns
    for column in columns:
        
        df=pd.merge(how='left', 
                      left=df,
                      right=mapping_file_df, 
                      left_on=column, right_on='Dimension String',
                      sort=False, copy=True)

        df.rename(columns={'Empower Short Code':column+' '+site_abbreviation+' Empower Short Name'
                          ,'Dimension String':column+' '+site_abbreviation+' Dimension String'},inplace=True)
        
        df=pd.merge(how='left', 
                  left=df,
                  right=exported_dim_df[['ID','Short Name']], 
                  left_on=column+' '+site_abbreviation+' Empower Short Name', right_on='Short Name',
                  sort=False, copy=True)

        df.rename(columns={'ID':column+' '+site_abbreviation+' PhysID' 
                         ,'Short Name':column+' '+site_abbreviation+' Short Name'},inplace=True)
        
        del df[column+' '+site_abbreviation+' Short Name']
        del df[column+' '+site_abbreviation+' Dimension String']

    return df

def create_empower_lookup_dataframe(site_abbreviation,mapping_file_df,exported_dim_df):
    '''Create a DataFrame with shortname mappings and empower ids, for use with basic Lookups
    
    :param site_abbreviation: abbreviation for the site that the Empower Ids have come from - this distinguishes Ids from different sites
    :param mapping_file_df: a DataFrame containing the mappings that do the job of the EAS-IAS. Columns Should be ['Dimension String','Empower Short Code']
    :param exported_dim_df: a DataFrame containing the dimension as exported from Empower columns should include ['ID','Short Name']
    '''

    mapping_file_df.rename(columns={'Empower Short Code':site_abbreviation+' Empower Short Name'
                      ,'Dimension String':site_abbreviation+' Dimension String'},inplace=True)
    
    mapping_file_df=pd.merge(how='left', 
              left=mapping_file_df,
              right=exported_dim_df[['ID','Short Name']], 
              left_on=site_abbreviation+' Empower Short Name', right_on='Short Name',
              sort=False, copy=True)

    mapping_file_df.rename(columns={'ID':site_abbreviation+' PhysID' 
                     ,'Short Name':site_abbreviation+' Short Name'},inplace=True)
    
    del mapping_file_df[site_abbreviation+' Short Name']
    #del mapping_file_df[site_abbreviation+' Dimension String']

    return mapping_file_df

def generate_simple_empower_mapping_file(site_abbreviation,empower_dimension_export_file,shortname_mapping_file,output_file):

    #Read in the Mapping File
    mapping_file_df=pd.read_csv(shortname_mapping_file, encoding = "ISO-8859-1")
    mapping_file_df.drop_duplicates(subset=['Dimension String'],inplace=True)

    #Now read the dimension values exported from the Empower Sites
    exported_dim_df=  pd.read_csv(empower_dimension_export_file,   sep='\t', encoding = "ISO-8859-1")
    
    #Combine the two files together
    combined_mapping=create_empower_lookup_dataframe(site_abbreviation,mapping_file_df,exported_dim_df)
    
    #Save the combined mappings down to file
    log.verbose( 'Saving '+site_abbreviation+' Empower mapping file to '+output_file)
    combined_mapping.to_csv(path_or_buf=output_file, sep=',', na_rep='', float_format=None, columns=None, header=True, index=False, index_label=None, mode='w', encoding=None, compression=None, quoting=csv.QUOTE_ALL, quotechar='"', line_terminator='\n', chunksize=None, tupleize_cols=False, date_format='%Y-%m-%d', doublequote=True, escapechar=None, decimal='.')

def physid_to_empower_file_suffix(physid,number_of_elements_per_file=1):
    '''Convert an Empower storage dimension physical ID (physid) into the suffix for the Empower data file that the storage dimension is stored in
    
    :param physid: Empower physical id from the storage dimension
    :param number_of_elements_per_file: Number of different Empower elements stored in each storage dimension file. The number of elements per storage dimension file is configurable in Empower. 
    :return:       Three character empower data file suffix

    .. doctest::
    
        >>> physid_to_empower_file_suffix(20)
        '00K'
        
        >>> physid_to_empower_file_suffix(37)
        '011'
        
        >>> physid_to_empower_file_suffix(2,2)
        '001'

        >>> physid_to_empower_file_suffix(46655)
        'ZZZ'
        
        >>> physid_to_empower_file_suffix(46656)
        '1000'
        
        >>> physid_to_empower_file_suffix(60466175)
        'ZZZZZ'
        
    '''
    
    physid=int(physid)
    file_number=1 + (physid - 1) // number_of_elements_per_file

    #file numbering runs from 0 to Z - i.e. 36 characters
    BASE36_LOOKUP={  0: '0'
                  ,  1: '1'
                  ,  2: '2'
                  ,  3: '3'
                  ,  4: '4'
                  ,  5: '5'
                  ,  6: '6'
                  ,  7: '7'
                  ,  8: '8'
                  ,  9: '9'
                  , 10: 'A'
                  , 11: 'B'
                  , 12: 'C'
                  , 13: 'D'
                  , 14: 'E'
                  , 15: 'F'
                  , 16: 'G'
                  , 17: 'H'
                  , 18: 'I'
                  , 19: 'J'
                  , 20: 'K'
                  , 21: 'L'
                  , 22: 'M'
                  , 23: 'N'
                  , 24: 'O'
                  , 25: 'P'
                  , 26: 'Q'
                  , 27: 'R'
                  , 28: 'S'
                  , 29: 'T'
                  , 30: 'U'
                  , 31: 'V'
                  , 32: 'W'
                  , 33: 'X'
                  , 34: 'Y'
                  , 35: 'Z'
                  }

              
    if file_number <=0:
        #Not for logging - this is a serious error - probably caused during development
        raise ValueError('File number must be greater than 0. file_number was '+str(file_number)+' for physid '+str(physid)+' with '+str(number_of_elements_per_file)+' elements per file')
    
    #we need to split the number into integers representing the places in base 36
    #so 35 -> 35
    #   36 -> 1 0
    #   37 -> 1 1
    #and so on
    #We don't know how many of these there will be so work them out one by one
    
    number_as_base_36_integers=0
    #A list of all of the base 36 digits that need translating to file suffixe characters
    #This list will run in reverse order with smallest places first
    base_36_integer_digits=[]
    #We need to keep track of the numerical place e.g. 100 in base 10 has 3 places 1000 has four places
    #The 1 in 109 is the digit in second place, the 0 in first place and the 9 is the digit in zeroeth place
    numerical_place=0
    
    #We will know we have finished getting all the place values, when the number derived from them equals the original number
    while number_as_base_36_integers<file_number:
        
        current_base_36_digit=(file_number // 36**numerical_place) % 36

        #Work out the value of that number, and add it onto our running total, so we will know when we have finished
        number_as_base_36_integers+=current_base_36_digit* 36**numerical_place
        #record it in our list
        base_36_integer_digits.append(current_base_36_digit)
        #print(current_base_36_digit)
        
        #finally increment the numerical place
        numerical_place+=1
       
    while len(base_36_integer_digits)<3:
        base_36_integer_digits.append(0)    

    #Reverse the numbers and translate to digits, before joining them all together
    return ''.join([BASE36_LOOKUP[digit] for digit in base_36_integer_digits[::-1]])

    
def empower_file_suffix_to_physid(empower_file_suffix,number_of_elements_per_file=1):
    '''Convert  the suffix for the Empower data file that the storage dimension is stored in into a range of Empower storage dimension physical IDs (physid) that could be found in the file
    
    :param empower_file_suffix:  Three character empower data file suffix
    :return:                     Tuple of maximum and minimum Empower physical id found in the storage dimension

    .. doctest::
    
        >>> empower_file_suffix_to_physid('00K')
        (20, 20)
        
        >>> empower_file_suffix_to_physid('011')
        (37, 37)
        
        >>> empower_file_suffix_to_physid('001',2)
        (1, 2)
        
        >>> empower_file_suffix_to_physid('0001')
        (1, 1)
        
        >>> empower_file_suffix_to_physid('1000')
        (46656, 46656)
        
    '''
    
    empower_file_suffix=str(empower_file_suffix)
    #file numbering runs from 0 to Z - i.e. 36 characters
    REVERSE_BASE36_LOOKUP={'0' :  0
                          ,'1' :  1
                          ,'2' :  2
                          ,'3' :  3
                          ,'4' :  4
                          ,'5' :  5
                          ,'6' :  6
                          ,'7' :  7
                          ,'8' :  8
                          ,'9' :  9
                          ,'A' : 10
                          ,'B' : 11
                          ,'C' : 12
                          ,'D' : 13
                          ,'E' : 14
                          ,'F' : 15
                          ,'G' : 16
                          ,'H' : 17
                          ,'I' : 18
                          ,'J' : 19
                          ,'K' : 20
                          ,'L' : 21
                          ,'M' : 22
                          ,'N' : 23
                          ,'O' : 24
                          ,'P' : 25
                          ,'Q' : 26
                          ,'R' : 27
                          ,'S' : 28
                          ,'T' : 29
                          ,'U' : 30
                          ,'V' : 31
                          ,'W' : 32
                          ,'X' : 33
                          ,'Y' : 34
                          ,'Z' : 35
                          }

    #JAT removed these 
    #if len(empower_file_suffix) != 3:
    #    raise ValueError("empower_file_suffix must be between '001' and 'ZZZ' as file name has 3 trailing characters. empower_file_suffix was "+str(empower_file_suffix))

    #if empower_file_suffix >'ZZZ' or empower_file_suffix <'001':
    #    raise ValueError("empower_file_suffix must be between '001' and 'ZZZ' as file name has 3 trailing characters. empower_file_suffix was "+str(empower_file_suffix))

    number_derived_from_characters=0
    
    #walk backwards through the suffix characters
    #increment i for every character going backwards
    for i, char in enumerate(empower_file_suffix[::-1]):
        #each character translates to a base 36 number, which must then be multiplied by the relevant position
        #so the last character (first we see since we are travelling backwards) 
        #gets multiplied by 1, the next by 36, the next by 36*36 and so on
        number_derived_from_characters+=(36**i)*REVERSE_BASE36_LOOKUP[char]
    
    
    physid_min = (number_derived_from_characters-1)*number_of_elements_per_file+1
    physid_max = physid_min + number_of_elements_per_file -1
    
    
    return physid_min, physid_max

    
def create_and_run_ebat_file(empower_batch_executable=None,ebat_file=None,comment=None,sitefile=None,user=None,password=None,commands=[],empower_batch_version = None,empower_batch_success_code = None):
    '''Create an Empower .ebat file that contains the given commands, and run it using the supplied executable.
    
        Empower Batch cannot take parameters as at the writing of this code
        This function will create a batch (.ebat) file with parameters for the site, and static or dynamically created commands,
        This function will write the file and then run it (using the Empower Batch executable supplied as the first parameter) 
        
        :param empower_batch_executable: The path to the Empower Batch executable
        :param ebat_file: The file path (usually with a .ebat extension, which will be created and run via this function
        :param comment: Lines written before the start of the script - usually a comment
        :param sitefile: The .eks /.beks site that will have the created script run against it - this will be written into the .ebat file or onto the command line. Pass the whole of the connection string for Mongo or MS SQL Server
        :param user: The user under which the script will run - this will be written into the .ebat file unless we are using Empower Batch Console
        :param password: The password with which the script will run - this will be written into the .ebat file unless we are using Empower Batch Console
        :param commands: A list of empower batch commands to run (can be a multiline string)
        :param empower_batch_success_code: Does nothing. We work out the empower batch success code based on version now - this keyword argument has been retained to avoid breaking the old API
    '''
    empower_batch_found = False
    empower_batch_console_found = False

    if empower_batch_executable is not None:
        log.verbose('Create and run EBAT running with supplied executable:'+str(empower_batch_executable))
    
    if empower_batch_version is not None:
        if empower_batch_version < 8:
            #looks like we passed in an Empower Batch success code (which used to be in this position) just ignore it and set empower_batch_version to None:
            #We will look up the version later
            empower_batch_version = None
        
    #If empower_batch_executable is None, then try to find an empower batch
    if empower_batch_executable is None and empower_batch_version is  None:
        
        root_empower_dir = "C:\Program Files\Metapraxis"
        try:
            #Try 
            #C:\Program Files\Metapraxis
            #Then look for directory Empower X.X
            #Get the directory with the highest version number

            #Try to get Empower Batch Console.exe 
            #If not, use Empower Batch.exe
        
            empower_version_directories = [d for d in os.listdir(root_empower_dir)]

        except FileNotFoundError:
        
            msg = 'Could not run Empower batch script, because Empower Batch is not in the usual place, and no path to the Empower Batch Executable was supplied'
            log.exception(msg)
            
            raise mpex.CompletelyLoggedError(msg)
            
        #e.g. "Empower 9.3"
        #remove "Empower " from the front, and compare what is left numerically (so 10 comes after 9)
        #Choose the latest version
        latest_version_directory = None
        max_version_number_found = 0
        for d in empower_version_directories:
            #Make sure the directory is an empower directory, not some stuff just thrown in there
            if d[:8] != 'Empower ':
                continue
            version_number_as_text = d[8:]
            #Try to convert the version number 
            try:
                version_number = float(version_number_as_text)
            except ValueError:   
                continue
        
            if version_number > max_version_number_found:
                empower_batch_found = False
                empower_batch_console_found = False
                
                for f in os.listdir(os.path.join(root_empower_dir,d)):
                    if f=="Empower Batch Console.exe":
                        empower_batch_console_found=True
                    if f=="Empower Batch.exe":
                        empower_batch_found=True
                
                if empower_batch_console_found or empower_batch_found:
                    max_version_number_found = version_number
                    latest_version_directory = d
        
        #Use Empower Batch as fallback position - hopefully we'll be able to use console instead
        if empower_batch_found:
            empower_batch_executable = os.path.join(root_empower_dir,latest_version_directory,"Empower Batch.exe")
            log.verbose('Found batch executable: '+str(empower_batch_executable))
        
        if empower_batch_console_found:
            empower_batch_console_executable = os.path.join(root_empower_dir,latest_version_directory,"Empower Batch Console.exe")
            log.verbose('Found batch console executable: '+str(empower_batch_console_executable))
    
   
        
    else:
        latest_version_directory = None
        if 'Console' in empower_batch_executable:
            empower_batch_console_executable = empower_batch_executable
            empower_batch_executable = None
            empower_batch_found = False
            empower_batch_console_found = True
        else:
            empower_batch_console_executable = None
            empower_batch_found = True
            empower_batch_console_found = False
        
        
    #See if the chosen/passed in executable is Console or Batch
    using_gui = True
    
    version_number_string = None
    #Work out the exact version of Empower batch we are using, as this may affect the return codes and/or the cmmands we are allowed to send
    if empower_batch_version is None:
        
        if empower_batch_console_found:
            #Get the version by running -h and parsing the help
            
            call_line = '"'+empower_batch_console_executable+ '" -h'
            return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            for line in return_value.stdout.decode("latin-1").split('\r\n'):
                #The version is the last word on the copyright line
                if 'Copyright' in line:
                    version_number_string = line.split(' ')[-1]
            
            if version_number_string is not None:
            
                empower_batch_version = version_number_string.split('.')
            else:
                empower_batch_version = None
                
        else:
            if latest_version_directory is not None:
                #Guess the version by checking the folder and running -v on Empower Importer Console.exe - Batch and Importer are likely to be the same version
                call_line = '"'+os.path.join(root_empower_dir,latest_version_directory,"Empower Importer Console.exe")+ '" -s "version" -s "output 1"'
            else:
                #If the batch executable was passed in, use its directory as the location to look for the Importer executable
                call_line = '"'+os.path.join(os.path.dirname(empower_batch_executable),"Empower Importer Console.exe")+ '" -s "version" -s "output 1"'
                
            return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            for line in return_value.stdout.decode("latin-1").split('\r\n'):
                version_number_string = line
                break
            
            if version_number_string is not None:
                empower_batch_version = version_number_string.split('.')
                if empower_batch_version == ['']:
                    #If Empower Importer has no version command, then we are pre 9.1
                    raise ValueError('Cannot run Empower Batch scripts with Empower Batch version lower than 9.1')
            else:
                empower_batch_version = None
            
    
    if empower_batch_version is not None and empower_batch_console_found and empower_batch_executable is not None:
        #We can use Console reliably after change set 64567 for versions greater than 9.4 (9.3 versions don't have the change backported in)
        if int(empower_batch_version[3]) >= 64567 and float(empower_batch_version[0]+'.'+empower_batch_version[1]) >= 9.4:
            #Don't use the GUI if we have a reliable console version
            using_gui = False
    
    log.verbose('Found version '+str(empower_batch_version))
    
    if ebat_file is None:
        ebat_file = r'C:\Temp\tmp.ebat'
    #Open the ebat file for write - overwrite if necessary
    f = open(ebat_file, 'w')
    
    if comment is not None:
        #Write the comments to the file - prefix each line with comment symbol - just in case
        #Split the comment into lines
        comments = comment.split('\n')
        for c in comments:
            #Write each line, prefixed with a #
            f.write('#'+c+'\n')
    
    #Write information about the generation of the file to the file
    f.write('#\n')
    f.write('#Generated automatically on '+str(datetime.datetime.now())+'\n')

    if using_gui:
        f.write('#Designed to be used with Empower Batch.exe\n')
    else:
        f.write('#Designed to be used with Empower Batch Console.exe\n')
    
    #Write the Sitefile, User and password to the file
    if using_gui:
        f.write('SiteFile '+str(sitefile)+'\n')
        f.write('User "'+str(user)+'"\n')
        f.write('Password "'+str(password)+'"\n')
    
    #Write the commands to the file
    for command in commands:
        #Remove SilentExit - we will put it in if necessary ourselves
        if command.lower()!='silentexit':
            f.write(str(command)+'\n')
    
    silent_exit_invoked = False
    if using_gui:
        silent_exit_invoked = True
        f.write('SilentExit'+'\n')
    
    #Close the file
    f.close()
    
    run_silent = False
    if empower_batch_version is not None and float(empower_batch_version[0]+'.'+empower_batch_version[1]) >= 9.2:
        #pre 9.1 isn't really suitable for silent running
        run_silent = True
        
    #Run the file using Empower Batch or Empower Batch Console
    log.verbose("Running EBAT: "+str(ebat_file))
    if using_gui:
        if run_silent:
            call_line=[os.path.abspath(empower_batch_executable),'-a','-r',ebat_file]
        else:
            call_line=[os.path.abspath(empower_batch_executable),ebat_file]
            
        log.verbose('Calling: '+str(call_line))
    else:
        call_line='"{}" -f "{}" -s "{}" -u "{}" -p "{}"'.format(os.path.abspath(empower_batch_console_executable),ebat_file,sitefile,user,password)
        log.verbose('Calling: "{}" -f "{}" -s "{}" -u "{}" -p "{}"'.format(os.path.abspath(empower_batch_console_executable),ebat_file,sitefile,user,'REDACTED'))
    
    return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    log.debug("STDOUT:")
    log.debug(return_value.stdout.decode("utf-8") )
    log.debug("STDERR:")
    log.debug(return_value.stderr.decode("utf-8") )
    
    
    ##This is the error that old bad versions of empower console used to run before V9.4 PR6
    #4294967293
    
    #A string that reports that the Console version was used - used in reporting errors
    console_string = ''
    if using_gui:
        console_string = ' Console'
    
    #There is an odd return code which means that Empower Batch has run correctly, but it is not 1 - it was causing unnecessary pain
    if return_value.returncode==3221225477:
        log.verbose('WARNING!: Empower Batch'+console_string+' returned Code:'+str(return_value.returncode))
        log.verbose('This is a non-fatal error, and does not indicate that the batch has truly failed.')
        log.verbose('Args:'+str(return_value.args))
    elif silent_exit_invoked and return_value.returncode != 1:
        log.error('Empower Batch'+console_string+' failed and returned Code:'+str(return_value.returncode))
        log.error('Args:'+str(return_value.args))
        
        raise mpex.CompletelyLoggedError('Empower Batch'+console_string+' failed and returned Code:'+str(return_value.returncode))
    elif not silent_exit_invoked and return_value.returncode != 0:
        msg = 'Empower Batch'+console_string+' failed and returned Code:'+str(return_value.returncode)
        log.error(msg)
        log.error('Args:'+str(return_value.args))
        
        raise mpex.CompletelyLoggedError(msg)
        
    log.verbose("Completed  EBAT: "+str(ebat_file))

    if ebat_file == r'C:\Temp\tmp.ebat':
        os.remove(ebat_file)
    
def delete_cache_files_for_site(sitefile):
    '''Delete Berkeley cache files of the form "__db.001" in the same directory as the Empower Site (.beks) file
    
    This function should be called prior to bulk loading an Empower site on berkeley db, as the cache files speed up reading, but significantly slow down loading.
    
    :param sitefile: The .beks file of the site which needs its cache files deleting. The beks file should be in the same folder as the cache files.
    '''

    site_file_dir = os.path.dirname(sitefile)
    for file in os.listdir(site_file_dir):
        if fnmatch.fnmatch(file,"__db.[0-9][0-9][0-9]"):
            log.verbose("Deleting the __db.00X cache file:"+str(os.path.join(site_file_dir,file)))
            os.remove(os.path.join(site_file_dir,file))
    

def run_empower_importer_script(script,parameters=[],empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE):
    '''Run an Empower Importer script, with the parameters supplied.
    
    :param script: Importer script to be run
    :param parameters: a list of parameters for the script to be run. -p will be appended before each, and they will be double quoted before calling
    :param empower_importer_executable: path to the Empower Importer executable
    '''
    #Check for existence of script
    try:
        with open(script,'r'):
            pass
    except FileNotFoundError:
        log.error('Empower Importer Script: '+script+' could not be run because it could not be found. Please check it exists')
        open(script,'r')
    
    #Check for existence of importer executable
    
    #generate the parameters
    
    log.verbose( "Running IMPORTER: "+script)
    log.debug( "...with parameters "+str(parameters))
    
    try:
        call_line=[os.path.abspath(empower_importer_executable), os.path.abspath(script)]
        for  param in parameters:
            call_line.append("-p")
            call_line.append(''+param+'')
        
        log.debug('run_empower_importer_script:'+str(call_line))
        #return_value=subprocess.call(call_line)
        return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #log.debug("STDOUT:")
        #log.debug(str(return_value.stdout.decode("utf-8") ))
        log.debug("STDERR:")
        try:
            log.debug(str(return_value.stderr.decode(_get_standard_empower_encoding_from_importer_path(empower_importer_executable)) ))
        except UnicodeDecodeError:
            log.debug(str(return_value.stderr.decode("cp1252") ))
        
    except FileNotFoundError:
        error_message='Empower Importer could not be run because the importer executable could not be found. Please check it exists in: '+str(empower_importer_executable)
        log.error(error_message)
        raise mpex.CompletelyLoggedError(error_message)

    
    if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
        log.error('Empower Importer failed for script '+script+' and returned Code: '+str(return_value))
        raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code: '+str(return_value))

    try:  
        retval = return_value.stdout.decode(_get_standard_empower_encoding_from_importer_path(empower_importer_executable))
    except UnicodeDecodeError:
        retval = return_value.stdout.decode("cp1252")
    
    return retval
    
def export_empower_dimensions(empower_site,empower_user,empower_pwd,export_dimensions_dir,dimension_index=None,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE,encrypted_user=None,encrypted_pwd=None):
    '''Export all of the dimensions for the Site to csv file in the directory specified
    
    :param empower_importer_executable: path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param empower_site: (str) Path to the .eks or .beks site file, for the Empower site 
    :param empower_user: User name for the Empower site
    :param empower_pwd: Password for the Empower site
    :param export_dimensions_dir: The directory that the exported dimensions will be written to as csv files
    :param dimension_index: To export a subset of dimensions pass in a 0 based index for a single dimension , or a list of 0 based indexes for more
    '''

    #importer_script=pkg_resources.resource_filename('pympx', 'ExportAllDimensionElements.eimp')
    all_dimensions_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/ExportAllDimensionElements.eimp')
    single_dimension_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/ExportDimensionElements.eimp')
        
    try:
        os.mkdir(os.path.dirname(export_dimensions_dir))
    except Exception:
        pass

    try:
        os.mkdir(export_dimensions_dir)
    except FileExistsError:
        pass
    
    if dimension_index is None:
        #Export Dimensions 
        log.verbose( "Running IMPORTER: "+"ExportAllDimensionElements.eimp"+" to export the Empower Site dimensions from "+empower_site)
        return_value=subprocess.run([os.path.abspath(empower_importer_executable)
                                    ,os.path.abspath(all_dimensions_importer_script)
                                    ,"-p"
                                    ,'"'+empower_site+'"'
                                    ,"-p"
                                    ,'"'+empower_user+'"'
                                    ,"-p"
                                    ,'"'+empower_pwd+'"'
                                    ,"-p"
                                    ,''+os.path.abspath(export_dimensions_dir)+''
                                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
            log.error("STDOUT:")
            log.error(str(return_value.stdout.decode("utf-8") ))
            log.error("STDERR:")
            log.error(str(return_value.stderr.decode("utf-8") ))
            log.error('Empower Importer failed and returned Code:'+str(return_value))
            raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
        else:
            log.debug("STDOUT:")
            log.debug(str(return_value.stdout.decode("utf-8") ))
            log.debug("STDERR:")
            log.debug(str(return_value.stderr.decode("utf-8") ))
        
            
    else:
        list_of_dimension_indexes_to_export=[]
        #use a list comprehension to try to provoke a TypeError if the dimension_index is a singleinteger
        try:
            list_of_dimension_indexes_to_export=[x for x in dimension_index]
        except TypeError:
            #Create a single element list for the dimensions we wish to export - cast the dimension index to an integer, to make sure it is one
            list_of_dimension_indexes_to_export=[int(dimension_index)]
    
        for dim_index in list_of_dimension_indexes_to_export:
            #Export Dimensions 
            if encrypted_user is None: 
                log.verbose( "Running IMPORTER: "+"ExportDimensionElements.eimp"+" to export the Empower Site dimension "+str(dim_index)+" from "+empower_site)
                try:
                    call_line = [os.path.abspath(empower_importer_executable)
                                                ,os.path.abspath(single_dimension_importer_script)
                                                ,"-p"
                                                ,'"'+empower_site+'"'
                                                ,"-p"
                                                ,'"'+empower_user+'"'
                                                ,"-p"
                                                ,'"'+empower_pwd+'"'
                                                ,"-p"
                                                ,''+os.path.abspath(export_dimensions_dir)+''
                                                ,"-p"
                                                ,str(dim_index)]
                    return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except FileNotFoundError as e:
                    log.error('Error running call:')
                    log.error(str(call_line[0:4]+['-p','"REDACTED_USER"','-p','"REDACTED_PWD"']+call_line[-4:]))
                    log.exception(e)
                    msg = 'File Not Found: Empower Importer failed could not run with call line'+str(call_line)
                    raise mpex.CompletelyLoggedError(msg)
                
                
                if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
                    log.error("STDOUT:")
                    log.error(str(return_value.stdout.decode("utf-8") ))
                    log.error("STDERR:")
                    log.error(str(return_value.stderr.decode("utf-8") ))
                    log.error('Empower Importer failed and returned Code:'+str(return_value))
                    raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
                else:
                    log.debug("STDOUT:")
                    log.debug(str(return_value.stdout.decode("utf-8") ))
                    log.debug("STDERR:")
                    log.debug(str(return_value.stderr.decode("utf-8") ))                
            else:
                log.verbose( "Running IMPORTER: from <stdin> with encrypted logon to export the Empower Site dimension "+str(dim_index)+" from "+empower_site)
                
                command_list = ['set-encrypted-parameter user='    +encrypted_user.decode('utf8')
                               ,'set-encrypted-parameter password='+encrypted_pwd .decode('utf8')
                               ,'set-parameter site='              +empower_site
                               ,'set-parameter target='            +os.path.abspath(export_dimensions_dir)
                               ,'set-parameter dimension_index='   +str(dim_index)
                               
                               ,'empower-export-elements "${site}" "${user}" "${password}" ${dimension_index}'
                               ,'tsv-encode'
                               ,'save-file "${target}\Dimension_${dimension_index}.tsv"'
                               ]
            
                run_single_output_importer_commands(command_list
                                                   ,empower_importer_executable=os.path.abspath(empower_importer_executable)
                                                   )
    
def import_empower_commentary(empower_importer_executable,empower_site,empower_user,empower_pwd,commentary_data_file,commentary_text_file):
    '''Import Commentary into the Sales Pipeline Site
    
    The commentary_data_file and commentary_text_file must be in .tsv format with the correct columns for the empower-save-data and empower-save-text-data importer commands respectively.
    
    This function uses Empower Importer to load the data
    
    :param empower_importer_executable: path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param empower_site: (str) Path to the .eks or .beks site file, for the site which 
    :param empower_user: User name for the Sales Pipeline Empower site
    :param empower_pwd: Password for the Sales Pipeline Empower site
    :param commentary_data_file: Path to the .tsv file containing data formatted for the Importer empower-save-data command. The file should have no headers
    :param commentary_text_file: Path to the .tsv file containing text formatted for the Importer empower-save-text command. The file should have no headers
    '''
    commentary_data_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/LoadCommentaryData.eimp')
    commentary_text_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/LoadCommentaryText.eimp')
    
    if commentary_data_file:
        #Import Commentary into Site
        log.verbose( "Running IMPORTER: LoadCommentaryData.eimp to import the commentary data")
        return_value=subprocess.run([os.path.abspath(empower_importer_executable), commentary_data_importer_script,"-p",'"'+empower_site+'"',"-p",'"'+empower_user+'"',"-p",'"'+empower_pwd+'"',"-p",os.path.abspath(commentary_data_file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

        if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
            log.error("STDOUT:")
            log.error(str(return_value.stdout.decode("utf-8") ))
            log.error("STDERR:")
            log.error(str(return_value.stderr.decode("utf-8") ))
            log.error('Empower Importer failed and returned Code:'+str(return_value))
            raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
        else:
            log.debug("STDOUT:")
            log.debug(str(return_value.stdout.decode("utf-8") ))
            log.debug("STDERR:")
            log.debug(str(return_value.stderr.decode("utf-8") ))

    if commentary_text_file:        
        #Import Commentary into Site
        log.verbose( "Running IMPORTER: LoadCommentaryText.eimp to import the commentary text")
        return_value=subprocess.run([os.path.abspath(empower_importer_executable), commentary_text_importer_script,"-p",'"'+empower_site+'"',"-p",'"'+empower_user+'"',"-p",'"'+empower_pwd+'"',"-p",os.path.abspath(commentary_text_file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
            log.error("STDOUT:")
            log.error(str(return_value.stdout.decode("utf-8") ))
            log.error("STDERR:")
            log.error(str(return_value.stderr.decode("utf-8") ))
            log.error('Empower Importer failed and returned Code:'+str(return_value))
            raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
        else:
            log.debug("STDOUT:")
            log.debug(str(return_value.stdout.decode("utf-8") ))
            log.debug("STDERR:")
            log.debug(str(return_value.stderr.decode("utf-8") ))
   
    
def msgsink__run_single_dim0_empower_load(bulkload_queue=None
                                         ,empower_main_site=None
                                         ,empower_work_site=None
                                         ,empower_user=None
                                         ,empower_pwd=None
                                         ,encrypted_empower_user=None
                                         ,encrypted_empower_pwd=None
                                         ,bulk_load_processing_dir=None
                                         ,shard_file_prefix=None
                                         ,empower_data_file_prefix=None
                                         ,number_of_storage_elements_per_empower_data_file=1
                                         ,main_site_output_data_files_dir=None
                                         ,do_voodoo=False
                                         ,voodoo_bytes=8192
                                         ,voodoo_cache_dimension_number=0
                                         ,voodoo_cache_elements=[]
                                         ,voodoo_key_signature=b'\x44\x04\x01\0\0\0'
                                         ,voodoo_cache_instructions_dir=None
                                         ,storage_dimension_index=0
                                         ,pre_hook_function=lambda x:None
                                         ,post_hook_function=lambda x:None
                                         ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                                         ,load_method='bulk'
                                         ,exit_on_failure=True
                                         ,logging_queue=None
                                         ,safe_load=True
                                         ):

    '''
    Poll the bulkload_queue, and bulk load single shards of data into the Empower site, using the Work Site
    
    * In a loop, getting messages from the bulkload_queue until the DONE message is received:
    * For each message, which refers to a single shard of data (i.e.e a single storage dimension entity, and therefore a single storage file)
    * Clear out the data file in the work site
    * Copy the appropriate data file into the work site from the main site
    * Bulk load into the work site
    * Move the final data file into the main_site_output_data_files_dir
    * Perform Voodoo Caching. Voodoo Caching warms the Window file cache for a better end user response. It is most effective for dimensions at the start of Empowers physical key - Mode or Metric for instance, or the first unit dimension

        
    .. note::
        Each of the many processes running this function **must** have their own work site
    
    :param empower_importer_executable: (str) path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param empower_work_site: Path to the .beks file of the **Work** copy of the empower site
    :param empower_user: User name for the empower Empower site
    :param empower_pwd: Password for the empower Empower site
    :param number_of_storage_elements_per_empower_data_file: Number of storage elements found in each Empower Data file
    :param bulkload_queue: The multiprocessing.Queue which communicates which shards are ready for bulk loading. Shards are pulled from this queue and processed
    :param do_voodoo: (Boolean) Create instructions to warm the windows file cache with a given set of elements. Does not warm the cache. You must kick off the cache warmer separately for this to work
    :param voodoo_bytes: The number of bytes to cache at a time. 8192 is good for Berkeley, 4092 or less might be better for EKS
    :param voodoo_cache_elements: Empower PhysIDs for the elements we want to voodoo cache
    :param storage_dimension_index:
    :param pre_hook_function: Function to run on a file before running BulkImport.eimp - useful for say exploding data in a shard for testing
    :param post_hook_function: Function to run on a file before running BulkImport.eimp
    :param exit_on_failure: Boolean. If this process is being called in its own process, set this as true for neater logging during error handling
    :param logging_queue: multiprocessing.Queue, if we are logging to file, we need a queue created in conjunction with the filelogger process to send logging messages to
    '''
    
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
        
    main_site_data_files_dir=os.path.join(os.path.dirname(empower_main_site),'Data Files')
    
    #There are multiple working site files
    working_site_dir=os.path.dirname(empower_work_site)
    working_data_files_dir=os.path.join(working_site_dir,'Data Files')
    try:
        os.mkdir(working_data_files_dir)
    except FileExistsError:
        pass 
    

        
    voodoo_cache_instructions_dir=voodoo_cache_instructions_dir
    exitcode=None
    try:
        
        while True:
            msg=bulkload_queue.get()
            if  msg==FAILED:
                raise mpex.UpstreamFailureError('Upstream Queuing Process Failed')
                break
                
            #When DONE (0) stop
            if  msg==DONE:
                break
                
            else:
                #Get a shard off the queue
                shard_suffix=msg
                
                run_single_dim0_empower_load(shard_suffix
                                             ,main_site_data_files_dir=main_site_data_files_dir
                                             ,empower_work_site=empower_work_site
                                             ,empower_user=empower_user
                                             ,empower_pwd=empower_pwd
                                             ,encrypted_empower_user=encrypted_empower_user
                                             ,encrypted_empower_pwd=encrypted_empower_pwd
                                             ,bulk_load_processing_dir=bulk_load_processing_dir
                                             ,shard_file_prefix=shard_file_prefix
                                             ,empower_data_file_prefix=empower_data_file_prefix
                                             ,number_of_storage_elements_per_empower_data_file=number_of_storage_elements_per_empower_data_file
                                             ,main_site_output_data_files_dir=main_site_output_data_files_dir
                                             ,storage_dimension_index=storage_dimension_index
                                             ,do_voodoo=do_voodoo
                                             ,voodoo_bytes=voodoo_bytes
                                             ,voodoo_cache_dimension_number=voodoo_cache_dimension_number
                                             ,voodoo_cache_elements=voodoo_cache_elements
                                             ,voodoo_cache_instructions_dir=voodoo_cache_instructions_dir
                                             ,voodoo_key_signature=voodoo_key_signature
                                             ,pre_hook_function=pre_hook_function
                                             ,post_hook_function=post_hook_function
                                             ,empower_importer_executable=empower_importer_executable
                                             ,load_method=load_method
                                             ,safe_load=safe_load
                                             )
                #Record the task completion
                bulkload_queue.task_done(shard_suffix)
    
        exitcode=0
        log.verbose('Load has completed all work on the queue')
        
    except mpex.UpstreamFailureError:
        log.error('Load stopping because Upstream Process Failed')
        if exit_on_failure:
            exitcode=1 
    except Exception as e:
        try:
            log.error(str(e)) 
        except Exception:
            pass
    
        if exit_on_failure:
            exitcode=1 
    
    finally:
        if bulkload_queue:
            try:
                log.debug('Disposing of bulkload queue')
                bulkload_queue.dispose()
                log.debug('Disposed of bulkload queue')
                
            except Exception as e:
                try:
                    log.error(str(e))    
                except Exception:
                    pass
        if exitcode:
            try:
                log.debug('Exiting with exitcode '+str(exitcode))   
            except Exception:
                pass
            sys.exit(exitcode)
    
        log.debug('Exiting with 0')
        sys.exit(0)


def msgsink__run_single_sql_empower_bulk_load(bulkload_queue=None
                                             ,empower_main_site=None
                                             #,empower_work_site=None
                                             ,encrypted_empower_user=None
                                             ,encrypted_empower_pwd=None
                                             ,bulk_load_processing_dir=None
                                             ,shard_file_prefix=None
                                             ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                                             ,logging_queue=None
                                             ):
    '''
    Poll the bulkload_queue, and bulk load single shards of data into the Empower site
    
    * In a loop, getting messages from the bulkload_queue until the DONE message is received:
    * For each message, which refers to a single shard of data (i.e. a single storage dimension entity, and therefore a single storage file)
    * Bulk load into the work site
        
    .. note::
        Unlike with eks processing, we don't use multiple work sites for bulk loading eks
    
    :param empower_importer_executable: (str) path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param bulkload_queue: The multiprocessing.Queue which communicates which shards are ready for bulk loading. Shards are pulled from this queue and processed
    :param logging_queue: multiprocessing.Queue, if we are logging to file, we need a queue created in conjunction with the filelogger process to send logging messages to
    '''
    
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
        
    exitcode=None
    log.verbose('Bulk Loader Starting work on Queue')
        
    try:
        
        while True:
            msg=bulkload_queue.get()
            if  msg==FAILED:
                raise mpex.UpstreamFailureError('Upstream Queuing Process Failed')
                break
                
            #When DONE (0) stop
            if  msg==DONE:
                break
                
            else:
                #Get a shard off the queue
                shard_suffix=msg
                
                bulkload_empower(bulk_load_file_path = os.path.join(bulk_load_processing_dir,shard_file_prefix+shard_suffix+'.tsv') 
                                 ,empower_site=empower_main_site
                                 ,encrypted_empower_user=encrypted_empower_user
                                 ,encrypted_empower_pwd=encrypted_empower_pwd
                                 ,empower_importer_executable=empower_importer_executable
                                 )
                #Record the task completion
                bulkload_queue.task_done(shard_suffix)
    
        exitcode=0
        log.verbose('Load has completed all work on the queue')
        
    except mpex.UpstreamFailureError:
        log.error('Load stopping because Upstream Process Failed')
        if exit_on_failure:
            exitcode=1 
    except Exception as e:
        try:
            log.error(str(e)) 
        except Exception:
            pass
    
        if exit_on_failure:
            exitcode=1 
    
    finally:
        if bulkload_queue:
            try:
                log.debug('Disposing of bulkload queue')
                bulkload_queue.dispose()
                log.debug('Disposed of bulkload queue')
                
            except Exception as e:
                try:
                    log.error(str(e))    
                except Exception:
                    pass
        if exitcode:
            try:
                log.debug('Exiting with exitcode '+str(exitcode))   
            except Exception:
                pass
            sys.exit(exitcode)
    
        log.debug('Exiting with 0')
        sys.exit(0)   
                                                 
def run_single_dim0_empower_load( shard_suffix
                                 ,main_site_data_files_dir
                                 ,empower_work_site=None
                                 ,empower_user=None
                                 ,empower_pwd=None
                                 ,encrypted_empower_user=None
                                 ,encrypted_empower_pwd=None
                                 ,bulk_load_processing_dir=None
                                 ,shard_file_prefix=None
                                 ,empower_data_file_prefix=None
                                 ,number_of_storage_elements_per_empower_data_file=1
                                 ,storage_dimension_index=0
                                 ,main_site_output_data_files_dir=None
                                 ,do_voodoo=False
                                 ,voodoo_bytes=8192
                                 ,voodoo_cache_dimension_number=0
                                 ,voodoo_cache_elements=[]
                                 ,voodoo_cache_instructions_dir=None
                                 ,voodoo_key_signature=b'\x44\x04\x01\0\0\0'
                                 ,pre_hook_function=lambda x:None
                                 ,post_hook_function=lambda x:None
                                 ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                                 ,load_method='bulk'
                                 ,safe_load=True
                                 ):
    '''
    Bulk load a single shard of data into an Empower site, using a working version Work Site
    
    * Clear out the data file in the work site
    * Copy the appropriate data file into the work site from the main site
    * Bulk load into the work site
    * Move the final data file into the processed folder main_site_output_data_files_dir
    * Perform Voodoo Caching. Voodoo Caching warms the Window file cache for a better end user response. It is most effective for dimensions at the start of Empowers physical key - Mode or Metric for instance, or the first unit dimension

    .. note::
        Each of the many processes running this function **must** have their own work site
    
    :param empower_importer_executable: (str) path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param empower_work_site: Path to the .beks file of the **Work** copy of the Empower site
    :param empower_user: User name for the  Empower site
    :param empower_pwd: Password for the Empower site
    :param number_of_storage_elements_per_empower_data_file: Number of storage elements found in each Empower Data file
    :param storage_dimension_index: Index of the storage dimension, used in voodoo caching
    :param main_site_data_files_dir: 'Data Files' directory from the main site - used as a source of data files for processing
    :param bulk_load_processing_dir: Path to the directory holding single shard bulk load files in .tsv format
    :param do_voodoo: (Boolean) Create instructions to warm the windows file cache with a given set of elements. Does not warm the cache. You must kick off the cache warmer separately for this to work
    :param voodoo_bytes: The number of bytes to cache at a time. 8192 is good for Berkeley, 4092 or less might be better for EKS
    :param voodoo_cache_elements: Empower PhysIDs for the elements we want to voodoo cache
    :param voodoo_cache_instructions_dir: Directory to save voodoo cache instructions
    :param pre_hook_function: Function to run on a file before running BulkImport.eimp - useful for say exploding data in a shard for testing
    :param post_hook_function: Function to run on a file before running BulkImport.eimp
    :param shard_suffix: Suffix of the single shard to be loaded
    :param load_method: method of loading Empower - bulk load:'bulk' or import: 'import'. This method depends on whether the file is in bulk load or import format 
    :param safe_load: copy files from main site Data Files instead of moving them
    '''        
    #Get the storage physid to be used in checking
    storage_phys_id_min, storage_phys_id_max=empower_file_suffix_to_physid(shard_suffix,number_of_elements_per_file=number_of_storage_elements_per_empower_data_file)
    

    
    #Work out the sharded file name
    empower_data_file_name=empower_data_file_prefix+shard_suffix+'.000'
    working_site_data_dir=os.path.join(os.path.dirname(empower_work_site),'Data Files')
    
    #Clear out the working directory
    #Empty the working site data directory
    for f in os.listdir(working_site_data_dir):
        file_path = os.path.join(working_site_data_dir, f)
        if os.path.isfile(file_path):
            log.verbose('Deleting file '+str(file_path))
            os.unlink(file_path)
            
    source_file_name=os.path.join(bulk_load_processing_dir,shard_file_prefix+shard_suffix+'.tsv')
    
    if os.path.isfile(source_file_name):
        main_site_data_file=os.path.join(main_site_data_files_dir,empower_data_file_name)
        work_site_data_file=os.path.join(working_site_data_dir,empower_data_file_name)
            
        log.verbose( "Preparing to Load shard: "+str(empower_data_file_name)+ ' into ' + str(work_site_data_file))
    
        #Move the file from the main directory into the working site directory
        #if it is not there that's fine
        try:
            log.verbose( "Moving Data File into place from "+str(main_site_data_file)+' to '+str(work_site_data_file))
            #Try doing the move as a copy and delete, in order to get the data in the windows cache - and speed up subsequent reads
            shutil.copy(os.path.join(main_site_data_files_dir,empower_data_file_name),os.path.join(working_site_data_dir,empower_data_file_name))
            
        except FileNotFoundError:
            log.verbose( "Did not find: "+str(main_site_data_file)+'. A new file will be created when the shard is loaded.')
            pass
            
        pre_hook_function(source_file_name)
    
        delete_cache_files_for_site(empower_work_site)
    
        bulk_import_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/BulkImport.eimp')
        nonbulk_import_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/EmpowerImport.eimp')
    
        if load_method=='bulk':
            if encrypted_empower_user is None:
                #Run the bulk import into SMD using Empower Importer
                log.verbose( "Running IMPORTER: "+"BulkImport.eimp"+" to bulk import the file: "+str(source_file_name) + ' into ' + empower_work_site)
                return_value=subprocess.run([os.path.abspath(empower_importer_executable), bulk_import_importer_script,"-p",'"'+os.path.abspath(empower_work_site)+'"',"-p",'"'+empower_user+'"',"-p",'"'+empower_pwd+'"',"-p",os.path.abspath(source_file_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
                    log.error("STDOUT:")
                    log.error(str(return_value.stdout.decode("utf-8") ))
                    log.error("STDERR:")
                    log.error(str(return_value.stderr.decode("utf-8") ))
                    log.error('Empower Importer failed and returned Code:'+str(return_value))
                    raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
                else:
                    log.verbose("STDOUT:")
                    log.verbose(str(return_value.stdout.decode("utf-8") ))
                    log.verbose("STDERR:")
                    log.verbose(str(return_value.stderr.decode("utf-8") ))
            else:
                
                command_list = ['set-encrypted-parameter user='     + encrypted_empower_user.decode('utf8')
                               ,'set-encrypted-parameter password=' + encrypted_empower_pwd .decode('utf8')
                               ,'set-parameter site='               + os.path.abspath(empower_work_site)
                               ,'load-file-tsv "'                   + os.path.abspath(source_file_name) + '"'
                               ,'empower-import-bulk-data "${site}" "${user}" "${password}"'
                               ]

                run_single_output_importer_commands(command_list
                                                        ,empower_importer_executable=os.path.abspath(empower_importer_executable)
                                                        )
                log.verbose( "Bulk Import complete: "+str(source_file_name))  
            
            
        elif load_method=='import':
            if encrypted_empower_user is None:
                #Run the bulk import into SMD using Empower Importer
                log.verbose( "Running IMPORTER: "+"EmpowerImport.eimp"+" to import the file: "+str(source_file_name) + ' into ' + empower_work_site)
                return_value=subprocess.run([os.path.abspath(empower_importer_executable), nonbulk_import_importer_script,"-p",'"'+os.path.abspath(empower_work_site)+'"',"-p",'"'+empower_user+'"',"-p",'"'+empower_pwd+'"',"-p",os.path.abspath(source_file_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
                    log.error("STDOUT:")
                    log.error(str(return_value.stdout.decode("utf-8") ))
                    log.error("STDERR:")
                    log.error(str(return_value.stderr.decode("utf-8") ))
                    log.error('Empower Importer failed and returned Code:'+str(return_value))
                    raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
                else:
                    log.verbose("STDOUT:")
                    log.verbose(str(return_value.stdout.decode("utf-8") ))
                    log.verbose("STDERR:")
                    log.verbose(str(return_value.stderr.decode("utf-8") ))
            else:
                command_list = ['set-encrypted-parameter user='     + encrypted_empower_user.decode('utf8')
                               ,'set-encrypted-parameter password=' + encrypted_empower_pwd .decode('utf8')
                               ,'set-parameter site='               + os.path.abspath(empower_work_site)
                               ,'load-file-tsv "'                   + os.path.abspath(source_file_name) + '"'
                               ,'empower-import-data "${site}" "${user}" "${password}"'
                               ]

                run_single_output_importer_commands(command_list
                                                        ,empower_importer_executable=os.path.abspath(empower_importer_executable)
                                                        )

            log.verbose( "Import complete: "+str(source_file_name))   
        else:
            log.error( "Import failed because of incorrect load_method: "+str(load_method))   
            log.error( "load_method argument must be 'bulk' or 'import'")   
            #This is not an end user error message - it is caused by incorrect programming
            raise ArgumentError("load_method argument must be 'bulk' or 'import' not '"+ str(load_method)+ "'")
        

        
        post_hook_function(source_file_name)
        
        #We only need to generate voodoo caching instructions if we have changed the data
        if do_voodoo:
            log.verbose("Generating cache instructions for Mode elements: "+str(voodoo_cache_elements))
            generate_cache_instructions(data_file=os.path.join(working_site_data_dir,empower_data_file_name)
                                                                   ,voodoo_cache_instructions_dir=voodoo_cache_instructions_dir
                                                                   ,voodoo_cache_elements=voodoo_cache_elements
                                                                   ,storage_dimension_physid_min=storage_phys_id_min
                                                                   ,storage_dimension_physid_max=storage_phys_id_max
                                                                   ,storage_dimension_index=storage_dimension_index
                                                                   ,voodoo_cache_dimension=voodoo_cache_dimension_number
                                                                   ,chunksize=voodoo_bytes
                                                                   ,key_signature=voodoo_key_signature
                                                                   ,found_key_jump=92)
            log.verbose("Voodoo caching complete: "+os.path.join(working_site_data_dir,empower_data_file_name))
        
        #move single Storage Dimension file from working site to completed data directory
        log.verbose( "Moving Completed Data File from "+str(os.path.join(working_site_data_dir,empower_data_file_name))+' to '+str(os.path.join(main_site_output_data_files_dir,empower_data_file_name)))
        shutil.move(os.path.join(working_site_data_dir,empower_data_file_name),os.path.join(main_site_output_data_files_dir,empower_data_file_name))
        log.verbose( "Import Shard complete: "+str(source_file_name))

        #During non-safe loads, remove files from Data Files after the bulk load has successfully put a file into the 
        try:
            if not safe_load:
                os.unlink(os.path.join(main_site_data_files_dir,empower_data_file_name))           
        except FileNotFoundError:
            pass
            
    else:
        log.verbose( "Load source file does not exist: "+str(source_file_name))
        if not safe_load:
            log.verbose( "Moving data file direct to completed directory: "+str(os.path.join(main_site_data_files_dir,empower_data_file_name))+' to '+str(os.path.join(main_site_output_data_files_dir,empower_data_file_name)))
            shutil.move(os.path.join(main_site_data_files_dir,empower_data_file_name),os.path.join(main_site_output_data_files_dir,empower_data_file_name))
        else:
            log.verbose( "Copying data file direct to completed directory: "+str(os.path.join(main_site_data_files_dir,empower_data_file_name))+' to '+str(os.path.join(main_site_output_data_files_dir,empower_data_file_name)))
            shutil.copy(os.path.join(main_site_data_files_dir,empower_data_file_name),os.path.join(main_site_output_data_files_dir,empower_data_file_name))
            
def bulkload_empower( bulk_load_file_path
                                 ,empower_site=None
                                 ,encrypted_empower_user=None
                                 ,encrypted_empower_pwd=None
                                 ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                                 ):
    '''
    Bulk load a single tsv into an Empower site
    
    * Bulk load into the work site
    
    .. note::
        Each of the many processes running this function **must** have their own work site
    
    :param bulk_load_file_path: path to the empower bulk load file in tsv format
    :param empower_site: site locator for Empower site
    :param encrypted_empower_user: Encrypted user name for the  Empower site
    :param encrypted_empower_pwd: Encrypted Password for the Empower site
    
    :param empower_importer_executable: (str) path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    '''        
    #Get the storage physid to be used in checking
            
    command_list = ['set-encrypted-parameter user='     + encrypted_empower_user.decode('utf8')
                   ,'set-encrypted-parameter password=' + encrypted_empower_pwd .decode('utf8')
                   ,'set-parameter site='               + empower_site
                   ,'load-file-tsv "'                   + os.path.abspath(bulk_load_file_path) + '"'
                   ,'empower-import-bulk-data "${site}" "${user}" "${password}"'
                   ]

    run_single_output_importer_commands(command_list ,empower_importer_executable=os.path.abspath(empower_importer_executable))
    
    log.verbose( "Import Shard complete: "+str(bulk_load_file_path))


def four_bytes_to_int(bytes):
    return int.from_bytes(bytes[0:2],'little')+int.from_bytes(bytes[2:4],'little')*256*256

def int_to_four_bytes(int):
    return int.to_bytes(4,'little')

    
def generate_cache_instructions(data_file,voodoo_cache_instructions_dir,voodoo_cache_elements,storage_dimension_physid_min,storage_dimension_physid_max=None,storage_dimension_index=0,voodoo_cache_dimension=0,chunksize=8192,key_signature=b'\x44\x04\x01\0\0\0',found_key_jump=92):    
    '''Write Windows cache warming instructions to a file, with the page locations of the elements we want to warm the cache with
    
    * The cache warming instructions will be in a file with the same name as the data file.
    * The cache warming instructions consist of offset and size of read (both in bytes)
    
    .. hardcode::
        Element ids encoded in bytes are used in the 'accuracy_required' mode. This is turned off currently
    
    :param data_file: The Empwoer data file we are searching for keys
    :param voodoo_cache_instructions_dir: The directory we are writing to with the caching instructions
    :param voodoo_cache_elements: A list of physical ids (as integers) that we wish to warm the cache for.
    :param storage_dimension_physid_min: To help detect wheteher we have a key match or not we need to know the range of possible storage id identifiers 
    :param storage_dimension_physid_max: To help detect wheteher we have a key match or not we need to know the range of possible storage id identifiers
    :param voodoo_cache_dimension: The dimension we wish to cache 0 is Mode, 1 is Metric.
    :param chunksize: size of chunk we wish to read. The default is twcie the page size, because often Berkeley db is reading 2 pages at a time
    :param key_signature: Bytes we always find at the start of a key. The default is 44 04 01 00 00 00 Meaning D for date, 4 for 'Month', and four bytes 1 (i.e. all currency)
    :param found_key_jump: Smallest numebr of bytes between keys. When we find a key we can jump forward this number of bytes to speed up searching for the next key
    '''
    
    #Nice fast file reading for the voodoo file cacher
    from mmap import ACCESS_READ, mmap

    start_time=datetime.datetime.now()
    
    data_files_dir=os.path.dirname(data_file)
    filename=os.path.basename(data_file)
    
    signature_length=len(key_signature)

    key_length=signature_length+4*11

    #Choose smallest differences between keys
    
    accuracy_required=False
    sloppy=False

    pos_range=range(0,10)
    differences_between_keys={}

    dimension_offset_from_sig=signature_length+(voodoo_cache_dimension*4)

    #Cast all elements to integers in case they have come through as floats or strings
    voodoo_cache_elements=[int(i) for i in voodoo_cache_elements]

    voodoo_cache_elements_bytes=[int_to_four_bytes(bb) for bb in voodoo_cache_elements]

    storage_dimension_physid_bytes_min=int_to_four_bytes(storage_dimension_physid_min)
    if storage_dimension_physid_max==None:
        storage_dimension_physid_max=storage_dimension_physid_min
    storage_dimension_physid_bytes_max=int_to_four_bytes(storage_dimension_physid_max)
    #log.debug(voodoo_cache_elements_bytes)
        
    voodoo_cache_chunks=[]
    
    dimension_tracker={}
    jumps=0
    seeks=0
    with open(os.path.join(voodoo_cache_instructions_dir,filename),'w') as out_f:

        with open(os.path.join(data_files_dir,filename), 'rb') as f, mmap(f.fileno(), 0, access=ACCESS_READ) as mm:
            pos=0
            
            num_keys_in_file=0
            num_index_errors=0
            num_sig_matches_in_file=0
            
            len_bytes=len(mm)
            log.verbose('Bytes in '+filename+'='+str(len_bytes))
            while pos < len_bytes:
                
                bytes = mm[pos:pos+chunksize]
                next_position_to_search_from=0
                num_keys_in_block=0
                previous_start_of_key_signature=0
                while True: 
                    try:
                        start_of_key_signature=bytes.index(key_signature,next_position_to_search_from)
                        next_position_to_search_from=start_of_key_signature+signature_length
                    except ValueError as e:
                        break    
                    
                    num_sig_matches_in_file+=1
                    
                    #It is faster to scan if we don't mind some false positives
                    if accuracy_required:
                        
                        #Check the SBU in [2,48]
                        if bytes[start_of_key_signature+26:start_of_key_signature+30] not in [b'\x02\0\0\0',b'\x30\0\0\0']:
                            continue

                        #Check the Probability stage in 1-6
                        if bytes[start_of_key_signature+34:start_of_key_signature+38] not in [b'\x01\0\0\0',b'\x02\0\0\0',b'\x03\0\0\0',b'\x04\0\0\0',b'\x05\0\0\0',b'\x06\0\0\0']:
                            continue
                        
                        #Check the Deal Size in 1-4
                        if bytes[start_of_key_signature+38:start_of_key_signature+42] not in [b'\x01\0\0\0',b'\x02\0\0\0',b'\x03\0\0\0',b'\x04\0\0\0']:
                            continue
                        
                        #No key can ever be zero, but it is a common value - search for it before continuing
                        #None of our keys is > 65536
                        try:
                            zero_byte_found=False
                            greater_than_65536_found=False
                            for p in pos_range:
                                if bytes[start_of_key_signature+signature_length+p*4:start_of_key_signature+signature_length+p*4+4]==b'\0\0\0\0':
                                    zero_byte_found=True
                                    break
                                
                                #if bytes[start_of_key_signature+signature_length+p*4+2:start_of_key_signature+signature_length+p*4+4]!=b'\0\0':
                                #    greater_than_65536_found=True
                                #    break
                                
                            if zero_byte_found or greater_than_65536_found:
                                continue
                            
                        except IndexError:
                            break
                        
                        pass

                    if not sloppy:
                        #Check the Age of Opp is 1
                        if bytes[start_of_key_signature+42:start_of_key_signature+46] != b'\x01\0\0\0':
                            continue
                        
                        #Check the storage dimension is this file's physid
                        #JAT 2019-06-25 Looks like this only works by luck - surely all should be converted to bytes, or the bytes compared one by one
                        #since the bytes are little endian
                        #Not changing right now, because voodoo caching is not currently being used and may be deprecated
                        putative_storage_dimension_physid_bytes=bytes[start_of_key_signature+14+4*storage_dimension_index:start_of_key_signature+18+4*storage_dimension_index]
                        if putative_storage_dimension_physid_bytes<storage_dimension_physid_bytes_min or putative_storage_dimension_physid_bytes>storage_dimension_physid_bytes_max:
                            continue
                                                
                    num_keys_in_file+=1
                    num_keys_in_block+=1
                    log.debug(bytes[start_of_key_signature:start_of_key_signature+4],bytes[start_of_key_signature+4:start_of_key_signature+8], 'at offset',str(pos+start_of_key_signature) )
                    try:
                        dimension_start_pos=start_of_key_signature+dimension_offset_from_sig 
                        element_bytes=bytes[dimension_start_pos:dimension_start_pos+4]
                    except IndexError:
                        num_index_errors+=1
                        break

                    #element_int=four_bytes_to_int(element_bytes)
                    if element_bytes in voodoo_cache_elements_bytes:
                        try:
                            #Keep track of where the keys cn be found
                            dimension_tracker[element_bytes].append(pos)
                            
                        except KeyError:
                            #First time we've seen this element
                            #element_byte_positions=[]
                            dimension_tracker[element_bytes]=[pos]

                        #We do not need to count all of the keys - continue and jump to the next position
                        jumps+=1
                        break    
                    else:
                        #advance by further if we have found a key
                        next_position_to_search_from=start_of_key_signature+found_key_jump
                        seeks+=1
                    
                #Advance our position
                pos+=chunksize
                
                if num_keys_in_block==0:
                    log.debug(pos, num_keys_in_block)
                    
            mid_time=datetime.datetime.now()                
                
            
            #for dimension_dict in dimension_tracker[1]:
            dimension_tracker = {four_bytes_to_int(k):sorted(list(set(v))) for k,v in dimension_tracker.items()}

            voodoo_cache_chunks=[]
            #How many locations are there per metric?
            for k,v in dimension_tracker.items():
                log.debug(str(k)+' '+str(len(v))+' X' if k in voodoo_cache_elements else '')
                
                voodoo_cache_chunks+=v
            
            voodoo_cache_chunks=sorted(list(set(voodoo_cache_chunks)))
            
            log.verbose('Selected cache chunks in '+filename+'='+str(len(voodoo_cache_chunks))+'/'+str(len_bytes/chunksize)+' chunks of '+str(chunksize)+' bytes each')
            
            count_cache_chunks_contiguous=0
            
            previous_offset=None
            initial_offset_in_range=None
            
            
            for offset in voodoo_cache_chunks:
            
                #This is the case for the first iteration
                if initial_offset_in_range is None:
                    initial_offset_in_range=offset
                    rangesize=0
                
                if previous_offset is None or previous_offset+chunksize==offset:
                    rangesize+=chunksize
                else:
                    out_f.write(str(initial_offset_in_range))
                    out_f.write(' ')
                    out_f.write(str(rangesize))
                    out_f.write('\n')
                    
                    initial_offset_in_range=offset
                    rangesize=chunksize
                    count_cache_chunks_contiguous+=1
                    
                previous_offset=offset
            
            if initial_offset_in_range is not None:
                #Write final range
                out_f.write(str(initial_offset_in_range))
                out_f.write(' ')
                out_f.write(str(rangesize))
                out_f.write('\n')
            
                count_cache_chunks_contiguous+=1            
            
            log.verbose('Contiguous cache chunks= '+str(count_cache_chunks_contiguous))
            
    end_time=datetime.datetime.now()
    
    log.debug('Start Read '+str(start_time))
    log.debug('Finish Read '+str(mid_time))
    log.debug('Complete   '+str(end_time))
    log.debug('Jumps '+str(jumps))
    log.debug('Seeks '+str(seeks))
    log.debug('IndErr '+str(num_index_errors))   
            

def shard_files_in_list_by_storage_dim(files_to_shard=[]
                                      ,storage_dimension_index=0
                                      ,load_processing_dir=None
                                      ,shard_prefix='Shard_'
                                      ,number_of_storage_elements_per_empower_data_file=1
                                      ,separator='\t'
                                      ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                                      ,storage_dimension_short_name_physid_lookup=None
                                      ,logging_queue=None
                                      ):
    log.verbose('Sharding files in list')

    
    #Create the queue
    q=mpq.PersistentQueue(pickup_file_prefix='Sharding Queue')
    
    #Start the message sink
    sharder=multiprocessing.Process(target=msgsink__shard_files_by_storage_dim
                                   ,kwargs={'storage_dimension_index':storage_dimension_index
                                           ,'load_processing_dir':load_processing_dir
                                           ,'file_mask':'*.tsv'
                                           ,'shard_prefix':shard_prefix
                                           ,'number_of_storage_elements_per_empower_data_file':number_of_storage_elements_per_empower_data_file
                                           ,'separator':separator
                                           ,'site_exploded_queue':q
                                           ,'site_sharded_queue':None
                                           ,'empower_importer_executable':empower_importer_executable
                                           ,'storage_dimension_short_name_physid_lookup':storage_dimension_short_name_physid_lookup
                                           ,'logging_queue':logging_queue
                                           }                                                
                                   ,name='Shard Files')

    #Start the (single threaded) sharder in it's own thread
    sharder.start()    
    
    try:
        #push work to the queue
        for file in files_to_shard:

            file_name,file_extension=os.path.splitext(file)
            file_mask='*'+file_extension
            
            #put the message on the queue
            q.put(file)
            log.verbose('Queuing file for sharding:'+file)
        
        log.verbose('Closing sharding queue...')
        q.close() 
        log.verbose('Sharding queue closed')
        
    except Exception:
        log.error('Failing sharding queue...')
        q.fail()
        log.error('Failed  sharding queue')
        raise
        
    log.verbose('Joining sharder')
    sharder.join()

    if sharder.exitcode != 0:
        log.error('{}.exitcode = {}'.format(sharder.name, sharder.exitcode))   
        raise mpex.CompletelyLoggedError('Sharder Job:'+sharder.name+' failed with exit code '+str(sharder.exitcode)) 
    else:
        log.verbose('{}.exitcode = {}'.format(sharder.name, sharder.exitcode))           


        
#TODO-break out into queue pulling msgsink, and a function which does the actual work
def msgsink__shard_files_by_storage_dim(storage_dimension_index=0
                                      ,load_processing_dir=None
                                      ,file_mask='*.tsv'
                                      ,shard_prefix='Shard_'
                                      ,separator='\t'
                                      ,site_exploded_queue=None
                                      ,site_sharded_queue=None
                                      ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                                      ,storage_dimension_short_name_physid_lookup=None
                                      ,number_of_storage_elements_per_empower_data_file=1
                                      ,exit_on_failure=True
                                      ,multiple_logical_shards = False
                                      ,logging_queue=None
                                      ):
    '''Take files (*.tsv) and shard them into separate *_XXX.tsv files, which contain only a single storage dimension element
    
    The load process will load "shards" of data, which are standard format bulk/or import load data with only a single storage element. These can be parallel bulk loaded/imported later.
    
    This function reads normal format files, one at a time, and writes to multiple sharded files.
    
    This function can be run in it's own process, but only one worker should exist at any time, because it is in control of *all* of the bulk load shard files.

    This function will create brand new sharded files it needs to, translating the PhysID for the storage dimension into the suffix that Empower tags each data file with..
    
    :param storage_dimension_index: Zero based index of the storage dimension
    :param load_processing_dir: Directory in which to put the sharded files
    :param file_mask: windows style file mask - which files to consider as bulk load files for 
    :param shard_prefix: prefix for start of shard file name
    :param separator: separator in the incoming and outgoing bulk load files - usually this is a tab (i.e. the default)
    :param site_exploded_queue: A PersistentQueue which has messages representing which files have been exploded to bulk insert files.
    :param site_sharded_queue: A PersistentQueue (file only - no actual queue) which will have messages representing which files have been sharded, so that the bulk load process can mark everything as complete in the pickup file
    :param empower_importer_executable: path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
        
    :param storage_dimension_short_name_physid_lookup: (dict) short name to physid lookup - to be used if this function is being used on a file with shortnames, rather than a file with physids    
    :param exit_on_failure:
    :param multiple_logical_shards: The original process creates a single shard and adds to it. The new process creates multiple shards and concatenates them later
    :param logging_queue: multiprocessing.Queue, if we are logging to file, we need a queue created in conjunction with the filelogger process to send logging messages to
    '''
    
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
    
    #log.verbose('msgsink__shard_files_by_storage_dim Received file_mask'+str(file_mask))
    if file_mask==str(file_mask):
        file_masks=[file_mask]
    else:
        #File mask is a list
        file_masks=file_mask    
    
    #Create the Bulk Load Processing Directory if it doesn't exist already
    try:
        os.mkdir(load_processing_dir)
    except FileExistsError:
        pass
    

    #Concatenate the three letter suffixes from both the bulk load files, and all .000 files in SMD
    current_file_suffixes=[]
    
    #We need to maintain a dictionary of the Geography physids to the data files that will hold the data for those physids
    #These broken out files will not be dated 
    physid_to_file_lookup={}
    file_name_to_file_lookup={}
    
    try:

        
        is_first_message=True
        #get files off of the site_exploded_queue
        #and shard them
        while True:
            msg=site_exploded_queue.get()
            if  msg==FAILED:
                raise mpex.UpstreamFailureError('Upstream Queuing Process Failed')
                break
                
            #When DONE (0) stop
            if  msg==DONE:
                log.verbose('Got DONE message on exploded_queue')
                #Try to empty the rest of the queue
                try:
                    while True:
                        msg=site_exploded_queue.get_nowait()
                        log.debug(msg)    
                except qq.Empty:
                    pass
                
                break
                
            else:
            
                if not multiple_logical_shards:
                    #Empty the directory after the first message - otherwise we will empty out files we intended to load during a pickup process
                    if is_first_message:  
                        is_first_message=False
                        #Empty the processing directory
                        for f in os.listdir(load_processing_dir):
                            file_path = os.path.join(load_processing_dir, f)
                            if os.path.isfile(file_path):
                                log.verbose('Deleting file '+str(file_path))
                                os.unlink(file_path)
                                
                #shard file into into dim0 files
                target_file_name=msg
                log.verbose( "Received message from exploded_queue: "+str( target_file_name))
                    
                target_file_name_no_dir=os.path.basename(target_file_name)
                
                #get date from file
                #Break out bulk load file into separate storage dimension entities, look up the storage dimension file name from the physid 
                #File masks may be strings or lists of strings - if the file mask is a string, turn it into a list of strings, so we can process all file masks in the same way


                def process_one_file(target_file_name,target_file_name_no_dir):
                        #processing_file_name=target_file_name
                    
                        #copy the unzipped file into the working directory for the final file set - as they probably will not have been archived yet
                        #load_processing_dir
                        if multiple_logical_shards:
                            #When processing multiple logical shards we have a rename process inherent in the queuing process, so tehre is no need to take a physical copy
                            processing_file_name = target_file_name
                        else:
                            processing_file_name=os.path.join(load_processing_dir,target_file_name_no_dir)
                            shutil.copyfile(target_file_name,processing_file_name)

                        log.verbose( "Breaking out storage dimension in file "+str(processing_file_name))
                        
                        with open(processing_file_name) as original_bulk_load_file:
                        
                            n=0
                            #for each line in the file
                            #see if we already have a file for the physid
                            #if not, create one
                            for n, l in enumerate(original_bulk_load_file):
                                #ignore empty lines
                                if l != '\n':
                                    #Get the storage id - there is no need to translate to an integer
                                    #The storage identifier may be a short name or a physid - if it is a shortname we will translate it to a physid to get the correct file name
                                    storage_dimension_identifier = l.split(separator)[storage_dimension_index]
                                    
                                    try:
                                        target_bulk_load_file=physid_to_file_lookup[storage_dimension_identifier]
                                    except KeyError:
                                        if storage_dimension_short_name_physid_lookup:
                                            
                                            #If a short name to physid lookup dictionary has been supplied, we are dealing with a file of shortnames, and the
                                            #storage dimension column refers to a shortname, and thus must be translated to a physid
                                            storage_dimension_physid=storage_dimension_short_name_physid_lookup[storage_dimension_identifier]
                                        else:
                                            storage_dimension_physid=storage_dimension_identifier
                                            
                                        shard_suffix=physid_to_empower_file_suffix(storage_dimension_physid,number_of_storage_elements_per_empower_data_file)
                                        target_bulk_load_file_name=os.path.join(load_processing_dir, shard_prefix+shard_suffix+'.tsv')
                                        try:
                                            target_bulk_load_file=file_name_to_file_lookup[target_bulk_load_file_name]
                                        except KeyError:
                                            log.verbose('Creating target load file '+str(target_bulk_load_file_name))
                                            target_bulk_load_file=open(target_bulk_load_file_name,'w')
                                            file_name_to_file_lookup[target_bulk_load_file_name]=target_bulk_load_file
                                            
                                        physid_to_file_lookup[storage_dimension_identifier]=target_bulk_load_file
                                        
                
                                    #write the record to the bottom of the file                        
                                    target_bulk_load_file.write(l)
                            
                                    if n % 500000 == 0 and n != 0:
                                        log.verbose('Sharded '+str(n)+' records')
               
                            log.verbose('Sharded '+str(n)+' records')
                            
                        if not multiple_logical_shards:
                            #When processing multiple logical shards we have a rename process inherent in the queuing process, so tehre is no need to take a physical copy
                            #Delete the unzipped file - it is taking up valuable space
                            log.verbose( "Deleting "+str( processing_file_name))
                            os.unlink(processing_file_name)
                
                if multiple_logical_shards:
                    process_one_file(target_file_name,target_file_name_no_dir)

                else:
                    #This could go wrong if the target file name matches more than one file mask, so we break at the end of the if fnmatch, once a filename matches a mask
                    for file_mask in file_masks:
                        log.debug('Trying mask '+file_mask+' on file '+target_file_name_no_dir)
                        if fnmatch.fnmatch(target_file_name_no_dir,file_mask):
                            log.debug('Matched mask '+file_mask+' on file '+target_file_name_no_dir)
                        
                            process_one_file(target_file_name,target_file_name_no_dir)
                            
                            #Once a filename matches a mask we break, we don't need to process the file for every mask it matches, and the file name could match more than one mask, accidentally
                            break
                        else:
                            log.debug('Did not match mask '+file_mask+' on file '+target_file_name_no_dir)    
                        
                    
                    if site_sharded_queue:
                        site_sharded_queue.put(target_file_name)
                
    
        exitcode=None
    except mpex.UpstreamFailureError:
        log.error('Sharding is stopping because Upstream Process Failed')
        if exit_on_failure:
            exitcode=1 
    finally:
    
        if site_sharded_queue and not multiple_logical_shards:
            log.verbose('Closing site_sharded_queue')
            site_sharded_queue.close()
            
        for f in physid_to_file_lookup.values():
            try:
                log.verbose('Closing file '+str(f.name))
                f.close()
            except Exception as e:
                log.error(e)

    if multiple_logical_shards:
        if site_sharded_queue:
            for shard_file in physid_to_file_lookup.values():
                site_sharded_queue.put(shard_file.name)                        
            
    #Record all of the files which have had shards created, so we can track what has been loaded during a pickups event    
    #Do this outside the finally, because we have no idea what may have caused the finally to fail, and we will end up resharding if this has failed
    if site_exploded_queue:
        log.verbose('Disposing site_exploded_queue')
        site_exploded_queue.dispose()
                
    
    if exitcode:
        log.error('File Sharding failed')
        sys.exit(exitcode)
    
    log.verbose('File Sharding is complete')
  

def load_empower_from_shards(empower_site
                             ,empower_user
                             ,empower_pwd
                             ,shard_file_prefix
                             ,empower_data_file_prefix
                             ,number_of_storage_elements_per_empower_data_file=1
                             ,storage_dimension_index=0
                             ,load_method='bulk'
                             ,main_site_output_data_files_dir=None
                             ,load_processing_dir=None
                             ,working_sites=[]
                             ,site_shards_ready_to_bulk_load_queue=None
                             ,do_voodoo=False
                             ,voodoo_bytes=8192
                             ,voodoo_cache_dimension_number=0
                             ,voodoo_cache_elements=[]
                             ,voodoo_key_signature=b'\x44\x04\x01\0\0\0'
                             ,voodoo_cache_instructions_dir=None
                             ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                             ,empower_batch_executable=EMPOWER_BATCH_EXECUTABLE
                             ,empower_calcset_executable=EMPOWER_CALCSET_EXECUTABLE
                             ,logging_queue=None
                             ,safe_load=True
                             ,encrypted_empower_user=None
                             ,encrypted_empower_pwd=None
                             ):  
    ''' Bulk load sharded data into an Empower site, using parallelism.
    
    A "shard" is a single storage dimension element, and the data has already been put into files of single storage elements, ready to be combined with the Empower data files.
    Data is combined in parallel, in multiple separate sites, before being reassembled in to 
    
    * Look for sharded files, and all Empower data files, to see what needs processing
    * Start multiple worker processes which will bulk load single shards in parallel
    * Send the names of the shards we need to load to a queue which the multiple worker processes are listening on
    * Each worker process will bulk load a single storage element, in a separate copy of the site (i.e. as foudn in worker_sites list)
    * Gather the data together into the main Empower site
    
    As a rule of thumb, for quickest loading, use one less worker sites than you have cpus on the machine
        
    :param empower_site: The Empower site being bulk loaded
    :param empower_user: User name for the Empower site
    :param empower_pwd: Password for the Empower site
    :param encrypted_empower_user: Windows encrypted user for the Empower site
    :param encrypted_empower_pwd:  Windows encrypted password for the Empower site
    :param load_method: method of loading Empower - bulk load:'bulk' or import: 'import'. This method depends on whether the file is in bulk load or import format 
    :param shard_file_prefix: The shard files will have been created with a prefix, before the three changing characters. We need to know it to discover the files in the directory
    :param empower_data_file_prefix: Empower data files have a common prefix before the three changing characters. Specify it so that we can find the correct data files
    :param number_of_storage_elements_per_empower_data_file: Number of storage elements found in each Empower Data file
    :param storage_dimension_index: Index of the storage dimension, used in voodoo caching
    :param main_site_output_data_files_dir=Directory which will contain processed data files for the site being bulk loaded This defaults to 'Output Data Files'
    :param load_processing_dir=Directory containing the shards of (bulk) load files
    :param working_sites=a list of .eks or .beks files of the sites that will be used to do the load in parallel
    :param site_shards_ready_to_bulk_load_queue: Persistent Queue to write complete work to
    :param do_voodoo: warm the windows cache with pages containing a given set of modes (if 0 chosen), metrics (if 1 is chosen) and so on, in the order in which the key is held by Empower
    :param voodoo_bytes: number of bytes to read at one time during voodoo caching. This depends on how many bytes berkeley is typically reading at a time.
    :param voodoo_cache_dimension_number: the dimension number to be used for voodoo caching.
    :param voodoo_cache_elements: a list of empower physids of the elements which get warmed in the voodoo_caching process
    :param voodoo_key_signature: a set of bytes which indicates to the voodoo file cacher that the upcoming string of bytes is likely to be an empower key
    :param voodoo_cache_instructions_dir: The output directory in which to put voodoo caching instructions for use by the cache warmer
    :param empower_importer_executable: path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param empower_batch_executable: path to the Empower Batch executable
    :param empower_calcset_executable: path to the Empower Calculation Setter executable
    :param safe_load: copy files from main Data Files rather than moving them - this uses more space but is restartable in the event of a failure (such as running out of disk space or power failure
    '''
    
    #We use the source locations a lot, so give it a short name
    
    log.verbose('Starting to load Empower from shards')
                
    empower_site_dir=os.path.dirname(empower_site)
    empower_site_data_files_dir=os.path.join(empower_site_dir,'Data Files')
    
    if voodoo_cache_instructions_dir==None:
        voodoo_cache_instructions_dir=os.path.join(empower_site_dir,'Cache Warming Instructions')
    
    if main_site_output_data_files_dir==None:
        main_site_output_data_files_dir=os.path.join(empower_site_dir,'Output Data Files')
    
    #make the output directory if it doesn't exist - if it does, then clear out all of the files in it
    try:
        os.mkdir(main_site_output_data_files_dir)
    except FileExistsError:
        for f in os.listdir(main_site_output_data_files_dir):
            file_path = os.path.join(main_site_output_data_files_dir, f)
            if os.path.isfile(file_path):
                log.verbose('Deleting file '+str(file_path))
                os.unlink(file_path)
    
    #Create the last_successful_bulk_load directory in the Output Data Files - we'll populate this with the truly last successful load
    #then overwrite files with the ones we are about to load
    #This way when we complete successfully we will move a consistent set of files back - data files with the true last successful load data
    try:
        os.mkdir(os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load'))
    except FileExistsError:
        for f in os.listdir(os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load')):
            file_path = os.path.join(os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load'), f)
            if os.path.isfile(file_path):
                log.verbose('Deleting file '+str(file_path))
                os.unlink(file_path)
                
    #Create the directory in case we are not doing a delta load and it has been deleted
    try:
        os.mkdir(os.path.join(empower_site_data_files_dir,'last_successful_bulk_load'))
    except FileExistsError:
        pass
    #Copy all sorted.tsv files from Data Files Previous to Output Data Files
    #This means old bulkloads using old versions of this code will be moved across to the directory too
    for f in os.listdir(os.path.join(empower_site_data_files_dir,'last_successful_bulk_load')):
        #log.verbose('Examining file "'+f+'" in "'+data_files_previous_dir+'"')
        if fnmatch.fnmatch(f,'*sorted.tsv'):
            log.verbose('Moving current bulk load file "'+os.path.join(empower_site_data_files_dir,'last_successful_bulk_load',f)+'" to "'+os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load')+'"')
            shutil.copy(os.path.join(empower_site_data_files_dir,'last_successful_bulk_load',f),os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load'))
    
    #At this point any previous version of the loaded bulkload file may be in place - we are about to replace it 
    
    #Move the current bulk load files into history (i.e. Output Data Files)
    #The History bulk load files are used to create correct bulk-load deltas, so must travel with the Data Files
    #History shows the last (full) bulk load state that we set, thus we know that the site only contains these elements in that bulk load space, since we would have 'deleted' any others
    log.verbose('About to move current files into Output Data files/last_successful_bulk_load')
    #Check the directory is in place - if it isn't then we have probably run the load twice - without correctly processing the data
    if os.path.isfile(os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load')):
        
        try:
            os.listdir(os.path.join(empower_site_data_files_dir,'currently_processing_bulk_load'))
        except FileNotFoundError:
            msg='Directory "'+ os.path.join(empower_site_data_files_dir,'currently_processing_bulk_load')+'" was not found. Most likely this is the result of the load_shards process happening before any bulk load delta process has run, for instance by running the bulk load process twice in a row, without creating new data'
            log.error(msg)
            raise mpex.CompletelyLoggedError(msg)
    else:
        try:
            #If there is no last_successful_bulk_load, then create the currently_processing_bulk_load file
            os.makedirs(os.path.join(empower_site_data_files_dir,'currently_processing_bulk_load'))
        except FileExistsError:
            pass
            
    for f in os.listdir(os.path.join(empower_site_data_files_dir,'currently_processing_bulk_load')):
        #Remove the file from the target Output Data Directory if it already exists
        if os.path.isfile(os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load',f)):
            os.remove(os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load',f))
                    
        shutil.move(os.path.join(empower_site_data_files_dir,'currently_processing_bulk_load',f), os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load'))
        log.verbose('Moved file "'+os.path.join(empower_site_data_files_dir,'currently_processing_bulk_load',f)+'" to "'+os.path.join(main_site_output_data_files_dir,'last_successful_bulk_load')+'"')
    
    #At this point, the target Output Data Files directory, should contain bulk load history files matching what has been loaded throughout history - provided this load succeeds
    #The Output files will be shuffled into 'Data Files' at the end of a successful load
         
    bulkloader_threads=[]
    
    #It is easy to mis-specify working sioets as None (rather than []). Handle this gracefully
    if working_sites is None:
        working_sites=[]
        
    if working_sites==[]:
        #if no working sites have been specified, then create some - one less than the number of cpus 
        number_of_workers=multiprocessing.cpu_count()-1         
        for n in range(number_of_workers):
       
            #Copy N sites into the bulk load processing dir
            working_site_directory=os.path.join(load_processing_dir,'Working Site '+str(n))
            
            try:
                os.mkdir(working_site_directory)
            except FileExistsError: 
                #the directory may already exist, that's OK
                pass
                
            try:
                os.mkdir(os.path.join(working_site_directory,'Data Files'))
            except FileExistsError: 
                #the directory may already exist, that's OK
                pass
            
            empower_site_file_name=os.path.basename(empower_site)
            
            working_site=os.path.join(working_site_directory,empower_site_file_name)
            
            log.verbose('Creating Working Site '+str(working_site))
            shutil.copy(empower_site,working_site)
            
            working_sites.append(working_site)
    
    #Create a new Queue to pass work to the worker threads
    #unless we have been passed in a queue by the calling process
    if not site_shards_ready_to_bulk_load_queue:
        #This persistent queue is essentially a normal Multiprocessing Queue, and will not actually be persistent.
        #I've chosen to use the persistent queue in order to keep the calls to task_done and dispose() the same throughout
        dim0_ready_to_bulkload_queue=mpq.PersistentQueue(number_of_workers=len(working_sites))
    else:
        dim0_ready_to_bulkload_queue=site_shards_ready_to_bulk_load_queue
        #We need to know the number of worker threads in order to put the correct number of DONE messages on the Queue
        dim0_ready_to_bulkload_queue.number_of_workers=len(working_sites)
    
    #JAT 2019-11-26 moved this here, because attempting to share working directory as per EM-66661
    #Clear out the working directory
    #Empty the working site data directory
    #Create the worker threads
    for n, working_site in enumerate(working_sites):
    
        working_site_data_dir=os.path.join(os.path.dirname(working_site),'Data Files')
        for f in os.listdir(working_site_data_dir):
            file_path = os.path.join(working_site_data_dir, f)
            if os.path.isfile(file_path):
                log.verbose('Deleting file '+str(file_path))
                os.unlink(file_path)
        
    #Create the worker threads
    for n, working_site in enumerate(working_sites):
    
        log.verbose('Creating Load worker '+str(n)+' on '+str( working_site))
        
        #Create a new worker the thread, telling it where to find the work queue, and which site to use
        loader_process=multiprocessing.Process(target=msgsink__run_single_dim0_empower_load
                                          ,kwargs={'bulkload_queue':dim0_ready_to_bulkload_queue
                                                 ,'empower_main_site':empower_site
                                                 ,'empower_work_site':working_site
                                                 ,'empower_user':empower_user
                                                 ,'empower_pwd':empower_pwd
                                                 ,'encrypted_empower_user':encrypted_empower_user
                                                 ,'encrypted_empower_pwd':encrypted_empower_pwd
                                                 ,'bulk_load_processing_dir':load_processing_dir
                                                 ,'shard_file_prefix':shard_file_prefix
                                                 ,'empower_data_file_prefix':empower_data_file_prefix
                                                 ,'number_of_storage_elements_per_empower_data_file':number_of_storage_elements_per_empower_data_file
                                                 ,'storage_dimension_index':storage_dimension_index
                                                 ,'main_site_output_data_files_dir':main_site_output_data_files_dir
                                                 ,'do_voodoo':do_voodoo
                                                 ,'voodoo_bytes':voodoo_bytes
                                                 ,'voodoo_cache_dimension_number':voodoo_cache_dimension_number
                                                 ,'voodoo_cache_elements':voodoo_cache_elements
                                                 ,'voodoo_key_signature':voodoo_key_signature
                                                 ,'voodoo_cache_instructions_dir':voodoo_cache_instructions_dir
                                                 ,'empower_importer_executable':empower_importer_executable
                                                 ,'load_method':load_method
                                                 ,'logging_queue':logging_queue
                                                 ,'safe_load':safe_load
                                                 }                                                
                                          ,name='Loader '+str(n))
        bulkloader_threads.append(loader_process)
        #kick off load job
        log.verbose('Starting Load worker '+str(n)+' on '+str( working_site))
        loader_process.start()
        log.verbose('Started Load worker '+str(n)+' on '+str( working_site))

        
    #push work to the queue
    try:
        #The total set of data to load is the files currently in the SMD site, plus the xxxxxxxx_???.tsv files which are ready for loading
        #In short, load old + new
        current_file_suffixes=[]
        current_file_size_dict={}
        '''for basename in os.listdir(dirname):
        filename = os.path.join(dirname, basename)
        if os.path.isfile(filename):
            filepaths.append(filename)

        # Re-populate list with filename, size tuples
        for i in xrange(len(filepaths)):
            filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))'''
        
        for f in os.listdir(empower_site_data_files_dir):
            file_name, file_extension = os.path.splitext(f)
            if file_extension=='.000':
                suffix=file_name[len(empower_data_file_prefix):]
                current_file_suffixes.append(suffix)
                #We don't need the size of the Data File, only the size of the Shard file
                current_file_size_dict[suffix]=0
    
        for f in os.listdir(load_processing_dir):
            file_name, file_extension = os.path.splitext(f)
            if file_extension=='.tsv' and fnmatch.fnmatch(file_name, shard_file_prefix+'*'):
                suffix=file_name[len(shard_file_prefix):]
                file_size=os.path.getsize(os.path.join(load_processing_dir,f))
                suffix=file_name[len(shard_file_prefix):]
                current_file_suffixes.append(suffix)
                current_file_size_dict[suffix]=file_size
    
        #Get unique three letter suffixes - by casting to a set and then back to a list - a common python trick
        current_file_suffixes=list(set(current_file_suffixes))
        #Get the filesize of the shard (not the data file) and make a tuple of size and file suffix, so we can sort largest shards first
        current_file_suffixes=[(sfx, current_file_size_dict[sfx]) for sfx in current_file_suffixes]
        #sort the suffixes - by size of shard, so largest shards load first
        current_file_suffixes.sort(key=lambda sfx_sz: sfx_sz[1],reverse=True)
        
        
    
        #now put all of the shards onto the queue - so that the individual worker threads can pick them up in turn
        for shard_suffix,filesize in current_file_suffixes:
            #put each shard on the Queue
            log.verbose('Queuing Bulk Load Shard: '+str(shard_suffix)+' sized: '+str(filesize))
            dim0_ready_to_bulkload_queue.put(shard_suffix)
            log.debug('Queuing Bulk Load Shard: '+str(shard_suffix))
            
        dim0_ready_to_bulkload_queue.close()
        
    except Exception as e:
        try:
            log.error('Exception while bulk loading') 
        except Exception:
            pass
            
        dim0_ready_to_bulkload_queue.fail()
        for bulkloader in bulkloader_threads:
            bulkloader.terminate()
        try:
            #Got to be careful - the pipe has a habit of closing while we are logging
            log.error('Bulk Loader threads terminated') 
        except Exception:
            pass
        raise e
    
    try:    
        #Join the bulkloader threads
        #Count the number of threads left, so that users aren't left hanging on
        n=len(bulkloader_threads)
        for bulkloader in bulkloader_threads:
            log.verbose('Waiting for '+str(n)+' remaining loaders to finish, next pid in line:'+str(bulkloader.pid) ) 
            bulkloader.join()
            log.verbose('{}:{} exitcode = {}'.format(bulkloader.name, bulkloader.pid, bulkloader.exitcode)) 
            n-=1
            
    #If CTRL-C is pressed, terminate the jobs and re-raise CTRL-C
    except KeyboardInterrupt as e:
        dim0_ready_to_bulkload_queue.fail()
        for bulkloader in bulkloader_threads:
            bulkloader.terminate()
        raise e    
        
    for bulkloader in bulkloader_threads:
        #test the return value
        if bulkloader.exitcode!=0:
            msg='Parallel Bulk Loader '+bulkloader.name+' finished with non zero exit code '+str(bulkloader.exitcode)
            log.error(msg)
            
            #If in non-safe mode, copy completed files back into Data Files - if the file is already there we do NOT overwrite it, as the file we are trying to move into place is probably corrupt
            if not safe_load:
                for f in main_site_output_data_files_dir:
                    if not os.path.isfile(os.path.join(empower_site_data_files_dir,f)):
                        try:
                            log.error('Rolling back processed file "'+os.path.join(main_site_output_data_files_dir,f)+'" to "'+os.path.join(empower_site_data_files_dir,f)+'"')
                        except Exception:
                            print('ERROR! Rolling back processed file "'+os.path.join(main_site_output_data_files_dir,f)+'" to "'+os.path.join(empower_site_data_files_dir,f)+'"')
                        shutil.move(os.path.join(main_site_output_data_files_dir,f), empower_site_data_files_dir)
    
            
            raise mpex.CompletelyLoggedError(msg)
    
    #First, before deleting the data, remove the Data Files Previous Folder, then move Data Files to Data Files Previous
    #By shuffling the files within the Output Data Files location, then if we have put those on a different drive for space, the previous files won't be sat with 
    data_files_previous_dir=os.path.join(os.path.dirname(main_site_output_data_files_dir),'Data Files Previous')
    log.verbose('Data Files Previous directory set to "'+data_files_previous_dir+'"')
    #remove Data Files Previous
    try:
        shutil.rmtree(data_files_previous_dir)
        log.verbose('Removed old directory "'+data_files_previous_dir+'"')
    except FileNotFoundError:
        #if there was no 'previous files' directory, that's fine-  we were deleting it anyway
        pass
    

    
    #rename Data Files to Data Files Previous
    try:
        shutil.move(empower_site_data_files_dir, data_files_previous_dir)
    except PermissionError:
        #Sleep before recreating directory so slow operating systems have time to process the rmtree command - seems to happen only on VMs, very intermittently
        time.sleep(10)
        shutil.move(empower_site_data_files_dir, data_files_previous_dir)
    
    log.verbose('Moved directory "'+empower_site_data_files_dir+'" to "'+data_files_previous_dir+'"')

    #finally move main_site_output_data_files_dir to empower_site_data_files_dir
    #Once this is done the site has the new data
    shutil.move(main_site_output_data_files_dir, empower_site_data_files_dir)
    log.verbose('Moved directory "'+main_site_output_data_files_dir+'" to "'+empower_site_data_files_dir+'"')
    
    delete_cache_files_for_site(empower_site)
    
    log.verbose('Bulk Loading Finished')

def load_sql_empower_from_shards(empower_site
                             ,encrypted_empower_user
                             ,encrypted_empower_pwd
                             ,shard_file_prefix
                             ,number_of_workers=1
                             ,load_processing_dir=None
                             ,site_shards_ready_to_bulk_load_queue=None
                             ,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE
                             ,logging_queue=None
                             ,_single_bulk_load_function = msgsink__run_single_sql_empower_bulk_load
                             ):
    ''' Bulk load sharded data into an SQL Empower site, using parallelism.
    
    A "shard" is a single storage dimension element, and the data has already been put into files of single storage elements, ready to be combined with the Empower data files.
    Data is bulk loaded in parallel
    
    * Look for sharded files, and all Empower data files, to see what needs processing
    * Start multiple worker processes which will bulk load single shards in parallel
    * Send the names of the shards we need to load to a queue which the multiple worker processes are listening on
    * Each worker process will bulk load a single storage element, in a separate copy of the site (i.e. as found in worker_sites list)
    * Gather the data together into the main Empower site
    
    As a rule of thumb, for quickest loading, use one less worker sites than you have cpus on the machine
        
    :param empower_site: The Empower site being bulk loaded
    :param encrypted_empower_user: Windows encrypted user for the Empower site
    :param encrypted_empower_pwd:  Windows encrypted password for the Empower site
    :param shard_file_prefix: The shard files will have been created with a prefix, before the three changing characters. We need to know it to discover the files in the directory
    
    :param load_processing_dir=Directory containing the shards of (bulk) load files
    :param working_sites=a list of .eks or .beks files of the sites that will be used to do the load in parallel
    :param site_shards_ready_to_bulk_load_queue: Persistent Queue to write complete work to
    :param empower_importer_executable: path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    '''
    
    #We use the source locations a lot, so give it a short name
    
    log.verbose('Starting to load SQL Empower from shards')
         
    bulkloader_threads=[]
    
    #Create a new Queue to pass work to the worker threads
    #unless we have been passed in a queue by the calling process
    if not site_shards_ready_to_bulk_load_queue:
        #This persistent queue is essentially a normal Multiprocessing Queue, and will not actually be persistent.
        #I've chosen to use the persistent queue in order to keep the calls to task_done and dispose() the same throughout
        dim0_ready_to_bulkload_queue=mpq.PersistentQueue(number_of_workers=number_of_workers)
    else:
        dim0_ready_to_bulkload_queue=site_shards_ready_to_bulk_load_queue
        #We need to know the number of worker threads in order to put the correct number of DONE messages on the Queue
        dim0_ready_to_bulkload_queue.number_of_workers=number_of_workers
       
    #Create the worker threads
    for n in range(number_of_workers):
    
        log.verbose('Creating Load worker '+str(n)+' on '+str( empower_site))
        
        #Create a new worker the thread, telling it where to find the work queue, and which site to use
        loader_process=multiprocessing.Process(target=_single_bulk_load_function
                                          ,kwargs={'bulkload_queue':dim0_ready_to_bulkload_queue
                                                 ,'empower_main_site':empower_site
                                                 #,'empower_work_site':working_site
                                                 ,'encrypted_empower_user':encrypted_empower_user
                                                 ,'encrypted_empower_pwd':encrypted_empower_pwd
                                                 ,'bulk_load_processing_dir':load_processing_dir
                                                 ,'shard_file_prefix':shard_file_prefix
                                                 ,'empower_importer_executable':empower_importer_executable
                                                 ,'logging_queue':logging_queue
                                                 }                                                
                                          ,name='Loader '+str(n))
        bulkloader_threads.append(loader_process)
        #kick off load job
        log.verbose('Starting Load worker '+str(n))
        loader_process.start()
        log.verbose('Started Load worker '+str(n))

        
    #push work to the queue
    try:
        #The total set of data to load is the files currently in the SMD site, plus the xxxxxxxx_???.tsv files which are ready for loading
        #In short, load old + new
        current_file_suffixes=[]
        current_file_size_dict={}
        
    
        for f in os.listdir(load_processing_dir):
            file_name, file_extension = os.path.splitext(f)
            if file_extension=='.tsv' and fnmatch.fnmatch(file_name, shard_file_prefix+'*'):
                suffix=file_name[len(shard_file_prefix):]
                file_size=os.path.getsize(os.path.join(load_processing_dir,f))
                suffix=file_name[len(shard_file_prefix):]
                current_file_suffixes.append(suffix)
                current_file_size_dict[suffix]=file_size
    
        #Get unique three letter suffixes - by casting to a set and then back to a list - a common python trick
        current_file_suffixes=list(set(current_file_suffixes))
        #Get the filesize of the shard (not the data file) and make a tuple of size and file suffix, so we can sort largest shards first
        current_file_suffixes=[(sfx, current_file_size_dict[sfx]) for sfx in current_file_suffixes]
        #sort the suffixes - by size of shard, so largest shards load first
        current_file_suffixes.sort(key=lambda sfx_sz: sfx_sz[1],reverse=True)
        
        
    
        #now put all of the shards onto the queue - so that the individual worker threads can pick them up in turn
        for shard_suffix,filesize in current_file_suffixes:
            #put each shard on the Queue
            log.verbose('Queuing Bulk Load Shard: '+str(shard_suffix)+' sized: '+str(filesize))
            dim0_ready_to_bulkload_queue.put(shard_suffix)
            log.debug('Queuing Bulk Load Shard: '+str(shard_suffix))
            
        dim0_ready_to_bulkload_queue.close()
        
    except Exception as e:
        try:
            log.error('Exception while bulk loading') 
        except Exception:
            pass
            
        dim0_ready_to_bulkload_queue.fail()
        for bulkloader in bulkloader_threads:
            bulkloader.terminate()
        try:
            #Got to be careful - the pipe has a habit of closing while we are logging
            log.error('Bulk Loader threads terminated') 
        except Exception:
            pass
        raise e
    
    try:    
        #Join the bulkloader threads
        #Count the number of threads left, so that users aren't left hanging on
        n=len(bulkloader_threads)
        for bulkloader in bulkloader_threads:
            log.verbose('Waiting for '+str(n)+' remaining loaders to finish, next pid in line:'+str(bulkloader.pid) ) 
            bulkloader.join()
            log.verbose('{}:{} exitcode = {}'.format(bulkloader.name, bulkloader.pid, bulkloader.exitcode)) 
            n-=1
            
    #If CTRL-C is pressed, terminate the jobs and re-raise CTRL-C
    except KeyboardInterrupt as e:
        dim0_ready_to_bulkload_queue.fail()
        for bulkloader in bulkloader_threads:
            bulkloader.terminate()
        raise e    
        
    for bulkloader in bulkloader_threads:
        #test the return value
        if bulkloader.exitcode!=0:
            msg='Parallel Bulk Loader '+bulkloader.name+' finished with non zero exit code '+str(bulkloader.exitcode)
            log.error(msg)
            
            raise mpex.CompletelyLoggedError(msg)

    log.verbose('Bulk Loading Finished')
    
def msgsink__process_empower_import_metrics(metrics_queue, intermediate_file_name,d1_levels,d2_levels,d3_levels,d4_levels,d5_levels,d6_levels,d7_levels,d8_levels,mode_levels,currency_column_name,time_column_name,intermediate_file_separator='\t',logging_queue=None,completed_metric_queue=None,ignore_zero_values = True):
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
    
    while True:
        msg=metrics_queue.get()
        
        if msg==DONE:
            log.verbose('Got DONE message - stopping')
            break
            
        metric_column_name,metric_shortname,output_file_path=msg

        #For nbulk loads we will receive a physid, not a shortname on the queue
        metric_physid=metric_shortname
        
        log.verbose('Processing message '+str(msg))

        try:
        
            process_one_metric_for_empower_import(intermediate_file_name     =intermediate_file_name
                                                 ,output_file_path           =output_file_path
                                                 ,d1_levels                  =d1_levels
                                                 ,d2_levels                  =d2_levels
                                                 ,d3_levels                  =d3_levels
                                                 ,d4_levels                  =d4_levels
                                                 ,d5_levels                  =d5_levels
                                                 ,d6_levels                  =d6_levels
                                                 ,d7_levels                  =d7_levels
                                                 ,d8_levels                  =d8_levels
                                                 ,mode_levels                =mode_levels
                                                 ,metric_column_name         =metric_column_name
                                                 ,metric_shortname           =metric_shortname
                                                 ,metric_physid              =metric_physid
                                                 ,currency_column_name       =currency_column_name
                                                 ,time_column_name           =time_column_name
                                                 ,intermediate_file_separator=intermediate_file_separator
                                                 ,ignore_zero_values         = ignore_zero_values)

            if completed_metric_queue is not None:
                log.verbose('Queuing file for sharding:'+output_file_path)                                             
                completed_metric_queue.put(output_file_path)        
            
        except Exception as e:
            log.error('Error Message '+str(e))
            if completed_metric_queue is not None:
                log.error('Failing sharding queue...')
                completed_metric_queue.fail()
                log.error('Failed  sharding queue')
            raise

        

def cumulate_dataframe_for_empower_import(dataframe, dim1_column_name, dim2_column_name, dim3_column_name, dim4_column_name, dim5_column_name, dim6_column_name, dim7_column_name, dim8_column_name, metric_shortname,mode_column_name, currency_column_name, date_element_column_name,  datapoint_column_name,logging_queue=None):
    
    #TODO - handle the case when the column name is None (because the Empower implementation does not contain that column)
    
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
    
    #Copy the dataframe-only the columns we want
    #.loc[:, means get all rows. (i.e. row [default:default,  the defaults being 'first' and 'last')
    df=pd.DataFrame(dataframe.loc[:,[dim1_column_name
                                    ,dim2_column_name
                                    ,dim3_column_name
                                    ,dim4_column_name
                                    ,dim5_column_name
                                    ,dim6_column_name
                                    ,dim7_column_name
                                    ,dim8_column_name
                                    ,mode_column_name
                                    ,currency_column_name
                                    ,date_element_column_name
                                    ,datapoint_column_name
                                    ]])
    
    #If the Metric shortname is none, then we follow the convention that the shortname is in the metrci column, and the value is 1
    if metric_shortname is None:
        log.debug('Cumulating dynamic metric column ['+ datapoint_column_name+'] with empty shortname' )
        #Rename the columns to make them meaningful in the context of an Empower load
        df.columns=['D1','D2','D3','D4','D5','D6','D7','D8','MODE','CUR','DATE_ELEMENT','Met']

        #Put the Value in after metric (i.e. in 13th position) which gives us 12 using zero based columns indices
        df.insert(12, column='VAL', value=1, allow_duplicates=False)
        
        #Do the cumulation
        df=df.groupby(by=['D1','D2','D3','D4','D5','D6','D7','D8','Met','MODE','CUR','DATE_ELEMENT']).sum().reset_index(drop=False)
        
    else:    
        log.debug('Cumulating metric column ['+ datapoint_column_name+'] with shortname '+ metric_shortname)
        
        if metric_shortname=='-1' or metric_shortname=='-1.0' or metric_shortname==-1:
            #Programming error
            raise SystemError('Cannot cumulate with an unknown metric')
        #Rename the columns to make them meaningful in the context of an Empower load
        df.columns=['D1','D2','D3','D4','D5','D6','D7','D8','MODE','CUR','DATE_ELEMENT','VAL']
   
        #Do the cumulation
        df=df.groupby(by=['D1','D2','D3','D4','D5','D6','D7','D8','MODE','CUR','DATE_ELEMENT']).sum().reset_index(drop=False)
        
        #Put the Metric in after d8_col (i.e. in 9th position) which gives us 8 using zero based columns indices
        df.insert(8, column='Met', value=metric_shortname, allow_duplicates=False)
        
         
        
    #Remove records with -2 in any dimension - these are not-applicable records - where we do not wish to load at that level 
    d1_to_ignore=df['D1']==-2
    d2_to_ignore=df['D2']==-2
    d3_to_ignore=df['D3']==-2
    d4_to_ignore=df['D4']==-2
    d5_to_ignore=df['D5']==-2
    d6_to_ignore=df['D6']==-2
    d7_to_ignore=df['D7']==-2
    d8_to_ignore=df['D8']==-2
    na_value_to_ignore=df['VAL'].isnull()
    #We don't need to store zeroes
    zero_value_to_ignore=df['VAL']==0
    
    record_to_ignore=d1_to_ignore|d2_to_ignore|d3_to_ignore|d4_to_ignore|d5_to_ignore|d6_to_ignore|d7_to_ignore|d8_to_ignore|na_value_to_ignore|zero_value_to_ignore
    
    #remove the records we want to ignore
    df=df[~record_to_ignore]
    
    #Column 13 (index 12) is the Raw transformation element
    df.insert(12, column='Trans', value='Raw', allow_duplicates=False)
    
    #The format must be
    #'D1','D2','D3','D4','D5','D6','D7','D8', 'METRIC','MODE','CUR','DATE_ELEMENT','Trans',  Datapoint
    
    return df

def cumulate_dataframe_for_empower_bulkload(dataframe, dim1_column_name, dim2_column_name, dim3_column_name, dim4_column_name, dim5_column_name, dim6_column_name, dim7_column_name, dim8_column_name, metric_physid, comparison_column_name, currency_column_name, datapoint_column_name, time_constant=None,time_empower_period_number=None, ignore_zero_values = True):
    
    #Not all sites have all 8 dimensions
    #only use the dimensions which have not been flagged None
    in_unit_dim_columns=[]
    out_unit_dim_columns=[]
    for in_column,out_column in [(dim1_column_name,'D1')
                                ,(dim2_column_name,'D2')
                                ,(dim3_column_name,'D3')
                                ,(dim4_column_name,'D4')
                                ,(dim5_column_name,'D5')
                                ,(dim6_column_name,'D6')
                                ,(dim7_column_name,'D7')
                                ,(dim8_column_name,'D8')]:
        if in_column is not None:
            in_unit_dim_columns.append(in_column)
            out_unit_dim_columns.append(out_column)
    
    
    
    #Copy the dataframe-only the columns we want
    #.loc[:, means get all rows. (i.e. row [default:default,  the defaults being 'first' and 'last')
    df=pd.DataFrame(dataframe.loc[:,in_unit_dim_columns+[
                                     comparison_column_name
                                    ,currency_column_name
                                    ,'empower year'
                                    ,'empower period type'
                                    ,'empower period'
                                    ,datapoint_column_name
                                    ]])
    #If the Metric PhysId is none, then we follow the convention that the Physid is in the Metric column, and the value is 1
    if metric_physid is None:
        log.debug('Cumulating dynamic metric column ['+ datapoint_column_name+'] with empty metric_physid' )
        #Rename the columns to make them meaningful in the context of an Empower bulk load
        df.columns=out_unit_dim_columns+['COMP','CUR','YR','DCONST','PER','Met']

        #Put the Value in after metric (i.e. in 15th position) which gives us 14 using zero based columns indices
        df.insert(len(in_unit_dim_columns)+6, column='VAL', value=1, allow_duplicates=False)
        
        #Do the cumulation
        df=df.groupby(by=out_unit_dim_columns+['Met','COMP','CUR','YR','DCONST','PER']).sum().reset_index(drop=False)

        #Ignore Deliberately Empty active metrics
        met_to_ignore=df['Met']==-2
    
    else:    
        log.debug('Cumulating metric column ['+ datapoint_column_name+'] with shortname '+ str(metric_physid))
        
        #Rename the columns to make them meaningful in the context of an Empower bulk load
        df.columns=out_unit_dim_columns+['COMP','CUR','YR','DCONST','PER','VAL']
        
        #Do the cumulation
        df=df.groupby(by=out_unit_dim_columns+['COMP','CUR','YR','DCONST','PER']).sum().reset_index(drop=False)

        #Put the Metric in after d8_col (i.e. in 9th position) which gives us 8 using zero based columns indices
        df.insert(len(in_unit_dim_columns), column='Met', value=metric_physid, allow_duplicates=False)        
    
        #We should never ignore empty metrics if they are non-dynamic
        met_to_ignore=df['Met']!=df['Met']
    
    #Remove records with -2 in any dimension - these are not-applicable records - where we do not wish to load at that level 
    d1_to_ignore=df['D1']==-2
    try:
        d2_to_ignore=df['D2']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d2_to_ignore=d1_to_ignore
    
    try:
        d3_to_ignore=df['D3']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d3_to_ignore=d1_to_ignore
        
    try:
        d4_to_ignore=df['D4']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d4_to_ignore=d1_to_ignore
        
    try:
        d5_to_ignore=df['D5']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d5_to_ignore=d1_to_ignore    
    
    try:
        d6_to_ignore=df['D6']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d6_to_ignore=d1_to_ignore

    try:
        d7_to_ignore=df['D7']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d7_to_ignore=d1_to_ignore
        
    try:
        d8_to_ignore=df['D8']==-2
    except KeyError:
        #There may be no dimension 2 - reuse the first dimension
        d8_to_ignore=d1_to_ignore    
        
    na_value_to_ignore=df['VAL'].isnull()
    
    #We usually don't need to store zeroes
    if ignore_zero_values:
        zero_value_to_ignore=df['VAL']==0
    else:
        #Reuse the first dimension mask 
        zero_value_to_ignore=d1_to_ignore
    
    record_to_ignore=d1_to_ignore|d2_to_ignore|d3_to_ignore|d4_to_ignore|d5_to_ignore|d6_to_ignore|d7_to_ignore|d8_to_ignore|met_to_ignore|na_value_to_ignore|zero_value_to_ignore
    
    #remove the records we want to ignore
    df=df[~record_to_ignore]
    
    
    #The format must be
    #Where the dimensions follow the dimensions as found in Empower, and Transformation is ignored (it will always be 'Raw')
    #D1  D2  D3  D4  D5  D6  D7  D8  Met Comp    Cur YR      DCONST PER  Datapoint
    #1	1	2	5	2	4	2	1	535	831	    1	2015	3 12	1
    
    return df    
    
def process_one_metric_for_empower_import(intermediate_file_name,output_file_path,d1_levels,d2_levels,d3_levels,d4_levels,d5_levels,d6_levels,d7_levels,d8_levels,mode_levels,metric_column_name,metric_shortname,metric_physid,time_column_name,currency_column_name,intermediate_file_separator='\t',logging_queue=None,ignore_zero_values = True):
    
    ''' '''
    
    #If there is an empower date tuple, we are doing a bulk load, and we don't need a time column
    if time_column_name is not None:
        all_dimension_columns=d1_levels+d2_levels+d3_levels+d4_levels+d5_levels+d6_levels+d7_levels+d8_levels+mode_levels+[time_column_name,currency_column_name]
        do_bulk_load_cumulation=False
        log.verbose('Performing standard cumulation on Intermediate File '+intermediate_file_name)
    else:
        do_bulk_load_cumulation=True
        log.verbose('Performing bulk load cumulation on Intermediate File '+intermediate_file_name)
        all_dimension_columns=d1_levels+d2_levels+d3_levels+d4_levels+d5_levels+d6_levels+d7_levels+d8_levels+mode_levels+[currency_column_name]+['empower year','empower period','empower period type']
        
        
    all_columns=all_dimension_columns+[metric_column_name]
    
    #Read in the intermediate file
    log.verbose( 'Reading Intermediate File '+intermediate_file_name)
    try:
        df=pd.read_csv(intermediate_file_name,encoding='utf-8',sep=intermediate_file_separator, usecols=all_columns,index_col=False)
        msg= 'Read Intermediate File '+intermediate_file_name+' with usecols='+str(all_columns)
        log.debug(msg)
        
    except ValueError:
        msg= 'Could not read Intermediate File '+intermediate_file_name+' with usecols='+str(all_columns)
        log.error(msg)
        raise mpex.CompletelyLoggedError(msg)

    if do_bulk_load_cumulation:
        log.debug('Converting dimension columns to integers')
        for col in all_dimension_columns:
            df[col]=df[col].astype('int')        
    
    
    #Cast to categoricals to make it go faster
    #if metric_shortname is None:
    #    df[metric_column_name]=df[metric_column_name].astype('category')
    
    #for dimension_column in all_dimension_columns:
    #    df[dimension_column]=df[dimension_column].astype('category')
        
    #Hold all the cumulated DataFrames, ready for concatenation and writing to file.
    #We could write out a file for each level, and then load these individually, but we'll end up spending forever trying to get file desciptors from the OS
    #Instead we cumulate in Memory
    all_dfs=[]

    #Empty dimensions list can happen when the dimension does not exist in the Empower implementation
    #Put None in to make the itertools work, and then we can filter out the None levels later
    #We can't simply append the None, because the list, being mutable will affect the reading of the file later
    d1_padded=[]
    d2_padded=[]
    d3_padded=[]
    d4_padded=[]
    d5_padded=[]
    d6_padded=[]
    d7_padded=[]
    d8_padded=[]
    for dim_list,padded_list in [(d1_levels,d1_padded)
                                ,(d2_levels,d2_padded)
                                ,(d3_levels,d3_padded)
                                ,(d4_levels,d4_padded)
                                ,(d5_levels,d5_padded)
                                ,(d6_levels,d6_padded)
                                ,(d7_levels,d7_padded)
                                ,(d8_levels,d8_padded)
                                ]:
        #Use the original list if it is not empty, otherwise use a list with None         
        #Note - this code relies heavily on the mutability of the list
        if dim_list!=[]:
            padded_list+=dim_list
        else:
            padded_list.append(None)
    
    log.debug('Creating itertools.product for lists of columns ')
    log.debug('d1   '+str(d1_padded))
    log.debug('d2   '+str(d2_padded))
    log.debug('d3   '+str(d3_padded))
    log.debug('d4   '+str(d4_padded))
    log.debug('d5   '+str(d5_padded))
    log.debug('d6   '+str(d6_padded))
    log.debug('d7   '+str(d7_padded))
    log.debug('d8   '+str(d8_padded))
    log.debug('mode '+str(mode_levels))
    
    #itertools.product() will give us all of the combinations of the different hierarchy levels
    #We've added on a padding list, with [None] where the Empower site does not contain that particular dimension
    for d1_col,d2_col,d3_col,d4_col,d5_col,d6_col,d7_col,d8_col,mode_column_name in itertools.product(d1_padded
                                                                                                     ,d2_padded
                                                                                                     ,d3_padded
                                                                                                     ,d4_padded
                                                                                                     ,d5_padded
                                                                                                     ,d6_padded
                                                                                                     ,d7_padded
                                                                                                     ,d8_padded
                                                                                                     ,mode_levels):
        
        if do_bulk_load_cumulation:
            df_cumulated=cumulate_dataframe_for_empower_bulkload(dataframe =df
                                            ,dim1_column_name= d1_col 
                                            ,dim2_column_name= d2_col 
                                            ,dim3_column_name= d3_col 
                                            ,dim4_column_name= d4_col 
                                            ,dim5_column_name= d5_col 
                                            ,dim6_column_name= d6_col 
                                            ,dim7_column_name= d7_col 
                                            ,dim8_column_name= d8_col 
                                            ,metric_physid=metric_physid
                                            ,comparison_column_name=mode_column_name
                                            ,currency_column_name=currency_column_name
                                            ,datapoint_column_name=metric_column_name
                                            ,time_constant=None
                                            ,time_empower_period_number=None
                                            ,ignore_zero_values = ignore_zero_values
                                            )
        else:
            df_cumulated=cumulate_dataframe_for_empower_import(dataframe =df
                                             ,dim1_column_name= d1_col 
                                             ,dim2_column_name= d2_col 
                                             ,dim3_column_name= d3_col 
                                             ,dim4_column_name= d4_col 
                                             ,dim5_column_name= d5_col 
                                             ,dim6_column_name= d6_col 
                                             ,dim7_column_name= d7_col 
                                             ,dim8_column_name= d8_col 
                                             ,metric_shortname= metric_shortname
                                             ,mode_column_name=mode_column_name
                                             ,currency_column_name=currency_column_name
                                             ,date_element_column_name=time_column_name
                                             ,datapoint_column_name=metric_column_name
                                            )        
        
        all_dfs.append(df_cumulated)
        
    df=pd.concat(all_dfs)
    
    #print(r'Started  writing file '+output_file_path+' for '+metric_column_name)
    log.verbose( r'Started  writing file '+output_file_path+' for '+metric_column_name)
    df.to_csv(output_file_path,sep='\t', header=False, index=False)
    log.verbose( r'Finished writing file '+output_file_path+' for '+metric_column_name)
    #print(r'Finished writing file '+output_file_path+' for '+metric_column_name)
    
    df = None
    gc.collect()
    
def create_exploded_bulkload_files(input_file_path = None
                                  ,intermediate_file_name = None
                                  ,target_file_name = None
                                  ,lookup_metric_shortname_from_column=None
                                  ,lookup_metric_physid_from_column=None
                                  ,d1_levels=[]
                                  ,d2_levels=[]
                                  ,d3_levels=[]
                                  ,d4_levels=[]
                                  ,d5_levels=[]
                                  ,d6_levels=[]
                                  ,d7_levels=[]
                                  ,d8_levels=[]
                                  ,mode_levels=[]
                                  ,currency_column_name=None
                                  ,empower_date_tuple=None
                                  ,exported_metric_physid_df=None
                                  ,metric_columns=None
                                  ,dynamic_metric_columns=None
                                  ,identifier_columns=[]
                                  ,file_separator='\t'
                                  ,logging_queue=None
                                  ,dataframe=None
                                  ,completed_metric_queue=None
                                  ,ignore_zero_values         = True):
    '''Create exploded files for bulk or non-bulk Empower import, using parallel processing
    
    :param empower_date_tuple: date tuple for bulk loads only
    :param time_column_name:   column with time element short name for standard loads only (i.e. non bulk)
    :param lookup_metric_shortname_from_column: A dictionary of column name:shortname pairs. The column named will contain a value for the metric with the shortname
    :param storage_physid_lookup_df: a dataframe containing columns ['ID','Short Name'] for the Storage dimension, so that we can shard files for parallel loading. We do not need this if the Storage dimension column(s) already contains Physids
    :param ignore_zero_values: Do not load zero values into Empower - this is usually a timesaver, because many Empower implementations will display N/As as zero anyway
    '''
    _create_exploded_files(input_file_path=input_file_path
                         ,intermediate_file_name=intermediate_file_name
                         ,target_file_name=target_file_name
                         ,lookup_metric_shortname_from_column=lookup_metric_shortname_from_column
                         ,lookup_metric_physid_from_column=lookup_metric_physid_from_column
                         ,d1_levels=d1_levels
                         ,d2_levels=d2_levels
                         ,d3_levels=d3_levels
                         ,d4_levels=d4_levels
                         ,d5_levels=d5_levels
                         ,d6_levels=d6_levels
                         ,d7_levels=d7_levels
                         ,d8_levels=d8_levels
                         ,mode_levels=mode_levels
                         ,currency_column_name=currency_column_name
                         ,time_column_name=None
                         ,empower_date_tuple=empower_date_tuple
                         ,exported_metric_physid_df=exported_metric_physid_df
                         ,metric_columns=metric_columns
                         ,dynamic_metric_columns=dynamic_metric_columns
                         ,identifier_columns=identifier_columns
                         ,file_separator=file_separator
                         ,storage_physid_lookup_df=None
                         ,logging_queue=logging_queue
                         ,dataframe=dataframe
                         ,completed_metric_queue = completed_metric_queue
                         ,ignore_zero_values         = ignore_zero_values)    
    
def create_exploded_shortname_files(input_file_path
                         ,intermediate_file_name
                         ,target_file_name
                         ,lookup_metric_shortname_from_column=None
                         ,lookup_metric_physid_from_column=None
                         ,d1_levels=[]
                         ,d2_levels=[]
                         ,d3_levels=[]
                         ,d4_levels=[]
                         ,d5_levels=[]
                         ,d6_levels=[]
                         ,d7_levels=[]
                         ,d8_levels=[]
                         ,mode_levels=[]
                         ,currency_column_name=None
                         ,time_column_name=None
                         ,exported_metric_physid_df=None
                         ,metric_columns=None
                         ,dynamic_metric_columns=None
                         ,identifier_columns=[]
                         ,file_separator='\t'
                         ,storage_physid_lookup_df=None
                         ,logging_queue=None):
    '''Create exploded files for non-bulk Empower import, using parallel processing
    
    :param empower_date_tuple: date tuple for bulk loads only
    :param time_column_name:   column with time element short name for standard loads only (i.e. non bulk)
    :param lookup_metric_shortname_from_column: A dictionary of column name:shortname pairs. The column named will contain a value for the metric with the shortname
    :param storage_physid_lookup_df: a dataframe containing columns ['ID','Short Name'] for the Storage dimension, so that we can shard files for parallel loading. We do not need this if the Storage dimension column(s) already contains Physids
    
    '''
    _create_exploded_files(input_file_path=input_file_path
                         ,intermediate_file_name=intermediate_file_name
                         ,target_file_name=target_file_name
                         ,lookup_metric_shortname_from_column=lookup_metric_shortname_from_column
                         ,lookup_metric_physid_from_column=lookup_metric_physid_from_column
                         ,d1_levels=d1_levels
                         ,d2_levels=d2_levels
                         ,d3_levels=d3_levels
                         ,d4_levels=d4_levels
                         ,d5_levels=d5_levels
                         ,d6_levels=d6_levels
                         ,d7_levels=d7_levels
                         ,d8_levels=d8_levels
                         ,mode_levels=mode_levels
                         ,currency_column_name=currency_column_name
                         ,time_column_name=time_column_name
                         ,empower_date_tuple=None
                         ,exported_metric_physid_df=exported_metric_physid_df
                         ,metric_columns=metric_columns
                         ,dynamic_metric_columns=dynamic_metric_columns
                         ,identifier_columns=identifier_columns
                         ,file_separator=file_separator
                         ,storage_physid_lookup_df=storage_physid_lookup_df)
 
def _create_exploded_files(input_file_path
                         ,intermediate_file_name
                         ,target_file_name
                         ,lookup_metric_shortname_from_column=None
                         ,lookup_metric_physid_from_column=None
                         ,d1_levels=[]
                         ,d2_levels=[]
                         ,d3_levels=[]
                         ,d4_levels=[]
                         ,d5_levels=[]
                         ,d6_levels=[]
                         ,d7_levels=[]
                         ,d8_levels=[]
                         ,mode_levels=[]
                         ,currency_column_name=None
                         ,time_column_name=None
                         ,empower_date_tuple=None
                         ,exported_metric_physid_df=None
                         ,metric_columns=None
                         ,dynamic_metric_columns=None
                         ,identifier_columns=[]
                         ,file_separator='\t'
                         ,storage_physid_lookup_df=None
                         ,logging_queue=None
                         ,dataframe=None
                         ,completed_metric_queue = None
                         ,ignore_zero_values = True
                         ):
    '''Create exploded files for bulk or non-bulk Empower import, using parallel processing
    
    :param empower_date_tuple: date tuple for bulk loads only
    :param time_column_name:   column with time element short name for standard loads only (i.e. non bulk)
    :param lookup_metric_shortname_from_column: A dictionary of column name:shortname pairs. The column named will contain a value for the metric with the shortname
    :param lookup_metric_physid_from_column:
    :param storage_physid_lookup_df: a dataframe containing columns ['ID','Short Name'] for the Storage dimension, so that we can shard files for parallel loading. We do not need this if the Storage dimension column(s) already contains Physids
    :param logging_queue: multiprocessing.Queue, if we are logging to file, we need a queue created in conjunction with the filelogger process to send logging messages to
    
    '''    
    if empower_date_tuple is not None and time_column_name is not None:
        raise ValueError('Either call this function with a time column (For a standard load) or with ane empower date tuple (for a bulk load)')
    
    log=logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
    
    if lookup_metric_shortname_from_column is None:
        lookup_metric_shortname_from_column = {}
    
    if lookup_metric_physid_from_column is None:
        lookup_metric_physid_from_column = {}
    
    if lookup_metric_shortname_from_column!={} and lookup_metric_physid_from_column!={}:
        raise ValueError('Either lookup_metric_shortname_from_column or lookup_metric_physid_from_column should contain a dictionary not both')
    
    
    #Default metric columns to the keys of the metrics lookup
    if metric_columns is None:
        if lookup_metric_shortname_from_column!={}:
            metric_columns=list(set([col for col in lookup_metric_shortname_from_column.keys()]))
        else :
            metric_columns=list(set([col for col in lookup_metric_physid_from_column.keys()]))
    
    #Default the dynamic metric columns to the keys of the metrics lookup which have no shortname (we assume that the shortname is in the dynamic metric column, and that the datapoint is a 1)
    if dynamic_metric_columns is None:
        dynamic_metric_columns=[]
        for k, v in lookup_metric_shortname_from_column.items():
            if v is None:
                dynamic_metric_columns.append(k)
        for k, v in lookup_metric_physid_from_column.items():
            if v is None:
                dynamic_metric_columns.append(k)
    
    
    
    if time_column_name is not None:
        all_dimension_columns=d1_levels+d2_levels+d3_levels+d4_levels+d5_levels+d6_levels+d7_levels+d8_levels+mode_levels+[time_column_name,currency_column_name]
    else:
        all_dimension_columns=d1_levels+d2_levels+d3_levels+d4_levels+d5_levels+d6_levels+d7_levels+d8_levels+mode_levels+[currency_column_name]+['empower year','empower period','empower period type']
    
        
    all_columns=all_dimension_columns+metric_columns+dynamic_metric_columns
    
    
    columns_to_read=identifier_columns+all_columns
    log.verbose( 'Using Columns '+str(columns_to_read))
    for col in identifier_columns+all_columns:
        if col != str(col):
            log.error('Columns name "'+str(col)+'" is not a string, A column was not a string in columns: {}'.format(columns_to_read))
            log.error('Identifier Columns: {}'.format(identifier_columns))
            log.error('Dimension Columns: {}'.format(all_dimension_columns))
            log.error('Metric Columns: {}'.format(metric_columns))
            log.error('Dynamic Metric Columns: {}'.format(dynamic_metric_columns))
            
    column_counts={}
    for col in columns_to_read:
        col=col.upper()
            
        try:
            column_counts[col]+=1
        except KeyError:
            column_counts[col]=1

    #Log each individual issue before raising any errors
    do_raise_error=False
    for col, count in column_counts.items():
        if count > 1:
            log.error('Column "'+col+" appears "+ str(count) +" times in columns definitions. It should only appear once")
            do_raise_error=True
    
    if do_raise_error:
        raise mpex.CompletelyLoggedError('Column(s) appear multiple times in columns definitions. Each should only appear once')
    
    #Use the dataframe if one has been apssed in - otherwise read it in from file
    if dataframe is not None:
        log.verbose( 'Using passed in DataFrame with columns to read:'+str([c for c in columns_to_read]))
        df = dataframe[columns_to_read].copy()
        #if df.columns != columns_to_read:
        #    for col in identifier_columns+all_columns:
        #        if col not in df.columns:
        #            log.error('Column: '+str(col)+ 'missing from dataframe')
        #            raise mpex.CompletelyLoggedError()   
    
        log.debug('Read Intermediate Columns: '+str(df.columns))
        
    else:
        log.verbose( 'Reading Source File '+input_file_path)
        log.verbose( 'Using file separator '+repr(file_separator))
    
        try:    
            df=pd.read_csv(input_file_path,sep=file_separator,encoding='utf-8',usecols=columns_to_read)
                
        except ValueError as e:
            #One of the columns is incorrect - see which one
            for col in identifier_columns+all_columns:
                log.error('Diagnosing missing columns: '+str(col))
                pd.read_csv(input_file_path,sep=file_separator,encoding='utf-8',usecols=[col])
                log.error('Column: '+str(col)+ ' read correctly')
            log.error('If all columns look correct - DOUBLE CHECK YOUR FILE SEPARATOR. In your code it is '+repr(file_separator))
            raise mpex.CompletelyLoggedError(str(e))

        log.verbose( 'Read    Source File '+input_file_path)
    
    if time_column_name is None:
        do_bulk_load_cumulation=True
        log.debug('Converting dimension columns to integers')
        for col in all_dimension_columns:
            try:
                df[col]=df[col].astype('int')
            except ValueError as e:
                log.error('Column ['+str(col)+'] could not be converted to an integer')
                #Loop through the values in the column, attempting to convert them to integers, and then report on the first value that did not convert
                for index,value in df[col].iteritems():
                    try:
                        int(value)
                    except ValueError:
                        log.error('Index '+str(index)+' in Column '+str(col)+' had value '+str(value))
                        print(df.loc[index])
                        if dataframe is not None:
                            print('Failed record')
                            print()
                            print(dataframe.loc[index])
                        break
                    
                raise mpex.CompletelyLoggedError(e)
    else:
        do_bulk_load_cumulation=False
            
    df=df.dropna(how='all')
    
    log.debug( 'Intermediate Columns: '+str(df.columns))
    
    #Fill nulls in the identifiers to make it easier to distinguish nulls in the data
    df[identifier_columns]=df[identifier_columns].fillna('-')
    
    #Replace -1 in the data with NaN otherwise we will miss the data flagged as bad
    for col in all_dimension_columns:
        df.loc[df[col]==-1,col]=np.NaN
    
    #Do checks for nulls in the dimensions - write them out to file and raise an error
    df_bad= df[pd.isnull(df[all_dimension_columns]).any(axis=1)]
    
    #If there is bad stuff, write just the bad stuff to csv and raise an error
    if not df_bad.dropna(how='all').empty:
        log.error(df_bad.info())
        df_bad.to_csv(input_file_path+'.bad.csv',index=False)
        msg='Could not load empower when NULL values for Empower Short Names found in file '+input_file_path+'. Find problem records in file: '+input_file_path+'.bad.csv'
        log.error(msg)
        raise mpex.CompletelyLoggedError(msg)
        
    #log.verbose( 'Intermediate Columns @2753: '+str(df.columns))
    
    #Once we've done the checks we can group the data and save the file 
    #We don't need the identifier columns any more - we wanted them to help us identify issues written to the '.bad' file
    for column in identifier_columns:
        del df[column]

    #log.verbose( 'Intermediate Columns @3051: '+str(df.columns))
        
    #Data which rolls up to itself over multiple levels needs the most granular level removed (set to -2)
    #Otherwise the total at the higher level might be overwritten by one at a lower level - after all, we only need to insert each element once
    #Note the dimensions must be ordered from most granular to least granular
    for dimension_level_list in [d1_levels,d2_levels,d3_levels,d4_levels,d5_levels,d6_levels,d7_levels,d8_levels,mode_levels]:
        for i in range(len(dimension_level_list)):
            higher_level_dim_index=len(dimension_level_list)-i-1
            lower_level_dim_index=len(dimension_level_list)-i-2
            
            #When the lower level index is -1, python allows the index to wrap around (to get the last element of the list).
            #We don't want to do this so just jump to the next index
            if lower_level_dim_index<0:
                continue
                
            log.verbose('Consolidating '+ str(dimension_level_list[lower_level_dim_index])+' into '+str(dimension_level_list[higher_level_dim_index])+' '+str(len(df.loc[(df[dimension_level_list[higher_level_dim_index]]==df[dimension_level_list[lower_level_dim_index]]) & (df[dimension_level_list[higher_level_dim_index]] != -2)]))+ ' items.')
            #get all of the higher level dimensions that are set to the same value as the lower level dimension, and set the lower level dimension to -2 (unneeded)
            #This expression will translate to somthing like df.loc[df['All']==df['Atomic'],'Atomic']=-2
            #i.e. set the value in df['Atomic'] to -2 if the value in df'[Atomic'] is equal to the value in df['All']
            df.loc[df[dimension_level_list[higher_level_dim_index]]==df[dimension_level_list[lower_level_dim_index]],dimension_level_list[lower_level_dim_index]]=-2

    #log.verbose( 'Intermediate Columns @2781: '+str(df.columns))
        
    #Group the data, summing all of the metrics columns 
    #This is the first level of cumulation, and will reduce the work done in the parallel cumulation stages
    #Since dynamic Metric columns must have the metrics preserved, include these in the group by
    groupby_columns=all_dimension_columns+dynamic_metric_columns
    log.verbose('Group by columns for intermediate file are '+str(groupby_columns))
    
    log.verbose('Converting dimension columns to integers')
    
    #log.verbose( 'Intermediate Columns @3082: '+str(df.columns))
    
    #Any NaNs in the data will prevent the group bys working
    for column in groupby_columns:
        if do_bulk_load_cumulation:
            df[column]=df[column].astype('int')
        
        df[column]=df[column].fillna(-1)
    
    for column in df.columns:
        if column in groupby_columns:
            pass
        else:
            if do_bulk_load_cumulation:
                #It looks like this is causing serious rounding errors on some floats
            
                #try:
                #    df[column]=df[column].astype('int')        
                #except (TypeError,ValueError):
                df[column]=df[column].astype('float')        
    
    #log.verbose( 'Intermediate Columns @2807: '+str(df.columns))
    
    log.verbose( 'Start  Aggregating')
    original_count=len(df.index)
    df=df.groupby(by=groupby_columns, axis=0).sum().reset_index(drop=False)
    final_count=len(df.index)
    log.verbose( 'Finish Aggregating '+str(original_count)+' records into '+str(final_count)+' records')
    
    #log.verbose( 'Intermediate Columns @2815: '+str(df.columns))
    
    
    log.verbose( 'Writing Intermediate File '+intermediate_file_name)
    log.debug( 'Columns: '+str(df.columns))
    df.to_csv(intermediate_file_name,sep='\t', index=False)
    log.verbose( 'Written Intermediate File '+intermediate_file_name)
    
    #Remove the DataFrame, to help the Garbage Collector
    df=None
    gc.collect()
    
    #Create simultaneous processes for each metric
    #Explode and Cumulate for each
    
    log.verbose( 'Starting to Explode and Cumulate')

    #Keep a list of all of the running jobs - to make it easier to kill them
    jobs = []

    metrics_queue=multiprocessing.Queue()
    
    number_of_jobs=multiprocessing.cpu_count()-1 
    
    for n in range(number_of_jobs):
      
        j = multiprocessing.Process(target=msgsink__process_empower_import_metrics
                                   ,kwargs=({'metrics_queue'                : metrics_queue
                                            ,'intermediate_file_name'       : intermediate_file_name
                                            ,'d1_levels'                    : d1_levels
                                            ,'d2_levels'                    : d2_levels
                                            ,'d3_levels'                    : d3_levels
                                            ,'d4_levels'                    : d4_levels
                                            ,'d5_levels'                    : d5_levels
                                            ,'d6_levels'                    : d6_levels
                                            ,'d7_levels'                    : d7_levels
                                            ,'d8_levels'                    : d8_levels
                                            ,'mode_levels'                  : mode_levels
                                            ,'currency_column_name'         : currency_column_name
                                            ,'time_column_name'             : time_column_name
                                            ,'intermediate_file_separator'  : '\t' #tab is set above, and is not the same as the original file_separator parameter which was passed in
                                            ,'logging_queue'                : logging_queue
                                            ,'completed_metric_queue'       : completed_metric_queue
                                            ,'ignore_zero_values'           : ignore_zero_values
                                            })
                                   ,name='Exploder '+str(n))
                        
        jobs.append(j)
        j.start()
        log.verbose('Started job '+j.name)    
    
    #We will be appending the output files, when we have finished all of the jobs
    output_file_paths=[]
    
    try:
        #If there is no shortname (because the shortname should be read from the data in the column rather than looked up from the Column Name) use an incrementing integer to keep file names unique
        shortname_replacement_int=0
        
        for metric_column_name in metric_columns:
            
            if lookup_metric_shortname_from_column!={}:
                #Lookup the empower short name
                metric_shortname=lookup_metric_shortname_from_column[metric_column_name]
                original_metric_shortname=metric_shortname
                #Start with None for physid - it will remain None if we are not bulk loading
                metric_physid=None
            else:
                #Lookup the empower physical id
                metric_shortname=None
                original_metric_shortname=None
                metric_physid=lookup_metric_physid_from_column[metric_column_name]
            

                
            #metric_shortname will be None for Dynamic columns - they should also have the PhysID in them already
            if exported_metric_physid_df is not None and metric_shortname is not None and metric_physid is None:
                try:
                    metric_physid=exported_metric_physid_df.loc[exported_metric_physid_df["Short Name"]==metric_shortname,"ID"].iloc[0]

                except IndexError as e:
                    log.error('Error trying to retrieve Empower physical ID from original columns name:'+metric_column_name+' shortname:'+metric_shortname)
                    log.error(exported_metric_physid_df.loc[exported_metric_physid_df["Short Name"]==metric_shortname,"ID"])
                    log.error(exported_metric_physid_df[["Short Name","ID"]].tail(20))
                    
                    raise mpex.CompletelyLoggedError(e)
       
            #Split off the extension of the file name, so that we can name the new output file correctly
            intermediate_file_no_extension,extension=os.path.splitext(intermediate_file_name)
            
            if metric_shortname is None:
                if metric_physid is None:
                    output_file_path=intermediate_file_no_extension+'_Dynamic'+str(shortname_replacement_int)+'.tsv'
                    shortname_replacement_int+=1
                else:
                    output_file_path=intermediate_file_no_extension+'_Physid'+str(metric_physid)+'.tsv'
                    
            else:
                try:
                    #Rather than just cast to a string, treat integers (physids) differently - that way if we get something truly weird (A tuple for instance, we can handle it)
                    if type(metric_shortname) in [int, float, np.int64]:
                        output_file_path=intermediate_file_no_extension+'_'+str(int(metric_shortname))+'.tsv'
                    else:
                        output_file_path=intermediate_file_no_extension+'_'+metric_shortname+'.tsv'
            
                except TypeError:
                    msg ='Metric Shortname/Physid of type '+str(type(metric_shortname))+' could not be used to create an intermediate file name:'+str(metric_shortname)
                    log.error(msg)
                    raise mpex.CompletelyLoggedError(msg)

            if metric_physid is None and (metric_shortname==-1 or metric_shortname=="-1"  or metric_shortname=="-1.0"):
                #This should never happen - it is a coding error of some sort in the lookups
                #So don't log it and call and already logged exception
                raise SystemError('The Metric shortname has looked up as -1 from shortcode: '+str(original_metric_shortname)+', column name:'+str(metric_column_name))
                    
            if metric_physid is not None:
                msg=(metric_column_name,metric_physid,output_file_path)
            else:
                msg=(metric_column_name,metric_shortname,output_file_path)
            metrics_queue.put(msg)
            log.verbose('Queued metric:'+str(msg))    
            output_file_paths.append(output_file_path)
    finally:
        for n in range(number_of_jobs):
            metrics_queue.put(DONE) 
        
    temp_file_name=target_file_name+'.temp'
            
    #Join all of the jobs
    #this means wait for each job to finish...
    for j in jobs:
        j.join()
        
        if j.exitcode != 0:
            log.error('{}.exitcode = {}'.format(j.name, j.exitcode))  
            log.error('Parallel Job '+j.name+' failed with exit code '+str(j.exitcode))
            
            try:
                if not completed_metric_queue is None:
                    completed_metric_queue.close()
            except Exception:
                pass
                
            raise mpex.CompletelyLoggedError('Parallel Job '+j.name+' failed with exit code '+str(j.exitcode)) 
        else:
            log.verbose('{}.exitcode = {}'.format(j.name, j.exitcode))   
    
    #If we are not queuing completed metrics, save to 1 big file
    if completed_metric_queue is None:
        #Create one big file to concatenate into - this will bulk load a lot quicker than each small file
        with open(temp_file_name,'wb') as wfd:
            
            for output_file_path in output_file_paths:
                log.verbose('Concatenating file '+output_file_path)
                    
                #Concatenate the smaller file into the big output file
                with open(output_file_path,'rb') as fd:
                    shutil.copyfileobj(fd, wfd, 1024*1024*8)
                    #8MB per writing chunk to avoid reading big file into memory.
                
                #Now remove the output file
                os.remove(output_file_path)

        log.verbose('Copying temp file to target:'+str(target_file_name))
        return_value = subprocess.run(r'COPY /B'+' "'+temp_file_name+'" "'+target_file_name+'" ',shell=True,check=True , stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
        os.remove(temp_file_name)
    
    else:
        completed_metric_queue.close()
    
    log.verbose( 'Finished Exploding and Cumulating')    

def create_na_bulk_load_file(source_bulk_load_ready_file, target_bulk_load_ready_file ,number_of_unit_dimensions=8): 
    '''Read a bulk load file, and generate a differently named bulk laod files with the same tuples - only with N/A values
    
    The purpose of this function is to allow us to 'un bulk load' data, reversing out previously bulk loaded data, by bulk loading not-applicable values over the original data
    
    :param source_bulk_load_ready_file: Name of a valid bulk load ready file, with data in it. 
    :param target_bulk_load_ready_file: Name of the bulk load ready file we want to create.
    :param number_of_unit_dimensions: Number of unit dimensions used in the site - the bulk load file needs to match the site specification
    
    '''
    
    newline_position_in_split_line=6+number_of_unit_dimensions
    
    #Read file
    with open(source_bulk_load_ready_file,'r') as src:
        with open(target_bulk_load_ready_file,'w') as tgt:
        
            for line in src:
                #split by tab into
                #D1  D2  D3  D4  D5  D6  D7  D8  Met Comp    Cur YR      DCONST PER  Datapoint
                split_line=line.split('\t')
                
                #Replace datum with nothing, by replacing the final datum+newline with just the newline
                split_line[newline_position_in_split_line]='\n'
            
                #Join with tabs and write to output
                tgt.write('\t'.join(split_line))


def create_overwrite_bulk_load_file(old_source_bulk_load_ready_file_sorted
                                   ,new_source_bulk_load_ready_file_sorted
                                   ,target_bulk_load_ready_file
                                   ,target_bulk_load_reversion_file=os.devnull
                                   ,create_true_delta=False
                                   ,number_of_unit_dimensions=8
                                   ,ignore_missing_old=False): 
    '''Read an old and a new bulk load file, both of which have been sorted, and generate a differently named target bulk load files which will reverse out the data in the old and apply the data in the new bulk load file
    
    Note that by default the data is not a true delta - i.e. the diffrence between the two files, but rather a new bulk load file which overwrite old data with new data if it exists
    and puts NA in for data that does not exist in the new file. the delta can safely be loaded on its own, because it will load the correct data, and add additional NAs which
    increase the size of the site but do not corrupt the data
    
    :param old_source_bulk_load_ready_file_sorted: Name of a valid bulk load ready file, with data in it. The file must have been sorted.
    :param new_source_bulk_load_ready_file_sorted: Name of a valid bulk load ready file, with data in it. The file must have been sorted. 
    :param target_bulk_load_ready_file: Name of the bulk load ready file we want to create.
    :param target_bulk_load_reversion_file: Name of a file that can be used to revert to the previous date - this file can be used to rebuild a previous position. Defaults to dev\null
    :param create_true_delta: Boolean, default False. If this is True then the files created will be the smallest possible delta file to take you from the old site to the new site and vice versa
    :param number_of_unit_dimensions: Numebr of unit dimensions used in the site - the bulk load file needs to match the site specification
    :param ignore_missing_old: Do not raise an error if there is no old_source_bulk_load_ready_file_sorted file in place. Just create a simple delta and reversion
    Even when we are creating a true delta, we have the absolute value for the data, and not some sort of difference between the values, because we still need to write actual values
    '''
    #This code is doing a merge join - reading data from two sorted files, and merging the results where possible
    
    newline_position_in_array=number_of_unit_dimensions+5
    #Note total dimensions in a bulk load file is not +5, because Transformation is never bulk loaded
    number_of_total_dimensions=number_of_unit_dimensions+4
    #datapoint index is equal to the total number of dimensions
    datapoint_index=number_of_unit_dimensions
    
    log.verbose('Creating target bulk load file "'+target_bulk_load_ready_file+'" from...')
    log.verbose('New bulkload sorted file '+new_source_bulk_load_ready_file_sorted)
    log.verbose('previous bulkload sorted file '+old_source_bulk_load_ready_file_sorted)
    
    
    if ignore_missing_old and not os.path.isfile(old_source_bulk_load_ready_file_sorted):
        #Open the old file for write then stop, leaving an empty file
         with open(old_source_bulk_load_ready_file_sorted,'w'):
            pass

    with open(old_source_bulk_load_ready_file_sorted,'r') as src_old:
        with open(new_source_bulk_load_ready_file_sorted,'r') as src_new:
            with open(target_bulk_load_ready_file,'w') as tgt:
                with open(target_bulk_load_reversion_file,'w') as rvrt:

                    old_line = src_old.readline()
                    new_line = src_new.readline()
                
                    while old_line or new_line:
                    
                        if not old_line:
                            #Write the new line to the target file
                            tgt.write(new_line)
                            
                            #Write a not applicable value to the reversion file
                            #We need this whether we are loading a true delta or not
                            split_new_line=new_line.split('\t')   
                            #The last element would be value newline e.g. '9.515\n'
                            #It should become '\n' - i.e. no value
                            split_new_line[-1]='\n'
                            rvrt.write('\t'.join(split_new_line))
                            
                            new_line = src_new.readline()
                            continue
                        
                        if not new_line:
                            split_old_line=old_line.split('\t') 
                            #The last element would be value newline e.g. '9.515\n'
                            #It should become '\n' - i.e. no value
                            split_old_line[-1]='\n'
                        
                            #Write a not applicable value to the target bulk load file
                            #We need this whether we are loading a true delta or not
                            tgt.write('\t'.join(split_old_line))
                            
                            #Write the old line to the reversion file
                            rvrt.write(old_line)
                            
                            old_line = src_old.readline()
                            continue
                        
                        split_old_line=old_line.split('\t')                        
                        split_new_line=new_line.split('\t')                        

                        #If both lines contain the same datapoint (even if the values differ) then write out the new line
                        if split_old_line[0:number_of_total_dimensions]==split_new_line[0:number_of_total_dimensions]:
                            #No need to write the data out if it is a true delta and the values are equal since the data is already present in the site
                            if create_true_delta and split_old_line[-1]==split_new_line[-1]:
                                pass
                            else:
                                tgt.write(new_line)
                                rvrt.write(old_line)
                                
                            new_line = src_new.readline()
                            old_line = src_old.readline()
                            continue
                        
                        elif split_old_line[0:number_of_total_dimensions]>split_new_line[0:number_of_total_dimensions]:  
                            #The old file is ahead of the new file - so the new data is not present in the old file
                            #The data would need to be present in both a full bulk load file and a delta file - so it doesn't matter which option has been chosen
                            #Write out the new line
                            #Read another new line, in the hope that we will catch up with the old line
                            split_new_line=new_line.split('\t') 
                            #The last element would be value newline e.g. '9.515\n'
                            #It should become '\n' - i.e. no value
                            split_new_line[-1]='\n'

                            #Write an NA record to the revert file - whether we are making true deltas or not
                            rvrt.write('\t'.join(split_new_line))
                            
                            tgt.write(new_line)
                            #Read another new line, in the hope that we will catch up with the old line
                            new_line = src_new.readline()
                            
                        elif split_old_line[0:number_of_total_dimensions]<split_new_line[0:number_of_total_dimensions]:                    
                            #The new file is ahead of the old file - so the new data was not present in the old file
                            #NA the measure and write out the old line
                            #Read another old line, in the hope that we will catch up with the new line
                            split_old_line=old_line.split('\t') 
                            #The last element would be value newline e.g. '9.515\n'
                            #It should become '\n' - i.e. no value
                            split_old_line[-1]='\n'

                            #Join new with tabs and write to output
                            tgt.write('\t'.join(split_old_line))
                            #Record the revert, becasue the new file contains an NA
                            rvrt.write(old_line)

                            #read another old line, in the hope that we will catch up with the new line
                            old_line = src_old.readline()
                        
                        else:
                            #We shouldn't have got to here - if we have I've made a mistake in the logic above
                            assert False

def set_calculation(site,user, dimension_index, use_shortnames = True,
                    calc_file = None, 
                    calculation = None, framework = -1, virtual = True, elements = [],
                    calc_set_exe = EMPOWER_CALCSET_EXECUTABLE):
        '''
		Run the calc setter utility. Runs either from a calc file, or can set a targeted calculation
		A single calculation can be applied to an element, or list of elements.
		Alternatively, a tab-separated file can be provided giving calculations to apply to different elements.
		
		Parameters:
        * site: the site object for which the calculations are set
		* dimension_index: 0-indexed dimension number to apply calculations to
		* use_shortnames: Optional, default True; specifies that the provided calculation is written using shortnames (rather than Physids)
		* calc_file: Optional, default None; file path of a file containing the required calculations
		- The following parameters will be used if a calc file is not provided
		* calculation: Optional, default None; string specifying the calculation to apply
		* framework: Optional, default -1; physid of the framework to apply the calculations to (-1 is default)
		* elements: Element shortname or list of element shortnames to apply calculation to
		
		Example:
		e.set_calculation(dimension = 0, calc_file = 'update_calculations.tsv')
		e.set_calculation(dimension = 8, calculation = 'Sales |- COGS', virtual = False, elements = 'GProfit')
		e.set_calculation(dimension = 0, use_shortnames = False, calculation = '@100 | @200', elements = 'NSales')
        
        Original code by Owen Kelly
        '''
		
        # Validate provided paraneters
        assert type(dimension_index) == int, 'dimension_index: must provide dimension for calculations, as 0-indexed integer'
        assert type(use_shortnames) == bool, 'use_shortnames: must be True (default) or False, but {} was provided'.format(str(use_shortname))
        assert calc_file or calculation, 'Either a calculation file, or a calculation must be provided'
        if calc_file:
            assert os.path.exists(calc_file) or os.path.exists(os.path.join(self.script_folder, calc_file)), 'calc_file: provided calculation file does not exist: {}'.format(calc_file)
        else:
            assert type(calculation) == str, 'calculation: must be provided as a string'
            assert type(virtual) == bool, 'virtual: Virtual must be True or False'
            assert (type(elements) == str) or (type(elements) == list), 'elements: must provide a shortname, or list of shortnames'
            if type(elements) == list:
                assert len(elements) > 0, 'elements: must provide a shortname, or list of shortnames'
                assert all(type(i) == str for i in elements), 'elements: must provide a shortname, or list of shortnames'
		
        # Get the calculation setter
        assert os.path.exists(calc_set_exe), 'Calculation Setter not found in {}; ensure this has been installed correctly'.format(EMPOWER_ROOT)
		
        # Create a call line based on the required parameters
        # Run the calc setter, and capture the response
        # Note: all parameters must be string, and each parameter is en item in the  commandline list
        # 'Empower Calculation Setter.exe' does not accept encrypted username, so username has to be passed  
        
        call_line = [calc_set_exe]
        call_line.append('-site')
        call_line.append(site.site_file())
        call_line.append('-user')
        call_line.append(user)     
        call_line.append('-password')
        call_line.append(site.password())
        call_line.append('-dimension')
        dimension = str(dimension_index)
        call_line.append(dimension)
        if use_shortnames: call_line.append('-shortnames ')
		
        # If using a calculation file, provide that
        if calc_file:
            log.verbose('Setting calculations for dimension {}; using file {}...'.format(dimension_index, calc_file))
            if os.path.exists(calc_file):
                call_line.append('-file {}'.format(calc_file))
            else:
                call_line.append('-file {}'.format(os.path.join(self.script_folder, calc_file)))
		
        
        # Otherwise provide all the required details for the calculation    
        else:
            log.verbose('Setting calculations {}, for dimension {}...'.format(calculation, dimension_index))
            call_line.append('-framework {} '.format(framework))
            call_line.append('-calculation "{}" '.format(calculation))
            call_line.append('-{} '.format('virtual' if virtual else 'real'))
            call_line.append(' '.join(elements) if type(elements) == list else elements)
					
        #print('cmdline',call_line)
        
        return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
        if return_value.returncode != 0:
            print('error msg:',return_value.stdout.decode('ansi'))
            log.error('Calculation Setter failed, and returned code {}'.format(return_value.returncode))
            raise mpex.CompletelyLoggedError('Calculation Setter has failed')
        else:
            print('set calculation is successful')
            log.verbose('Calculation(s) set successfully.')
            log.debug(return_value.stdout.decode('ansi'))
            log.debug(return_value.stderr.decode('ansi'))       
            
def set_calculation0(self, dimension_index, use_shortnames = True,
                    calc_file = None, 
                    calculation = None, framework = -1, virtual = True, elements = [],
                    calc_set_exe = EMPOWER_CALCSET_EXECUTABLE):
		'''
		Run the calc setter utility. Runs either from a calc file, or can set a targeted calculation
		A single calculation can be applied to an element, or list of elements.
		Alternatively, a tab-separated file can be provided giving calculations to apply to different elements.
		
		Parameters:
		* dimension_index: 0-indexed dimension number to apply calculations to
		* use_shortnames: Optional, default True; specifies that the provided calculation is written using shortnames (rather than Physids)
		* calc_file: Optional, default None; file path of a file containing the required calculations
		- The following parameters will be used if a calc file is not provided
		* calculation: Optional, default None; string specifying the calculation to apply
		* framework: Optional, default -1; physid of the framework to apply the calculations to (-1 is default)
		* elements: Element shortname or list of element shortnames to apply calculation to
		
		Example:
		e.set_calculation(dimension = 0, calc_file = 'update_calculations.tsv')
		e.set_calculation(dimension = 8, calculation = 'Sales |- COGS', virtual = False, elements = 'GProfit')
		e.set_calculation(dimension = 0, use_shortnames = False, calculation = '@100 | @200', elements = 'NSales')
        
        Original code by Owen Kelly
		'''
		
		# Validate provided paraneters
		assert type(dimension_index) == int, 'dimension_index: must provide dimension for calculations, as 0-indexed integer'
		assert type(use_shortnames) == bool, 'use_shortnames: must be True (default) or False, but {} was provided'.format(str(use_shortnames))
		assert calc_file or calculation, 'Either a calculation file, or a calculation must be provided'
		if calc_file:
			assert os.path.exists(calc_file) or os.path.exists(os.path.join(self.script_folder, calc_file)), 'calc_file: provided calculation file does not exist: {}'.format(calc_file)
		else:
			assert type(calculation) == str, 'calculation: must be provided as a string'
			assert type(virtual) == bool, 'virtual: Virtual must be True or False'
			assert (type(elements) == str) or (type(elements) == list), 'elements: must provide a shortname, or list of shortnames'
			if type(elements) == list:
				assert len(elements) > 0, 'elements: must provide a shortname, or list of shortnames'
				assert all(type(i) == str for i in elements), 'elements: must provide a shortname, or list of shortnames'
		
		# Get the calculation setter
		assert os.path.exists(calc_set_exe), 'Calculation Setter not found in {}; ensure this has been installed correctly'.format(self.empower_folder)
		
		# Create a call line based on the required parameters
		call_line = []
		
		call_line.append('-site "{}" '.format(self.site_file))
		call_line.append('-user "{}" '.format(self.username))
		call_line.append('-password "{}" '.format(self.password))
		call_line.append('-dimension {} '.format(dimension))
		if use_shortnames:
			call_line.append('-shortnames ')
		
		# If using a calculation file, provide that
		if calc_file:
			log.verbose('Setting calculations for dimension {}; using file {}...'.format(dimension, calc_file))
			if os.path.exists(calc_file):
				call_line.append('-file {}'.format(calc_file))
			else:
				call_line.append('-file {}'.format(os.path.join(self.script_folder, calc_file)))
		
		# Otherwise provide all the required details for the calculation    
		else:
			log.verbose('Setting calculations {}, for dimension {}...'.format(calculation, dimension))
			call_line.append('-framework {} '.format(framework))
			call_line.append('-calculation "{}" '.format(calculation))
			call_line.append('-{} '.format('virtual' if virtual else 'real'))
			call_line.append(' '.join(elements) if type(elements) == list else elements)
			
		# Run the calc setter, and capture the response
		return_value=subprocess.run([calc_set_exe, call_line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		if return_value.returncode != 0:
			log.error('Calculation Setter failed, and returned code {}'.format(return_value.returncode))
			raise CompletelyLoggedError('Calculation Setter has failed')
		else:
			log.verbose('Calculation(s) set successfully.')
			log.debug(return_value.stdout.decode('ansi'))
			log.debug(return_value.stderr.decode('ansi'))                             
                            
def export_empower_shortname_tuples(source_file_name,target_file_name,empower_site=None,empower_user=None,empower_pwd=None,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE,number_of_unit_dimensions=8):
    '''Export empower tuples from the file source_file_name into the file target_file_name, and return a dataframe of the data
    
    :param source_file: tsv encoded file of up to 8 unit dimension shortcodes followed by '''
    exporter_script=pkg_resources.resource_filename('pympx','importer_scripts/ExportSiteData'+str(int(number_of_unit_dimensions))+'Units.eimp')

    #Run the bulk import into SMD using Empower Importer
    log.verbose( "Running IMPORTER: "+"ExportSiteData"+str(int(number_of_unit_dimensions))+"Units.eimp"+" to export to file: "+str(target_file_name) + ' from ' + empower_site)
    return_value=subprocess.run([os.path.abspath(empower_importer_executable)
                                , exporter_script
                                ,"-p",'"'+empower_site+'"'
                                ,"-p",'"'+empower_user+'"'
                                ,"-p",'"'+empower_pwd+'"'
                                ,"-p",os.path.abspath(source_file_name)
                                ,"-p",os.path.abspath(target_file_name)]
                                , stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if return_value.returncode!=EMPOWER_IMPORTER_SUCCESS:
        log.error("STDOUT:")
        log.error(str(return_value.stdout.decode("utf-8") ))
        log.error("STDERR:")
        log.error(str(return_value.stderr.decode("utf-8") ))
        log.error('Empower Importer failed and returned Code:'+str(return_value))
        raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code:'+str(return_value))
    else:
        log.verbose("STDOUT:")
        log.verbose(str(return_value.stdout.decode("utf-8") ))
        log.verbose("STDERR:")
        log.verbose(str(return_value.stderr.decode("utf-8") ))
    log.verbose( "Empower Data Export complete: "+str(source_file_name))

    df =pd.read_csv(target_file_name,sep='\t',index_col=False,header=None,names=['Unit '+str(n) for n in range(number_of_unit_dimensions)]+['Metric','Mode','Currency','Time','Transformation','Value'])
    return df

def get_simple_translation_df(dimension_index,output_column_name,empower_export_data_dir,empower_site,empower_user,empower_pwd):
    df  = pd.read_csv(os.path.join(os.path.abspath(empower_export_data_dir),'Dimension_'+str(dimension_index)+'.tsv'),   sep='\t', encoding = "ISO-8859-1")
    df = df[['ID','Short Name','Long Name']]
    df['ID']=df['ID'].astype(int)
    df.rename(columns={col:'LKUP '+col for col in df.columns},inplace=True)
    df[output_column_name]=df['LKUP ID']
    return df
    
    
def translate_dim(df,dim_identifier,dim_type,translate_df):
    #Lookup either on shortname, longname or physid
    #Lookup either a single or multiple columns

    #If a singular item, convert it to a list
    if dim_identifier is str or dim_identifier is int or dim_identifier is float:
        dim_identifier=dim_identifier[dim_identifier]

    left_on=None
    right_on=None

    #Copy the translation dataframe to avoid corrupting it
    translate_df=translate_df.copy()

    ################################
    ##TODO
    ################################

    #Are all dim identifiers column in df?

    #Otherwise they are literals
    #Literal physids don't need looking up
    #Literal shortnames need a lookup, but not a merge as such

    ################################

    columns_for_explosion=[]

    #For every column that needs translating, translate it
    #TODO - optimise this so we are not unnecessarily translating single physids to physids
    for column in dim_identifier: 

        left_on=column
        if dim_type=='physid':
            right_on='LKUP ID'
        if dim_type=='shortname':
            right_on='LKUP Short Name'
        if dim_type=='longname':
            right_on='LKUP Long Name'

        try:
            newdf = df.merge(how='left',right=translate_df,left_on=left_on,right_on=right_on)
        except KeyError:
            print(df.head())
            print(translate_df.head())
            raise

        #Get the columns for the explode call
        columns_for_explosion+=[c for c in translate_df.columns if c not in ['LKUP Long Name','LKUP Short Name','LKUP ID']]

        #Add the new columns into the original dataframe
        for column in columns_for_explosion:
            df[column]=newdf[column]
            
    return columns_for_explosion
        
#TODO - create a background version of this
def zip_file(source_path,target_file,utility_path=r'C:\Program Files\7-Zip\7z.exe'):
    
    if utility_path[-6:]=='7z.exe':
        call_line='"'+utility_path+'" a "'+target_file+'" "'+source_path+'"'
        #call_line=[,]
        log.verbose("Calling: "+str(call_line))
        return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        log.debug("STDOUT:")
        log.debug(return_value.stdout.decode("utf-8") )
        log.debug("STDERR:")
        log.debug(return_value.stderr.decode("utf-8") )
    
        if return_value.returncode != 0:
            message='7-zip could not zip '+source_path+' into '+target_file+' and returned Code: '+str(return_value)
            log.error(message)
            raise mpex.CompletelyLoggedError(message)
         
def unzip_file(source_file,target_path,utility_path=r'C:\Program Files\7-Zip\7z.exe'):

    if utility_path[-6:]=='7z.exe':
        call_line='"'+utility_path+'" x "'+source_file+'" -o"'+target_path+'" * -r -aos'
        #call_line=[,]
        log.verbose("Calling: "+str(call_line))
        return_value=subprocess.run(call_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        log.debug("STDOUT:")
        log.debug(return_value.stdout.decode("utf-8") )
        log.debug("STDERR:")
        log.debug(return_value.stderr.decode("utf-8") )
    
        if return_value.returncode != 0:
            message='7-zip could not unzip '+source_file+' into '+target_path+' and returned Code: '+str(return_value)
            log.error(message)
            raise mpex.CompletelyLoggedError(message)

    
def concatenate_files(*args,target_file_name=None):
    '''Concatenate files together, using the shell COPY command for speed
    
    :param *args: names of source files to be concatenated, separated with commas 
    :param target_file_name: the name of the target file which we are concatenating to
    '''
    
    if target_file_name is None:
        raise ArgumentError('target_file_name must be set or we cannot concatenate the files')
 
    call_line='COPY '+'+'.join(['"'+arg+'"' for arg in args])
    call_line=call_line+ ' "'+target_file_name+'"'
    log.verbose("Calling: "+str(call_line))
    return_value=subprocess.run(call_line,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

    if return_value.returncode != 0:
        message='Shell could not concatenate files '+str(args)+' into '+target_file_name+' and returned Code: '+str(return_value)
        log.debug("STDOUT:")
        log.debug(return_value.stdout.decode("utf-8") )
        log.debug("STDERR:")
        log.debug(return_value.stderr.decode("utf-8") )
        log.error(message)
        raise mpex.CompletelyLoggedError(message)

    #Now remove the trailing SUB character introduced by the shell COPY command
    #See https://en.wikipedia.org/wiki/Substitute_character
    with open(target_file_name, 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()

def sort_file(source_file_name=None,target_file_name=None):
    '''Sort a file, using the shell SORT command for speed
    
    :param source_file_name: the name of the source file which we are sorting
    :param target_file_name: the name of the target file which we are writing to
    '''
    
    if source_file_name is None:
        raise ValueError('source_file_name must be set or we cannot concatenate the files')
    if target_file_name is None:
        raise ValueError('target_file_name must be set or we cannot concatenate the files')
 
    call_line='SORT "'+source_file_name+'" /LOCALE "C" /OUTPUT "'+target_file_name+'"'
         
    log.verbose("Calling: "+str(call_line))
    return_value=subprocess.run(call_line,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    log.debug("STDOUT:")
    log.debug(return_value.stdout.decode("utf-8") )
    log.debug("STDERR:")
    log.debug(return_value.stderr.decode("utf-8") )

    if return_value.returncode != 0:
        message='Shell could not sort file '+source_file_name+' into '+target_file_name+' and returned Code: '+str(return_value)
        log.error(message)
        raise mpex.CompletelyLoggedError(message)

        
def write_structure_file_to_site(structure_file, dimension_index, shortname, empower_sitepath, empower_user, empower_pwd,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE,encrypted_empower_pwd=None,encrypted_empower_user=None):

    imported_structure_filepath=structure_file
    
    
    #Export the structure to working_directory
    if encrypted_empower_user is None:
        importer_script=pkg_resources.resource_filename('pympx','importer_scripts/ImportDimensionStructure.eimp')
            
        run_empower_importer_script(script=importer_script
                                        ,parameters=[empower_sitepath
                                                    ,empower_user
                                                    ,empower_pwd
                                                    ,str(dimension_index)
                                                    ,shortname
                                                    ,imported_structure_filepath
                                        ]
                                        ,empower_importer_executable=empower_importer_executable
                                        )
    else:
        
        command_list = ['set-encrypted-parameter user='    + encrypted_empower_user.decode('utf8')
                       ,'set-encrypted-parameter password='+ encrypted_empower_pwd .decode('utf8')
                       ,'set-parameter site='              + empower_sitepath
                       ,'set-parameter dimension_index='   + str(dimension_index)
                       ,'set-parameter structure_shortname='+ shortname
                       ,'load-file-tsv "'+imported_structure_filepath+'"'
                       ,'empower-import-structure "${site}" "${user}" "${password}" ${dimension_index} ${structure_shortname}'
                       ]
                
        output = run_single_output_importer_commands(command_list
                                                        ,empower_importer_executable=os.path.abspath(empower_importer_executable)
                                                        )
        
def get_password(prompt = 'Password: '):
    import msvcrt
    import sys
    '''
    Collects and returns a user input password, provided via command prompt, and anonymously displays '*' in place of password characters
    
    Originally written by Owen Kelly before incorporation into the utils
    
    :param prompt: Message to display to screen to prompt for password input
    '''
    
    # Ensure there is a space after the prompt message
    actual_prompt = prompt if prompt[-1] == ' ' else '{} '.format(prompt)
    
    # Setup special characters that may be provided by the user and need handling
    return_char = '\r'.encode('utf-8')
    newline_char = '\n'.encode('utf-8')
    ctrl_c_char = '\003'.encode('utf-8')
    backspace_char = '\b'.encode('utf-8')
    
    #Prompt the user to enter their password
    sys.stdout.write(prompt)
    sys.stdout.flush()
    
    # Start with a blank password, and user msvcrt getch to collect characters as they are written to the console
    pw = ""

    # Keep collecting until enter is pressed, or keyboard interrupt is provided
    while True:
        c = msvcrt.getch()
        if c == return_char or c == newline_char:
            break # end on enter
        if c == ctrl_c_char:
            raise KeyboardInterrupt # raise an error if control c is provided
        if c == backspace_char:
            # If backspace is provided, remove the last character of the password, and re-write the '*'s to screen 
            sys.stdout.write('\r{}{}'.format(prompt, ' ' * len(pw))) # remove the existing password
            pw = pw[:-1] # remove the last character
            sys.stdout.write('\r{}{}'.format(prompt, '*' * len(pw))) # re-write the *s
            sys.stdout.flush()
        else:
            
            pw += str(c, 'utf-8')
            sys.stdout.write('*')
            sys.stdout.flush()

    # Move onto the next line for the next message to standard out
    sys.stdout.write('\n')
    
    # Return
    return pw

def encrypt_site_usr_pwd(tgtDir=None):
    userName=None
    cnt=0
    while not userName:
        cnt+=1
        user = input('Site supervisor name (6 characters or longer): ')
        user =user.strip(' ')
        if len(user)<6: print('invalid user name, must be at least 6 characters')
        else: 
            userName = user
            break
        if cnt>=10: 
            print('Too many mistakes are made in providing a site supervisor name. Action aborted')
            return False
    cnt=0
    password=None   
    prompt= 'Password(>=8 characters, with at least 2 numerical numbers): '
    while not password:
        pwd1 = get_password(prompt = prompt)
        cnt_num=0
        cnt+=1
        pwd1 = pwd1.strip(' ')
        nchr=len(pwd1)
        for c in pwd1:
            if c.isnumeric():cnt_num+=1
        if len(pwd1)<8 or cnt_num<2:
            print('Security requirement not met for password')
        else:  
            password=pwd1 
            break
        if cnt>=10: 
            print('Too many mistakes are made in providing a password. Action aborted')
            return False
    prompt= 'Repeat password: '
    cnt=0
    pwd=None
    while not pwd:
        pwd2 = get_password(prompt = prompt)
        cnt+=1
        if pwd2==password:
            pwd=pwd2
            break
        if cnt>=1: print('password does not match')
        
        if cnt>=10: 
            print('Too many mistakes are made in repeating the password. Action aborted')
            return False
            
    if not tgtDir : tgtDir=os.getcwd()
    fname=os.path.join(tgtDir,'site_init')
    key = Fernet.generate_key()
    fernet = Fernet(key)
    uname = fernet.encrypt(userName.encode())
    pwd = fernet.encrypt(password.encode())
    ulist=[key,uname,pwd]
    fid=open(fname,'wb')
    pickle.dump(ulist,fid)
    fid.close()
    print('Site security details are written to: ',fname)
    return True
    
def prompt_for_login_details():
    try:
        get_ipython().__class__.__name__    
        using_ipython = True
        #import getpass
    except Exception:
        using_ipython = False

    user = input('User: ')

    if using_ipython:
        pwd = getpass.getpass(prompt='Password: ',stream=None)
    else:
        #Use Owen's code for getting passwords
        pwd = get_password(prompt='Password: ')

    return user, pwd    

def get_secure_login(site_path,work_path,explicit_security_path,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE,machine_locked=False):
    '''Prompt for a user and logon for an Empwoer Site, and then save these down as a user-locked encrypted file and key'''
    return _get_secure_login(site_path=site_path,work_path=work_path,explicit_security_path=explicit_security_path,empower_importer_executable=     empower_importer_executable,machine_locked=machine_locked)

def _get_secure_login(site_path,work_path,user=None,password=None,explicit_security_path=None,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE,machine_locked=False):
    '''
    :param user: For backward compatibility only - we don't want the user entered as part of a script
    :param password: For backward compatibility only - we don't want the password entered as part of a script. We can encrypt it with the new code and then use encryption throughout
    '''
    #from cryptography.fernet import Fernet


    empower_sites = r"C:\Empower Sites"
    _sitename_for_security = os.path.splitext(os.path.basename(site_path))[0]
    if explicit_security_path is not None:
        empower_sites_security_folder = explicit_security_path
    else:
        empower_sites_security_folder = os.path.join(empower_sites,'PythonSecurity')
    if work_path is not None and os.path.isdir(work_path):
        work_path_security_folder = os.path.join(work_path,'PythonSecurity')
    else:
        work_path_security_folder = None

    #Sort out folders to hold encrypted security
    security_folder = None
    empower_sites_security_folder_does_not_exist = True
    if explicit_security_path is None:
        if os.path.isdir(empower_sites):
            if os.path.isdir(empower_sites_security_folder):
                empower_sites_security_folder_does_not_exist = False
                security_folder = empower_sites_security_folder
                    
            else:
                empower_sites_security_folder_does_not_exist = True
                try:
                    os.mkdir(empower_sites_security_folder)
                    security_folder = empower_sites_security_folder
                    empower_sites_security_folder_does_not_exist = False
                except:
                    pass
        if empower_sites_security_folder_does_not_exist:
            os.makedirs(work_path_security_folder,mode = 555, exist_ok = True)
            security_folder = work_path_security_folder
    else:
        os.makedirs(explicit_security_path,mode = 555, exist_ok = True)
        security_folder = explicit_security_path
    
    site_security_folder = os.path.join(security_folder,_sitename_for_security)    
    os.makedirs(site_security_folder,mode = 555, exist_ok = True)
    
    fernet = None

    
    #Cycle through the subfolders, tryign to read an encrypted password from a file we have access to

    for d in os.listdir(site_security_folder):
        if os.path.isdir(os.path.join(site_security_folder,d)):
            #Try to read the security key file
            security_key_file = os.path.join(site_security_folder,d,'key1')
            user_file = os.path.join(site_security_folder,d,'key2')
            password_file = os.path.join(site_security_folder,d,'key3')
            try:
                with open(security_key_file,mode='rb') as f:
                    fernet = Fernet(f.read())

                #The fernet encrypted files are still windows encrypted after being decrypted
                #windows encrypted strings will be used in the empower scripts
                with open(password_file,mode='rb') as f:
                    windows_encrypted_password = fernet.decrypt(f.read())

                #The fernet encrypted files are still windows encrypted after being decrypted
                #windows encrypted strings will be used in the empower scripts
                with open(user_file,mode='rb') as f:
                    windows_encrypted_user = fernet.decrypt(f.read())    
                    
                break    
            except:
                fernet = None
                windows_encrypted_password = None
                windows_encrypted_user = None

    created_security_dir = None
                
    #If we couldn't get access            
    if fernet is None:
        import ntsecuritycon
        import win32security

        created_security_dir = os.path.join(site_security_folder,datetime.datetime.now().strftime('key%Y%m%d%H%M%S'))
        security_key_file = os.path.join(created_security_dir,'key1')
        user_file = os.path.join(created_security_dir,'key2')
        password_file = os.path.join(created_security_dir,'key3')
        os.mkdir(created_security_dir)

        with open(security_key_file, mode ='wb') as key_file:
             pass

        #Set the access
        os_user = os.getlogin()
        everyone, _, _ = win32security.LookupAccountName ("", "Everyone")

        entries = [{'AccessMode': win32security.GRANT_ACCESS,
                    'AccessPermissions': (ntsecuritycon.DELETE),
                    'Inheritance': win32security.CONTAINER_INHERIT_ACE |
                                   win32security.OBJECT_INHERIT_ACE,
                    'Trustee': {'TrusteeType': win32security.TRUSTEE_IS_USER,
                                'TrusteeForm': win32security.TRUSTEE_IS_NAME,
                                'Identifier': "Everyone"}}
                   ,{'AccessMode': win32security.GRANT_ACCESS,
                    'AccessPermissions': (ntsecuritycon.GENERIC_READ |
                                          ntsecuritycon.GENERIC_WRITE|
                                          ntsecuritycon.DELETE),
                    'Inheritance': win32security.CONTAINER_INHERIT_ACE |
                                   win32security.OBJECT_INHERIT_ACE,
                    'Trustee': {'TrusteeType': win32security.TRUSTEE_IS_USER,
                                'TrusteeForm': win32security.TRUSTEE_IS_NAME,
                                'Identifier': os_user}}
                  ]

        #dacl = sd.GetSecurityDescriptorDacl()
        dacl = win32security.ACL()
        dacl.Initialize()
        dacl.SetEntriesInAcl(entries)
        win32security.SetNamedSecurityInfo(security_key_file, win32security.SE_FILE_OBJECT,
                                            win32security.DACL_SECURITY_INFORMATION |
                                            win32security.PROTECTED_DACL_SECURITY_INFORMATION,
                                            None, None, dacl, None)          

        with open(security_key_file, mode ='wb') as key_file:
            #generate and write the key                            
            fernet_key = Fernet.generate_key()
            key_file.write(fernet_key)      
        fernet = Fernet(fernet_key)
        #wipe the original key from memory - just in case
        fernet_key = None
        gc.collect()
    
        #We wish to have a prompt every time, but for backward compatibility, we may already have user and password in the site script code, and wish to 
        #encrypt these for easy usage next time
        if user is None or password is None:
            user, pwd = prompt_for_login_details()
        else:
            user = user
            pwd  = password

        with open(password_file, mode ='wb') as password_file:
            #encrypt and write the password
            if machine_locked:
                windows_encrypted_password = encrypt_machine_locked(text=pwd,empower_importer_executable=empower_importer_executable)            
            else:
                windows_encrypted_password = encrypt_user_locked(text=pwd,empower_importer_executable=empower_importer_executable)
            password_file.write(fernet.encrypt(windows_encrypted_password))
        #wipe the original from memory - just in case
        pwd = None
        gc.collect()

        with open(user_file, mode ='wb') as user_file:
            #encrypt and write the user
            if machine_locked:
                windows_encrypted_user = encrypt_machine_locked(text=user,empower_importer_executable=empower_importer_executable)
            else:
                windows_encrypted_user = encrypt_user_locked(text=user,empower_importer_executable=empower_importer_executable)
            user_file.write(fernet.encrypt(windows_encrypted_user))
        #wipe the original from memory - just in case
        user = None
        gc.collect()      

    fernet = None
    gc.collect()

    return windows_encrypted_user,windows_encrypted_password, created_security_dir  

def encrypt_machine_locked(text,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE):
    

    #Wait for 100 milliseconds so that we can read SRDERR and STDOUT
    command_list = ['encrypt-text -machine-locked "{}"'.format(text)]

    return run_single_output_importer_commands(command_list,empower_importer_executable=empower_importer_executable).rstrip('\r\n').encode('utf8')

def encrypt_user_locked(text,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE):
    

    #Wait for 100 milliseconds so that we can read SRDERR and STDOUT
    command_list = ['encrypt-text "{}"'.format(text)]

    return run_single_output_importer_commands(command_list,empower_importer_executable=empower_importer_executable).rstrip('\r\n').encode('utf8')
    
def run_single_output_importer_commands(command_list,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE):    
    try:
        #The dash means run importer by reading commands from STDIN
        call_line=[os.path.abspath(empower_importer_executable), '-']

        #Turn list into new text separated by new lines
        #waits for 0.01 seconds to allow the pipe to open successfully, then quits
        command_text = '\n'.join(command_list+['wait','quit'])
        
        #return_value=subprocess.call(call_line)
        proc=subprocess.Popen(args=call_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)

        proc.stdin.write(command_text.encode('utf8'))
        proc.stdin.flush()
        proc.stdin.close()
        
        output = proc.stdout.read()
        errors = proc.stderr.read()

        #Close the input pipe
        proc.communicate()

        try:
            std_err =str(errors.decode(_get_standard_empower_encoding_from_importer_path(empower_importer_executable)))
        except UnicodeDecodeError:
            std_err =str(errors.decode("cp1252"))

            
        log.debug("STDERR:")
        log.debug(std_err)
        
    except FileNotFoundError:
        error_message='Empower Importer could not be run because the importer executable could not be found. Please check it exists in: '+str(empower_importer_executable)
        log.error(error_message)
        raise mpex.CompletelyLoggedError(error_message)

    if proc.returncode==17:
        log.error('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)
        raise mpex.EmpowerImporterError('Empower Importer failed because it requires an "output" command and returned Code: '+str(proc.returncode)+'\n'+std_err)

    if proc.returncode!=18 and proc.returncode!=0:
        log.error('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)
        raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)

    retval = output.decode(_get_standard_empower_encoding_from_importer_path(empower_importer_executable))
    return retval     
    
def run_and_yield_single_output_importer_commands(command_list,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE):    

    if not os.path.isfile(empower_importer_executable):
        error_message='Empower Importer could not be run because the importer executable could not be found. Please check it exists in: '+str(empower_importer_executable)
        log.error(error_message)
        raise mpex.CompletelyLoggedError(error_message)
        
    #The dash means run importer by reading commands from STDIN
    call_line=[os.path.abspath(empower_importer_executable), '-']

    command_text = '\n'.join(command_list+['wait','quit'])
    
    #return_value=subprocess.call(call_line)
    proc=subprocess.Popen(args=call_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=1,universal_newlines=True)
    try:
        proc.stdin.write(command_text)
        proc.stdin.flush()
        proc.stdin.close()
        
        
        for line in proc.stdout:
            #log.debug(line.strip('\n'))
        
            yield line.strip('\n')
        
        #Close the input pipe?
        proc.wait()
        errors = proc.stderr.read()
        #proc.poll()

        std_err =str(errors)
            
        log.debug("STDERR:")
        log.debug(std_err)
        #log.debug(proc.returncode)
        
        if proc.returncode!=18 and proc.returncode!=0:
            log.error('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)
            #raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code: '+str(proc.returncode)+'. Command text:\n'+command_text+'\nSTDERR:\n'+std_err)
            raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code: '+str(proc.returncode)+'.\nSTDERR:\n'+std_err)

    finally:
        try:
            proc.stdout.close()
        except Exception:
            pass
        try:
            proc.stderr.close()
        except Exception:
            pass
        try:
            proc.stdin.close()
        except Exception:
            pass
        
    #retval = output.decode('cp1252')
    #return retval     

def start_no_output_importer_commands(command_list,empower_importer_executable=EMPOWER_IMPORTER_EXECUTABLE):  
    '''Starts an Importer process with a list of commands and returns the process so you can see if it has failed
    This way another process can start immediately afterward, and pass a named pipe some data, without starting an unnecessary new thread
    '''

    if not os.path.isfile(empower_importer_executable):
        error_message='Empower Importer could not be run because the importer executable could not be found. Please check it exists in: '+str(empower_importer_executable)
        log.error(error_message)
        raise mpex.CompletelyLoggedError(error_message)
        
    #The dash means run importer by reading commands from STDIN
    call_line=[os.path.abspath(empower_importer_executable), '-']

    command_text = '\n'.join(command_list+['wait','quit'])
    
    #return_value=subprocess.call(call_line)
    proc=subprocess.Popen(args=call_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=1,universal_newlines=True)
    try:
        proc.stdin.write(command_text)
        proc.stdin.flush()
    
    finally:    
        try:
            proc.stdin.close()
        except Exception:
            pass

    return proc

def complete_no_output_importer_process(proc):              
    '''Finish work on a process created by start_no_output_importer_commands
    Raise errors returned by Importer
    This function is designed to be called after a named pipe has been fed with input data for the process in the proc parameter
    '''
    
    if proc is None:
        return
                        
    try:
        #Throw away output lines. This process shouldn't be passed commands that create output       
        for line in proc.stdout:
            pass
                    
        #Close the input pipe?
        proc.wait()
        errors = proc.stderr.read()
        #proc.poll()

        std_err =str(errors)
            
        log.debug("STDERR:")
        log.debug(std_err)
        #log.debug(proc.returncode)
        
        if proc.returncode!=18 and proc.returncode!=0:
            log.error('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)
            #raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code: '+str(proc.returncode)+'. Command text:\n'+command_text+'\nSTDERR:\n'+std_err)
            raise mpex.CompletelyLoggedError('Empower Importer failed and returned Code: '+str(proc.returncode)+'.\nSTDERR:\n'+std_err)

    finally:
        try:
            proc.stdout.close()
        except Exception:
            pass
        try:
            proc.stderr.close()
        except Exception:
            pass

from contextlib import contextmanager

@contextmanager
def outbound_pipe(pipename):
    '''Create a connected outbound Windows named pipe and return it for writing to.
    Use it with the 'with' operator and it'll close nicely - so like this:
    >>> with outbound_pipe(pipename=r'\\.\pipe\foo') as pipe:
    ...     win32file.WriteFile(pipe, str.encode('bar'))
    '''
    pipe = win32pipe.CreateNamedPipe(
                            pipename,
                            win32pipe.PIPE_ACCESS_OUTBOUND,
                            win32pipe.PIPE_TYPE_BYTE, # | win32pipe.PIPE_WAIT, 
                            1, 65536, 65536,
                            0,
                            None)
    win32pipe.ConnectNamedPipe(pipe, None)
    #win32file.WriteFile(pipe,"".encode())
   
    log.debug("Pipe {} connected".format(pipename))  
    try:
        yield pipe         
    finally:    
        try:
            #if pipe, need to call FlushFileBuffers?
            win32file.FlushFileBuffers(pipe)
        except Exception:
            pass
        try:
            win32pipe.DisconnectNamedPipe(pipe)
        except Exception:
            pass
        try:
            win32file.CloseHandle(pipe)
            log.debug("Pipe {} closed".format(pipename))
        except Exception:
            pass
