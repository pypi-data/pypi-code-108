'''

/****************************************************************************/
/* Metapraxis Limited                                                       */
/*                                                                          */
/* Copyright (©) Metapraxis Ltd, 2017-present, all rights reserved.          */
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
class MPXError(Exception):
    '''Root Metapraxis exception, allows us to catch any exception in this module'''
    pass

    
class UpstreamFailureError(MPXError):
    '''Exception designed to be thrown when there is a failure in an upstream parallel process'''
    pass


class CompletelyLoggedError(MPXError):
    '''If we have logged everything we need to know about an error, 
    we do not need to print a stacktrace to the logs, or log an Unhandled Error for the end user.
    Raise this error once all the pertinent captured error is logged, to improve the end user experience'''
    pass    

class EmpowerSecurityError(Exception):
    '''Exception to be thrown when encrypted password or user name has not been set'''
    pass
    
class EmpowerImporterError(MPXError):
    '''Generic error used to catch any error caused when using Empower Importer or Batch'''
    pass
    
class EmpowerImporterVersionError(EmpowerImporterError):
    '''When functionality is not available in a version of Empower Importer or Batch this error can be thrown'''
    pass

class EmpowerImporterOutputLostError(EmpowerImporterError):
    '''Thrown when running importer causes output to be lost because it requires a final output command'''
    pass
  
class LoaderSetupError(MPXError):
    '''Thrown when the setup of a loader is incomplete or inconsistent'''
    pass

class MonitoringError(MPXError):
    '''Thrown when a process monitor discovers a process is unresponsive'''
    pass
    
    
class ValidationError(MPXError):
    pass

class RecordLengthError(ValidationError):
    def __init__(self,record_index,expected_record_length,record):
        self.record_index = record_index
        self.expected = expected_record_length
        self.record = record
        self.column = None
        #Look backwards for the first value
        number_of_blanks_at_end = 0
        for n, v in enumerate(list(record.values())[::-1]):
            if v is not None:
                number_of_blanks_at_end = n
                break
                
        self.actual = expected_record_length - number_of_blanks_at_end

class ColumnNotExistsError(ValidationError):
    def __init__(self,column_key,columns_in_reader):
        self.record_index = 0
        self.expected = 'Expected a column named "{}"'.format(column_key)
        self.column = column_key
        
        self.actual = str(columns_in_reader)  
        
class FormatConversionError(ValidationError):
    def __init__(self,record_index,expected_format,column_key,record):
        self.record_index = record_index
        self.expected = str(expected_format)
        self.record = record
        self.column = column_key
        
        self.actual = record[column_key]   

class LookupError(ValidationError):
    def __init__(self,record_index,expected_lookup
                 ,column_key,record):
        self.record_index = record_index
        self.expected = str(expected_lookup)
        self.record = record
        self.column = column_key
        self.actual = record[column_key]        

class BusinessLogicError(ValidationError): 
    def __init__(self,record_index,expected_logic,actual_logic,record,column_key=None):
       
        self.record_index = record_index
        self.expected = str(expected_logic)
        self.record = record
        self.column = column_key
        self.actual = actual_logic        
        
        