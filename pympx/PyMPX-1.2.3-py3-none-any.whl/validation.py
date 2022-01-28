#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation
'''Data Validation



/****************************************************************************/
/* Metapraxis Limited                                                       */
/* Date: 09-07-2018                                                         */
/*                                                                          */
/*                                                                          */
/* Copyright (c) Metapraxis Limited, 2018.                                  */
/* All Rights Reserved.                                                     */
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

import sys
import os
import shutil
import fnmatch

import numpy as np
import pandas as pd
#pandas uses constants from the csv module when reading and saving
import csv

import datetime

#Need this for the OrderedDict
import collections


#from pympx import low_level_utilities as llu
from pympx import logconfig
from pympx.exceptions import *
log=logconfig.get_logger()

class validate(object):
    '''Magic class to return common type conversion and validation functions'''

    @staticmethod
    def str(column_name,default=False,use_lookup_optimisation=False):
        '''
        
        :param default: replacement for empty strings. If False, then empty strings will not be replaced. If None, then None will be used instead
        '''
        return ColumnValidator(column   = column_name
                              ,function = lambda x: x
                              ,expected_message  = 'a string'
                              ,default = default
                              ,use_lookup_optimisation=use_lookup_optimisation
                              )

                              
    @staticmethod
    def int(column_name,default=False,use_lookup_optimisation=False):
        '''
        
        :param default: replacement for empty strings. If False, then empty strings will not be replaced. If None, then None will be used instead
        '''
        return ColumnValidator(column   = column_name
                              ,function = int
                              ,expected_message  = 'an integer'
                              ,default = default
                              ,use_lookup_optimisation=use_lookup_optimisation
                              )
    
    @staticmethod
    def float(column_name,default=False,use_lookup_optimisation=False):
        '''
        
        :param default: replacement for empty strings. If False, then empty strings will not be replaced. If None, then None will be used instead
        '''
        return ColumnValidator(column   = column_name
                              ,function = float
                              ,expected_message  = 'a float'
                              ,default = default
                              ,use_lookup_optimisation=use_lookup_optimisation
                              )
        
    @staticmethod
    def strptime(column_name,format_string,default=False,use_lookup_optimisation=True):
        '''
        
        :param default: replacement for empty strings. If False, then empty strings will not be replaced. If None, then None will be used instead
        '''
        return ColumnValidator(column   = column_name
                              ,function = lambda x: datetime.datetime.strptime(x,format_string)
                              ,expected_message  = 'a date in the format "{}"'.format(format_string)
                              ,default = default
                              ,use_lookup_optimisation=use_lookup_optimisation
                              )
    

class FileValidator():
    '''Reads a file and yields  dictionaries just like a DictReader, only it validates the file on the way through'''


	#STANDARD_FUNCTION_MESSAGES:
		

    def __init__(self, src,bad_file=None,encoding = 'utf8',pass_bad_values = False, pass_bad_records = False):
		
        if bad_file:
            self.bad_file = open(bad_file,'w')
        else:
            self.bad_file = None
            
        self.src        = src
        
        self._errors = []
        self.column_validators = {}
        #record validators get run after columns have been validated
        self.record_validators = []

        self.record_index = 0
        
        if isinstance(src,csv.DictReader): 
            self.reader = src
        else:
            self.reader = csv.DictReader(self.src)
            #[line for n, line in enumerate(open_file) if n >0]
        
        self.pass_bad_records = pass_bad_records
        self.pass_bad_values  = pass_bad_values
        
        self.bad_record_count = 0
        self.good_record_count = 0
        
    @property    
    def total_record_count(self):    
        return self.record_index
        
    def __del__(self):
        if self.bad_file:
            self.bad_file.close()
    
    def __iadd__(self,other):
		#Check it's a column validator
		#or a dictionary {'column name':function}
		#or a dictionary {'column name':'date format string'}
        if isinstance(other,RecordValidator):    
            self.record_validators.append(other)
           
        else:
            assert isinstance(other,ColumnValidator)
            self.column_validators[other.column] = other

        return self
    
    def __iter__(self):
        return self
    
    def __next__(self):
		#validate the next row and yield the output dictionary
        record = next(self.reader)
        #print(record)
        return self._convert_record(record)
    
        
    def _convert_record(self,record):
        #if len(record) !=145:
        #    self.errors.append(RecordLengthError(record_index,145,record))
        #if record["settlement_term"] is None:
        #    self.errors.append(RecordLengthError(record_index,145,record))   

        output = collections.OrderedDict()
        
        er = None
        
        if self.record_index == 0:
            #validate that all columns exists
            for k in self.column_validators.keys():
                if not k in self.reader.fieldnames:
                    er = ColumnNotExistsError(column_key=k,columns_in_reader=self.reader.fieldnames)
                    self.errors.append(er)
            
        for k, v in record.items():
        
            try:
                cv = self.column_validators[k]
            except KeyError:
                if v == "":
                    output[k] = None
                else:    
                    output[k] = v
                continue
               
            try:
                converted = cv.function(v)
            except AssertionError as e:    
                er = BusinessLogicError(self.record_index
                                      ,actual_logic      =str(e)
                                      ,expected_logic    = cv.expected_message
                                      ,column_key        = cv.column
                                      ,record            = record
                                      ) 
                    
                self.errors.append(er)
                    
            except Exception:
                if cv.default == False:
                    if self.pass_bad_values:
                        converted = v
                    else:
                        converted = None
                elif v == "":
                    converted = cv.default
                elif self.pass_bad_values:
                    converted = v
                else:
                    converted = None
                    
                    
                if cv.default == False and v != "":                
                    er = FormatConversionError(self.record_index
                                              ,expected_format    = cv.expected_message
                                              ,column_key         = cv.column
                                              ,record             = record
                                              ) 
                    
                    self.errors.append(er)
                    
                if self.bad_file:
                    pass
            
            output[k] = converted
    
        if er is None:
            for rv in self.record_validators:
                try:
                    rv.function(record)
                except AssertionError as e:               
                    er = BusinessLogicError(self.record_index
                                          ,actual_logic      =str(e)
                                          ,expected_logic    = rv.expected_message
                                          ,record             = record
                                          ) 
                    
                    self.errors.append(er)
                
        
        #for column_key, lookup in lookup_dict.items():
        #    try:
        #        lookup['lookup'][record[column_key]]
        #    except Exception:
        #        raise LookupError(record_index
        #                          ,expected_lookup=lookup['expected']
        #                          ,column_key=column_key
        #                          ,record=record)  
    
        self.record_index+=1
        #print(self.record_index)
        
        if er is None:
        #TODO calc total good and bad records
            pass
            
        if self.pass_bad_records or er is None:
            return output
        else:
            return {}
		
    @property
    def errors(self):
        return self._errors
	
    @property
    def dataframe(self):
        return pd.DataFrame([d for d in self])

	
class ColumnValidator():
	
    def __init__(self,column,function,expected_message,default=False,use_lookup_optimisation=False):
        '''
        
        :param default: replacement for empty strings. If False, then empty strings will not be replaced. If None, then None will be used instead
        '''
        
        self.column             = column
        if use_lookup_optimisation:
            self._function      = function
            self.previous_work_lookup = {}
            self.function       = self.lookup_wrapper
        else:
            self.function       = function
            
        self.expected_message   = expected_message
        self.default            = default
        
        
    def lookup_wrapper(self, value):
        try:
            return self.previous_work_lookup[value]
        except KeyError:
            retval = self._function(value)
            self.previous_work_lookup[value] = retval
            return retval
    
class RecordValidator():
    '''Does post-column validation record validation
    '''

    def __init__(self,function,expected_message):
        '''
        
        :param function: A function which takes a record and asserts a business rule, raising an assertion error if the rule is not met
        '''
        
        self.function           = function
        self.expected_message     = expected_message
