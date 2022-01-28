'''An object model which allows Metapraxis Empower sites to be manipulated programatically
'''

#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation

#/****************************************************************************/
#/* Metapraxis Limited                                                       */
#/* Date: 28-06-2018                                                         */
#/*                                                                          */
#/*                                                                          */
#/* Copyright (c) Metapraxis Limited, 2018-2021.                             */
#/* All Rights Reserved.                                                     */
#/****************************************************************************/
#/* NOTICE:  All information contained herein is, and remains the property   */
#/* of Metapraxis Limited and its suppliers, if any.                         */
#/* The intellectual and technical concepts contained herein are proprietary */
#/* to Metapraxis Limited and its suppliers and may be covered by UK and     */
#/* Foreign Patents, patents in process, and are protected by trade secret   */
#/* or copyright law.  Dissemination of this information or reproduction of  */
#/* this material is strictly forbidden unless prior written permission is   */
#/* obtained from Metapraxis Limited.                                        */
#/*                                                                          */
#/* This file is subject to the terms and conditions defined in              */
#/* file "license.txt", which is part of this source code package.           */
#/****************************************************************************/

import sys
import os
import shutil
import fnmatch
import uuid
import win32file #, win32pipe#

#multiprocessing is used as a 'threading' tool
import multiprocessing
import queue as qq

# Avoid the annoying NUMEXPR warning
os.environ['NUMEXPR_MAX_THREADS'] = '8'

import numpy as np
import pandas as pd
#pandas uses constants from the csv module when reading and saving
import csv
#PYM-25
csv.field_size_limit(2147483647)

import datetime
from dateutil import relativedelta

#Need this for the OrderedDict
import collections

#Need this to use embedded importer scripts
import pkg_resources
import sys
import gc

#import getpass


from pympx import queuing as mpq
from pympx import low_level_utilities as llu
from pympx import logconfig
from pympx import exceptions as mpex


log=logconfig.get_logger()

empower_versions = ['8.3','9.0','9.1','9.2','9.3','9.4','9.5','9.6','9.7', '9.8', '9.9']

DAY=relativedelta.relativedelta(days=1)
MONTH=relativedelta.relativedelta(months=1)
YEAR=relativedelta.relativedelta(years=1)

TABBYTES = str.encode('\t')
NEWLINEBYTES = str.encode('\n')

#pandas monkeypatching
import pandas as pd
#
def to_empower_viewpoint(self,tgt,mappings=None,safe_load=True,identifier_columns=None,ignore_zero_values=True,clear_focus_before_loading=True):
    '''
    Load a DataFrame into an Empower Viewpoint.
    Data in the viewpoint will be cleared out (with a block-set) command prior to loading, and a parallel bulk load will load the data

    :param tgt: A pympx.Viewpoint object. The viewpoint must be formed of single hierarchy Structures. Site.viewpoints['SHORTNAME'] will retrieve a pre-existing viewpoint from a Site
    :param mappings: A zero indexed dictionary of dimension mappings - {0: mapping, 1: mapping ... 12: mapping }. If mapping is a string, it specifies a column or shortcode. If a dictionary then {column:field} where field is a Dimension attribute. if {column:shortcode, column:shortcode} then column to metric shortcode
    :param safe_load: Leaves the site with the viewpoint cleared of data if a failure occurs, rather than with partially loaded data. This option will cause about twice as much space to be needed for the load
    :param identifier_columns: Columns in the DataFrame that will help find an erroneous row if an error occurs with the load.
    :param ignore_zero_values: Load N/A in place of zero values, saving time and space.
    :param clear_focus_before_loading: Do a block-set to N/A on the focus before loading. if a previous block set has been run (in a similar partial load) you may be able to gain time by setting this parameter to False.
    '''
    vp = tgt

    assert isinstance(tgt, Viewpoint)
    if identifier_columns is None:
        identifier_columns = []
    if mappings is None:
        mappings = {}

    vp.load( src                        = self
           , mappings                   = mappings
           , safe_load                  = safe_load
           , identifier_columns         = identifier_columns
           , ignore_zero_values         = ignore_zero_values
           , clear_focus_before_loading = clear_focus_before_loading
           )

pd.DataFrame.to_empower_viewpoint = to_empower_viewpoint

def _read_empower(src):
    if isinstance(src,_ElementsGetter):
        return src.dataframe
    if isinstance(src,Dimension):
        return src.elements.dataframe

    raise ValueError('read_empower() cannot read an object of type {} in this version of the code. it can currently read Dimension objects. If you need this functionality, please raise a ticket'.format(type(src)))

pd.read_empower = _read_empower


#TODO - we want sites to be better - a dictionary or list of Site objects
# we must handle password getting though, so that we don't have to enter password until site actually used
#

#class _Empower(object):
#maybe don't do this as a class - do it direct out of the module
#
#    @property
#    def sites(self):
#        '''Get the sites available in the registry on this machine'''
#
#        _sites = {}
#
#        for version in empower_versions:
#
#            #Import the elements in the working file into Empower
#            #Export the structure to working_directory
#            importer_script=pkg_resources.resource_filename('pympx','importer_scripts/GetEmpowerSites.eimp')
#            output = llu.run_empower_importer_script(script=importer_script
#                                            ,parameters=[version]
#                                            ,empower_importer_executable=llu.EMPOWER_IMPORTER_EXECUTABLE
#                                            )
#
#            for n, line in enumerate(output.split('\r\n')):
#                #Ignore the header record
#                if n > 0:
#                    if len(line) > 1:
#                        name_and_locator = line.split('\t')
#                        locator = name_and_locator[1][:-1]
#                        try:
#                            site_info = _sites[locator]
#                            site_info["versions"].append(version)
#                        except KeyError:
#                            site_info = {"versions":[version], "name": name_and_locator[0][1:]}
#                            _sites[locator] = site_info
#
#        return _sites
#
#Empower = _Empower()

class Site(object):
    r'''
       Representation of a Metapraxis Empower site.
    '''

    def __init__(self
                ,site_locator                   = None
                ,work_directory                 = None
                ,storage_dimension_index        = None
                ,elements_per_storage_dimension = None
                ,number_of_unit_dimensions      = None
                ,empower_importer_executable    = llu.EMPOWER_IMPORTER_EXECUTABLE
                ,logging_queue                  = None
                ,security_storage_path          = None
                ,debug                          = False         
                ,machine_locked                 = False
                ):
        '''Log on to the site and access Dimensions, Structures and transactional data.
        If you have never logged on before on the machine you are calling from, you will be prompted for a user name and password.
        The password will be stored in C:\\Empower Sites\\PythonSecurity\\ under a directory containing the site name

        If you have Empower Importer 9.5 RC6 or greater installed you only need to specify site_locator (or site path)
        Specify the work_directory if you want to, otherwise it will default to C:\\Empower Sites\\Temp Work\\[Site Name]

        :param site_locator: Path to the .eks or .beks containing the site, or site locator string for an SQL site
        :param work_directory: a directory for work files used when exporting and importing data into Empower.
        :param storage_dimension_index: If you are using an Empower Importer version before 9.5..855 specify  the 0 based index of the storage dimension. This can be found in "Site Details" in Empower. This information is read automatically with later versions of Importer.
        :param elements_per_storage_dimension: If you are using an Empower Importer version before 9.5..855 specify  the number of elements in each the storage dimension. This can be found in "Site Details" in Empower. This information is read automatically with later versions of Importer.
        :param number_of_unit_dimensions: If you are using an Empower Importer version before 9.5..855 specify  the number of unit dimensions in this empower site. This can be found in "Site Details" in Empower. This information is read automatically with later versions of Importer.
        :param empower_importer_executable: If you wish to interface with Empower using a version of Empower Importer that is not kept in the standard location then set a path to the executable you wish to use here. By default PyMPX will try to find the latest Empower Importer installed on the system.
        :param logging_queue: multiprocessing.Queue used to send log messages to. Log messages are sent to the console by default, but can be redirected to a file listener at the other end of this queue.
        :param security_storage_path: directory for holding encrypted and user locked security credentials. This will default to C:\Empower Sites if no path is set.
        :param debug: Boolean, set to true when you want exports and imports performed by Importer written to file rather than being passed around in memory. Useful for debugging probelematic Imports/Exports
        :param machine_locked: Boolean, set to true when you want security to be machine locked, so that a servcie account can run Empower, after the password has been set up and the Key1 key has been given read access
        
        '''

        #Refugee parameters from the old obmod module live here. Just in case, in dire need, they need to be resurrected.
        source_locations = None
        prefix = None
        user = None
        pwd = None

        self._debug = debug

        if source_locations is None:
            source_locations = {}
        #Check source locations contains the directories we are going to need
        sloc = source_locations

        #Explicit path to hold security settings. the plan is to replace this with the windows vault
        self._explicit_security_path = security_storage_path

        if empower_importer_executable is None:
            empower_importer_executable    = llu.EMPOWER_IMPORTER_EXECUTABLE

        if site_locator is not None:
            temp_site_path = site_locator
        else:
            try:
                temp_site_path = os.path.abspath(sloc['empower_site_file'])
            except KeyError:
                temp_site_path = None

        if temp_site_path and (temp_site_path[:9] == "{SQL-KVP}" or temp_site_path[:14] == "{MSSQL-CARDED}" ):
            self.storage_type = "sql"
        elif temp_site_path and os.path.splitext(temp_site_path)[1] == '.eks':
            self.storage_type = "eks"
        elif temp_site_path and os.path.splitext(temp_site_path)[1] == '.beks':
            self.storage_type = "beks"
        else:
            raise ValueError("Could not work out storage type of Empower site with path {}".format(temp_site_path))

        if self.storage_type == 'sql':
            self._path = None
            self._site_locator = site_locator
        else:
            #We may wish to specify the site path, for instance if we are using a non-standard sloc (e.g. for dual site loads)
            if site_locator:
                self._path=os.path.abspath(site_locator)
                self._site_locator=self._path
            else:
                self._path  = os.path.abspath(sloc['empower_site_file'])
                self._site_locator=self._path

            if not os.path.isfile(self._site_locator):
                raise ValueError('Site path "{}" is not valid. Check that backslashes are escaped or the sitepath is prefixed r"" as a raw string'.format(repr(self._site_locator)))


        if work_directory is None:
            self._work_directory = None
        else:
            self._work_directory = os.path.abspath(work_directory)

        if self.storage_type == 'sql':
            self.db_name = self._site_locator.split('|')[3]

        #First set the work directories to the default, then overwrite these with the passed in source locations if we got them
        if self._work_directory is not None and os.path.isdir(self._work_directory):
            pass
        elif self._path:
            self._work_directory             = os.path.join(r'C:\Empower Sites\Temp Work',os.path.splitext(os.path.basename(self._path))[0])
        elif self.storage_type == 'sql':
            self._work_directory             = os.path.join(r'C:\Empower Sites\Temp Work',self.db_name)


        self._empower_dim_import_dir     = os.path.join(self._work_directory,'Empower Dimension Imports')
        self._empower_export_data_dir    = os.path.join(self._work_directory,'Empower Exports')
        self._bulk_load_delta_dir        = os.path.join(self._work_directory,'Bulk Load Deltas')
        self._bulk_load_intermediate_dir = os.path.join(self._work_directory,'Bulk Load Intermediate')
        self._load_processing_dir        = os.path.join(self._work_directory,'Load Processing')
        self._output_data_files_dir      = os.path.join(self._work_directory,'Output Data Files')

        try:
            self._empower_dim_import_dir     = os.path.abspath(sloc['empower_dim_import_dir'])
        except KeyError:
            pass
        try:
            self._empower_export_data_dir    = os.path.abspath(sloc['empower_export_data_dir'])
        except KeyError:
            pass
        try:
            self._bulk_load_delta_dir        = os.path.abspath(sloc['bulk_load_delta_dir'])
        except KeyError:
            pass
        try:
            self._bulk_load_intermediate_dir = os.path.abspath(sloc['bulk_load_intermediate_dir'])
        except KeyError:
            pass
        #self._bulk_load_current_dir      = sloc['bulk_load_current_dir']
        try:
            self._load_processing_dir        = os.path.abspath(sloc['load_processing_dir'])
        except KeyError:
            pass
        try:
            self._output_data_files_dir      = os.path.abspath(sloc['output_data_files_dir'])
        except KeyError:
            pass

        ##Try to make the required directories
        #for dir in [self._empower_dim_import_dir
        #           ,self._empower_export_data_dir
        #           ,self._bulk_load_delta_dir
        #           ,self._bulk_load_intermediate_dir
        #           ,self._load_processing_dir
        #           ,self._output_data_files_dir
        #           ]:
        #
        #    try:
        #        os.makedirs(dir)
        #    except FileExistsError:
        #        pass
        #    except OSError as e:
        #        if e.winerror == 123:
        #            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
        #        else:
        #            raise e

        #With the release of pympx (i.e. the upgrade from obmod) user and pwd are no longer supplied. Secure login must be used instead.
        self._user  = user
        self._pwd   = pwd
        self._encrypted_user = None
        self._encrypted_pwd = None
        
            
        if self.storage_type == 'sql':
            if user is None or pwd is None:
                self._encrypted_user, self._encrypted_pwd, security_dir = llu.get_secure_login(site_path=self.db_name,work_path=self._work_directory,explicit_security_path=self._explicit_security_path,empower_importer_executable=empower_importer_executable )
            else:
                self._encrypted_user, self._encrypted_pwd, security_dir = llu._get_secure_login(site_path=self.db_name,work_path=self._work_directory, user = user, password = pwd,explicit_security_path=self._explicit_security_path,empower_importer_executable=empower_importer_executable )
        else:
            if user is None or pwd is None:
                self._encrypted_user, self._encrypted_pwd, security_dir = llu.get_secure_login(site_path=self._path,work_path=self._work_directory,explicit_security_path=self._explicit_security_path,empower_importer_executable=empower_importer_executable )
            else:
                self._encrypted_user, self._encrypted_pwd, security_dir = llu._get_secure_login(site_path=self._path,work_path=self._work_directory, user = user, password = pwd,explicit_security_path=self._explicit_security_path,empower_importer_executable=empower_importer_executable )

        self.importer_version = _get_importer_version(empower_importer_executable)

        site_details = {}

        try:
            if self.importer_version is not None:
                major_version, minor_version, release, release_number = self.importer_version

                if (major_version == 9 and (release_number >= 855 or minor_version >= 7)) or major_version > 9:
                    #Call using a tuple of strings - this way we can memoize during testing to speed up the test scripts
                    #without circumventing integration testing (as would happen with mocks)
                    site_details = _get_site_details(tuple(self._logon_parameter_importer_commands),empower_importer_executable)

        except Exception:
            #Delete incorrectly created passwords
            if security_dir is not None:
                shutil.rmtree(security_dir)
            print('Error create a site: incorrect supervor name or password')
            raise mpex.EmpowerImporterError('Error create a site: incorrect supervor name or password')

        self.number_of_unit_dimensions=number_of_unit_dimensions
        if self.number_of_unit_dimensions is None:
            try:
                _number_of_unit_dimensions = site_details['Number of unit dimensions']
                _number_of_unit_dimensions = int(_number_of_unit_dimensions)

                self.number_of_unit_dimensions=_number_of_unit_dimensions
            except KeyError:
                pass

        if self.number_of_unit_dimensions is None:
            raise ValueError('Site object was initialised without a number_of_unit_dimensions parameter, and the number of unit dimensions could not be read from the site. Either change your code to call Site() with the parameter number_of_unit_dimensions set or upgrade to a later version of Importer greater than or equal to 9.5..855')

        self.definition = _SiteDefinitionManipulator(site=self)

        self._dimensions = {**{n:Dimension(site=self,index=n) for n in range(self.number_of_unit_dimensions)},**{n:Dimension(site=self,index=n) for n in [8,9,10,11,12]}}

        if self.storage_type == 'sql':
            #Shard on metric for sql sites
            self.storage_dimension_index = 8
            self.elements_per_storage_dimension = 1
        else:

            self.storage_dimension_index=storage_dimension_index
            if self.storage_dimension_index is None:
                try:
                    _storage_dimension_index = site_details['Storage dimension index']
                    _storage_dimension_index = int(_storage_dimension_index)

                    self.storage_dimension_index=_storage_dimension_index
                except KeyError:
                    pass

            self.elements_per_storage_dimension=elements_per_storage_dimension
            if self.elements_per_storage_dimension is None:
                try:
                    _storage_multiplicity = site_details['Storage multiplicity']
                    _storage_multiplicity = int(_storage_multiplicity)

                    self.elements_per_storage_dimension=_storage_multiplicity
                except KeyError:
                    pass

        try:
            _data_locking_dimension_index = site_details['Data locking dimension index']
            try:
                _data_locking_dimension_index = int(_data_locking_dimension_index)
            except ValueError:
                _data_locking_dimension_index = None

            self.data_locking_dimension_index=_data_locking_dimension_index
        except KeyError:
            self.data_locking_dimension_index=None

        try:
            _default_measure = site_details['Default measure']

            self.default_measure=_default_measure
        except KeyError:
            self.default_measure=None

        if self.storage_type == 'sql':
            self._data_files_dir = None
        else:
            self._data_files_dir = os.path.join(os.path.dirname(self._path),'Data Files')

        self._loaders = {}

        self.logging_queue = logging_queue


        #We use a prefix so that dual site loads can specify what site they are loading with the same sloc
        if prefix:
            self.prefix = prefix
        else:
            if self.storage_type == 'sql':
                #Use the first 5 characters of the database name if no prefix was specified
                self.prefix =self.db_name[0:5]
            else:
                #Use the first 5 characters of the .eks file name if no prefix was specified
                self.prefix = os.path.splitext(os.path.basename(self._path))[0][0:5]

        self.empower_importer_executable=os.path.abspath(empower_importer_executable)

        self._viewpoints = _ViewpointsGetter(site=self)



    def site_file(self):
        return self._site_locator
    
    def username(self):
        return self._encrypted_user
    
    def password(self):
        return self._encrypted_pwd
        
    def loader(self,name,source=None,delta=True,identifier_columns=None,empower_period_type = llu.EMPOWER_MONTH_CONSTANT):
        '''Create a named loader for this site.
        Loaders need to be named to ensure the bulk load process works correctly
        '''
        if identifier_columns is None:
            identifier_columns = []

        l=Loader(source              = source
                ,site                = self
                ,logging_queue       = self.logging_queue
                ,delta               = delta
                ,identifier_columns  = identifier_columns
                ,name                = name
                ,empower_period_type = empower_period_type
                )
        self._loaders[name]=l
        return l

    @property
    def loaders(self):
        '''The named loaders for this site.
        A :class:`~pympx.Loader`
        Loaders need to be named to ensure the bulk load process works correctly
        '''
        return self._loaders

    @property
    def dimensions(self):
        '''A dictionary like object of zero indexed dimensions for the site

        >>> #Create a reference the the customer dimension, assuming it is the first dimension in the site `mysite`
        >>> customer = mysite.dimensions[0]
        '''

        return self._dimensions

    @property
    def viewpoints(self):
        '''A dictionary-like object of shortname indexed `Viewpoint`s for this site
        '''

        return self._viewpoints

    @property
    def metric(self):
        '''Gets the metric dimension i.e. .dimensions[9] '''
        return self.dimensions[8]

    @property
    def mode(self):
        '''Gets the mode dimension i.e. .dimensions[9] '''
        return self.dimensions[9]

    @property
    def base(self):
        '''Gets the base dimension i.e. .dimensions[10] '''

        return self.dimensions[10]

    @property
    def time(self):
        '''Gets the time dimension i.e. .dimensions[11] '''
        return self.dimensions[11]

    @property
    def transformation(self):
        '''Gets the transformation dimension i.e. .dimensions[12] '''
        return self.dimensions[12]

    #Utility properties - commonly used pseudonyms
    @property
    def indicator(self):
        ''' A synonym for `.metric`'''
        return self.metric
    @property
    def comparison(self):
        ''' A synonym for `.mode`'''
        return self.mode
    @property
    def currency(self):
        ''' A synonym for `.base`'''
        return self.base

    def housekeep(self):
        '''Housekeep this site, to reduce the size of data files'''

        self.importer.run_commands(['Housekeep'])

        log.info('Site {} housekept'.format(self._path))

    @property
    def importer(self):
        '''Get the Importer object for this site. See Importer api documentation for how to use the returned Importer object'''

        return Importer(self)

    @property
    def _logon_parameter_importer_commands(self):
        '''Return the standard '''
        if self._encrypted_user is None:
            return ['set-parameter user='     + self._user
                   ,'set-parameter password=' + self._pwd
                   ,'set-parameter site='     + self._site_locator
                   ]
        else:
            return ['set-encrypted-parameter user='     + self._encrypted_user.decode('utf8')
                   ,'set-encrypted-parameter password=' + self._encrypted_pwd .decode('utf8')
                   ,'set-parameter site='               + self._site_locator
                   ]


class Importer(object):

    def __init__(self,site):
        self.site = site

    @property
    def version(self):
        '''Get the version of imported as a list of 4 integers. major, minor, release and build'''

        return self.site.importer_version

    @property
    def executable(self):
        return self.site.empower_importer_executable

    def yield_commands(self,command_list,header = None, split_on_tab = True,return_dicts = True, force_generator = False, append_output_command = True):
        '''Run a list of importer commands on the attached site
        Use ${site}, ${user} and ${password} placeholders in commands, which will be filled with the site location and encrypted logon information from the Site

        :param command_list: commands you want to run. Don't include the batch commands SiteFile, User or Password, because these are included
        :param header: use a list of header columns - by default run_commands uses the first record in the output as a header
        :param split_on_tab: split the output by the tab character, returning lists or dictionaries
        :param return_dicts : return a dictionary with the keys as the header
        :param force_generator: a python generator object is created if the final command is 'output', or if this flag is set to True

        :return: a generator object that loops over the output as it is streamed by the Importer executable
        '''

        if command_list == []:
            return

        if append_output_command:
            output_found = False
            for command in command_list:
                if command.strip().lower() == 'output':
                    output_found = True
                    break
            if not output_found:
                command_list.append('output')

        command_list = ['set-encrypted-parameter unquoted_user='     + self.site._encrypted_user.decode('utf8') + ''
                       ,'set-encrypted-parameter unquoted_password=' + self.site._encrypted_pwd .decode('utf8') + ''
                       ,'set-parameter site="'                       + self.site._site_locator + '"'
                       ,'set-parameter user="${unquoted_user}"'
                       ,'set-parameter password="${unquoted_password}"'
                       ,'SiteFile ${site}'
                       ,'User ${user}'
                       ,'Password ${password}'
                       ] + command_list


        log.verbose('Started running importer commands')

        n = None

        for n, line in enumerate(llu.run_and_yield_single_output_importer_commands(command_list
                                                                    ,empower_importer_executable=self.site.empower_importer_executable
                                                                    )):
            if n == 0 and return_dicts and header is None:
                if split_on_tab:
                    header = line.split('\t')
                else:
                    header = line
                continue

            if return_dicts:
                if split_on_tab:
                    yield collections.OrderedDict(zip(header,line.split('\t')))
                else:
                    yield {header:line}
            else:
                if split_on_tab:
                    yield line.split('\t')
                else:
                    yield line

        if n == 0 and line != '':
            if len(line) > 20:
                printed_line = line[:20] + '... <followed by {} characters>'.format(len(line) - 20)
            else:
                printed_line = line

            log.warning('Empower importer returned "{}", but this was not displayed because it was interpreted as a header. To read this line set parameter return_dicts = False or set the header parameter in .run_commands() or .yield_commands()'.format(printed_line))

        log.verbose('Finished running importer commands')

    def run_commands(self,command_list,header = None,split_on_tab = True,return_dicts = True, force_generator = False, append_output_command = False):
        '''Run a list of importer commands on the attached site
        Use ${site}, ${user} and ${password} placeholders in commands, which will be filled with the site location and encrypted logon information
        If the final importer command is the 'output' command, then this function will return a generator object that can be looped over

        :param command_list: commands you want to run. Don't include the batch commands SiteFile, User or Password, because these are included
        :param header: use a list of header columns - by default run_commands uses the first record in the output as a header
        :param split_on_tab: split the output by the tab character, returning lists or dictionaries
        :param return_dicts : return a dictionary with the keys as the header
        '''

        return [l for l in self.yield_commands(command_list=command_list,header=header,split_on_tab = split_on_tab,return_dicts = return_dicts, force_generator = True,append_output_command=append_output_command)]

class _SiteDefinitionManipulator(object):
    '''A helper object that allows us to keep site definition manipulation off to one side.
    Site definition manipulation processes are essentially DDL like - adding fields to a dimension in Empower is like adding columns to a table in a database
    Sites can still be defined in their sub-objects. E.g. You can add a field to a Dimension.fields
    However synchronising the definition is done in one place.
    That way, if you didn't mean to change the definition, you won't accidentally do so, but if you did mean to change the definition then all of your changes can be synchronised at once
    The definition object is also used to get textual representations of the site
    '''

    def __init__(self,site):

        self.site = site

    def synchronise(self):
        '''Bring the Empower definition up-to-date with our Site definition, applying all definition changes'''

        self.synchronise_viewpoint_definitions()


    def synchronise_viewpoint_definitions(self):
        '''Bring the Empower Viewpoints definition up-to-date with our Site definition, applying all definition changes'''
        
        self.synchronise_dimension_definitions()

        #TODO - run the viewpoints synchronise code
        pass

    def synchronise_dimension_definitions(self):
        '''Bring the Empower Dimensions definition up-to-date with our Site definition, applying all definition changes'''

        self.synchronise_field_definitions()
        for dimension in self.site.dimensions.values():
            self.synchronise_structure_definitions(dimension=dimension)


    def synchronise_structure_definitions(self,dimension):
        '''Bring the Empower Structures definition up-to-date with our Site definition, applying all definition changes'''

        #TODO - run the structures synchronise code
        structures_to_create = []

        debug = dimension.site._debug

        #JAT 2019-10-03
        #Only synchronise if the structure has been read. Structure wouldn't have been added if not read
        #This saves us doing a full structure values load for untouched dimensions
        if dimension.structures._structures_read:
            for structure in dimension.structures.values():
                if not structure._exists_in_empower:
                    structures_to_create.append(structure)

        if len(structures_to_create) > 0:

            if debug:
                for dir in [self._empower_dim_import_dir]:

                    try:
                        os.makedirs(dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if e.winerror == 123:
                            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                        else:
                            raise e

                structure_metadata_filepath = os.path.join(self.site._empower_dim_import_dir,'Structures_{}.tsv'.format(dimension.index))
            else:
                structure_metadata_filepath = r'\\.\pipe\{}'.format(uuid.uuid4())

            #Check version of Empower
            major_version, minor_version, release, release_number = self.site.importer_version
            if (major_version == 9 and (release_number >= 1943 or minor_version >=7)) or major_version > 9:
                if self.site._encrypted_user is None:
                    raise mpex.EmpowerImporterVersionError('After upgrading to 9.5.18.1724 or beyond, you must upgrade your python code to use encrypted passwords in pympx.Site objects')

                log.info('Creating new Structure definitions in Empower site '+self.site._site_locator)

                def _yield_new_structures_strings(structures_to_create):
                    #Switch description for a concatenated key - we will be able to grab the shortname and link correct elements in order to update fields
                    #Write the tab separated header
                    yield 'Dimension\tLongname\tShortname\tDescription\n'

                    #Write data for all of the new fields to the file
                    for n, new_structure in enumerate(structures_to_create):

                        yield new_structure.dimension.longname
                        yield '\t'

                        #Oddly, longname is the key here, not short name
                        yield new_structure.longname

                        yield '\t'

                        if new_structure.shortname is not None:
                            yield new_structure.shortname
                        yield '\t'


                        if new_structure.description is not None:
                            yield new_structure.description
                        yield '\n'

                        log.info('Creating new Structure definition: '+str(new_structure.longname))

                command_list = self.site._logon_parameter_importer_commands + \
                               ['load-file-tsv "'                   + structure_metadata_filepath + '"'
                               ,'empower-import-structures -has-header -upsert "${site}" "${user}" "${password}"'
                               ]

                #In debug mode write the data into a tsv file and read it with Importer, putting the elements into Empower
                if debug:
                    with open(structure_metadata_filepath,'w') as new_structures_file:
                        for s in _yield_new_structures_strings(structures_to_create):
                            new_structures_file.write(s)

                    llu.run_single_output_importer_commands(command_list, empower_importer_executable=self.site.empower_importer_executable)

                else:
                    #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
                    #structure_metadata_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
                    #The merry dance means starting empower, referencing the pipe, opening the pipe before empower is properly started
                    #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
                    #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
                    #before we have created it. But we will block on our side until Importer has connected
                    try:
                        proc = None
                        proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=self.site.empower_importer_executable)
                        with llu.outbound_pipe(structure_metadata_filepath) as pipe:

                            for s in _yield_new_structures_strings(structures_to_create):
                                win32file.WriteFile(pipe, str.encode(s))

                            log.debug("Pipe {} finished writing".format(structure_metadata_filepath))

                    finally:

                        #Check if Importer returned an error and raise it as a python if it did
                        llu.complete_no_output_importer_process(proc)

                log.info('New structures created in Empower site '+self.site._site_locator)

                for structure in structures_to_create:
                    structure._exists_in_empower = True

            else:
                raise mpex.EmpowerImporterVersionError('You must upgrade to Empower Importer 9.5.18.1943 or beyond and use encrypted passwords in order to create new fields in Empower')


    def synchronise_field_definitions(self):
        '''Bring the Empower dimension fields definition up-to-date with our Site definition, applying all definition changes'''

        #Create new fields in empower
        #Do all dimensions at once, for speed

        debug = self.site._debug

        new_fields = []
        new_fields_by_index = {}
        for dimension in self.site.dimensions.values():
            new_fields_by_index[dimension.index] = []
            #JAT 2019-10-03 Check that there are any fields at all using private members - otherwise dimension.fields does an element load
            if len(dimension._fields._fields) > 0:
                for field_name in dimension.fields._new_field_names:
                    field = dimension.fields[field_name]
                    if field.longname is None:
                        raise mpex.MPXError('Cannot create field without a longname. Dimension: {}, shortname: {}, field_name: {}'.format(dimension.longname,field.shortname,field_name))
                    new_fields.append({'Dimension':dimension.longname, 'Longname':field.longname, 'Shortname': field.shortname,'Description':field.description})
                    new_fields_by_index[dimension.index] += [field.shortname]

        #Only spend time logging in to Empower if there are new fields to create
        if len(new_fields) > 0:

            if debug:
                for dir in [self.site._empower_dim_import_dir]:

                    try:
                        os.makedirs(dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if e.winerror == 123:
                            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                        else:
                            raise e
                field_metadata_filepath = os.path.join(self.site._empower_dim_import_dir,'Fields.tsv')
            else:
                field_metadata_filepath = r'\\.\pipe\{}'.format(uuid.uuid4())

            #Check version of Empower
            major_version, minor_version, release, release_number = self.site.importer_version
            if ((major_version == 9 and (release_number >= 1943 or minor_version >=7)) or major_version > 9) and self.site._encrypted_user is not None:

                log.info('Creating new Field definitions in Empower site '+self.site._site_locator)

                def _yield_field_metadata_strings(new_fields):
                    #Write the tab separated header
                    yield 'Dimension\tLongname\tShortname\tDescription\n'

                    #Write data for all of the new fields to the file
                    for n, new_field in enumerate(new_fields):

                        yield new_field['Dimension']
                        yield '\t'

                        #Oddly, longname is the key here, not short name
                        yield new_field['Longname']
                        yield '\t'

                        if new_field['Shortname'] is not None:
                            yield new_field['Shortname']
                        yield '\t'


                        if new_field['Description'] is not None:
                            yield new_field['Description']
                        yield '\n'

                        log.info('Creating new Field definition: '+str(new_field))

                command_list = self.site._logon_parameter_importer_commands + \
                               ['load-file-tsv "'                   + field_metadata_filepath + '"'
                               ,'empower-import-field-elements -has-header -upsert "${site}" "${user}" "${password}"'
                               ]
                #Switch description for a concatenated key - we will be able to grab the shortname and link correct elements in order to update fields
                #In debug mode write the data into a tsv file and read it with Importer, putting the elements into Empower
                if debug:
                    with open(field_metadata_filepath,'w') as new_field_file:
                        for s in _yield_field_metadata_strings(new_fields):
                            new_field_file.write(s)

                    llu.run_single_output_importer_commands(command_list, empower_importer_executable=self.site.empower_importer_executable)

                else:
                    #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
                    #field_metadata_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
                    #The merry dance means starting empower, referencing the pipe, opening the pipe before empower is properly started
                    #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
                    #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
                    #before we have created it. But we will block on our side until Importer has connected
                    proc = None
                    try:
                        proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=self.site.empower_importer_executable)
                        with llu.outbound_pipe(field_metadata_filepath) as pipe:
                            ## From 9.8 onwards write the Windows Byte Order Marker (BOM)
                            #if ((major_version == 9 and minor_version >=8) or major_version > 9):
                            #    win32file.WriteFile(pipe, "".encode("utf-8-sig"))
                            print('new_fields',new_fields)
                            for s in _yield_field_metadata_strings(new_fields):
                                win32file.WriteFile(pipe, s.encode())

                            log.debug("Pipe {} finished writing".format(field_metadata_filepath))

                    finally:

                        #Check if Importer returned an error and raise it as a python error if it did
                        llu.complete_no_output_importer_process(proc)

                log.info('New fields created in Empower site '+self.site._site_locator)
                for dim_index, field_shortnames in new_fields_by_index.items():
                    for sn in field_shortnames:
                        if sn is not None:
                            self.site.dimensions[dim_index].fields._add_field_name(sn)
            else:
                raise mpex.EmpowerImporterVersionError('You must upgrade to Empower Importer 9.5.18.1943 or beyond and use encrypted passwords in order to create new fields in Empower')

    #todo
    #to/from JSON
    #to/from YAML

class _StructureGetter(object):
    '''Does a bit of magic to allow Dimensions to have a structures object which behaves like a lazy loading dictionary'''
    def __init__(self,dimension, empower_importer_executable=llu.EMPOWER_IMPORTER_EXECUTABLE):
        self.dimension=dimension
        self.empower_importer_executable = empower_importer_executable
        self._structures={}

        self.__structures_read   = False
        self.__structures_synced = True

        self._encoding_list = ['utf8','cp1252','latin1']

    def set_preferred_encoding_list(self,item):
        '''Set a list of encodings that will be tried when reading a structure from Empower. The encodings will be tried in the order presented in the list

        :param item: A list of encodings that will be tried. The default list is ['utf8','cp1252','latin1']
        '''
        if isinstance(item,str):
            self._encoding_list = [item]
        else:
            self._encoding_list = list(item)

        return self

    #Set these as properties for debugging - when all is working make them normal attributes again
    @property
    def _structures_read(self):
        #log.warning('_structures_read returning {} for {}'.format(self.__structures_read,id(self)))
        return self.__structures_read

    @_structures_read.setter
    def _structures_read(self,val):
        #log.warning('_structures_read set to {} for {}'.format(val,id(self)))
        self.__structures_read = val

    @property
    def _structures_synced(self):
        return self.__structures_synced

    @_structures_synced.setter
    def _structures_synced(self,val):
        #log.warning('_structures_synced set to {}'.format(val))
        self.__structures_synced = val

    #Unlike a standard dictionary which returns keys in iter, return values (since that's what we usually want)
    def __iter__(self):
        self._iterator = iter(self.values())
        return self

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self,item):
        #Load the Structures if we haven't already
        try:
            if not self._structures_read:
                self._load_structures()
        except mpex.EmpowerImporterVersionError as e:
            #If there is an Importer Version Error, just load the particular structure
            try:
                s = self._structures[item]
                if not s._hierarchies_read:
                    #log.info('_load_structure 465')
                    self._load_structure(item,old_structure = self._structures,encoding_list=self._encoding_list)
                    self._structures[item].dimension=self.dimension

            except KeyError:
                self._load_structure(item,encoding_list=self._encoding_list)
                #log.info('_load_structure 471')
                self._structures[item].dimension=self.dimension

        return self._structures[item]

    def __setitem__(self,key,item):

        #TODO - allow the adding of strings, by creating a new structure
        assert isinstance(item,Structure)
        assert isinstance(key,str)

        if item.dimension != self.dimension:
            item.dimension = self.dimension

        #If the item is already in the dictionary, swap it out for the new one
        #otherwise add it on the end
        self._structures[key] = item
        #We are clearly no longer synchronised with empower
        self.__structures_synced = False

    #Define what happens when we call +=
    #We want to append
    def __iadd__(self,other):
        assert isinstance(other,Structure)
        #add the new structure into the dictionary using __setitem__
        self[other.shortname] = other
        return self

    #Define what happens when we call |=
    #We want to append if it is not there already
    def __ior__(self,other):
        assert isinstance(other,Structure)
        #add the new structure into the dictionary using __setitem__
        try:
            self[other.shortname]
        except KeyError:
            self[other.shortname] = other
        return self

    def _load_structure(self,item,old_structure = None,encoding_list=None):
        #log.info('Reading Structure '+str(item)+' for dimension '+str(self.dimension.index))
        if old_structure is not None:
            old_structure._hierarchies_read = True

        if encoding_list is None:
            encoding_list = self._encoding_list

        for n, encoding in enumerate(encoding_list):
            try:
                self._structures[item] = _read_structure_from_site(dimension     = self.dimension
                                                                  ,shortname     = item
                                                                  ,encoding      = encoding
                                                                  ,old_structure = old_structure
                                                                  )
                break
            except UnicodeDecodeError:
                if n > len(encoding_list):
                    raise UnicodeDecodeError('Could not read structure {} with any of the encodings {}'.format(item,encoding_list))
                else:
                    log.warning('Slow structure read {} was caused by trying {}.'.format(item,' before '.join(encoding_list[:n+1])))

        self._structures[item].dimension = self.dimension

    def values(self):
        try:
            if not self._structures_read:
                self._load_structures()
        except mpex.EmpowerImporterVersionError as e:
            raise AttributeError('.structures behaves like a dictionary but does not have a values() method because we cannot load all of the structures for a given dimension from Empower with the Importer version you are using.\n You will need to call each item separately. e.g. site.dimensions[0].structures["SPAM"]. '+str(e))

        return self._structures.values()

    def items(self):
        try:
            if not self._structures_read:
                self._load_structures()
        except mpex.EmpowerImporterVersionError as e:
            raise AttributeError('.structures behaves like a dictionary but does not have a items() method because we cannot load all of the structures for a given dimension from Empower with the Importer version you are using.\n You will need to call each item separately. e.g. site.dimensions[0].structures["SPAM"]. '+str(e))

        return self._structures.items()

    def keys(self):
        try:
            if not self._structures_read:
                self._load_structures()
        except mpex.EmpowerImporterVersionError as e:
            raise AttributeError('.structures behaves like a dictionary but does not have a keys() method because we cannot load all of the structures for a given dimension from Empower with the Importer version you are using.\n You will need to call each item separately. e.g. site.dimensions[0].structures["SPAM"]. '+str(e))

        return self._structures.keys()

    def __len__(self):
        try:
            if not self._structures_read:
                self._load_structures()
        except mpex.EmpowerImporterVersionError as e:
            raise AttributeError('.structures behaves like a dictionary but does not have a keys() method because we cannot load all of the structures for a given dimension from Empower with the Importer version you are using.\n You will need to call each item separately. e.g. site.dimensions[0].structures["SPAM"]. '+str(e))

        return len(self._structures)

    def _load_structures(self):
        self._structures_read = True
        try:
            log.verbose('Reading Structures for dimension '+str(self.dimension.index))
            major_version, minor_version, release, release_number = self.dimension.site.importer_version

            if (major_version == 9 and (release_number >= 1894 or minor_version >=7)) or major_version > 9:

                self._structures = _create_empower_dimension_shortname_structure_dict(dimension      = self.dimension
                                                                                     ,old_structures = self._structures.values()
                                                                                     )

            else:
                raise mpex.EmpowerImporterVersionError('Functionality not available in this Empower Importer version {} need at least {}'.format('.'.join([str(v) for v in self.dimension.site.importer_version]), '9.5.17.1894'))
        except Exception:
            self._structures_read = False
            raise


    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self)) )

class _HierarchiesGetter(object):
    '''Does a bit of magic to allow Structures to have hierarchies (i.e. root structures) appear like a dictionary'''
    def __init__(self,structure):
        self.structure=structure
        self.clear()

    #Unlike a standard dictionary which returns keys in iter, return values (since that's what we usually want)
    def __iter__(self):
        if not self.structure._hierarchies_read:
            #log.info('_load_structure 602')
            self.structure.dimension.structures._load_structure(self.structure.shortcode)
        self._iterator = iter(self._root_elements.values())
        return self

    def __next__(self):
        return next(self._iterator)


    def __getitem__(self,item):
        #if not self.structure._hierarchies_read:
        #    self._load_structure(item)
        #    self._structures[item].dimension=self.dimension
        hier = self.structure.get_root_element(item)
        if hier is None:
            raise KeyError('StructureElement with shortcode {} is not in hierarchies (i.e. root elements) of Structure {}'.format(item,self.structure.shortcode))
        return hier

    def __setitem__(self, key, item):
        self.append(item)

    def clear(self):
        self._root_elements=collections.OrderedDict()
        #If we've cleared it, we don't need to read it, we'll only accidentally overwrite on the first read!
        self.structure._hierarchies_read = True

    def append(self, item):



        _item_is_structure_element = False
        _item_is_element = False
        _item_is_shortcode = False

        if isinstance(item, str):
            _item_is_shortcode = True
        else:

            try:
                item.is_root
                _item_is_structure_element = True
            except AttributeError:
                try:
                    item._measure
                    _item_is_element = True
                except AttributeError:
                    #if the item is an iterable (and isn't a string), append all items to self
                    #This way we can add a list of things to a hierarchy
                    #try:
                    for sub_item in item:
                        self.append(sub_item)
                    return
                    ##We'll get a TypeError if the object is not iterable
                    #except TypeError:
                    #    pass

        if _item_is_structure_element:
            _structure_element = item
            if _structure_element.structure is None:
                #We are probably appending a copied hierarchy - set the structure throughout the tree
                _structure_element.structure = self.structure
                for ch in _structure_element.walk():
                    ch.structure = self.structure

        elif _item_is_element:
            try:
                _structure_element = self.structure.hierarchies[item.shortcode]
                #print(item.shortcode, _structure_element)
            except KeyError:
                _structure_element = StructureElement(structure=self.structure,element=item,is_root=True)

        elif _item_is_shortcode:
            try:
                _structure_element = self.structure.hierarchies[item]
            except KeyError:
                _element = self.structure.dimension.elements[item]
                _structure_element = StructureElement(structure=self.structure,element=_element,is_root=True)

        if not _structure_element.element.mastered:
            raise AttributeError('Cannot create a hierarchy with un-synchronised Element {} use Dimension.elements.synchronise() before creating the hierarchy')


        _structure_element.is_root = True

        try:
            self._root_elements.pop(_structure_element.shortcode)
        except KeyError:
            pass

        self._root_elements[_structure_element.shortcode] = _structure_element

    #Define what happens when we call +=
    #We want to append
    def __iadd__(self,other):
        self.append(item=other)
        return self

    #Define what happens when we call |=
    #We want to append if it doesn't exist already
    def __ior__(self,other):
        shortname = None
        if str(other) == other:
            shortname = other
        else:
            try:
                shortname = other.shortname
            except AttributeError:
                try:
                    for el in other:
                        self |= el
                    return self
                except AttributeError:
                    raise TypeError("unsupported operand types(s) for |=: '_HierarchiesGetter' and '{}'".format(type(other)))

        try:
            self[shortname]
        except KeyError:
            self.append(item=other)
        return self


    def keys(self):
        if not self.structure._hierarchies_read:
            self.structure.dimension.structures._load_structure(self.structure.shortcode,old_structure = self.structure)

        return self._root_elements.keys()

    def items(self):
        if not self.structure._hierarchies_read:
            self.structure.dimension.structures._load_structure(self.structure.shortcode,old_structure = self.structure)

        return self._root_elements.items()

    def values(self):
        if not self.structure._hierarchies_read:
            self.structure.dimension.structures._load_structure(self.structure.shortcode,old_structure = self.structure)

        return self._root_elements.values()

    def __len__(self):

        return len(self._root_elements)

    def __str__(self):

        return '{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self._root_elements.items()]) + '}'


    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self)) )

    #TODO
    # __add__
    # and
    # __radd__

class StructureElementChildren(object):
    '''The object returned by a call to StructureElement.children
    Does a bit of magic to allow StructureElements.children to appear like a dictionary, only with extra special functions like += '''

    def __init__(self,structure_element):
        '''It is unlikely that a user of PyMPX would want to initialise a StructureElementChildren object directly.
        This object is usually returned by calling e.g. my_structure_element.children

        :param structure_element: The StructureElement that the children will belong to
        '''

        self._structure_element          = structure_element

    #The StructureElementChildren has the unfortunate property of behaving like both a list iterator and a dictionary
    #It's a bit of a mess
    def __iter__(self):
        self._iterator = iter(self.values())
        return self

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self,key):
        for n,el in enumerate(self._structure_element._child_structure_elements[::-1]):
            if el.shortname == key:
                return el

        raise KeyError('StructureElement {} does not contain a child with shortname {}'.format(self._structure_element.path,key))

    def __setitem__(self, key, item):
        '''Set the final element in the children with key shortcode to the item value
        If the item element is not in the children then add it'''
        if not isinstance(item,StructureElement):
            raise ValueError("StructureElement children can only be set using the dictionary syntax to another StructureElement. You called {}['{}'] = {}, attempting to set the child to an object of type {}".format(repr(self),repr(key),repr(item),type(item)))

        if not key == item.shortname:
            raise ValueError("StructureElement children can only be set using the dictionary syntax to a StructureElement with the same shortcode as the key. You called {}['{}'] = {}, attempting to set the child to a StructureElement with shortname {}".format(repr(self),repr(key),repr(item),item.shortname))


        #If the item is already in the dictionary, swap it out for the new one
        #otherwise add it on the end

        element_found = False
        for n,el in enumerate(self._structure_element._child_structure_elements[::-1]):
            if el.shortname == key:
                self._structure_element._child_structure_elements[-(1+n)] = item
                element_found = True
                break

        if not element_found:
            self.append(item)

    def append(self, item, merge = False):
        '''Add a child StructureElement to the children.

        :param item: Specification of the child StructureElement to eb added. Valid valeus are a StructureElement, an Element or a shortname string, refering to an Element in the Dimension that this Structure belongs to.
        '''

        _item_is_structure_element = False
        _item_is_element = False
        _item_is_shortcode = False

        if isinstance(item, str):
            _item_is_shortcode = True
        else:

            #if the item is an iterable (and isn't a string), append all items to self
            #This way we can add a list of things to a hierarchy
            items = None
            try:
                #Try treating the item as a list (now that we know it is not a string)
                #And appending each of the members in turn
                items = [el for el in item]
            except TypeError:
                pass

            if items is not None:
                for el in item:
                    self.append(el,merge=merge)
                #Return once we've appended every element
                return

            #If we got this far then item is not a string (i.e. shortcode) or list
            try:
                item.is_root
                _item_is_structure_element = True
            except AttributeError:
                try:
                    item._measure
                    _item_is_element = True
                except AttributeError:
                    #We'll raise the error as a TypeError further down
                    pass

        if _item_is_structure_element:
            _child_structure_element = item

            #Structure elements could have been cut or (implicitly) copied
            #Cut elements will not have a parent, and want to be set to have this structure element parent
            #Implicitly copied elements will have a parent, and need to be explicitly copied
            if _child_structure_element._parent_structure_element is None:
                _child_structure_element.structure = self._structure_element.structure
            elif _child_structure_element._parent_structure_element == self._structure_element:
                pass
            else:
                #Do the explicit copy
                _child_structure_element = item.copy()

            if _child_structure_element.structure is None:
                _child_structure_element.structure = self._structure_element.structure

        elif _item_is_element:
            _child_structure_element = StructureElement( structure=self._structure_element.structure,element=item,is_root=False)
        elif _item_is_shortcode:
            _element = self._structure_element.dimension.elements[item]
            _child_structure_element = StructureElement(structure=self._structure_element.structure,element=_element,is_root=False)
        else:
            raise TypeError('Cannot append item of unknown type: {}'.format(repr(item)))

        if not _child_structure_element.element.mastered:
            raise AttributeError('Cannot create a hierarchy with un-synchronised Element {} use Dimension.elements.synchronise() before creating the hierarchy')

        #If we are adding merge elements, return ifwe find an identical element
        if merge:
            try:
                self[_child_structure_element.shortcode]
                return
            except KeyError:
                pass

        self._structure_element._add_child(_child_structure_element)

    def order_by_shortcode_list(self,shortcode_list):
        '''Order the children using a list of shortcodes. Because Elements can come and go over time, shortnames in the list that are not children are ignored, and any shortnames of children that are not mentioned go to the end of the list in their original order.'''
        _initial_children = self._structure_element._child_structure_elements.copy()
        _initial_positions_by_shortcode = {}

        #Create a list of positions for each shortcode
        for n, se in enumerate(self._structure_element._child_structure_elements):
            try:
                pos_list = _initial_positions_by_shortcode[se.shortcode]
                pos_list.append(n)
            except KeyError:
                _initial_positions_by_shortcode[se.shortcode] = [n]

        #Clear out children
        self.clear()

        all_moved_shortcodes = {}
        #Order by the shortcodes
        for shortcode in shortcode_list:
            #Record shortcodes of moved elements, so we can work out (quickly) what didn't move
            all_moved_shortcodes[shortcode] = shortcode

            try:
                _child_structure_element_indices = _initial_positions_by_shortcode[shortcode]
                for ind in _child_structure_element_indices:
                    se = _initial_children[ind]
                    self._structure_element._add_child(se)

            except KeyError:
                continue


        #Add anything left in the original children
        for _child_structure_element in _initial_children:
            #See if the initial child has been orderd by the shortcode, or if it is one of the leftovers
            #leftovers will be added back in their original order, after the ordered elements
            try:
                all_moved_shortcodes[_child_structure_element.shortname]
            except KeyError:
                #The child has not been moved in during the ordering process, so add it in now
                self._structure_element._add_child(_child_structure_element)

    def cut(self):
        '''
        Remove the children from the parent and return them as a list.
        This function is useful when we are about to 'paste' the children into another spot
        '''
        #We need to detach each child from the parent structure element, clear ourself and return a new StructureElementChildren
        #This way, when pasted in, the children will remain the same entities, but the new parent StructureElement will not be pointing
        #to some other children

        retval = [ch for ch in self.values()]

        #Clear children out of self
        self.clear()

        return retval

    #Define what happens when we call +=
    #We want to append
    def __iadd__(self,other):
        self.append(item=other,merge=False)
        return self

    #Define what happens when we call |=
    #We want to append unique items
    def __ior__(self,other):
        self.append(item=other,merge=True)
        return self

    #Define what happens when we call -=
    #We want to remove the final child with that key
    def __isub__(self,other):
        self._structure_element.remove_child(other)
        return self


    def keys(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()
        for el in self._structure_element._child_structure_elements:
            yield el.shortname

    def items(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()
        for el in self._structure_element._child_structure_elements:
            yield el.shortname, el

    def values(self):
        #if not self.dimension._elements_read:
         #   self._load_elements()
        for el in self._structure_element._child_structure_elements:
            yield el



    def __len__(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return len(self._structure_element._child_structure_elements)

    def __str__(self):
        return '[' + '\n'.join([ v.shortname for  v in self._structure_element._child_structure_elements]) + ']'


    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self)))

    def clear(self):
        '''Remove all of the children from the parent'''
        self._structure_element.remove_children()

class _StructureElementDescendantsGetter(object):
    '''Does a bit of magic to allow StructureElements.descendants to appear like a dictionary, only with extra special functions like += '''
    def __init__(self,structure_element):
        self._structure_element          = structure_element

    #The _StructureElementDescendantsGetter has the unfortunate property of behaving like both a list iterator and a dictionary
    #It's a bit of a mess
    def __iter__(self):
        self._iterator = iter(self._structure_element.walk())
        return self

    def __next__(self):
        return next(self._iterator)

    def _normalise_key(self,key):
        #The important part of descendants is that you can give a composite key, either as a string or as a list
        #if key is a string then we want to split it (on forward slashes) and create a list of shortcodes
        if isinstance(key,str):
            temp_key = key.split('/')
            key = []
            for k in temp_key:
                k = k.strip()
                if len(k)>30:
                    raise ValueError('Key contains a shortcode longer than 30 characters :'+str(k))
                else:
                    key.append(k)
        else:
            pass

        return key

    #TODO - change this to call get elements on a single shortcode key which is not at root
    #Change this to search for first element using get_elements and then match the rest of the tree
    def __getitem__(self,key):
        #The important part of descendants is that you can give a composite key, either as a string or as a list

        key = self._normalise_key(key)

        #assume we can iterate over the key passed in or the key created from the string
        #descend the hierarchy until we find the element
        retval = self._structure_element
        if len(key) > 0:
            for k in key:
                retval = retval.children[k]

        return retval

    def __setitem__(self, key, item):
        assert isinstance(item,StructureElement)

        key = self._normalise_key(key)

        looked_up_item = self[key]

        assert isinstance(looked_up_item,StructureElement)

        if looked_up_item.is_root:
            #Set the hierarchy to the correct item
            looked_up_item.structure.hierarchies[looked_up_item.shortcode] = item
        else:
            looked_up_item.parent.children[looked_up_item.shortcode] = item

    def append(self, item):
        self._structure_element.children.append(item)

    #JAT 2018-08-10: Not really sure how this would be coded - maybe by returning ancestors while walking
    #def keys(self):
    #    #if not self.dimension._elements_read:
    #    #    self._load_elements()
    #
    #    return self._structure_element._child_structure_elements.keys()
    #
    #def items(self):
    #    #if not self.dimension._elements_read:
    #    #    self._load_elements()
    #
    #    return self._structure_element._child_structure_elements.items()

    #IS this right? are we really walking?
    def values(self):
        #if not self.dimension._elements_read:
         #   self._load_elements()

        return self._structure_element.walk()

    #def __len__(self):
    #    #if not self.dimension._elements_read:
    #    #    self._load_elements()
    #
    #    return len(self._structure_element._child_structure_elements)

    #def __str__(self):
    #    return str(self._structure_element._child_structure_elements)

    def clear(self):
        '''Remove all of the children from the StructureElement whose descendants are being returned.'''
        self._structure_element.remove_children()

class _StructureDescendantsGetter(object):
    '''Does a bit of magic to allow Structure.descendants to appear like a dictionary, only with extra special functions like += '''
    def __init__(self,structure):
        self._structure          = structure

    #The _StructureElementDescendantsGetter has the unfortunate property of behaving like both a list iterator and a dictionary
    #It's a bit of a mess
    def __iter__(self):
        self._iterator = iter(self._structure.walk())
        return self

    def __next__(self):
        return next(self._iterator)

    def _normalise_key(self,key):
        #The important part of descendants is that you can give a composite key, either as a string or as a list
        #if key is a string then we want to split it (on forward slash) and create a list of shortcodes
        if isinstance(key,str):
            temp_key = key.split('/')
            key = []
            for k in temp_key:
                k = k.strip()
                if len(k)>10:
                    raise ValueError('Key contains a shortcode longer than 10 characters :'+str(k)+' Make sure key is separated by forwards slashes (/)')
                else:
                    key.append(k)
        else:
            pass

        return key

    def __getitem__(self,key):
        #The important part of descendants is that you can give a composite key, either as a string or as a list

        key = self._normalise_key(key)

        #assume we can iterate over the key passed in or the key created from the string
        #descend the hierarchy until we find the element
        hierarchy = self._structure.hierarchies[key[0]]

        if len(key) > 1:
            return hierarchy.descendants[key[1:]]
        else:
            return hierarchy

    def __setitem__(self, key, item):
        assert isinstance(item,StructureElement)

        key = self._normalise_key(key)

        looked_up_item = self[key]

        if isinstance(looked_up_item, Structure):
            raise ValueError('Cannot set a structure using .descendants')
        elif isinstance(looked_up_item, StructureElement):
            #Check if we are setting a hierarchy (root structure element) or further down
            if len(key)==2:
                #Set the hierarchy to the correct item
                self._structure.hierarchies[looked_up_item.shortcode] = item
            else:
                looked_up_item.parent.children[looked_up_item.shortcode] = item

    #def append(self, item):
    #    self._structure.hierarchies(item)

    #JAT 2018-08-10: Not really sure how this would be coded - maybe by returning ancestors while walking
    #def keys(self):
    #    #if not self.dimension._elements_read:
    #    #    self._load_elements()
    #
    #    return self._structure_element._child_structure_elements.keys()
    #
    #def items(self):
    #    #if not self.dimension._elements_read:
    #    #    self._load_elements()
    #
    #    return self._structure_element._child_structure_elements.items()

    #IS this right? are we really walking?
    def values(self):

        return self._structure.walk()

    #def __len__(self):
    #    #if not self.dimension._elements_read:
    #    #    self._load_elements()
    #
    #    return len(self._structure_element._child_structure_elements)

    #def __str__(self):
    #    return str(self._structure_element._child_structure_elements)

    def clear(self):
        self._structure.hierarchies.clear()

class _ElementsGetter(object):
    '''Does a bit of magic to allow Dimensions to have a elements object which behaves like a lazy loading dictionary'''
    def __init__(self,dimension, empower_importer_executable=llu.EMPOWER_IMPORTER_EXECUTABLE):
        self.dimension=dimension
        self.empower_importer_executable = empower_importer_executable
        self._elements={}
        self._elements_without_shortnames = []

        self.__elements_read = False
        self.__elements_synced = True
        self.__element_dataframe = None

        self.__security_edited = False
        self._security_read = False

    #Set these as properties for debugging - when all is working make them normal attributes again
    @property
    def _elements_read(self):
        return self.__elements_read

    @_elements_read.setter
    def _elements_read(self,val):
        #log.warning('_elements_read set to {}'.format(val))
        self.__elements_read = val

    @property
    def _security_edited(self):
        #print('1739: ',self.__security_edited )
        return self.__security_edited

    @_security_edited.setter
    def _security_edited(self,val):
        #log.warning('_elements_read set to {}'.format(val))
        self.__security_edited = val
        #print('885: ',self.__security_edited )

    @property
    def _elements_synced(self):
        return self.__elements_synced

    @_elements_synced.setter
    def _elements_synced(self,val):
        #log.warning('_elements_synced set to {}'.format(val))
        self.__elements_synced = val

    @property
    def _element_dataframe(self):
        return self.__element_dataframe

    @_element_dataframe.setter
    def _element_dataframe(self,val):
        #if val is None:
        #    #log.warning('_element_dataframe set to None')
        #    pass
        #else:
        #    #log.warning('_element_dataframe set')
        self.__element_dataframe = val

    def __delitem__(self,item):
        #Load the Elements if we haven't already
        if not self._elements_read:
            self._load_elements()

        del self._elements[item]

    #Unlike a standard dictionary which returns keys in iter, return values (since that's what we usually want)
    def __iter__(self):
        #JAT 2019-03-10 PYM-42, changed to get the default iterator to do the lazy load from Empower before returning self
        self._iterator = iter(self.values())
        return self

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self,item):
        #Load the Elements if we haven't already
        if not self._elements_read:
            self._load_elements(debug=self.dimension.site._debug)

        return self._elements[item]

    def __setitem__(self, key, item):
        # Does the [] set overloading
        
        if not self._elements_read:
            self._load_elements(debug=self.dimension.site._debug)

        #Adding an element nullifies the dataframe
        self._element_dataframe = None

        # Flag that edits have been made
        self._elements_synced = False

        if key is None:
            raise ValueError('.elements[] can not have an item added with a None key')
        else:
            self._elements[key]   = item

        #Add the item to the _elements dataframe if it exists

    def __ior__(self,item):
        '''Define syntax for |= i.e. add if doesn't already exist - otherwise ignore'''
        if isinstance(item,Element):
            try:
                self[item.shortname]
            except KeyError:
                self.append(item)
        elif isinstance(item,str):
            #Create a stub and add it
            self |= Element(dimension=self.dimension, shortname = item,longname=item.capitalize(),description=item.capitalize())
        else:
            try:
                for i in item:
                    self |= i
            except TypeError: #non iterables will raise a TypeError

                try:
                    el = item.element
                    self |= el
                except AttributeError:

                    raise ValueError('Could not combine objects {} and {} using |= syntax'.format(repr(self),repr(item)))

        return self

    def __iadd__(self,item):
        '''Define syntax for += i.e. add if doesn't already exist - otherwise raise ValueError'''
        if isinstance(item,Element):
            #Only add the element if it diesn't already exist - if it does, raise a value error
            try:
                self[item.shortname]
                raise ValueError('Cannot add item {} to .elements because an item with this shortname already exists'.format(repr(item)))
            except KeyError:
                self.append(item)

        elif isinstance(item,str):
            #Create a stub and add it
            self += Element(dimension=self.dimension, shortname = item,longname=item.capitalize(),description=item.capitalize())
        else:
            try:
                for i in item:
                    self += i
            except TypeError: #non iterables will raise a TypeError

                try:
                    el = item.element
                    self += el
                except AttributeError:

                    raise ValueError('Could not combine objects {} and {} using += syntax'.format(repr(self),repr(item)))

        return self

    def append(self,item):
        assert isinstance(item,Element)
        self[item.shortname] = item

    def _load_elements(self,debug                       = False):
        log.verbose('Reading Elements for dimension '+str(self.dimension.index))
        #Set _elements_read now, or we'll end up in a loop
        self._elements_read = True
        try:
            self._elements = _create_empower_dimension_shortname_element_dict(dimension                   = self.dimension
                                                                             ,debug                       = debug
                                                                             )
        except:
            self._elements_read = False
            raise

    def _load_security(self):

        if self._security_read:
            return

        if not self._elements_read:
            self._load_elements()

        if self.dimension.longname is None:
            raise ValueError('Cannot import dimension security until the .longname property of dimension {} has been set'.format(self.dimension.index))

        log.verbose('Reading Element Security for dimension[{}]'.format(self.dimension.index))

        #pull the data in and set security
        security_data = []

        command_list = self.dimension.site._logon_parameter_importer_commands + \
                       ['set-parameter dimensionname='      + self.dimension.longname
                       ,'empower-export-security-settings "${site}" "${user}" "${password}" "${dimensionname}"'
                       ,'output'
                       ]

        output = llu.run_single_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)

        major_version, minor_version, release, release_number = self.dimension.site.importer_version

        #In older versions of Importer there was some weird double quotes in the output
        if (major_version == 9 and (release_number >= 1724 or minor_version >=7)) or major_version > 9:
            for n, line in enumerate(output.split('\n')):
                if n > 0 and len(line) > 0:
                    security_data.append(line.split('\t'))
        else:
            for n, line in enumerate(output.split('\n')):
                if n > 0 and len(line) > 0:
                    #Strip off double quotes and carriage return
                    assert line[0]=='"'
                    assert line[-2]=='"'

                    security_data.append(line[1:-2].split('\t'))


        for datum in security_data:

            dimension_name = datum[0]

            #Do this assertion to make help assure we've read the data correctly
            assert self.dimension.longname == dimension_name, 'Dimension name dimension.longname "{}" must match output from Importer "{}"'.format(self.dimension.longname, dimension_name)

            element_identifiers = datum[1]
            modifier_declaration = datum[2]
            modifier_function = datum[3]
            modifier_list_string = datum[4]
            viewer_declaration = datum[5]
            viewer_function = datum[6]
            viewer_list_string = datum[7]
            data_viewer_declaration = datum[8]
            data_viewer_function = datum[9]
            data_viewer_list_string = datum[10]

            element_identifier_parts = element_identifiers.split('(')
            element_sc = '('.join(element_identifier_parts[:-1]).strip()
            #Get the last bit after a open bracket, then strip the close bracket off the end
            element_physid = int(element_identifier_parts[-1][:-1].replace(')',''))

            assert modifier_declaration == 'Modifiers', 'Security output is in incorrect format'
            assert viewer_declaration == 'Viewers', 'Security output is in incorrect format'
            assert data_viewer_declaration == 'Data Viewers', 'Security output is in incorrect format'

            modifiers = []
            if modifier_function == 'Set':

                modifier_list = modifier_list_string.split('+')

                for modifier in modifier_list:
                    modifier_parts = modifier.split('(')
                    modifier_sc = '('.join(modifier_parts[:-1])
                    #Get the last bit after a open bracket, then strip the close bracket off the end
                    modifier_physid = modifier_parts[-1][:-1].replace(')','')

                    modifiers.append((modifier_sc,int(modifier_physid)))

            viewers = []
            if viewer_function == 'Set':

                viewer_list = viewer_list_string.split('+')

                for viewer in viewer_list:
                    viewer_parts = viewer.split('(')
                    viewer_sc = '('.join(viewer_parts[:-1])
                    #Get the last bit after a open bracket, then strip the close bracket off the end
                    viewer_physid = viewer_parts[-1][:-1].replace(')','')

                    viewers.append((viewer_sc,int(viewer_physid)))

            data_viewers = []
            if data_viewer_function == 'Set':

                data_viewer_list = data_viewer_list_string.split('+')

                for data_viewer in data_viewer_list:
                    data_viewer_parts = data_viewer.split('(')
                    data_viewer_sc = '('.join(data_viewer_parts[:-1])
                    #Get the last bit after a open bracket, then strip the close bracket off the end
                    data_viewer_physid = data_viewer_parts[-1][:-1].replace(')','')

                    data_viewers.append((data_viewer_sc,int(data_viewer_physid)))

            if not (modifier_function == 'Clear' and viewer_function == 'Clear' and data_viewer_function == 'Clear'):

                el = self._elements[element_sc]

                #Do this assertion to make sure we've read the shortcode correctly
                assert el.physid == element_physid

                #TODO - when we can get users from a site, assert their physid matches the scraped physid

                #if element_sc == 'Managemen':
                #    print(data_viewers,viewers,modifiers)

                el._security = ElementSecurity(element                  = el
                                              ,data_viewers             = {dv_sc for dv_sc, dv_physid in data_viewers}
                                              ,viewers                  = {v_sc  for v_sc,  v_physid  in viewers}
                                              ,modifiers                = {m_sc  for m_sc,  m_physid  in modifiers}
                                              ,initialise_synched       = True
                                              ,initialise_as_default    = False
                                              )
                #if element_sc == 'Managemen':
                #    print(datum)
                #    print(el._security.data_viewers,el._security.viewers,el._security.modifiers)

        self._security_read = True


    def keys(self):
        if not self._elements_read:
            self._load_elements()

        return self._elements.keys()

    def items(self):
        if not self._elements_read:
            self._load_elements()

        yield from self._elements.items()
        for el in self._elements_without_shortnames:
            yield None, el

    def values(self):
        if not self._elements_read:
            self._load_elements()

        yield from self._elements.values()
        yield from self._elements_without_shortnames

    def __len__(self):
        if not self._elements_read:
            self._load_elements()

        return len(self._elements) + len(self._elements_without_shortnames)


    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self))    )

    @property
    def dataframe(self):

        if self._element_dataframe is not None:
            return self._element_dataframe
        else:
            #make the dataframe out of elements in self._elements
            self._element_dataframe = pd.DataFrame([dict(ID=element.physid, **element.fields) for element in self.values()]+[dict(element.fields) for element in self._elements_without_shortnames]
                                                  #,columns = ['ID','Short Name','Long Name','Description','Group Only','Calculation Status','Calculation','Colour','Measure Element'])
                                                  ,columns = ['ID']+[k for k in self.dimension.fields.keys()])

            return self._element_dataframe

    @dataframe.setter
    def dataframe(self,df):
        raise AttributeError("Don't set the dataframe directly with Dimension.elements.dataframe - use Dimension.elements.merge(source=<dataframe>,keys=<keycolumns>) instead")

    def _canonical_elements_by_pk(self, keys):
        '''Get a dictionary of canonical elements by whichever key is passed in
        Split out as a new funtion to aid testing
        '''
        canonical_elements_by_pk={tuple(el.fields[primary_key_column] for primary_key_column in keys):el for el in self.values()}
        return canonical_elements_by_pk

    def _get_canonical_element(self, el, keys, canonical_elements_by_pk):
        '''Get a canonical element for a given element, using a given set of keys and a _canonical_elements lookup
        Split out as a new funtion to aid testing
        '''

        #See if, given the primary key defined by the user (could be for instance "Long Name" or a field) we already have this element in the site
        element_chosen_pk = tuple(el.fields[primary_key_column] for primary_key_column in keys)

        for primary_key_column in keys:
            primary_key_value = el.fields[primary_key_column]
            if primary_key_value is not None and ('\n' in str(primary_key_value) or '\t' in str(primary_key_value)):
                raise ValueError('An element with cannot be merged if its keys contain a string containing a tab or newline, or an object that evaluates to such as string. Element: {}, field: {}, field value: {}'.format(repr(el),primary_key_column,repr(primary_key_value)))


        #if element_chosen_pk == ('Home Improvement','Sector'):
        #    print('element_chosen_pk: ',element_chosen_pk)
        try:
            canonical_el = canonical_elements_by_pk[element_chosen_pk]
        except KeyError:
            canonical_el = None

        return canonical_el

    def merge(self,source,keys=['Short Name']):
        '''Merge in elements from the source into the Dimension's elements, saving if necessary in order to create physids and standard Empower shortnames

        :param source: a pandas DataFrame, list of Elements, or dictionary of Elements
        :param keys: a list of fields to be used as the key in the merge

        :return: Returns an object of the same type as was passed in (DataFrame, list of elements or Element) with the canonical versions of the elements - i.e. the ones synchronised with Empower if they already existed, or the new ones if they are brand new
        '''
        dataframe = None
        is_list = False
        is_dict = False
        is_df = False
        is_element = False

        #Not sure this is actually doing anything, so took from the parameters
        sync = True
        output_list = []


        #Reverse ducktype the source
        try:
            source.axes
            dataframe = source
            is_df = True
        except AttributeError:
            try:
                source.values()
                is_dict = True
            except AttributeError:
                if isinstance(source, Element):
                    is_element = True
                else:
                    is_list = True

        #Keep track of the elements we are creating - using the primary key passed in as a function parameter
        #First populate the dictionary with current elements indexed by the chosen primary key
        canonical_elements_by_pk=self._canonical_elements_by_pk(keys)

        if dataframe is not None:
            #Drop any duplicates
            dataframe = dataframe.copy().drop_duplicates(subset=keys,keep='last')
            iterator = _dataframe_as_elements(dataframe,dimension=self.dimension)
            fields_to_merge = list(dataframe.columns)
        if is_dict:
            iterator = source.values()
            fields_to_merge = None
        if is_list:
            iterator = source
            fields_to_merge = None
        if is_element:
            iterator = [source]
            fields_to_merge = None

        ##Keep track of the elements by their primary key
        #elements_by_pk = {}

        for el in iterator:

            canonical_el = self._get_canonical_element(el, keys, canonical_elements_by_pk)


            if canonical_el is not None:

                #if element_chosen_pk == ('Home Improvement','Sector'):
                #    print('canonical_el: ',canonical_el)

                #Once we have a canonical shortname we must remove the old shortname from the _ElementsGetter
                if el.shortname != canonical_el.shortname:
                    old_shortname = el.shortname
                    try:
                        del self[old_shortname]
                    except KeyError:
                        pass
                canonical_shortname = canonical_el.shortname

                #Merge the new element in with the old
                canonical_el.merge(el,fields_to_merge=fields_to_merge)
                #Just in case make sure the shortname stays the same
                canonical_el.shortname = canonical_shortname

                self[canonical_el.shortname] = canonical_el

                ##and update the working list version
                #elements_by_pk[element_chosen_pk] = old_el

                output_list.append(canonical_el)

            else:

                if el.dimension is None:
                    el.dimension = self.dimension


                #Add the element to the dimension's list of elements, and to our working list
                if el.shortname is None:
                    self._elements_without_shortnames.append(el)
                else:
                    #We do not want to overwrite the shortcode if it already exists but under a different key
                    #That could accidentally happen, but we certainly don't want to do it
                    shortname_already_exists = False

                    try:
                        self[el.shortname]
                        shortname_already_exists = True
                    except KeyError:
                        pass

                    if shortname_already_exists:

                        #Check whether the pre-existing element's keys are the same - if so copy fields in
                        #If keys don't match, then raise an error
                        pre_existing_element = self[el.shortname]
                        pre_existing_element_key = tuple(pre_existing_element.fields[primary_key_column] for primary_key_column in keys)
                        if pre_existing_element_key == tuple(el.fields[primary_key_column] for primary_key_column in keys):
                            pre_existing_element.merge(el,fields_to_merge=fields_to_merge)
                        elif pre_existing_element.longname == '~TE#MP~'+pre_existing_element.shortname:
                            #Fix partially loaded elements by overwriting them
                            pre_existing_element.merge(el,fields_to_merge=fields_to_merge)
                        else:
                            raise KeyError('Key: {}. Element with Short Name:"{}" already exists in the dimension with key {}. You will need to manually delete it from the site to repair the load.'.format(element_chosen_pk,el.shortname,pre_existing_element_key))
                    else:
                        self[el.shortname] = el

                #put in a default longname if none has been set and we are merging on shortname
                if keys == ['Short Name'] and el.shortname is not None and el.longname is None:
                    el.longname = str(el.shortname).capitalize()

                output_list.append(el)

                #elements_by_pk[element_chosen_pk] = el

            self._elements_synced = False

        #self._element_dataframe = pd.DataFrame([element.fields for element in self.values()]+[element.fields for element in self._elements_without_shortnames])

        if len(self._elements_without_shortnames) > 0:
            self.synchronise(reexport=sync,reimport=sync,primary_key_fields=keys)

        if is_dict:
            return {el.shortname:el for el in output_list}

        if is_list:
            return output_list

        if is_df:
            self._element_dataframe = None
            return self.dataframe

        if is_element:
            return output_list[0]

    def synchronise(self,reexport=True,reimport=False,primary_key_fields=['Short Name']):
        '''
        '''
        debug                       = self.dimension.site._debug
      
        ############################################
        #
        # NOTE: Time dimension elements are created using one empower function, and then updated to add the correct longname and description
        #       At the time being, we cannot create time Dimensions using a shortname, so we first put the shortname in the longname and Empower will default the shortname to the longname
        #       Then we update the time dimension by doing a standard import
        #

        keys_shortname_lkp = {}

        #if len(self._elements)+len(self._elements_without_shortcodes)==0:
        #    return

        is_time_dimension = self.dimension.index == 11

        ###################################
        #
        #
        #    TODO - check if we need to create new fields first, and throw an error if we do
        #           it is best to create new fields, structures and viewpoints (i.e. True Empower Metadata) as a DDL style step
        #
        #   Site.redefine()

        #   Site.definition.synchronise()

        #Create a new output_elements list - i.e. elements that have not been mastered before
        new_output_elements=[]
        #For each element in the input elements list, if it doesn't exist in the dictionary of elements from the site, then put it into the output elements
        #print([e.physid for e in self.values()])
        for input_element in self.values():
            #Master new elements
            if not input_element.mastered:
                new_output_elements.append(input_element)

        #print(new_output_elements)

        #In debug mode, write the output elements to a working file for importing into empower
        if debug:
            for dir in [self.dimension.site._empower_dim_import_dir]:

                try:
                    os.makedirs(dir)
                except FileExistsError:
                    pass
                except OSError as e:
                    if e.winerror == 123:
                        raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                    else:
                        raise e
            imported_dimension_filepath = os.path.join(self.dimension.site._empower_dim_import_dir,'Dimension_'+str(self.dimension.index)+'_NewElements.tsv')
            imported_fields_filepath = os.path.join(self.dimension.site._empower_dim_import_dir,'Dimension_'+str(self.dimension.index)+'_NewElementFields.tsv')
            imported_time_dimension_filepath = os.path.join(self.dimension.site._empower_dim_import_dir,'Dimension_'+str(self.dimension.index)+'_NewTimeElements.tsv')
        else:
            #Create unique named pipes to read and write to
            imported_dimension_filepath      = r'\\.\pipe\{}'.format(uuid.uuid4())
            imported_fields_filepath         = r'\\.\pipe\{}'.format(uuid.uuid4())
            imported_time_dimension_filepath = r'\\.\pipe\{}'.format(uuid.uuid4())


        #Lookup of characters that can go in a shortcode
        #good_shortcode_char = {'Q':1,'W':1,'E':1,'R':1,'T':1,'Y':1,'U':1,'I':1,'O':1,'P':1,'A':1,'S':1,'D':1,'F':1,'G':1,'H':1,'J':1,'K':1,'L':1,'Z':1,'X':1,'C':1,'V':1,'B':1,'N':1,'M':1,'q':1,'w':1,'e':1,'r':1,'t':1,'y':1,'u':1,'i':1,'o':1,'p':1,'a':1,'s':1,'d':1,'f':1,'g':1,'h':1,'j':1,'k':1,'l':1,'z':1,'x':1,'c':1,'v':1,'b':1,'n':1,'m':1,'1':1,'2':1,'3':1,'4':1,'5':1,'6':1,'7':1,'8':1,'9':1,'0':1}
        bad_shortcode_char = {'"':1,"'":1,"+":1,"-":1,"*":1,"(":1,")":1,"/":1,"@":1,",":1,"|":1,"^":1,"=":1,"\n":1,"\r":1,"\t":1,".":1," ":1}
        
        new_time_elements = []
        new_standard_elements = []

        if is_time_dimension:
            for el in new_output_elements:
                if isinstance(el,TimeElement):
                    new_time_elements.append(el)
                else:
                    new_standard_elements.append(el)
        else:
            new_standard_elements = new_output_elements


        if len(new_time_elements) > 0:
            _time_dimension_import_elements(dimension                        = self.dimension
                                           ,elements                         = new_time_elements
                                           ,imported_dimension_filepath      = imported_dimension_filepath
                                           ,imported_time_dimension_filepath = imported_time_dimension_filepath
                                           )

        if len(new_standard_elements) > 0:

            #Switch description for a concatenated key - we will be able to grab the shortname and link correct elements in order to update fields
            def _element_string_for_import_file(output_element,primary_key_fields,n):

                '''n disambiguates between each element to force Empower to create new shortnames for each element'''
                _element_string = ""
                #Put concatenated key into longname
                try:
                    _element_string+= '~TE#MP~'+'~#~'.join(output_element.fields[key] for key in primary_key_fields)
                    
                except TypeError:
                    #Not all new elements are being created because of the merge - there may be some standard elements being created with a shortname
                    if output_element.longname is None:
                        raise ValueError('Cannot create output element with no longname. Shortname is {}, physid is {}, keyfields are {}'.format(output_element.shortname,output_element.physid,{key: output_element.fields[key] for key in primary_key_fields}))
                    _element_string+= output_element.longname
                _element_string+= '\t'
                if output_element.shortname is not None:
                    _element_string+= output_element.shortname
                else:
                    #Make sure there are no bad characters in the stub shortnames
                    stub_shortname = ''
                    if output_element.longname is None:
                        raise ValueError('Cannot create output element with no longname. Shortname is {}, physid is {}, keyfields are {}'.format(output_element.shortname,output_element.physid,{key: output_element.fields[key] for key in primary_key_fields}))

                    for char in output_element.longname:
                        try:
                            #Check if the character is a bad one, if so abandon it, if not add it on
                            bad_shortcode_char[char]
                        except KeyError:
                            stub_shortname += char
                    #stub shortnames are deliberately too long and different from each other, to force Empower to generate new ones
                    #_element_string += stub_shortname[:10]+('+'*512)+str(n)
                    _element_string += stub_shortname[:10]+'+'+str(n)
                    
                _element_string += '\t'
                if output_element.description is not None:
                    _element_string += output_element.description
                _element_string += '\n'

                return _element_string

            #Create the commands to Import the elements in the working file into Empower
            #These will be run by Importer in a moment when we are ready to do our merry multi-processing dance with named pipes
            #Finish off the command list now we've set appropriate username/password
            command_list = self.dimension.site._logon_parameter_importer_commands + \
                           ['set-parameter dimension_index='    + str(self.dimension.index)
                           ,'load-file-tsv "'                   + imported_dimension_filepath + '"'
                           ,'empower-import-elements "${site}" "${user}" "${password}" ${dimension_index}'
                           ]

            #In debug mode write the data into a tsv file and read it with Importer, putting the elements into Empower
            if debug:
                with open(imported_dimension_filepath,'w') as imported_dimension_file:
                    for n, output_element in enumerate(new_standard_elements):
                        imported_dimension_file.write(_element_string_for_import_file(output_element,primary_key_fields,n))
               
                llu.run_single_output_importer_commands(command_list, empower_importer_executable=self.dimension.site.empower_importer_executable)

            else:
                #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
                #imported_dimension_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
                #The merry dance means starting empower, referencing the pipe, opening the pipe before empower is properly started
                #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
                #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
                #before we have created it. But we will block on our side until Importer has connected
                proc = None
                try:
                    proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)
                    with llu.outbound_pipe(imported_dimension_filepath) as pipe:

                        for n, output_element in enumerate(new_standard_elements):
                            win32file.WriteFile(pipe, str.encode(_element_string_for_import_file(output_element,primary_key_fields,n)))

                        log.debug("Pipe {} finished writing".format(imported_dimension_filepath))

                finally:
                    #Check if Importer returned an error and raise it as a python if it did
                    llu.complete_no_output_importer_process(proc)


        #Need to match up on key column for new items
        #First check there are fields

        for element in _create_empower_dimension_element_list(dimension = self.dimension,debug = debug):
            if element.longname[:7]=='~TE#MP~':
                keys = element.longname[7:].split('~#~')
                #keys = element.longname[7:].split('@')
                keys_shortname_lkp[tuple(keys)] = element
            if isinstance(element,TimeElement):
                keys_shortname_lkp[(element.shortname,)] = element

        #Read Time and Standard elements back into Dimension - ensuring we leave Element objects in Dimension as the same ones
        for element in new_output_elements:
            #get the key fields and look up the empower element that had a description linked to these key fields
     
            try:
                emp_element = keys_shortname_lkp[tuple(element.fields[key] for key in primary_key_fields)]
            except KeyError:
                emp_element = self[element.shortname]
            
            
            
            #New elements may already have shortnames - only those shortnames are not canonical Empower shortnames
            #we will need to remove those elements from the standard dimension _ElementsGetter dictionary as that they no longer appear under the old shortname
            if element.shortname != emp_element.shortname:
                old_shortname = element.shortname
                #Note - if old_shortname is None, then the element will be in self._elements_without_shortnames which will be reset a few lines below this one
                if old_shortname is not None:
                    del self[old_shortname]

            ##JAT 2019-10-10 we cannot assert emp_element.physid is not None, because we may be merging to a previously unsynchronised element
            #assert  emp_element.physid is not None

            #Copy in the data from empower - mastering it
            element.shortname = emp_element.shortname
            element.physid    = emp_element.physid
            #Transfer what was an element without a shortname into the standard element dictionary
            self[element.shortname] = element


        #We have now put all elements without shortnames into the standard _elements dictionary
        self._elements_without_shortnames = []

        #for element in self.values():
        #    for k, v in element.fields.items():
        #        print(element.shortname, k, v)

        def _yield_empty_calculations_strings(_elements_iterator):
            for element in _elements_iterator:
                for field_shortname, field_value in element.fields.edited_items:
                    if field_shortname == 'Calculation' and not field_value is None and not field_value == '':
                        yield element.shortname
                        yield '\tCalculation\t@Myself\n'

        #We will call this function twice to determine if we need to call Importer (which is slow)
        def _yield_fields_strings(_elements_iterator,field_change_count_list=[0]):
            total_field_changes = 0
            for element in _elements_iterator:
                for field_shortname, field_value in element.fields.edited_items:

                    #print(element.shortname, field_shortname, field_value)
                    if field_shortname not in ['Short Name'
                                              ,'Measure Element'
                                              ]:

                        try:
                            canonical_field_shortname = {'Long Name'          : 'Longname'
                                                        ,'Group Only'         : 'GroupOnly'
                                                        ,'Calculation Status' : 'Status'
                                                        }[field_shortname]
                        except KeyError:
                            canonical_field_shortname = field_shortname

                        if canonical_field_shortname in ['GroupOnly','Status','Calculation','Colour'] and field_value is None or field_value == '':
                            #We don't want to write empty values into these fields or we'll get errors
                            continue
                        else:
                            #ELEMENT SHORTNAME,FIELD SHORTNAME,VALUE
                            yield element.shortname
                            yield '\t'
                            #Map the output names for the fields to the input shortnames for the fields
                            yield str(canonical_field_shortname)
                            yield '\t'
                            if field_value is not None:
                                if '\n' in str(field_value) or '\t' in str(field_value):
                                    yield '"'
                                    yield str(field_value).replace('"','""')
                                    yield '"'
                                else:
                                    yield str(field_value).replace('"','""')

                            yield '\n'
                            total_field_changes += 1

            #This is the 'return value' passed in as a mutable list
            field_change_count_list[0]=total_field_changes

        #Do two passes, to determine whether we want to call the update fields importer script

        #Keep track of number of field changes so we don't do unnecessary work
        #We need to track changes in a mutable (i.e. list)
        field_change_count_list = [0]
        for s in _yield_fields_strings(self.values(),field_change_count_list):
            pass
        total_field_changes = field_change_count_list[0]

        if total_field_changes > 0:


            command_list = self.dimension.site._logon_parameter_importer_commands + \
                           ['set-parameter input_file='     + imported_fields_filepath
                           ,'load-file-tsv "${input_file}"'
                           ]

            #Create the element fields (for all elements - not just new ones)
            major_version, minor_version, release, release_number = self.dimension.site.importer_version

            if (major_version == 9 and (release_number >= 1724 or minor_version >=7)) or major_version > 9:
                command_list += ['empower-import-field-values "${site}" "${user}" "${password}" '+str(self.dimension.index)]
            else:
                #Use the empower-import-fields command deprecated in build 1724
                command_list += ['empower-import-fields "${site}" "${user}" "${password}" '+str(self.dimension.index)]

            #In debug mode write the data into a tsv file and read it with Importer, putting the elements into Empower
            if debug:
                #Non time dimensions may have fields - write the standard and non standard fields to file and import them
                with open(imported_fields_filepath,'w') as imported_fields_file:

                    #Write empty calculation elements for all changed calculations to help prevent circular calculations
                    #These will be overwritten immediately
                    for s in _yield_empty_calculations_strings(self.values()):
                        imported_fields_file.write(s)

                    #Write fields for all elements, only the changed fields will get written
                    for s in _yield_fields_strings(self.values()):
                        imported_fields_file.write(s)

                llu.run_single_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)

            else:
                #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
                #imported_fields_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
                #The merry dance means starting empower, referencing the pipe, opening the pipe before empower is properly started
                #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
                #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
                #before we have created it. But we will block on our side until Importer has connected
                proc = None
                try:
                    proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)
                    with llu.outbound_pipe(imported_fields_filepath) as pipe:

                        #Write empty calculation elements for all changed calculations to help prevent circular calculations
                        #These will be overwritten immediately
                        for s in _yield_empty_calculations_strings(self.values()):
                            win32file.WriteFile(pipe, str.encode(s))

                        #Write fields for all elements, only the changed fields will get written
                        for s in _yield_fields_strings(self.values()):
                            win32file.WriteFile(pipe, str.encode(s))

                        log.debug("Pipe {} finished writing".format(imported_fields_filepath))

                finally:

                    #Check if Importer returned an error and raise it as a python if it did
                    llu.complete_no_output_importer_process(proc)


            log.verbose('Loaded fields')

        for element in self.values():
            element.fields.reset_edit_status()
            element._edited = False


        if is_time_dimension:
            log.verbose('Time Elements updated for dimension '+str(self.dimension.index))
        else:
            log.verbose('Elements created for dimension '+str(self.dimension.index))

        self._elements_synced = True

        #synchronise security
        #print('1463:',self.dimension.elements._security_edited)
        if self.dimension.elements._security_edited:

            if self.dimension.longname is None:
                raise ValueError('Cannot synchronise dimension security until the .longname property of dimension {} has been set'.format(self.dimension.index))

            if debug:
                for dir in [self._empower_dim_import_dir]:

                    try:
                        os.makedirs(dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if e.winerror == 123:
                            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                        else:
                            raise e
                security_filepath=os.path.join(self.dimension.site._empower_dim_import_dir,'Dimension_'+str(self.dimension.index)+'_Security.tsv')
            else:
                #Create unique named pipes to read and write to
                security_filepath= r'\\.\pipe\{}'.format(uuid.uuid4())

            log.verbose('Synchronising Element Security for dimension[{}]'.format(self.dimension.index))

            #this is what we will be sending to Importer (as tsv) - maybe in a file, maybe in a pipe
            def _yield_security_strings():
                for element in self.values():
                    if element.security.edited:

                        yield self.dimension.longname
                        yield '\t'
                        yield element.shortname
                        yield '\t'
                        yield 'Modifiers'
                        yield '\t'
                        if len(element.security.modifiers) == 0:
                            yield 'Clear'
                        else:
                            yield 'Set'
                        yield '\t'
                        yield '+'.join(element.security.modifiers)

                        yield '\t'
                        yield 'Viewers'
                        yield '\t'
                        if len(element.security.viewers) == 0:
                            yield 'Clear'
                        else:
                            yield 'Set'
                        yield '\t'
                        yield '+'.join(element.security.viewers)

                        yield '\t'
                        yield 'Data Viewers'
                        yield '\t'
                        if len(element.security.data_viewers) == 0:
                            yield 'Clear'
                        else:
                            yield 'Set'
                        yield '\t'
                        yield '+'.join(element.security.data_viewers)

                        yield '\n'

            #Run the requisite importer commands

            command_list = self.dimension.site._logon_parameter_importer_commands + \
                           ['load-file-tsv "'                   + security_filepath + '"'
                           ,'empower-import-security-settings "${site}" "${user}" "${password}"'
                           ]

            #In debug mode write the data into a tsv file and read it with Importer, putting the structure into Empower
            if debug:
                #Non time dimensions may have fields - write the standard and non standard fields to file and import them
                with open(security_filepath,'w') as target_file:
                    for s in _yield_security_strings():
                        target_file.write(s)

                llu.run_single_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)

            else:
                #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
                #security_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
                #The merry dance means starting Importer, referencing the pipe, opening the pipe before Importer is properly started
                #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
                #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
                #before we have created it. But we will block on our side until Importer has connected
                proc = None
                try:
                    proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)

                    with llu.outbound_pipe(security_filepath) as pipe:

                        for s in _yield_security_strings():
                            win32file.WriteFile(pipe, str.encode(s))

                        log.debug("Pipe {} finished writing".format(security_filepath))

                finally:

                    #Check if Importer returned an error and raise it as a python if it did
                    llu.complete_no_output_importer_process(proc)

        ### Set flag  to get security to completely resynch next time
        for element in self.values():
            if element._security is not None:
                element._security._viewers = None
                element._security._modifiers = None
                element._security._data_viewers = None
            element._security = None

        self._security_read = False
        #edits have been synched
        self.__security_edited = False
        #print(self)
        #print('1527: ',self.__security_edited )

        ####################################################

        #check if all of the elements are mastered - if so, then we don't need to resynch (by lazy loading)
        for el in self.values():

            if not el.mastered:
                #Reimport lazily by setting self._elements_read = False
                #This will persuade the _elementsGetter to re-export and re-read the dimension, rather than using the cached version
                self._elements_read = False
                break


        self._element_dataframe = None

        gc.collect()

class _FieldsGetter(object):
    '''Does a bit of magic to allow Elements to have a fields attribute that records editing changes'''
    def __init__(self,element, fields,initialise_as_edited):
        self.element=element

        if element.dimension is not None:
            self._fields=collections.OrderedDict()
            for k in element.dimension._fields.keys():
                try:
                    self._fields[k] = fields[k]
                except KeyError:
                    self._fields[k] = None
        else:
            self._fields=collections.OrderedDict(fields)

        self._field_edits={}
        if initialise_as_edited:
            for k,v  in fields.items():
                if v is not None and v != '':
                    self._field_edits[k] = True
        else:
            self.reset_edit_status()

    @property
    def edited(self):
        #Return True if any of the fields have been edited

        for edited in self._field_edits.values():
            if edited:
                return True

        return False

    @property
    def edited_items(self):
        '''Return fields which have been edited as if calling items() i.e. key, value pairs'''

        for k, edited in self._field_edits.items():
            if edited:
                yield k, self._fields[k]

    def reset_edit_status(self):
        #Set edit status back to no edits
        #print('{} reset edit status'.format(self.element.physid))
        self._field_edits={}

    def __iter__(self):
        self._iterator = iter(self.keys())
        return self

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self,item):
        ##Load the Elements if we haven't already
        #if not self.dimension._elements_read:
        #    self._load_elements()

        try:
            return self._fields[item]
        except KeyError:
            if self.element.dimension is not None:
                if item in self.element.dimension.fields.keys():
                    #Add None to save this logic happening all of the time
                    self._fields[item] = None
                    return None
            #Re-raise only if we have not returned a None value (i.e. raise if the key is not a dimension field)
            raise


    def __setitem__(self, key, item):

        #if not self.dimension._elements_read:
        #    self._load_elements()

        #Add field names if we haven't read the dimension yet
        if not self.element.dimension is None and not self.element.dimension.elements._elements_read:
            self.element.dimension.fields._add_field_name(key,from_empower=False)

        try:
            if self._fields[key] == item:
                #don't do anything (including recording an edit) if the item is already the same as the value
                return
            elif key == 'Calculation':
                #Calculation has changed (to shortname based consolidation probably)
                #but the underlying calculation is the same, because Empower exported the physid string, whereas it requires the shortnames
                #so check if the physid version of the calculation has changed - if not then change it but don't mark the fields as edited.
                if self.element._physid_calculation == self._fields[key]:
                    self._fields[key]             = item
                    return


        except KeyError:
            #if  key == 'Description':
            #    try:
            #        print('{} {} edited {}. {} -> {} '.format(self.element.physid, self.element.shortname,key,self._fields[key],item))
            #    except KeyError:
            #        print('{} {} edited {}. {} -> {} '.format(self.element.physid, self.element.shortname,key,None,item))
            pass


        self._fields[key]             = item
        self._field_edits[key]        = True
        self.element._edited          = True
        self.element._synched         = False


    def keys(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return self._fields.keys()

    def items(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return self._fields.items()

    def values(self):
        #if not self.dimension._elements_read:
         #   self._load_elements()

        return self._fields.values()

    def __len__(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return len(self._fields)

    def __str__(self):
        return str(self._fields)

    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self))  )


class _DimensionFieldsGetter(object):
    '''Does a bit of magic to allow Dimension.fields to have |= and similar magic methods applied'''
    def __init__(self,dimension):
        self.dimension=dimension

        self._fields = collections.OrderedDict()
        self._field_names_in_empower = collections.OrderedDict()

    def _add_field_name(self,fieldname,from_empower=False):
        #TODO - as soon as we can get field names (alone) into the dimension from Empower get rid of this. It is slowing down so many other function calls

        if fieldname is None:
            raise ValueError('Dimension fields can not have an empty (None) key for item')

        self._fields[fieldname] = FieldDefinition(longname=fieldname)

        if from_empower:
            self._field_names_in_empower[fieldname] = fieldname

    @property
    def _new_field_names(self):
        if len(self._fields) == 0:
            return

        '''Yield all field names that are not in Empower - they'll be new'''
        for f in self.keys():
            try:
                self._field_names_in_empower[f]
            except KeyError:
                if f is not None:
                    yield f

    def __ior__(self,other):
        k=None
        v=None
        if isinstance(other,FieldDefinition):
            if other.shortname is None:
                k=other.longname
            else:
                k=other.shortname
            v=other
        elif str(other)==other:
            k = other
            v = FieldDefinition(shortname=other,longname=other)
        else:
            raise TypeError("unsupported operand types(s) for |=: '_DimensionFieldsGetter' and '{}'".format(type(other)))

        #Only add if doesn't exist already
        try:
            self[k]
        except KeyError:
            self[k] = v
        #return self, because that is what __ior__ must always do
        return self

    def __iadd__(self,other):
        k=None
        v=None
        if isinstance(other,FieldDefinition):
            if other.shortname is None:
                k=other.longname
            else:
                k=other.shortname
            v=other
        elif str(other)==other:
            k = other
            v = FieldDefinition(shortname=other,longname=other)
        else:
            raise TypeError("unsupported operand types(s) for |=: '_DimensionFieldsGetter' and '{}'".format(type(other)))

        self[k] = v
        return self

    def __iter__(self):
        self._iterator = iter(self.keys())
        return self

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self,item):
        return self._fields[item]

    def __setitem__(self, key, item):
        #if not self.dimension._elements_read:
        #    self._load_elements()
        if not isinstance(item, FieldDefinition):
            raise TypeError("You can only set a Dimension's fields to be FieldDefinition objects. Expecting object of type FieldDefinition, got object {} of type {}".format(item, type(item)))

        if item.longname is None:
            raise ValueError("You can only set a Dimension's fields to be FieldDefinition object with a longname. The longname is set to None which is not acceptable in Empower, for object {}".format(item))

        #Add field names if we haven't read the dimension yet
        if not self.dimension is None and not self.dimension.elements._elements_read:
            self._add_field_name(key,from_empower=False)

        if key is None:
            raise ValueError('Dimension fields can not have an empty (None) key for item: {}'.format(item))

        self._fields[key]             = item

    def keys(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return self._fields.keys()

    def items(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return self._fields.items()

    def values(self):
        #if not self.dimension._elements_read:
         #   self._load_elements()

        return self._fields.values()

    def __len__(self):
        #if not self.dimension._elements_read:
        #    self._load_elements()

        return len(self._fields)

    def __str__(self):
        return str(self._fields)

    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self))  )

class _SecurityUsersGetter(object):
    '''Does a bit of magic to allow Elements to have viewers, modifiers and data_viewers attributes that lazy load and record editing changes
    _SecurityUsersGetter behaves like a list (of user shortcodes)
    One _SecurityUsersGetter will be created for each of the .viewers, .modifiers and .data_viewers properties

    Normally Element.viewers, modifiers and data_viewers will be None
    '''
    def __init__(self,element, users = set,initialise_synched=False, initialise_as_default = True):
        '''
        :param initialise_synched:  when loading the security from Empower we are synchronised. When creating new Elements and adding security we are not

        :param initialise_as_default: when creating security for a new element we usually want to have just default security (i.e. nothing recorded). If this is the case record it here to keep processing light
        '''

        #When initialising as default, we want to keep the class light- just set self.default = True and set a pointer back to the element
        if initialise_as_default:
            self.default=True
        else:
            self.default=False

        self.element=element

        #We hold two sets of users and the current version and the synched version from Empower
        #We can check for edits best this way, since a complex process is likely to add and remove users
        self._users = set(users)

        #Default self.edited - this will get overwritten by self._set_edited() is necessary
        self._edited = False

        if initialise_synched:
            #We initialise synched when we create the security directly from Empower
            self._synched_users = set(users)
            self._security_read = True

        else:
            self._security_read = False
            self._synched_users = set()
            if len(self._users) > 0:
                self._set_edited()



    def _set_edited(self):
         self._edited = True
         self.element.dimension.elements._security_edited = True
         #print('1725: ',self.element.dimension.elements._security_edited )

    def _lazy_load(self):
        #Work out if security has been loaded for the elements
        #Use a local shortcut boolean, to save processing time

        if not self._security_read:
            self.element.dimension._load_security()
            self._security_read = True

    @property
    def edited(self):
        #Read only property
        #Return True if edited and _synched_users != _users
        #if self._edited:
            #print('1734:',self._synched_users != self._users)
            #print(self._synched_users , self._users)
        return  self._edited and self._synched_users != self._users


    def __contains__(self, item):
        #Load the Users if we haven't already
        self._lazy_load()

        return item in self._users

    def __iter__(self):
        self._iterator = iter(list(self._users))
        return self

    def __next__(self):
        return next(self._iterator)

    #update(*others)
    #set |= other | ...
    #
    #    Update the set, adding elements from all others.
    #
    #intersection_update(*others)
    #set &= other & ...
    #
    #    Update the set, keeping only elements found in it and all others.
    #
    #difference_update(*others)
    #set -= other | ...
    #
    #    Update the set, removing elements found in others.
    #
    #symmetric_difference_update(other)
    #set ^= other
    #
    #    Update the set, keeping only elements found in either set, but not in both.
    #

    def add(self, item):
        '''Add item to the set of user shortcodes'''
        #Load the Users if we haven't already
        #print('1782:',self._security_read)
        #print('1783: ',self.element.dimension.elements._security_edited )
        self._lazy_load()
        #print('1785:',self._security_read)
        #print('1786: ',self.element.dimension.elements._security_edited )
        retval = self._users.add(item)
        #print('1788:',self._security_read)
        #print('1789: ',self.element.dimension.elements._security_edited )
        self._set_edited()
        #print('1791:',self._security_read)
        #print('1792: ',self.element.dimension.elements._security_edited )
        #print('1793:',self._synched_users)
        #print('1794:',self._users)
        #print('1795:',repr(self))
        return retval

    def __iadd__(self,item):
        try:
            self._users.add(item)
        except TypeError as e:
            try:
                for subitem in item:
                    self._users.add(subitem)
            except AttributeError:
                raise e

        return self

    def __isub__(self,item):
        try:
            self._users.discard(item)
        except TypeError as e:
            try:
                for subitem in item:
                    self._users.discard(subitem)
            except AttributeError:
                raise e

        return self


    #remove(elem)
    #
    #

    def set(self,item):
        self.clear()
        if isinstance(item,str):
            self.add(item)
        else:
            for i in item:
                self.add(i)

    def remove(self, item):
        '''Remove item from the set of user shortcodes. Raises KeyError if item is not contained in the set.'''

        #Load the Users if we haven't already
        self._lazy_load()
        retval = self._users.remove(item)
        self._set_edited()
        return retval

    def __sub__(self,item):
        return self.discard(item)

    def discard(self, item):
        '''Remove item from the set of user shortcodes if it is present.'''

        #Load the Users if we haven't already
        self._lazy_load()
        retval = self._users.discard(item)
        self._set_edited()
        return retval

    #pop()
    #
    #    Remove and return an arbitrary element from the set. Raises KeyError if the set is empty.
    #
    def clear(self):
        '''Remove all users shortcodes from the set.'''

        #Load the Users if we haven't already
        self._lazy_load()
        retval =  self._users.clear()
        self._set_edited()
        #If we are cleared, we don't want to accidentally re-initialize via another read
        self._security_read = True
        return retval

    #isdisjoint(other)
    #
    #    Return True if the set has no elements in common with other. Sets are disjoint if and only if their intersection is the empty set.
    #
    #issubset(other)
    #set <= other
    #
    #    Test whether every element in the set is in other.
    #
    #set < other
    #
    #    Test whether the set is a proper subset of other, that is, set <= other and set != other.
    #
    #issuperset(other)
    #set >= other
    #
    #    Test whether every element in other is in the set.
    #
    #set > other
    #
    #    Test whether the set is a proper superset of other, that is, set >= other and set != other.
    #
    #union(*others)
    #set | other | ...
    #
    #    Return a new set with elements from the set and all others.
    #
    #intersection(*others)
    #set & other & ...
    #
    #    Return a new set with elements common to the set and all others.
    #
    #difference(*others)
    #set - other - ...
    #
    #    Return a new set with elements in the set that are not in the others.
    #
    #symmetric_difference(other)
    #set ^ other
    #
    #    Return a new set with elements in either the set or other but not both.
    #

    def __len__(self):
        #Load the Users if we haven't already
        self._lazy_load()

        return len(self._users)

    def __str__(self):
        #Load the Users if we haven't already
        self._lazy_load()

        return str(self._users)

    def __repr__(self):
        #Load the Users if we haven't already
        self._lazy_load()

        return 'Users {} from <{} object at {}>'.format('{'+ ', '.join(["'{}'".format(u) for u in self._users])+ '}',self.__class__.__name__,hex(id(self)) )

class _ViewpointsGetter(object):
    '''Does a bit of magic to allow Sites to have a viewpoints object which behaves like a lazy loading dictionary'''
    def __init__(self,site):
        log.debug('Creating _ViewpointsGetter')
        self.site=site
        self._viewpoints={}

        self.__viewpoints_read = False
        self.__viewpoints_synced = True

    #Set these as properties for debugging - when all is working make them normal attributes again
    @property
    def _viewpoints_read(self):
        return self.__viewpoints_read

    @_viewpoints_read.setter
    def _viewpoints_read(self,val):
        #log.debug('_viewpoints_read set to {}'.format(val))
        self.__viewpoints_read = val

    @property
    def _viewpoints_synced(self):
        return self.__viewpoints_synced

    @_viewpoints_synced.setter
    def _viewpoints_synced(self,val):
        #log.warning('_viewpoints_synced set to {}'.format(val))
        self.__viewpoints_synced = val

    #Unlike a standard dictionary which returns keys in iter, return values (since that's what we usually want)
    def __iter__(self):
        if not self._viewpoints_read:
            self._load_viewpoints()
        log.debug('Called _ViewpointsGetter.__iter__')
        self._iterator = iter(self._viewpoints.values())
        return self

    def __next__(self):
        log.debug('Called _ViewpointsGetter.__next__')
        return next(self._iterator)

    def __getitem__(self,item):
        #Load the Viewpoints if we haven't already
        if not self._viewpoints_read:
            self._load_viewpoints()

        return self._viewpoints[item]

    def _load_viewpoints(self):
        log.verbose('Reading Viewpoints')
        self._viewpoints_read = True

        try:
            major_version, minor_version, release, release_number = self.site.importer_version

            if self.site._encrypted_user is None:
                raise mpex.EmpowerSecurityError('The encrypted_user must be set to access viewpoints. Remove hardcoded passwords and user names in calls to Site() in your script, in order to be prompted for a user and password')

            if (major_version == 9 and (release_number >= 1943 or minor_version >=7)) or major_version > 9:

                return_dict={}

                #Helper function to convert strings correctly
                def convert_string(s):
                    if s == '':
                        return None
                    else:
                        return s

                #The viewpoint list that will be returned - we'll add viewpoints to this list
                viewpoint_list=[]

                #This is not a backported command, so run only with encryption, in order to nudge users toward best practice
                log.verbose( "Running IMPORTER: from <stdin> with encrypted logon to export the Empower Site viewpoints from "+self.site._site_locator)

                if (major_version == 9 and (release_number >= 2142 or minor_version >=7)) or major_version > 9:
                    result = self.site.importer.run_commands(['empower-export-viewpoints -phys-ids ${site} ${user} ${password}','output'])
                    physids_included = True
                else:
                    result = self.site.importer.run_commands(['empower-export-viewpoints ${site} ${user} ${password}','output'])
                    physids_included = False

                fieldnames =    result[0].keys()
                #Use canonical Structures if they have been loaded already or create stubs (we don't need every Structure loaded for every viewpoint)
                #Check for the existing structure by looking at the object directly - don't use the accessor method or we will provoke a lazy load


                #Use the field names of the viewpoints to set the long names of the dimensions
                for n, field in enumerate(fieldnames):
                    if n+1 < self.site.number_of_unit_dimensions:
                        self.site.dimensions[n]._longname = field

                    elif n >= self.site.number_of_unit_dimensions and n < self.site.number_of_unit_dimensions + 5:
                        self.site.dimensions[n + (8 - self.site.number_of_unit_dimensions)]._longname = field

                #example of the structure we are trying to read:
                #Subsidiary Product      Customer   Item     Comparison     Currency      Period       Transformation   Longname             Shortname   Description
                #Europe     AllProds     AllCust    P&L      ModeGroups     AllCurrenc    MainTime     Transforms       Europe Viewpoint     EurViewp
                #Americas   AllProds     AmCust     P&L      ModeGroups     USCurr        MainTime     Transforms       Americas Viewpoint   AmViewp     Targetted viewpoint for North and South America

                for record in result:

                    structures = {}

                    for n in range(self.site.number_of_unit_dimensions):
                        dim_n_fieldname = self.site.dimensions[n].longname
                        dim_n_structure = record[dim_n_fieldname]
                        if physids_included:
                            #Strip the physid of the structure off
                            dim_n_structure = dim_n_structure.split('(')[0].strip()
                        structures[n] = dim_n_structure

                    for n in range(8 - self.site.number_of_unit_dimensions):
                        structures[n+self.site.number_of_unit_dimensions] = None

                    for n in range(5):
                        dim_n_fieldname = self.site.dimensions[n+8].longname
                        dim_n_structure = record[dim_n_fieldname]
                        if physids_included:
                            #Strip the physid of the structure off
                            dim_n_structure = dim_n_structure.split('(')[0].strip()
                        structures[n+8] = dim_n_structure

                    shortname          = convert_string(record['Shortname'])
                    longname           = convert_string(record['Longname'])
                    description        = convert_string(record['Description'])
                    if physids_included:
                        physid         = int(record['ID'].strip())
                    else:
                        physid         = None

                    #TODO - correct parameters
                    viewpoint = Viewpoint(site         = self.site
                                         ,shortname    = shortname
                                         ,longname     = longname
                                         ,description  = description
                                         ,structure_0  = structures[0]
                                         ,structure_1  = structures[1]
                                         ,structure_2  = structures[2]
                                         ,structure_3  = structures[3]
                                         ,structure_4  = structures[4]
                                         ,structure_5  = structures[5]
                                         ,structure_6  = structures[6]
                                         ,structure_7  = structures[7]
                                         ,structure_8  = structures[8]
                                         ,structure_9  = structures[9]
                                         ,structure_10 = structures[10]
                                         ,structure_11 = structures[11]
                                         ,structure_12 = structures[12]
                                         ,physid       = physid
                                         )

                    viewpoint_list.append(viewpoint)


                for viewpoint in viewpoint_list:
                    #Attempt to keep the same object references for previously used elements
                    try:
                        current_viewpoint = self._viewpoints[viewpoint.shortname]

                        #If the viewpoint already exists, set the viewpoint's internals to be the same as the new viewpoint, but make sure we keep the same object references
                        current_viewpoint.longname       = viewpoint.longname
                        current_viewpoint.description    = viewpoint.description
                        current_viewpoint.structures[0]  = viewpoint.structures[0]
                        current_viewpoint.structures[1]  = viewpoint.structures[1]
                        current_viewpoint.structures[2]  = viewpoint.structures[2]
                        current_viewpoint.structures[3]  = viewpoint.structures[3]
                        current_viewpoint.structures[4]  = viewpoint.structures[4]
                        current_viewpoint.structures[5]  = viewpoint.structures[5]
                        current_viewpoint.structures[6]  = viewpoint.structures[6]
                        current_viewpoint.structures[7]  = viewpoint.structures[7]
                        current_viewpoint.structures[8]  = viewpoint.structures[8]
                        current_viewpoint.structures[9]  = viewpoint.structures[9]
                        current_viewpoint.structures[10] = viewpoint.structures[10]
                        current_viewpoint.structures[11] = viewpoint.structures[11]
                        current_viewpoint.structures[12] = viewpoint.structures[12]

                    except KeyError:

                        self._viewpoints[viewpoint.shortname] = viewpoint

            else:
                raise mpex.EmpowerImporterVersionError('Functionality not available in this Empower Importer version {} need at least {}'.format('.'.join([str(v) for v in self.dimension.site.importer_version]), '9.5.18.1943'))

        except Exception:
            self._viewpoints_read = False
            raise

    def values(self):
        if not self._viewpoints_read:
            self._load_viewpoints()

        return self._viewpoints.values()

    def items(self):
        if not self._viewpoints_read:
            self._load_viewpoints()

        return self._viewpoints.items()

    def keys(self):
        if not self._viewpoints_read:
            self._load_viewpoints()

        return self._viewpoints.keys()

    def __len__(self):
        if not self._viewpoints_read:
            self._load_viewpoints()

        return len(self._viewpoints)

    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self)) )

class Dimension(object):
    '''
    An Empower Dimension

    Manipulate a dimension's elements, structures and security using this class.
    '''
    def __init__(self
                ,site
                ,index
                ):

        self.site             = site
        self.index            = index


        ##We will get the field names by exporting the dimension from the site
        #self._field_names=[]

        self._structure_getter = _StructureGetter(dimension = self)
        self._elements_getter  = _ElementsGetter( dimension = self)

        #When creating elements for the first time we may rely on
        self._elements_without_shortnames = []

        self._fields = _DimensionFieldsGetter(dimension=self)

        #Dimensions have a name - at the time of writing (2018-08-21) these can't be read from Empower and must be set by the user
        self._longname = None

    @property
    def longname(self):
        '''The Dimension's Empower longname'''
        if self._longname is None:
            try:
                #provoke a structures lazy load which is the best way of getting dimension names at the moment
                self.structures.values()
            except AttributeError:
                pass
        return self._longname

    @longname.setter
    def longname(self,val):
        self._longname=val

    @property
    def structures(self):
        '''Structures for the dimension - by shortname

        .structures behaves like a dictionary (you can call .values(), .items() and .keys() on it), but when iterated over it yields Structures one after the other.

        A single Structure can be retrieved from .structures by indexing it on its shortname, e.g.:
        >>> site.dimension[0].structures['SPAM']
        '''
        #The _structure_getter implements __get_item__() to provide the subscriptable interface - and provide lazy loading
        return self._structure_getter

    @structures.setter
    def structures(self,val):
        if isinstance(val,_StructureGetter):
            self._structure_getter = val
        else:
            raise AttributeError('Dimension.structures cannot be set except back to itself in a += operation')

    @property
    def elements(self):
        '''Shortname indexed elements for the dimension

        .elements behaves like a dictionary (you can call .values(), .items() and .keys() on it), but when iterated over it yields Elements one after the other.

        A single element can be retrieved from .elements by indexing it on its shortname, e.g.:
        >>> site.dimension[0].elements['MYSHORTCO2']
        '''
        #The _elements_getter implements __get_item__() to provide the subscriptable interface - and provide lazy loading
        return self._elements_getter

    @elements.setter
    def elements(self,val):
        if val == self._elements_getter:
            pass
        else:
            raise AttributeError("can't set attribute")

    @property
    def fields(self):
        '''return a the field definitions of the dimension as an ordered dictionary'''
        #load elements to get fields, because there is no direct way of getting fields
        if not self._elements_getter._elements_read:
            self._elements_getter._load_elements(debug=self.site._debug)

        return self._fields

    @fields.setter
    def fields(self,val):
        pass

    #def _synchronise_elements_and_structures(self):
    #    pass
    #

    def get(self, path):
        '''Return a StructureElement within a Dimension by passing in the path as a string

        :path: A string describing the path to a StructureElement within a Dimension

        e.g.
        >>> site.dimension[0].get('SPAM.EGGS/BACON')

        Will return the 'BACON' Structure Element from the 'SPAM' Structure
        '''
        if not '.' in path:
            raise ValueError('path parameter must be a valid path to a StructureElement. Path must contain a "." character e.g. SPAM.EGGS/BACON- found {}'.format(path))

        path_parts = path.split('/')
        structure_and_hierarchy = path_parts[0]
        rest_of_path = ''
        if len(path_parts) > 1:
            rest_of_path = '/'+('/'.join(path_parts[1:]))
            
        #Split on .  We would expect 2 parts but might get more if there are more. Arrange these into the various combinations e.g. Test1.Test2.Test3 could be Test1 and Test2.Test3 or Test1.Test2 and Test3
        # The first valid combo wins
        structure_and_hierarchy_split_on_dots = structure_and_hierarchy.split('.')
        
        for n in range(len(structure_and_hierarchy_split_on_dots)):
            structure_str = '.'.join(structure_and_hierarchy_split_on_dots[0:n])
            hierarchy_str = '.'.join(structure_and_hierarchy_split_on_dots[n:])
            try:
                return self.structures[structure_str].descendants[hierarchy_str+rest_of_path]             
            except KeyError:
                pass
        

        raise KeyError('Path: '+path+' not found in dimension '+str(self.index)) 



    def make_elements_from_dataframe(self,dataframe,primary_key_columns=['Short Name'],deduplicate='last',longname_shortname_rule=None,subsequent_shortname_rule=None,sync=True,structure_shortname=None,structure_root_element_shortname=None,parent_key_column=None, parent_key_field_name=None,include_parent_key_column_in_element=False):
        '''Make new elements from a pandas Dataframe
        columns should be ['Short Name','Long Name','Description','Group Only','Calculation Status','Calculation','Colour','Measure Element'] followed by field shortnames
        If shortname is missing it will be generated from the long name
        All other columns should relate to a field shortname
        If parent_key_column is set

        :param primary_key_columns: the columns to be used when deciding what is a unique element. Should be a list of field names of the element
        :param deduplicate: remove duplicates based on the primary key name - set to False if you have manually removed duplicates already. Otherwise choose 'first' or 'last' to create dimension elements from the the first or last instance of the primary_key_field
        :param structure_shortname: Must be set if we want to create a structure from this dataframe simultaneously with creating the elements.
        :param parent_key_column:
        :param parent_key_field_name:

        :param include_parent_key_column_in_element: If set to false the parent_key_column will be only used to create the nominated structure. If set to True, the parent key column will be also saved as a field in the Element
        '''
        #SN
        #LN
        #PHYSID

        self.elements.merge(source = dataframe, keys = primary_key_columns)


        #If we are making the structure, join in the sent in dataframe to the dataframe imported from Empower, to get the canonical Empower shortnames
        #Join on the Key Field we previously used
        if structure_shortname is not None:
            if deduplicate is None:
                #We will have copied already if deduplicate was set - otherwise we need to copy for the first time
                dataframe = dataframe[primary_key_columns+[parent_key_column]].copy()
            else:
                dataframe = dataframe[primary_key_columns+[parent_key_column]]

            child_parent_dataframe = pd.merge(how   = 'inner'
                                             ,left  = self.elements.dataframe
                                             ,right = dataframe.rename(columns = { parent_key_column : 'Parent Short Name' })
                                             ,on    = primary_key_columns
                                             )

            self.make_structure_from_dataframe(dataframe                        = child_parent_dataframe
                                              ,structure_shortname              = structure_shortname
                                              ,structure_root_element_shortname = structure_root_element_shortname
                                              ,parent_key_column                = parent_key_column
                                              ,parent_key_field_name            = parent_key_field_name
                                              ,sync                             = sync
                                              )

    def make_structure_from_dataframe(self,dataframe,structure_shortname,structure_root_element_shortname=None,parent_key_column='Parent Short Name',parent_key_field_name='Short Name',sync=True):
        '''Make a structure from a pandas Dataframe
        columns should be ['Short Name'] and a parent key column (default 'Parent Short Name'). The key field of the parent should be specified - default is 'Short Name'

        :param structure_root_element_shortname: only needs to be set if there are multiple root elements in the structure
        :param parent_key_column: column name (in dataframe) which refers to the parent
        :param parent_key_field_name: the field to be used (in the parent element) when deciding what is a unique element
        '''

        parent_key_column_is_found = False
        short_name_column_is_found = False
        for c in dataframe.columns:
            if c == parent_key_column:
                parent_key_column_is_found  = True
            if c == 'Short Name':
                short_name_column_is_found = True

        if not short_name_column_is_found:
            raise ValueError('make_structure_from_dataframe(): The dataframe parameter must contain a dataframe with a "Short Name" column. Columns in the dataframe are: '+str(dataframe.columns))

        if not parent_key_column_is_found:
            raise ValueError('make_structure_from_dataframe(): The dataframe parameter must contain a dataframe with a "'+parent_key_column+'" column. Columns in the dataframe are: '+str(dataframe.columns)+'\n'+'Ensure this column is in the dataframe or set the parent_key_column parameter to a column that is in the dataframe, and denotes the parent key')

        #Parents are not always denoted by their shortname (after all we may not have known it at the point the original dataframe was passed in
        parent_lookup = {el.fields[parent_key_field_name]:el.shortname for el in self.elements.values()}

        #Get the structure - we'll update it
        structure = self.structures[structure_shortname]

        if structure is None:
            raise KeyError('There is no structure with shortname "'+structure_shortname+'" in dimension')

        #Child shortcode to parent shortcode lookup
        child_parents={}

        for d in dataframe[['Short Name',parent_key_column]].itertuples(index=False):
            #For some reason itertuples isn't coming back with the column names - create a dictionary using the original column anmes of the dictionary
            child_shortname  = d[0]

            if d[1] is not None and d[1] != '':
                parent_shortname = parent_lookup[d[1]]
                try:
                    parent_elements = structure.get_elements(parent_shortname)
                except KeyError:
                    #Get the Element
                    element = self.elements[parent_shortname]
                    #Create the StructureElement
                    structure._add_element(Structure_Element(element=element))
                    parent_elements = structure.get_elements(parent_shortname)

                parent_element = parent_elements[0]

            else:
                parent_element = None


            try:
                child_elements = structure.get_elements(child_shortname)
                if child_elements is None or child_elements == []:
                    found_child_elements = False
                else:
                    found_child_elements = True
            except KeyError:
                found_child_elements = False

            if not found_child_elements:
                #Get the Element
                element = self.elements[child_shortname]
                #Create the StructureElement
                structure._add_element(StructureElement(element=element))
                child_elements = structure.get_elements(child_shortname)

            if parent_element is not None:
                structure.set_child_element_parent(child = child_elements[0], parent = parent_element)
            else:
                structure.set_root_element(child_elements[0])

        if sync:
            structure.synchronise()

    def synchronise(self,reexport=True,reimport=False,primary_key_fields=['Short Name']):
        '''Synchronise the Elements in the Dimension with the Empower Site.

        New elements will be created in Empower and changed field values will be updated in the Empower Site
        '''

        self.elements.synchronise(reexport=reexport,reimport=reimport,primary_key_fields=primary_key_fields)

    @property
    def element_dataframe(self):
        raise SystemError('This property is deprecated - use Dimension.elements.dataframe instead')


    def _get_simple_translation_df(self,output_column_name,field_shortname):
        if field_shortname is None:
            df = self.elements.dataframe[['ID','Short Name','Long Name']].copy()
        else:
            df = self.elements.dataframe[['ID','Short Name','Long Name',field_shortname]].copy()

        df.rename(columns={col:'LKUP '+col for col in df.columns},inplace=True)
        df[output_column_name]=df['LKUP ID']
        return df

    def _load_security(self):
        #The _ElementsGetter determines if security is read
        self.elements._load_security()

class Element(object):
    '''An Empower Element. The Element is as would be found on the [All] Structure in Empower.

    Element's don't have parents or children - that is what a StructureElement has.
    '''
    def __init__(self
                ,shortname=None
                ,longname=None
                ,description=None
                ,physid=None
                ,group_only=None
                ,calculation_status=None
                ,calculation=None
                ,colour=None
                ,measure=None
                ,fields=None
                ,override_shortname_length_rule = False
                ,dimension = None
                ):
        '''Create a new Empower Element.

        :param shortname: A ten-character (or shorter) string with the shortname for the Element. If this is not set, Empower will create one when this Element is synchronised.
        :param longname: The name of the Element, as will be displayed in dashboards
        :param description: A longer description of the Element, as stored in Empower
        :param physid: the physical identifier of the Empower element - there is no need to set this, as Empower will set it automatically when this Element is synchronised.
        :param group_only: Set to 'Group' if this is a group-only Element
        :param calculation_status: 'Real' or 'Calculated'
        :param calculation: The Empower calculation for this element, as a string. This can be None for non-calculated elements
        :param colour: Empower colour of the Element
        :param measure:  Empower measure for the Element
        :param fields: A dictionary of fields. Keys must be the field longname as used in Empower.
        :param override_shortname_length_rule: Allows elements to be created in python with shortnames longer than 10 characters. These shortnames will be overwritten by Empower when the elements are synchronised with Empower.
        :param dimension: pympx.Dimension object that this element belongs to
        '''
        if fields is None:
            fields = {}
        nlimit=40   
        
        if shortname is not None and len(shortname) > nlimit and not override_shortname_length_rule:
            msg='Elements shortnames must be no longer than nlimit characters. Shortname:'+str(shortname)+' is '+str(len(shortname))+' characters long'
            log.error(msg)
            raise mpex.CompletelyLoggedError(msg)

        #set physid first as it is drives .mastered and si not a field
        self.physid             = physid

        #Must set dimension before fields - or we cannot set fields correctly
        self.dimension = dimension

        ##initialise the fields dictionary
        ##any keys related to the attributes of Element will be overwritten when the attributes are set
        #print('shortname '+str(shortname)+' physid '+str(physid)+ ' element '+str(self))
        #if shortname is None:
        #    raise SystemError()
        self._fields = _FieldsGetter(self,fields,initialise_as_edited = physid is None)

        #Set the internal elements - then we can use the setters for the externally visible version of the same
        #This way we can keep the fields dictionary in sync with the internal elements
        self._shortname          = None
        self._longname           = None
        self._description        = None
        self._group_only         = None
        self._calculation_status = None
        self._calculation        = None
        #physid calculation is for comparing to the Empower export
        self._physid_calculation = None
        self._colour             = None
        self._measure            = None

        self.shortname  = shortname
        #if longname is None:
        #    self.longname   = shortname
        #else:
        self.longname   = longname

        #if description is None:
        #    self.description    = self._longname
        #else:
        self.description    = description

        #print('set description to: "'+self.description+'" from: "'+str(description)+'"')

        self.group_only         = group_only
        self.calculation_status = calculation_status
        self.calculation        = calculation
        self.colour             = colour
        if self.dimension is None or self.dimension.index < 8:
            self.measure            = measure

        #Set self.synched at the end - when creating synched is true if it has been mastered
        self._synched           = self.mastered
        self._edited            = False

        if not physid is None:
            self._fields.reset_edit_status()

        self._security          = None

    @property
    def mastered(self):
        '''True if this element has been created in Empower, False otherwise. See .synched for the synchronisation (i.e. saved) status'''
        return not self.physid is None

    @property
    def synched(self):
        '''True if all of the attributes of this element have been synchronised with Empower. Will be true after reading the Element from Empower, or after synchronisation. Will be False if the Element has been edited, or does not exist in Empower at all.'''
        return self.mastered and not self.edited

    @property
    def edited(self):
        '''True if this Element has been changed since creation, or since reading it from Empower.'''
        return self._edited

    @property
    def shortcode(self):
        '''Synonym of shortname, the Empower shortname for this Element'''
        return self.shortname

    @shortcode.setter
    def shortcode(self,val):
        self.shortname=val

    @property
    def shortname(self):
        '''The Empower 'Short Name' for this Element'''
        return self._shortname

    @shortname.setter
    def shortname(self,val):
        self._shortname=val
        self._fields['Short Name']=self._shortname

    @property
    def longname(self):
        '''The Empower' Long Name' for this Element'''
        return self._longname

    @longname.setter
    def longname(self,val):
        self._longname=val
        self._fields['Long Name']=self._longname

    @property
    def description(self):
        '''The Empower 'Description' for this Element'''
        return self._description

    @description.setter
    def description(self,val):
        self._description=val
        self._fields['Description']=self._description

    @property
    def group_only(self):
        '''The Empower 'Group Only' for this Element, will be 'Group' or None'''
        return self._group_only

    @group_only.setter
    def group_only(self,val):
        self._group_only=val
        self._fields['Group Only']=self._group_only

    @property
    def calculation_status(self):
        '''The Empower 'Calculation Status' for this Element, will be 'Real' or 'Calculated' '''
        return self._calculation_status

    @calculation_status.setter
    def calculation_status(self,val):
        self._calculation_status=val
        self._fields['Calculation Status']=self._calculation_status

    @property
    def calculation(self):
        '''A string containing the Empower 'Calculation' for this Element. May be None '''
        return self._calculation

    @calculation.setter
    def calculation(self,val):
        self._calculation=val
        #print(self.shortname)
        #try:
        #    print(self._fields._field_edits['Calculation'])
        #except KeyError:
        #    print(False)
        self._fields['Calculation']=self._calculation
        #print(self._fields._field_edits['Calculation'])

    @property
    def colour(self):
        '''The Empower 'Colour' of this Element'''
        return self._colour

    @colour.setter
    def colour(self,val):
        self._colour=val
        self._fields['Colour']=self._colour

    @property
    def measure(self):
        '''The Empower 'Measure' for this Element'''
        return self._measure

    @measure.setter
    def measure(self,val):
        self._measure=val
        self._fields['Measure Element']=self._measure

    @property
    def fields(self):
        '''Returns a dictionary-like object containing the Empower fields (a.k.a. attributes) for this Element. Entries are of the form Long Name:String Value '''
        #Return a special field setter, so that changing the value updates the _synched flag

        return self._fields

    @property
    def date(self):
        '''Applies to time elements only. A read only property that returns a date based on year, month, day and interval_type'''
        return None

    @property
    def year(self):
        if self.date is not None:
            return self.date.year
        else:
            return None

    @property
    def month(self):
        if self.date is not None:
            return self.date.month
        else:
            return None

    @property
    def quarter(self):
        if self.date is not None:
            return (self.date.month -1) // 3 +1
        else:
            return None

    @property
    def day(self):
        if self.date is not None:
            return self.date.day
        else:
            return None

    @property
    def empower_period_number(self):
        return None

    @property
    def interval_index(self):
        return None

    def copy(self):
        '''Create a copy of self, not including the physid or shortname'''
        return Element(longname             = self.longname
                      ,shortname            = None
                      ,description          = self.description
                      ,group_only           = self.group_only
                      ,calculation_status   = self.calculation_status
                      ,calculation          = self.calculation
                      ,colour               = self.colour
                      ,measure              = self.measure
                      ,fields               = dict(self.fields)
                      ,dimension            = self.dimension
                      )

    def merge(self,other,fields_to_merge=None):
        '''Merge another element into this one'''

        if other.physid is not None and self.physid is not None and self.physid != other.physid:
            raise ValueError("Cannot merge two elements with different physids: {} into {}, on dimension {}, zero based index {}. Check these elements don't have empty shortnames".format(other.physid,self.physid,self.dimension.longname,self.dimension.index))

        if self.physid is None:

            self.physid = other.physid
            #Get the canonical shortname when merging in the physid
            self.shortname = other.shortname

        if self.shortname is None:
            self.shortname = other.shortname

        if other.longname is not None:
            self.longname             = other.longname
        if other.description is not None:
            self.description          = other.description
        if other.group_only is not None:
            self.group_only           = other.group_only
        if other.calculation_status is not None:
            self.calculation_status   = other.calculation_status
        if other.calculation is not None:
            self.calculation          = other.calculation
        if other.colour is not None:
            self.colour               = other.colour
        if other.measure is not None:
            self.measure              = other.measure
        for k,v in other.fields.items():
            #Merge in fields that we want to explicitly change, unless we have not specified fields explicitly, in which case merge in non-NULL fields
            if (fields_to_merge is not None and k in fields_to_merge) or (fields_to_merge is None and v is not None):
                self.fields[k] = v

    @property
    def security(self):
        '''Returns a Security object, which has python sets of users shortnames for .viewers, .modifiers and .data_viewers'''

        #Security is lazily loaded
        if self._security is None:
            #Create a new element security object
            self._security = ElementSecurity(element = self)
            #Load security to overwrite with correct values (if they exist)
            #This will only laod if not already loaded
            self.dimension.elements._load_security()

        return self._security

    def __repr__(self):
        return '<{} object, shortname {}, longname {} at {}>'.format(self.__class__.__name__,self.shortname,self.longname,hex(id(self)))

    def __eq__(self,other):
        #PYM-36 fix element should only be equal to another element with same dimension and shortname, excluding None unless same object id
        try:
            return self.shortname==other.shortname and (id(self) == id(other) or (self.dimension == other.dimension and isinstance(other, Element) and self.shortname is not None))
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.shortname)

class TimeElement(Element):

    def __init__(self,interval_index,shortname,year,month=None,day=None,longname=None,description=None,physid=None,dimension=None):

        if interval_index not in [llu.EMPOWER_YEAR_CONSTANT,llu.EMPOWER_HALFYEAR_CONSTANT,llu.EMPOWER_QUARTER_CONSTANT,llu.EMPOWER_MONTH_CONSTANT,llu.EMPOWER_WEEK_CONSTANT,llu.EMPOWER_DAY_CONSTANT,'Y','H','Q','M','W','D']:
            #Programming error
            raise AttributeError("interval_index must be in the Empower interval index range from 0 to 5 or one of 'Y','H','Q','M,'W' or 'D' - got:"+str(interval_index))
        #TODO add extra checking, add logic (elsewheer for creating weeks and days

        #Transform interval_index to a number
        interval_index = {llu.EMPOWER_YEAR_CONSTANT:     llu.EMPOWER_YEAR_CONSTANT
                         ,llu.EMPOWER_HALFYEAR_CONSTANT: llu.EMPOWER_HALFYEAR_CONSTANT
                         ,llu.EMPOWER_QUARTER_CONSTANT:  llu.EMPOWER_QUARTER_CONSTANT
                         ,llu.EMPOWER_MONTH_CONSTANT:    llu.EMPOWER_MONTH_CONSTANT
                         ,llu.EMPOWER_WEEK_CONSTANT:     llu.EMPOWER_WEEK_CONSTANT
                         ,llu.EMPOWER_DAY_CONSTANT:      llu.EMPOWER_DAY_CONSTANT
                         ,'Y': llu.EMPOWER_YEAR_CONSTANT
                         ,'H': llu.EMPOWER_HALFYEAR_CONSTANT
                         ,'Q': llu.EMPOWER_QUARTER_CONSTANT
                         ,'M': llu.EMPOWER_MONTH_CONSTANT
                         ,'W': llu.EMPOWER_WEEK_CONSTANT
                         ,'D': llu.EMPOWER_DAY_CONSTANT}[interval_index]

        super(TimeElement, self).__init__(shortname=shortname,longname=longname,description=description,physid=physid,dimension=dimension)

        self._year           = year
        self._month          = month
        self._day            = day
        self._interval_index = interval_index

        self._interval_amount = 1 # Default
        self._resolution      = 1 # Default
        self._offset          = None

        if self._month is None:
            self._month = 1

        if self._day is None:
            self._day = 1
    
        self._date = datetime.datetime(self._year, self._month, self._day)
        
    @property
    def date(self):
        return self._date

    @property
    def interval_index(self):
        return self._interval_index

    @property
    def interval(self):

        return {llu.EMPOWER_YEAR_CONSTANT:    'Year'
               ,llu.EMPOWER_HALFYEAR_CONSTANT:'Half-year'
               ,llu.EMPOWER_QUARTER_CONSTANT: 'Quarter'
               ,llu.EMPOWER_MONTH_CONSTANT:   'Month'
               ,llu.EMPOWER_WEEK_CONSTANT:    'Week'
               ,llu.EMPOWER_DAY_CONSTANT:     'Day'
               }[self.interval_index]


    @property
    def interval_amount(self):
        return self._interval_amount

    @property
    def resolution(self):
        return self._resolution

    @property
    def offset(self):
        return self._offset


    @property
    def empower_period_number(self):
        '''Applies to time elements only. A read only property that returns the Empower Period type number (e.g. 3 for a Month)'''
        return self.interval_index

    def copy(self):
        '''Create a copy of self, not including the physid or shortname'''
        return TimeElement(longname             = self.longname
                      ,shortname            = None
                      ,description          = self.description
                      ,interval_index           = self.interval_index
                      ,year   = self.year
                      ,month          = self.month
                      ,day               = self.day
                      ,week               = self.week
                      ,quarter               = self.quarter
                      ,half               = self.half
                      ,dimension            = self.dimension
                      )

class Structure(object):

    def __init__(self,shortname=None,longname=None,dimension_index=None,dimension=None,description=None):

        self._shortname=shortname
        self._longname =longname
        if self._longname is None:
            self._longname = self._shortname

        self.dimension = dimension
        if self.dimension:
            self.dimension_index = self.dimension.index
        else:
            self.dimension_index = dimension_index

        self._description = description

        #Dictionary of shortname, element pairs
        #allow root elements to behave like a dictionary - e.g. structure.hierarchies['EGGS']
        self._hierarchies = _HierarchiesGetter(structure = self)
        #log.info('Set _hierarchies')
        #log.info(str(self._hierarchies ))

        self._descendants = _StructureDescendantsGetter(structure = self)

        self._hierarchies_read = False

        self._exists_in_empower = False


    @property
    def hierarchies(self):
        '''Get a dictionary-like object contianing all of the hierarchies (top level StructureElements) in this Structure

        E.g. to get the root StructureElement for Structure my_structure, with shortcode 'SPAM':

        >>> my_structure.hierarchies['SPAM']
        '''

        if not self._hierarchies_read:
            #log.info('_load_structure 3035')
            if self.dimension is not None:
                if not self.shortcode: print('shortcode is None')
                assert self.shortcode is not None

                self.dimension.structures._load_structure(self.shortcode,old_structure = self)

        return self._hierarchies

    @hierarchies.setter
    def hierarchies(self,val):
        if isinstance(val,_HierarchiesGetter):
            self._hierarchies = val
        else:
            self._hierarchies.clear()
            #log.info('Setting hierarchies to {}'.format(val))
            self._hierarchies.append(val)

    def _get_elements_generator(self,shortname):
        '''Get all of the elements in this structure with the given shortname'''
        #Keep track of whether an element was passed in to help with debugging
        element_was_passed_in=False

        #If an element has been passed in, use the element's shortname
        try:
            shortname=shortname.shortname
            element_was_passed_in=True
        except AttributeError:
            pass

        #TODO -check that shortname is not None
        if shortname is None:
            #Programming error
            if element_was_passed_in:
                raise ValueError('element.shortname must have a value. None was supplied. debugging information: An utils.Element instance was passed in as the shortname parameter to function get_element()')
            else:
                raise ValueError('shortname must have a value. None was supplied.')
        try:
            shortname=shortname.shortname
        except AttributeError:
            pass

        for h in self.hierarchies:
            yield from h.get_elements(shortname)

    def get_elements(self,shortname):
        '''Get all of the elements in this structure with the given shortname'''
        #PYM-67, get_elements on a hierarchy can be indexed - people assume the same for a structure
        return list(self._get_elements_generator(shortname))

    def get_element(self,shortname):
        '''Deprecated, Don't use this function, You probably want .get_root_element(), Failing that you may want .get_elements('some_sn')[0].'''
        raise TypeError("Don't use this function. You probably want get_root_element. Failing that you may want get_elements")
        #The issue is that there can be multiple StructureElements in a given structure with the same shortname

    def get_root_element(self,shortname):
        '''Get the root element in this structure with the given shortname'''
        #Keep track of whether an element was passed in to help with debugging
        element_was_passed_in=False

        #If an element has been passed in, use the element's shortname
        try:
            shortname=shortname.shortname
            element_was_passed_in=True
        except AttributeError:
            pass

        #TODO -check that shortname is not None
        if shortname is None:
            #Programming error
            if element_was_passed_in:
                raise ValueError('element.shortname must have a value. None was supplied. debugging information: An utils.Element instance was passed in as the shortname parameter to function get_root_element()')
            else:
                raise ValueError('shortname must have a value. None was supplied.')
        try:
            shortname=shortname.shortname
        except AttributeError:
            pass

        #Return the first root element with the given shortname
        for structure_element in self.hierarchies.values():
            if structure_element.shortname == shortname:
                return structure_element

        return None

    def _add_element(self,structure_element):
        '''Deprecated. Add an element to the structure, but don't specify where.
        '''
        if structure_element.is_root:
            self._hierarchies.append(structure_element)


        if structure_element.structure is None:
            structure_element.structure = self

        log.debug('Added StructureElement '+structure_element.shortname+' to Structure')

    def _remove_element(self,structure_element):
        '''Deprecated.
        Remove a StructureElement in this Structure from its parent

        StructureElement.cut() does the same, and returns the StructureElement to be used elsewhere.
        '''
        if structure_element.is_root:
            raise TypeError("Can't remove the root element. Change the root element if you need to remove this element")
        else:
            structure_element.parent.remove_child(structure_element)

    def _set_sort_function(self,sort_function):
        '''Deprecated. The sort function is no longer used'''
        raise TypeError("Don't use this function. Set the sort function on the StructureElement instead")

    @property
    def descendants(self):
        '''Deprecated, Don't use this function, To visit all of the descendants, simply use .walk()
        '''
        return self._descendants

    #@property
    #def descendant(self,item):
    #    return self.descendants[item][0]


    @property
    def elements(self):
        '''Deprecated. Don't use this function - use walk() instead'''
        #elements sounds like a dictionary (use get_elements to do that) or a list (use walk elements for that))
        raise TypeError("Don't use this function - use walk() instead")

    @property
    def root_elements(self):
        '''Iterate over all of the hierarchies (root level structure elements) in turn.

        This proprty does not descend into those hierarchies - use .walk() to do that.

        Does the same thing as .hierarchies.values()
        '''
        for e in self.hierarchies.values():
            yield e

    @property
    def shortcode(self):
        '''The shortname for this Structure. Synonym for .shortname'''
        return self._shortname

    @property
    def shortname(self):
        '''The shortname for this Structure.'''
        return self._shortname

    @property
    def longname(self):
        '''The longname for this Structure.'''
        return self._longname

    @longname.setter
    def longname(self,val):
        self._longname = val

    @property
    def description(self):
        '''The Empower description for this Structure.'''

        return self._description

    @description.setter
    def description(self,val):
        '''The description for this Structure.'''
        self._description = val

    def add_child_element_parent(self,child,parent):
        '''Add the child element to have a given parent. This is the one way we can set elements in a structure.

        A more common way (and the preferred way) to set a child element would be to use the StructureElement directly using StructureElement.children .

        :param child: Child element. StructureElement
        :param parent: Parent element. StructureElement
        '''

        if child is None:
            #Programming error
            raise ValueError('child is None. Child should be a valid StructureElement')

        child_element=child
        parent_element=parent

        try:
            child_element.add_parent(parent_element)
            if child_element.parent is not None:
                log.verbose(child_element.shortname + '->' + str(child_element.parent.shortname))
            else:
                log.verbose(child_element.shortname + '->None')

        except AttributeError as e:
            log.error('Could not find the child_element in the hierarchy:'+str(child_element))
            raise mpex.CompletelyLoggedError(e)

    def set_child_element_parent(self,child,parent):
        '''Synonym for add_child_element_parent()
        This function will be deprecated in a future release of pympx
        '''

        if child is None:
            #Programming error
            raise ValueError('child is None. Child should be a valid element shortname')

        child_element=child
        parent_element=parent

        try:
            child_element.set_parent(parent_element)
            if child_element.parent is not None:
                log.verbose(child_element.shortname + '->' + str(child_element.parent.shortname))
            else:
                log.verbose(child_element.shortname + '->None')

        except AttributeError as e:
            #Programming Error
            log.error('Could not find the child_element in the hierarchy:'+str(child_element))
            raise e

    def walk_elements(self):
        '''Deprecated, Use .walk() instead.'''
        yield from self.walk()

    def walk(self):
        '''Step through every element in the structure in turn. Start with the first root element and walk trunk to leaf, and then on to next leaf
        Yield elements as the walk goes on.
        '''
        for e in list(self.root_elements):
            yield from e.walk(permissive=False)

    def print_hierarchy(self):
        '''Deprecated, Use the python print() function instead.
        Prints out the Structure in text form.

        >>> print(site.dimensions[0].structures['SPAM'])
        SPAM
        +-EGGS
          +-BACON
        '''
        for e in list(self.root_elements):
            e.print_hierarchy()

    def synchronise(self):
        '''Synchronise this structure with the Empower site.
        Changes made to this structure will be written back to the Empower site that this structure belongs to.
        '''

        #debug flag determines whether we wish to save to file in order to debug what has gone wrong wih an import
        debug = self.dimension.site._debug

        #In debug mode, write the output elements to a working file for importing into empower
        if debug:
            for dir in [self.dimension.site._empower_dim_import_dir]:

                try:
                    os.makedirs(dir)
                except FileExistsError:
                    pass
                except OSError as e:
                    if e.winerror == 123:
                        raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                    else:
                        raise e
            imported_structure_filepath=os.path.join(self.dimension.site._empower_dim_import_dir,'ImportedDimensionStructure_'+str(self.dimension_index)+'_'+str(self.shortname)+'.tsv')
        else:
            #Create unique named pipes to read and write to
            imported_structure_filepath      = r'\\.\pipe\{}'.format(uuid.uuid4())

        #Import the structure from the working_directory or from pipe
        command_list = self.dimension.site._logon_parameter_importer_commands + \
                       ['set-parameter dimension_index='   + str(self.dimension_index)
                       ,'set-parameter structure_shortname='+ self.shortname
                       ,'load-file-tsv "'+imported_structure_filepath+'"'
                       ,'empower-import-structure "${site}" "${user}" "${password}" ${dimension_index} ${structure_shortname}'
                       ]

        #In debug mode write the data into a tsv file and read it with Importer, putting the structure into Empower
        if debug:
            #Non time dimensions may have fields - write the standard and non standard fields to file and import them
            with open(imported_structure_filepath,'w') as target_file:
                for e in self.walk_elements():
                    target_file.write(e.shortname)
                    target_file.write('\t')
                    target_file.write(str(e.level))
                    target_file.write('\n')

            llu.run_single_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)

        else:
            #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
            #imported_structure_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
            #The merry dance means starting Importer, referencing the pipe, opening the pipe before Importer is properly started
            #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
            #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
            #before we have created it. But we will block on our side until Importer has connected
            proc = None
            try:
                proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=self.dimension.site.empower_importer_executable)

                with llu.outbound_pipe(imported_structure_filepath) as pipe:

                    for e in self.walk_elements():
                        win32file.WriteFile(pipe, str.encode(e.shortname))
                        win32file.WriteFile(pipe, TABBYTES)
                        win32file.WriteFile(pipe, str.encode(str(e.level)))
                        win32file.WriteFile(pipe, NEWLINEBYTES)

                    log.debug("Pipe {} finished writing".format(imported_structure_filepath))

            finally:

                #Check if Importer returned an error and raise it as a python if it did
                llu.complete_no_output_importer_process(proc)

        log.verbose('Wrote Structure: '+self.shortname)

    def __str__(self):

        result = ''
        for h in self.hierarchies:
            result+= str(h)

        return result


    def __len__(self):
        return len([x for x in self.walk()])


class StructureElement(object):
    '''An Element within a Structure.

    StructureElement is one of the most powerful PyMPX classes, allowing Structures to be manipulated in multiple ways. 
    Each StructureElement has a .parent and .children which define where it is in the Structure
    '''

    def __init__(self,parent_structure_element=None,structure=None,element=None,shortname=None,longname=None,physid=None,year=None,month=None,day=None,interval_index=None,is_root=False):
        '''Create a new StructureElement.

        StructureElement is one of the most powerful PyMPX classes, allowing Structures to be manipulated in multiple ways. 
        Each StructureElement has a .parent and .children which define where it is in the Structure

        :param parent_structure_element: The StructureElement that is the parent of this StructureElement
        :param structure: The Empower Structure this StructureElement belongs to. Doesn't need to be set if parent_structure_element has its structure set
        :param element: The Empower Element referred to. An Element can apepar in many StructureElements
        :param shortname: If element is not set, then the shortname of the underlying element. See Element.shortname api documentation for details.
        :param longname: If element is not set, then the longname of the underlying element. See Element.longname api documentation for details.
        :param physid: If element is not set, then the physical ID of the underlying element. See Element.physid api documentation for details.
        :param year: If element is not set, and this has a Time StructureElement, then the year of the underlying element. See Element.year api documentation for details.
        :param month: If element is not set, and this has a Time StructureElement, then the month of the underlying element. See Element.month api documentation for details.
        :param day: If element is not set, and this has a Time StructureElement, then the day of the underlying element. See Element.day api documentation for details.
        :param interval_index: If element is not set, and this has a Time StructureElement, then the interval_index of the underlying element. See Element.interval_index api documentation for details.
        :param is_root: Set this to True if the StructureElement is a root element in the hierarchy. This will automatically get set to False once a parent is set on this Element.

        '''
        assert shortname is not None or element is not None

        self._structure = None

        self._parent_structure_element=None
        self._child_structure_elements = []


        #add self to structure
        if parent_structure_element is not None:
            self.structure=parent_structure_element.structure
        elif structure is not None:
            self.structure=structure

        self._element = None

        if element is not None:
            self.element=element
        else:
            #initialise the Element
            if year is not None:
                self.element=TimeElement(longname=longname
                                        ,year=year
                                        ,month=month
                                        ,day=day
                                        ,interval_index=interval_index
                                        ,dimension=self.dimension
                                        )
            else:
                try:
                    self.element = self.structure.dimension.elements[shortname]
                except KeyError:

                    self.element=Element(shortname=shortname
                                        ,longname=longname
                                        ,physid=physid
                                        ,dimension=self.structure.dimension
                                        )

        self.is_root=is_root

        #Set parent after we have created the Element - otherwise it doesn't work
        self.set_parent(parent_structure_element)

        if self.structure is not None:
            self.structure._add_element(self)

        #Magic object which makes children behave as we would want them to
        self._children = StructureElementChildren(self)

        #Magic object which makes descendants behave as we would want them to
        self._descendants = _StructureElementDescendantsGetter(self)

        self.sort_function=None


    def set_sort_function(self,sort_function):
        '''Deprecated - the sort function is no longer used'''
        self.sort_function=sort_function

    @property
    def structure(self):
        '''The Empower Structure that this StructureElemtn belongs to. When this is set, all children have their structure set to the same Structure'''
        return self._structure

    @structure.setter
    def structure(self,val):
        self._structure = val

        #If we have set up children already, then change their structure
        #If not, we will change the children's structure when they get set
        try:
            for ch in self.children:
                ch.structure = val
        except AttributeError:
            pass

    @property
    def element(self):
        '''The Empower Element underpinning this StructureElement'''
        return self._element

    @element.setter
    def element(self,val):

        try:
            val = self.structure.dimension.elements[val.shortcode]
        except KeyError:
            pass
        except AttributeError:
            try:
                val = val.dimension.elements[val.shortcode]
            except KeyError:
                    pass

        if not val.mastered:
            raise AttributeError("Cannot set a StructureElement's .element until that Element has been synchronised. Use Dimension.elements.synchronise() before adding the element shortname:{}, longname: {} mastered: {}, fields: {}".format(val.shortcode,val.longname,val.mastered,dict(val.fields)))

        self._element =val

    @property
    def shortcode(self):
        '''The shortname of the Empower Element underpinning this StructureElement'''
        return self.element.shortname

    @shortcode.setter
    def shortcode(self,val):
        self.element.shortname=val

    @property
    def shortname(self):
        '''The shortname of the Empower Element underpinning this StructureElement'''
        return self.element.shortname

    @shortname.setter
    def shortname(self,val):
        self.element.shortname=val

    @property
    def longname(self):
        '''The longname of the Empower Element underpinning this StructureElement'''
        return self.element.longname

    @longname.setter
    def longname(self,val):
        self.element.longname=val

    @property
    def description(self):
        '''The description of the Empower Element underpinning this StructureElement'''
        return self.element.description

    @description.setter
    def description(self,val):
        self.element.description=val

    @property
    def group_only(self):
        ''''Group' if this is a Group Only StructureElement. A GroupOnly element does not have a calculation, and cannot have data associated with it'''
        return self.element.group_only

    @group_only.setter
    def group_only(self,val):
        self.element.group_only=val

    @property
    def calculation_status(self):
        '''The calculation_status of the Empower Element underpinning this StructureElement. Can be one of 'Real' or 'Calculated' (i.e. virtual).'''
        return self.element.calculation_status

    @calculation_status.setter
    def calculation_status(self,val):
        self.element.calculation_status=val

    @property
    def calculation(self):
        '''The calculation of the Empower Element underpinning this StructureElement.'''
        return self.element.calculation

    @calculation.setter
    def calculation(self,val):
        self.element.calculation=val

    @property
    def colour(self):
        '''The colour of the Empower Element underpinning this StructureElement.'''
        return self.element.colour

    @colour.setter
    def colour(self,val):
        self.element.colour=val

    @property
    def fields(self):
        '''A dictionary like object giving access to the underlying element's fields. See the api documentation for Element.fields'''
        return self.element.fields

    #Don't need a setter for fields because fields is a dictionary

    @property
    def security(self):
        '''The security of the underlying Element. See the api documentation for Element.security for information'''
        return self.element.security

    @property
    def physid(self):
        '''The physical identity of the underlying Element. See the api documentation for Element.physid for information'''
        return self.element.physid

    @physid.setter
    def physid(self,val):
        self.element.physid=val

    @property
    def year(self):
        '''For Time StructureElements only. The year of the underlying Time Element. See Element.year for information'''
        return self.element.year

    @year.setter
    def year(self,val):
        self.element.year=val

    @property
    def month(self):
        '''For Time StructureElements only. The month of the underlying Time Element. See Element.month for information'''
        return self.element.month

    @month.setter
    def month(self,val):
        self.element.month=val

    @property
    def day(self):
        '''For Time StructureElements only. The day of the underlying Time Element. See Element.day for information'''
        return self.element.day

    @day.setter
    def day(self,val):
        self.element.day=val

    @property
    def interval_index(self):
        '''For Time StructureElements only. The interval_index of the underlying Time Element. See Element.interval_index for information'''
        return self.element.interval_index

    @interval_index.setter
    def interval_index(self,val):
        self.element.interval_index=val

    @property
    def interval(self):
        '''For Time StructureElements only. The interval of the underlying Time Element. See Element.interval for information'''
        return self.element.interval

    @property
    def interval_amount(self):
        '''For Time StructureElements only. The interval_amount of the underlying Time Element. See Element.interval_amount for information'''
        return self.element.interval_amount

    @property
    def resolution(self):
        '''For Time StructureElements only. The resolution of the underlying Time Element. See Element.resolution for information'''
        return self.element.resolution

    @property
    def offset(self):
        '''For Time StructureElements only. The offset of the underlying Time Element. See Element.offset for information'''
        return self.element.offset

    @property
    def _start_date(self):
        '''For Time StructureElements only. The (private) _start_date of the underlying Time Element.'''
        return self.element._start_date

    @property
    def empower_period_number(self):
        '''Applies to time elements only. A read only property that returns the Empower Period type number (e.g. 3 for a Month)'''
        return self.element.interval_index

    @property
    def dimension(self):
        '''The Empower Dimension this StructureElement belongs to'''
        if self.structure is not None:
            return self.structure.dimension
        else:
            return self.element.dimension

    @property
    def site(self):
        '''The site this StructureElement belongs to'''
        return self.dimension.site

    def add_parent(self,parent_structure_element):

        #Only add self to parent when changing parent_structure_element to avoid an infinite loop
        if self._parent_structure_element is None or self._parent_structure_element!=parent_structure_element:
            self._parent_structure_element=parent_structure_element
            self.is_root = False

        parent_structure_element._add_child(self)

    def set_parent(self,parent_structure_element):

        if self==parent_structure_element:
            raise ValueError('Tried to set StructureElement.parent to self. self.shortname='+str(self.shortname))

        #Remove the current parent if it differs from the one being set
        if self._parent_structure_element is not None and self._parent_structure_element!=parent_structure_element:
            self._parent_structure_element.remove_child(self)
            self._parent_structure_element=None

        #Only add self to parent when changing parent_structure_element to avoid an infinite loop
        if self._parent_structure_element is None:
            self._parent_structure_element=parent_structure_element

            if self._parent_structure_element is not None:
                self._parent_structure_element._add_child(self)

    def cut(self):
        '''
        Remove this structure element from its parent and return it.
        This function is useful when we are about to 'paste' the element into another spot
        '''
        #Remove the current parent if it differs from the one being set
        if self._parent_structure_element is not None:
            self._parent_structure_element.remove_child(self)
            self._parent_structure_element=None

        return self

    def _add_child(self,child_structure_element):
        self._child_structure_elements.append(child_structure_element)
        if child_structure_element.parent is None or child_structure_element.parent != self:
            child_structure_element._parent_structure_element=self
            child_structure_element.is_root = False
            child_structure_element.structure=self.structure
        log.debug('Added Child '+child_structure_element.shortname+' to '+self.shortname)

    def add_child(self,child_structure_element):
        '''Add a child StructureElement to .children.

        :param child_structure_element: StructureElement, Element or shortcode string referring to an element. The child we wish to add to this StructureElement.
        '''
        if isinstance(child_structure_element,StructureElement):
            self._add_child(child_structure_element)
        elif isinstance(child_structure_element,Element):
            self._add_child(StructureElement(element=child_structure_element))
        elif isinstance(child_structure_element,str):
            #Create a StructureElement by looking up the element shortname from the string
            self._add_child(StructureElement(element=self.dimension.elements[child_structure_element]))


    def remove_children(self):
        '''Remove all children from this structure element/ Same as .children.clear()'''
        #reset the _child_structure_elements to an empty OrderedDict
        for ch in self.children.values():
            ch._parent_structure_element=None
        self._child_structure_elements=[]

    def remove_child(self,child_structure_element):
        '''Remove a Child StructureElement. If a shortcode is passed in, remove the final child StructureElement with that shortcode'''

        try:
            #Test if we are lookgin at a shortname or an element by provoking a type error
            shortname = child_structure_element + ''

        except TypeError:
            shortname = None

        if shortname is None:
            try:
                #If the element doesn't exist that's fine, making remove_child idempotent
                self._child_structure_elements.remove(child_structure_element)
            except ValueError:
                return
        else:
            element_to_remove = None
            #Remove the last element with that shortcode
            for n,el in enumerate(self._child_structure_elements[::-1]):
                if el.shortname == shortname:
                    element_to_remove = el
                    #log.info('Removing child {}'.format(-(n+1)))
                    break
            if element_to_remove is not None:
                self._child_structure_elements.remove(element_to_remove)

    def replace_child(self,child_structure_element,replacements=None):
        '''Replace one of the child structure elements with one or more structure elements in the same spot
        If there are no replacements, this function will behave in the same way as `remove_child` - only it will throw a KeyError if the child does not exist
        :param child_structure_element: Structure element in children to replace - if not found a KeyError will be raised
        :param replacements: a StructureElement or list of StructureElements to replace
        '''

        if not child_structure_element in self.children:
            raise KeyError('Child StructureElement({}, {}) did not exist in StructureElement({}, {})'.format(child_structure_element.shortname, child_structure_element.longname,self.shortname,self.longname))

        if replacements is None or len(replacements) == 0:
            self.remove_child(child_structure_element)
        else:
            #Make sure replacements is a list of structure elements
            try:
                #First is it a lone StructureElement? If so put it in a list
                replacements.shortname
                replacements = [replacements]
            except AttributeError:
                #Assume replacements is already a list (or iterable) of replacment values
                pass

            before_children_shortcodes = []
            after_children_shortcodes = []
            replacement_child_found = False

            #JAT 2019-08-16 removed copy command for speed
            original_child_structures = self._child_structure_elements.copy()
            self._child_structure_elements = []
            for child in original_child_structures:
                if child == child_structure_element:
                    replacement_child_found = True

                    for replacement_child in replacements:
                        self._add_child(replacement_child)
                else:
                    self._child_structure_elements.append(child)

    def embellish(self
                 , mappings
                 , element_type_field           = None
                 , parent_type                  = None
                 , parent_element_id_fields     = []
                 , parent_element_id_mappings   = []
                 , child_type                   = None
                 , child_element_id_fields      = []
                 , child_element_id_mappings    = []
                 , child_longname_mapping       = None
                 ):
        '''Add new elements in a layer to a StructureElement. This way StructureElement trees can be built incrementally, rather than setting the relationships at once

        :param mappings: A pandas DataFrame or dictionary containing the parent-child mappings
        :param element_type_field: if set, the Dimension field that holds the type of element we wish to include as either parent or child elements. Typically this dimension field is called 'Type'
        :param parent_type: The value in the type field for parent elements. If set, only elements in the tree with the  element_type_field set to parent_field will have children attached to them.
        :param parent_element_id_fields: The dimension Element field(s) that holds the identity of the parents we want to attach to
        :param parent_element_id_mappings: The columns in a pandas.DataFrame or keys in a Dictionary that identify the parent elements, and correspond to the parent_element_id_fields
        :param child_type: The value in the type field for child elements. Elements with this element_type_field set to child_field will be candidates for attaching to the tree. If not found in the relevant dimension, new elements will be created with element_type_field set to this value
        :param child_element_id_fields: The dimension Element field(s) that holds the identity of the children we want to attach
        :param child_element_id_mappings: The columns in a pandas.DataFrame or keys in a Dictionary that identify the child elements, and correspond to the child_element_id_fields
        :param child_longname_mapping: The longname of the child, as found in the mappings DataFrame or Dictionary - used to create new Elements when they do not exist in the relevant Dimension

        If parent_type,  parent_element_id_fields and parent_element_id_mappings are not set, then children will be attached to all nodes in the tree.
        This behaviour is most useful when adding the first layer to an ALL or TOTAL node.

        >>>



        '''

        #Create a field/child element lookup
        child_lookup = {}
        for el in self.dimension.elements.values():
            if element_type_field is None or el.fields[element_type_field] ==  child_type:
                child_lookup[tuple(el.fields[f] for f in child_element_id_fields)] = el

        is_dataframe = False
        is_dict      = False
        is_list      = False


        #Reverse ducktype the mappings parameter
        try:
            mappings.axes
            is_dataframe = True

        except AttributeError:
            #try:
            #    mappings.values()
            #    is_dict = True
            #    _relationship_dict = {}
            #    for child_shortname,parent_shortname in mappings.items():
            #        try:
            #            _relationship_dict[parent_shortname].append(child_shortname)
            #        except KeyError:
            #            _relationship_dict[parent_shortname] = [child_shortname]
            #except AttributeError:
            #    is_list = True
            #    _relationship_dict = {}
            #    for child_shortname,parent_shortname in mappings:
            #        try:
            #            _relationship_dict[parent_shortname].append(child_shortname)
            #        except KeyError:
            #            _relationship_dict[parent_shortname] = [child_shortname]
            pass

        #The canonical field to hold the type of StructureElement is 'Type' - use this if
        if (parent_type is not None or child_type is not None) and element_type_field is None:
            element_type_field = 'Type'

        child_elements_to_create = []

        if is_dataframe:
            #Ensure the correct columns are in the DataFrame, otherwise KeyErrors are going to be thrown in the oddest of places and make debugging a nightmare

            #Create a dictionary of relationships between parent to all of their children
            _relationship_dict = {}

            #Get unique columns, so that we can drop duplicates
            columns = child_element_id_mappings+parent_element_id_mappings
            if child_longname_mapping is not None:
                columns.append(child_longname_mapping)

            columns =list(set(columns))

            for index, row in mappings[columns].dropna().drop_duplicates(keep='first').iterrows():

                #    #Filter parents if that's what we are doing
                #if parent_type is not None and row[element_type_field] != parent_type:
                #    continue

                try:
                    child_element = child_lookup[tuple(row[mapping_column] for mapping_column in child_element_id_mappings)]
                except KeyError:
                    #make the child
                    if child_longname_mapping is None:
                        #Raise an error, since we can't create the child
                        raise ValueError('Child elements cannot be created without a child_longname_mapping. Child {} was not found when creating the StructureElement tree'.format((row[mapping_column] for mapping_column in child_element_id_mappings)))

                    fields={k:v for k,v in zip(child_element_id_fields,tuple(row[m] for m in child_element_id_mappings))}

                    longname = row[child_longname_mapping]
                    child_element = Element(dimension = self.dimension, shortname = None, longname = longname, fields={k:v for k,v in zip(child_element_id_fields,[row[m] for m in child_element_id_mappings])})
                    if element_type_field is not None:
                        child_element.fields[element_type_field] = child_type
                    #merge into dimension.elements
                    child_elements_to_create.append(child_element)

                    #Add to the lookup, so we don't create it again
                    child_lookup[tuple(row[mapping_column] for mapping_column in child_element_id_mappings)] = child_element

                #Append to the list of all child elements we will be putting under this parent element
                #Note children will be placed in the order they appear in the source
                try:
                    _child_element_list = _relationship_dict[tuple(row[mapping_column] for mapping_column in parent_element_id_mappings)]
                except KeyError:
                    _child_element_list = []
                    _relationship_dict[tuple(row[mapping_column] for mapping_column in parent_element_id_mappings)] = _child_element_list

                _child_element_list.append(child_element)

                #try:
                #    _relationship_dict[parent_shortname].append(child_shortname)
                #except KeyError:
                #    _relationship_dict[parent_shortname] = [child_shortname]

            created_element_lookup = {}
            #Merge and synchronise any new child elements, because StructureElements cannot be made with unsynchronised children
            if len(child_elements_to_create)  > 0:
                key_fields = child_element_id_fields

                if element_type_field is not None:
                    key_fields.append(element_type_field)
                created_elements = self.dimension.elements.merge(child_elements_to_create,keys=key_fields)

                created_element_lookup = {k:v for k,v in zip(child_elements_to_create,created_elements)}
                self.dimension.elements.synchronise()

                for _child_element_list in _relationship_dict.values():
                    for n, el in enumerate(_child_element_list):
                        try:
                            #try to replace un-created elements with their created (canonical) replacements
                            _child_element_list[n] = created_element_lookup[el]
                        except KeyError:
                            pass

        #list the structure, since we are iterating over it and changing it at teh same time
        for se in list(self.walk()):
            #Filter parents if that's what we are doing
            if parent_type is not None and se.element.fields[element_type_field] != parent_type:
                continue

            #Lookup the children to append - we've done the work to gather them already
            # Replace the looked up children with their mastered equivalents
            try:
                children_to_append = _relationship_dict[tuple([se.fields[f] for f in parent_element_id_fields])]
            except KeyError:
                #No children for this ragged hierarchy - continue on to next element
                continue

            if len(created_element_lookup) > 0:
                mastered_children_to_append = []
                for ch in children_to_append:
                    try:
                        mastered_children_to_append.append(created_element_lookup[ch])
                    except KeyError:
                        mastered_children_to_append.append(ch)
            else:
                #If no elements were created at all, dont' spend time doing any lookup
                mastered_children_to_append = children_to_append
            se.children += mastered_children_to_append


    def set_tree(self,relationships,update=False):
        '''
        Set all of the relationships in the tree below this StructureElement. Old relationships will get thrown away

        :param relationships: a list of parent child tuples, a dictionary of {child:parent} or a dataframe with columns 'Short Name' or 'PhysID' and 'Parent Short Name' or 'Parent PhysID'
        :param update: if set to True, the structure is updated, otherwise it is replaced (default)
        '''

        is_dataframe = False
        is_dict      = False
        is_list      = False

        #Reverse ducktype the relationships parameter
        try:
            relationships.axes
            is_dataframe = True
        except AttributeError:
            try:
                relationships.values()
                is_dict = True
                _relationship_dict = {}
                for child_shortname,parent_shortname in relationships.items():
                    try:
                        _relationship_dict[parent_shortname].append(child_shortname)
                    except KeyError:
                        _relationship_dict[parent_shortname] = [child_shortname]
            except AttributeError:
                is_list = True
                _relationship_dict = {}
                for child_shortname,parent_shortname in relationships:
                    try:
                        _relationship_dict[parent_shortname].append(child_shortname)
                    except KeyError:
                        _relationship_dict[parent_shortname] = [child_shortname]

        if is_dataframe:
            _relationship_dict = {}
            for index, child_shortname,parent_shortname in relationships[['Short Name','Parent Short Name']].itertuples():

                try:
                    _relationship_dict[parent_shortname].append(child_shortname)
                except KeyError:
                    _relationship_dict[parent_shortname] = [child_shortname]

        #print(_relationship_dict)
        self._set_tree(relationship_dict = _relationship_dict,update=update)

    def _set_tree(self,relationship_dict,update):

        #print('_set_tree {}'.format(self.shortcode))

        try:
            children_list = relationship_dict[self.shortname]

        except KeyError:
            return

        if not update:
            self.remove_children()

        for child_shortcode in children_list:
            child_se = StructureElement(parent_structure_element=self
                                       ,element = self.dimension.elements[child_shortcode]
                                       ,is_root=False
                                       )

        for ch in self.children:
            ch._set_tree(relationship_dict=relationship_dict,update = update)

    def update_tree(self,relationships):
        '''
        Add new relationships in the tree below this StructureElement. Children will be moved to new parents. Order will be preserved

        :param relationships: a list of parent child tuples, a dictionary of {child:parent} or a dataframe with columns 'Short Name' or 'PhysID' and 'Parent Short Name' or 'Parent PhysID'
        '''

        self.set_tree(relationships,update=True)


    def abdicate(self):
        '''Remove self from a hierarchy and replace self with children in the same spot
        This is very important for filtering, because we must leave an intact hierarchy when filtering, and successively abdicating elements will allow children to shuffle up
        '''
        #Replace self with children in parent element
        if not self.has_children:
            self.parent.remove_child(self)
        else:
            self.parent.replace_child(child_structure_element=self,replacements=self.children)

    @property
    def has_children(self):
        '''If this StructureElement has at least one childStructureElement, then return True, otherwise returns False'''
        return len(self._child_structure_elements) > 0

    @property
    def is_leaf(self):
        '''If this StructureElement has no children it is a 'leaf element', so return True, otherwise returns False'''
        return not self.has_children

    @property
    def parent(self):
        '''The Parent StructureElement of this StructureElement.

        Will return None if this StructureElement has no parent'''

        if isinstance(self._parent_structure_element,str):
            raise ValueError
        return self._parent_structure_element

    @property
    def ancestors(self):
        '''Generator which yields every parent up to the root from this element'''

        _next_ancestor = self.parent
        if _next_ancestor is not None:
            yield _next_ancestor
            yield from _next_ancestor.ancestors

    @property
    def ancestors_string(self):
        '''A string, similar to .path, of all ancestor StructureElements shortnames starting at the root ancestor StructureElement and seperated with ' -> '. Does not include this StructureElement's shortname '''
        return ' -> '.join([a.shortname for a in self.ancestors][::-1])

    @property
    def ancestors_longname_string(self):
        '''A string, similar to .path, of all ancestor StructureElements longnames starting at the root ancestor StructureElement and seperated with ' -> ' '''
        return ' -> '.join([a.longname for a in self.ancestors][::-1])

    @property
    def string_to_root(self):
        '''A string, similar to .path, of all ancestor StructureElements shortnames starting at the root ancestor StructureElement and seperated with ' -> '. Last shortname is  this StructureElement's shortname '''
        return ' -> '.join([a.shortname for a in self.ancestors][::-1]+[self.shortname])

    @property
    def children(self):
        '''The children of this '''
        #return the magic object which allows children to be indexed and iterated over
        return self._children

    @children.setter
    def children(self,val):
        if isinstance(val,StructureElementChildren) and (val._structure_element is None or val._structure_element is self):
            self._children = val
        else:
            self._children.clear()
            self._children.append(val)

    @property
    def descendants(self):
        '''return a magic object which allows descendants to be indexed by shortname'''
        return self._descendants

    @descendants.setter
    def descendants(self,val):
        if isinstance(val,_StructureElementDescendantsGetter):
            self._descendants = val
        else:
            #When someone sets descendants to be a structure element or list of structure elements, they are clearly thinking about setting the children
            self._children.clear()
            self._children.append(val)

    #@property
    #def descendant(self,item):
    #    return self.descendants[item][0]

    @property
    def path(self):
        '''Route from the structure to this StructureElement

        Returns a string with the Structure shortname, then a dot, followed by Element shortnames down the hierarchy separated by forward slashes.
        >>> my_structure_element.path()
        'SPAM.BACON/EGGS'
        '''
        if self.structure is None or self.structure.shortcode is None:
            return '.' + '/'.join([a.shortcode for a in self.ancestors][::-1]+[self.shortname])
        else:
            return self.structure.shortcode +  '.' + '/'.join([a.shortcode for a in self.ancestors][::-1]+[self.shortname])

    @property
    def level(self):
        '''return the zero-based depth of this structure from the root'''
        return len(list(self.ancestors))

    @property
    def depths(self):
        '''return a dictionary of depths (from root) and list of StructureElements at that depth'''
        _depths = {}

        for se, level in self.walk_with_levels():
            try:
                current_elements_at_this_depth  = _depths[level]
            except KeyError:
                current_elements_at_this_depth  = []

            current_elements_at_this_depth.append(se)
            _depths[level] = current_elements_at_this_depth

        return _depths

    @property
    def shallownesses(self):
        '''return a dictionary of shallownesses (from leaf) and list of StructureElements at that depth'''


        if self.is_leaf:
            #Return shallowness of self (i.e. 0) and a list of structure elements at this shallowness (i.e. [self]) in a dictionary
            return {0:[self]}
        else:
            _shallownesses = {}
            for ch in self.children:
                for shallowness, list_of_structure_elements in ch.shallownesses.items():
                    try:
                        current_elements_at_this_shallowness  = _shallownesses[shallowness]
                    except KeyError:
                        current_elements_at_this_shallowness  = []

                    current_elements_at_this_shallowness += list_of_structure_elements
                    _shallownesses[shallowness] = current_elements_at_this_shallowness

            #Work out shallowness of self
            self_shallowness = len(_shallownesses)
            #Add self to _shallownesses
            _shallownesses[self_shallowness] = [self]

            return _shallownesses

    def walk(self,level=None,permissive=True):
        '''
        Visit every descendant element in a Structure element in turn.
        The tree is traversed depth-first, with the first child of the first child of the first child being visited before the second child of the first child of the first child is visited

        :param level: Deprecated - do not set this
        :param permissive: Deprecated
        '''
        if level==None:
            if not permissive:
                assert self.is_root

            level=0

        yield self

        #PYM-65 - if we don't create a list here, calls to get_elements within the walk cause early termination - not sure why this fixes it
        for e in list(self.children):
            try:
                yield from e.walk(level=level+1,permissive=permissive)
            except RecursionError:
                #We've gone too deep, there must be some sort of loop in the hierarchy
                #print out the parents
                el=self
                log.error('Recursion error. Showing elements moving up the hierarchy, please try to detect loop, and fix it.')
                for i in range(20):
                    log.error('Recursion error. Entity shortname='+el.shortname+' parent='+repr(el.parent))
                    el=el.parent
                #Can't just reraise, or we will re-catch the same recursion error going back up the tree!
                raise SystemError()

    def walk_with_levels(self,level=0,permissive=True):
        '''Yield all elements in a structure, beginning with the root. At the same time yield the level that we are in in the hierarchy.

        :param level: Initial level we are counting from. Defaults to 0
        :param permissive: Deprecated
        '''
        yield self, level

        #PYM-65 - if we don't create a list here, calls to get_elements within the walk cause early termination - not sure why this fixes it
        for e in list(self.children):
            try:
                yield from e.walk_with_levels(level=level+1,permissive=permissive)
            except RecursionError:
                #We've gone too deep, there must be some sort of loop in the hierarchy
                #print out the parents
                el=self
                log.error('Recursion error. Showing elements moving up the hierarchy, please try to detect loop, and fix it.')
                for i in range(20):
                    log.error('Recursion error. Entity shortname='+el.shortname+' parent='+repr(el.parent))
                    el=el.parent
                #Can't just reraise, or we will re-catch the same recursion error going back up the tree!
                raise SystemError()

    def walk_subtree(self,subtree_shortname, permissive=True):
        '''Walk a tree starting at self (a root node) returning only the sub-tree specified by the shortname

        :param subtree_shortname: Empower Short Name of the Structure Element we want to start yielding items from
        :param permissive: If we know that we have an unambiguous element then do not assert that we are using a root node - this is especially good in get_leaves() when we don't care
        '''

        #Can only be called from a root node - this avoids the returned subtree being ambiguous, since shortnames may appear in more than a single tree in the structure
        #However since we sometimes know the structure element we are calling from, we allow this to be permissive
        if not permissive:
            assert self.is_root

        subtree_start_structure_element=None

        for se in self.walk(permissive=permissive):
            log.debug('walk_subtree found ['+se.shortname+'] in self.walk')
            #Detect the start of the subtree, and record the level, so we know when we are exiting the subtree
            if se.shortname==subtree_shortname:
                log.debug('walk_subtree found ['+se.shortname+'] matching parameter subtree_Shortname in self.walk')

                if subtree_start_structure_element is None:
                    subtree_start_structure_element=se
                    log.debug('walk_subtree setting subtree start element:'+str(subtree_start_structure_element))

            #While we are within a subtree, yield the StructureElements within
            if subtree_start_structure_element is not None:
                #When we return to the level of the start of the subtree (or below) we have exited the subtree, and may stop
                if se.level<=subtree_start_structure_element.level and se != subtree_start_structure_element:
                    log.debug('walk_subtree breaking at se:['+se.shortname+'] level:'+str(se.level))
                    break
                log.debug('walk_subtree yielding ['+se.shortname+']')
                yield se


    def ascend(self, by_depth = True):
        '''Traverse tree from leaves to trunk (root)

        By depth determines if the primary consideration is the depth from the root (by_depth = True) or the shallowness from the leaves

        Children always get returned before parents, but if by_depth is True, a leaf next to the root gets returned later, if False a leaf next to the root will be returned earlier

        :param by_depth: True if the distance from the root is used to determine ordering, False if distance from the leaf (i.e. shallowness) is used to determine ordering
        '''
        if by_depth:
            depths_as_list_of_tuples = [(k,v) for k,v in self.depths.items() ]
            depths_as_list_of_tuples.sort(reverse = True)

            for depth, structure_elements in depths_as_list_of_tuples:
                for se in structure_elements:
                    yield se

        else:
            depths_as_list_of_tuples = [(k,v) for k,v in self.shallownesses.items() ]
            depths_as_list_of_tuples.sort()

            for shallowness, structure_elements in depths_as_list_of_tuples:
                for se in structure_elements:
                    yield se

    def descend(self, by_depth = True):
        '''Traverse tree from trunk (root) to leaves

        By depth determines if the primary consideration is the depth from the root (by_depth = True) or the shallowness from the leaves

        Parents always get returned before children, but if by_depth is True, a leaf next to the root gets returned first, if False a leaf next to the root will be returned last

        :param by_depth: True if the distance from the root is used to determine ordering, False if distance from the leaf (i.e. shallowness) is used to determine ordering
        '''
        if by_depth:
            depths_as_list_of_tuples = [(k,v) for k,v in self.depths.items() ]
            depths_as_list_of_tuples.sort()

            for depth, structure_elements in depths_as_list_of_tuples:
                for se in structure_elements:
                    yield se

        else:
            shallownesses_as_list_of_tuples = [(k,v) for k,v in self.shallownesses.items() ]
            shallownesses_as_list_of_tuples.sort(reverse = True)

            for shallowness, structure_elements in shallownesses_as_list_of_tuples:
                for se in structure_elements:
                    yield se

    def get_subtree_translation_df(self,subtree_shortname,column_prefix=None, field_shortname=None):
        '''Starting at self (a root node) return a pandas DataFrame of shortname and physids for translating rollups for the sub-tree specified by the shortname

        The returned DataFrame will have columns ['Short Name','ID','level n physid',...,'level m physid'] where level n is the level of the supplied subtree_shortname parameter
        For shortnames which are not at the extreme leaves of the tree, the ['level m'] column plus some higher levels will have physid = -2
        Joining the DataFrame that this function returns to transactional data will create a dataframe that can be used as the basis of a standard explode and load
        We can use 'Short Name' or 'ID' to do our join

        :param subtree_shortname: Empower Short Name of the Structure Element we want to create a flattened translation below
        :returns: pandas DataFrame  ['Short Name','ID','level n physid',...,'level m physid']
        '''

        #A list of tuples, (string, list) where the string is the shortname and the list is the physids leading from the root
        #This will be a ragged hierarchy - we'll unrag it later by adding -2s beyond the leaves
        all_physid_root_to_tip_lists=[]

        #The current root to tip physid list is maintained, by chucking leaves away when we go up the hierarchy, and adding leaves when we go down
        #current_root_to_tip_physids=[]
        current_root_to_tip_structure_elements=[]
        current_level=None
        previous_level=None
        subtree_start_level=None

        longest_list_len = 0

        #walk_subtree can only be called from a root node unless we are returning the whole of the tree - this avoids the returned subtree being ambiguous, since shortnames may appear in more than a single tree in the structure
        permissive = subtree_shortname == self.shortname

        for se in self.walk_subtree(subtree_shortname,permissive=permissive):

            if subtree_start_level is None:
                subtree_start_level=se.level

            #Trim the list of structure elements, to only include this one's parents
            current_root_to_tip_structure_elements=current_root_to_tip_structure_elements[:se.level-subtree_start_level]

            #extend the list of current_root_to_tip_structure_elements to include the the current element
            current_root_to_tip_structure_elements.append(se)

            #JAT - commented this out 2018-12-14 because fieldvalue doesn't get used
            #if field_shortname:
            #    if field_shortname in ['Short Name','Long Name','ID']:
            #        #we'll already have these fields present, don't duplicate them
            #        fieldvalue = None
            #    else:
            #        fieldvalue = se.fields[field_shortname]
            #else:
            #    fieldvalue = None

            #Bauild a list of root to tip ids and add to the whole list, trimming to only include ids of non-virtual, non-group elements
            current_root_to_tip_physids = []
            for se_child in current_root_to_tip_structure_elements:
                #Only add non-group non calculated elements, or we end up adding up a whole load of calculated elements
                if (se_child.fields['Calculation'] is None or se_child.fields['Calculation Status'] == 'Real') and se_child.fields['Group Only'] is None:
                    current_root_to_tip_physids.append(se_child.physid)
            all_physid_root_to_tip_lists.append((current_root_to_tip_physids))

            #Keep track of the longest list length - we'll need this to pad the others
            if longest_list_len < len(current_root_to_tip_physids):
                longest_list_len = len(current_root_to_tip_physids)

        #Now we need to take the ragged hierarchy, something like this:
        # ('ALL',[1])
        # ('X02',[1, 2])
        # ('X03',[1, 2, 3])
        # ('X04',[1, 2, 3, 4])
        # ('X05',[1, 5])
        # ('X06',[1, 5, 6])
        # ('X07',[1, 5, 7])
        #
        # and turn it into something like this
        #
        # ('ALL',[1,-2,-2,-2])
        # ('X02',[1, 2,-2,-2])
        # ('X03',[1, 2, 3,-2])
        # ('X04',[1, 2, 3, 4])
        # ('X05',[1, 5,-2,-2])
        # ('X06',[1, 5, 6,-2])
        # ('X07',[1, 5, 7,-2])
        #
        # This hierarchy can then be turned into something like this, and from there into our dataframe
        #
        # {'Short Name':'ALL, 'level 0':1, 'level 1':-2, 'level 2':-2, 'level 3':-2 }
        # ...
        # {'Short Name':'ALL, 'level 0':1, 'level 1':5,  'level 2':7,  'level 3':-2 }

        #Create a list of dictionaries, ready for transformation into a pandas DataFrame
        list_of_dicts=[]

        #We need to maintain a record of the lowest level, so that we can create the names with an accurate ordering
        lowest_level=None

        #First Pad the lists with -2 - up to the longest length
        for physid_list in all_physid_root_to_tip_lists:
            #Root elements which are group will have empty physid lists - ignore these
            if len(physid_list)==0:
                continue
            #Record the physid for the leaf element - this is the one we will use to do the lookup
            dict_for_df={'ID':physid_list[-1]}

            physid_list.extend([-2] * (longest_list_len - len(physid_list)))

            #Then turn the list into a dictionary, ready to turn into a pandas DataFrame
            for level_offset, physid in enumerate(physid_list):
                level_to_be_used_in_name=level_offset+subtree_start_level

                #Keep track of the lowest level, so that we can recreate column names, and then get the df column names in the correct order
                if lowest_level is None or level_to_be_used_in_name < lowest_level:
                    lowest_level=level_to_be_used_in_name

                column_name='level '+str(level_to_be_used_in_name)+' physid'
                dict_for_df[column_name]=physid

            list_of_dicts.append(dict_for_df)

        #Create a list of column names in the correct order - without this, the dataframe has the column names in the wrong order which breaks explosion logic
        list_of_columns_in_correct_order=[]
        for n in range(longest_list_len):
            level_to_be_used_in_name=lowest_level+n
            column_name='level '+str(level_to_be_used_in_name)+' physid'
            list_of_columns_in_correct_order.append(column_name)

        list_of_columns_in_correct_order.reverse()

        #Get any shortname for field passed in - this needs to be converted to a list to make it easy to combine with another list - the default is an empty list (i.e. nothing was passed in)
        fieldshortname_list=[]
        if field_shortname and field_shortname not in ['Short Name','Long Name','ID']:
            fieldshortname_list=[field_shortname]

        #Finally convert the list of dictionaries into a pandas DataFrame, order the columns correctly, rename as necessary, and return
        return_df= pd.DataFrame(list_of_dicts)

        #Get shortnames and so on from the standard dataframe
        return_df=pd.merge(how='left',left=return_df,right=self.structure.dimension.elements.dataframe,left_on='ID',right_on='ID')

        try:
            return_df=return_df[['ID','Short Name','Long Name']+fieldshortname_list+list_of_columns_in_correct_order]
        except KeyError:
            print(return_df.head())
            raise

        #We will have a lot of dataframes with the same column names (level 0 physid...) and so on, so there is a parameter for an optional prefix to disambiguate joined column names later
        rename_dict={}
        if column_prefix is not None:
            #Rename the columns with the supplied prefix if there is one
            for col in return_df.columns:
                rename_dict[col]=column_prefix+col

        return_df.rename(columns=rename_dict,inplace=True)

        return return_df

    def print_hierarchy(self,prefix_string = '',counter = None):
        '''Deprecated, Use the python print() function instead.
        Prints out the StructureElement in text form.

        >>> print(site.dimensions[0].structures['SPAM'].hierarchies['EGGS'])
        EGGS
        +-BACON
        '''
        print(self._represent_hierarchy(prefix_string = prefix_string,counter = counter))

    def __repr__(self):
        return '<{} object, shortname {}, longname {} at {}>'.format(self.__class__.__name__,self.shortname,self.longname,hex(id(self)))

    def __str__(self):
        return self._represent_hierarchy()

    def __len__(self):
        return len([x for x in self.walk()])


    def _represent_hierarchy(self,prefix_string = '',counter = None):

        result = ''

        if counter is None:
            counter = _Counter()

        if prefix_string=='':
            result += '{:11}{:19}{}\n'.format(self.shortname,str(counter), self.longname)

        else:
            result += '{}+-{:11}{:19}{}\n'.format(prefix_string[:-2], self.shortname,str(counter),self.longname)

        kids = [c for c in self.children]
        for n, e in enumerate(kids):
            if n+1==len(kids):
                addendum = '  '
            else:
                addendum = '| '
            result += e._represent_hierarchy(prefix_string = prefix_string+addendum,counter = counter)

        return result

    def get_leaves(self,subtree_shortname=None,permissive=True):
        '''Yield the leaf StructureElements in a ragged hierarchy, below the given shortname
        :param subtree_shortname: Empower Short Name of the Structure Element we want to start yielding items from. Defaults to the root of the tree.
        '''

        if subtree_shortname is None:
            subtree_shortname=self.shortname

        for e in self.walk_subtree(subtree_shortname=subtree_shortname,permissive=permissive):
            if e.is_leaf:
                yield e

    @property
    def leaves(self):
        '''Yield the leaf StructureElements in a ragged hierarchy, below the given shortname'''

        yield from self.get_leaves(subtree_shortname=None,permissive=True)

    def get_unique_leaves(self,subtree_shortname=None):
        '''Yield unique leaf DimensionElements in a ragged hierarchy, below the given shortname
        :param subtree_shortname: Empower Short Name of the Structure Element we want to start yielding items from. Defaults to the root of the tree.
        '''

        if subtree_shortname is None:
            subtree_shortname=self.shortname

        yielded_shortnames = []

        for e in self.walk_subtree(subtree_shortname=subtree_shortname,permissive=True):
            if e.is_leaf:
                if e.shortname not in yielded_shortnames:
                    yielded_shortnames.append(e.shortname)
                    #Yield the dimension element in question
                    yield e.element

    def get_elements(self,shortname):
        '''Get all of the elements in this hierarchy with the given shortname'''
        #Keep track of whether an element was passed in to help with debugging
        element_was_passed_in=False

        #If an element has been passed in, use the element's shortname
        try:
            shortname=shortname.shortname
            element_was_passed_in=True
        except AttributeError:
            pass

        #Check that shortname is not None
        if shortname is None:
            #Programming error
            if element_was_passed_in:
                raise ValueError('element.shortname must have a value. None was supplied. debugging information: A pympx.Element instance was passed in as the shortname parameter to function get_element()')
            else:
                raise ValueError('shortname must have a value. None was supplied.')
        try:

            result = []
            for se in self.walk(permissive=True):
                if se.shortname == shortname:
                    result.append(se)
            return result

        except KeyError:
            return []

    def _get_first_element_with_shortname(self,shortname):
        '''Get the first element in this heirarchy with the given shortname - used internally, with care, for situations when we know that such an element should exist in the subtree once'''

        #If an element has been passed in, use the element's shortname
        try:
            shortname=shortname.shortname
        except AttributeError:
            pass

        #Check that shortname is not None
        if shortname is None:
            #Programming error
            raise ValueError('shortname must have a value. None was supplied.')
        try:

            result = []
            for se in self.walk(permissive=True):
                if se.shortname == shortname:
                    return se

        except KeyError:
            return None

    #############################################
    #
    # Structure manipulation functions
    #
    #############################################

    def copy(self, element_shortname_filter_out_list = []):
        '''Return a copy of the hierarchy'''
        copy_self = StructureElement(element = self.element, is_root = self.is_root)

        for e in self.children:
            if not (e.element.shortname in element_shortname_filter_out_list):
                try:
                    copy_self._add_child(e.copy(element_shortname_filter_out_list=element_shortname_filter_out_list))
                except RecursionError:
                    #We've gone too deep, there must be some sort of loop in the hierarchy
                    #print out the parents
                    el=self
                    log.error('Recursion error. Showing elements moving up the hierarchy, please try to detect loop, and fix it.')
                    for i in range(20):
                        log.error('Recursion error. Entity shortname='+el.shortname+' parent='+repr(el.parent))
                        el=el.parent
                    #Can't just reraise, or we will re-catch the same recursion error going back up the tree!
                    raise SystemError()

        return copy_self

    def apply(self, function):
        '''recursively apply a function to the hierarchy'''

        #Apply the function to the children
        new_children = []
        for ch in list(self.children):
            new_child = ch.apply(function)
            if not new_child is None:
                new_children.append(new_child)

        #Apply the function to self
        output_se = function(self)

        if output_se is None:
            return None

        #Replace children with the new children
        output_se.children.clear()
        output_se.children += new_children
        #log.info(str(dict(output_se.children)))

        return output_se

    def swap_elements(self, shortcode_element_dictionary):
        '''Swap out elements in the tree for new ones
        If self not in the shortcode_element_dictionary, then return a copy of self
        '''

        #Create a function that swap elements
        def _swap_element(structure_element):
            try:
                element = shortcode_element_dictionary[structure_element.shortcode]
            except KeyError:
                element = structure_element.dimension.elements[structure_element.shortcode]

            return StructureElement(element = element,structure = self.structure)

        #Apply the swapping function to self
        return self.apply(_swap_element)

    def graft_on(self, scion_hierarchy, element_graft_rule = lambda x,y:None,  scion_copied_once_only=False, return_copy=False, trace_element = None):
        '''
        When grafting apple trees together, you graft a scion (twig or branch) onto a rootstock tree. This function uses that terminology.
        Create an output hierarchy that takes the rootstock hierarchy and grafts on subtrees from the scion hierarchy.
        Scion StructureElement nodes are grafted on according to a rule which is passed in as a parameter: element_graft_rule.
        An example of an appropriate function to pass in, is one that looks at the underlying fields in the DimensionElements of both hierarchies and decides based on the fields whether a subtree is grafted on to the master tree

        :param scion_hierarchy: A StructureElement which is the root of the scion hierarchy
        :param element_graft_rule: A function which has 2 parameters - rootstock element, scion element and return True if the scion element belongs under the rootstock element and False otherwise
        :param scion_copied_once_only: Boolean - does the element merge rule only copy single copies of the scion elements? If so we can optimize by marking nodes as fully transcribed from the scion to the output hierarchy, and avoid visiting them again
        :param return_copy: Boolean - don't graft the scion onto self - rather return a copy of self, with the scion grafted on
        :param trace_element: shortcode or StructureElement. When the grafted tree is coming out with unexpected results you may wish to turn on log tracing for one of the rootstock elements (and its subtree)
        '''
        #Note - originally there was a plan to collapse long one dimensional sub-hierarchies in this function. There is no need to do that here - we can tidy up hierarchies in a subsequent step


        #In a nested loop
        #Walk the rootstock hierarchy
            #Walk the scion hierarchy
                #If the rule says to graft the scion element on then create a copy element and graft it to the output, incrementing the indent if the scion hierarchy requires it
            #After the whole of the scion hierarchy is walked, attach the next element of the rootstock hierarchy to the output hierarchy


        copied_scion_structure_elements={}

        #Create the root element of the output tree
        current_output_node = None
        #root_output_node = None
        new_rootstock_output_node = None
        previous_rootstock_node = None
        previous_rootstock_level = 0

        if trace_element is None:
            trace_element_shortcode = None
        else:
            try:
                #trace_element is a StructureElement or Element
                #ducktyping in action - both have a shortcode
                trace_element_shortcode = trace_element.shortname
            except AttributeError:
                #It didn't quack like a StructureElement or Element so it's a string
                #Add it to another string, just to be sure
                trace_element_shortcode = trace_element + ''

            log.info('trace_element_shortcode = {}'.format(trace_element_shortcode))

        #Tracing will get turned on by switching the log function
        #Start on debug until we pass the trace element
        trace_log_fn = log.debug
        #tracing_level helps us work out if we have gone far enough up the hierarchy
        tracing_level = 0
        tracing_path = None

        #Copy to a list before walking, otherwise the levels change during processing when grafting to self
        for rootstock_structure_element, rootstock_level in [(e, l) for e, l in self.walk_with_levels()]:

            #Tracing will get turned on by switching the log function
            #Start on debug until we pass the trace element
            if rootstock_structure_element.shortname == trace_element_shortcode:
                trace_log_fn = log.info
                tracing_level = rootstock_level

            if rootstock_level is None or rootstock_level < tracing_level:
                #If we have moved back up beyond the tracing level, stop tracing
                trace_log_fn = log.debug
                tracing_level = 0

            trace_log_fn('Rootstock walk at {},{}'.format(rootstock_structure_element.shortname,rootstock_level))

            if new_rootstock_output_node is not None:
                #Set the current root back to the previous rootstock output node
                current_output_node = new_rootstock_output_node

            #if we are returning a copy then we will need a new_rootstock_output_node
            #if we are grafting on to self without copying we need to set this new node to self
            if not return_copy:
                new_rootstock_output_node = rootstock_structure_element
                rootstock_structure_element.set_parent(None)
            else:
                new_rootstock_output_node = StructureElement(element = rootstock_structure_element.element)

            log.debug('rootstock_level          = '+str(rootstock_level))
            log.debug('previous_rootstock_level = '+str(previous_rootstock_level))

            if previous_rootstock_node is not None:
                log.debug('scion_level     = '+str(scion_level))

                if previous_rootstock_level is not None:
                    #Loop back up to the correct parent level
                    for n in range(1 + previous_rootstock_level-rootstock_level):
                        trace_log_fn('rootstock hierarchy stepping up to previous: ' + str(previous_rootstock_node.shortname))

                        #Parent should never be None if the logic is working
                        if previous_rootstock_node.parent is None:
                            raise SystemError('Moving from level {} to {} at iteration {}. previous_rootstock_node {} has no parent'.format(rootstock_level,previous_rootstock_level,n,previous_rootstock_node.shortname))

                        trace_log_fn('rootstock hierarchy stepping up to parent: ' + str(previous_rootstock_node.parent.shortname))

                        previous_rootstock_node = previous_rootstock_node.parent

                trace_log_fn('adding new_rootstock_output_node: {} as child to parent previous_rootstock_node: {}'.format(new_rootstock_output_node.shortname,previous_rootstock_node.shortname))
                previous_rootstock_node._add_child(new_rootstock_output_node)
            else:

                root_output_node = new_rootstock_output_node

            previous_rootstock_node = new_rootstock_output_node
            previous_rootstock_level = rootstock_level

            current_output_node = new_rootstock_output_node
            trace_log_fn('(Re)Starting scion loop current Rootstock Output Node = '+str(current_output_node.shortname))

            n = -1
            for scion_structure_element, scion_level in scion_hierarchy.walk_with_levels(permissive=True):
                n+=1

                if scion_copied_once_only:
                    try:
                        copied_scion_structure_elements[scion_structure_element.shortname]
                        #walk on to the next scion element
                        continue
                    except KeyError:
                        pass

                #Sometimes a Structure Element will appear both in the rootstock and the scion - don't attach to self
                if current_output_node.element == scion_structure_element.element:
                    trace_log_fn('Counting scion as copied since rootstock and scion elements are equal: {} ({})'.format(current_output_node.element.shortname,n))
                    copied_scion_structure_elements[scion_structure_element.shortname] = scion_structure_element
                    continue

                keep_trying_to_graft = element_graft_rule(rootstock_structure_element, scion_structure_element)

                while keep_trying_to_graft and current_output_node is not None:

                    #Attach the scion if the current output node is the current new_rootstock_output_node - i.e. if we are at rootstock level
                    #Don't link it if it is the same thing - sometimes the rootstock element is also in the scion tree - just use the rootstock version
                    if current_output_node == new_rootstock_output_node:
                        new_scion_output_node = StructureElement(element = scion_structure_element.element)
                        trace_log_fn('Returned to rootstock. Adding {} ({}) to {} '.format(scion_structure_element.string_to_root,n, current_output_node.shortname))
                        current_output_node._add_child(new_scion_output_node)
                        #record the copied scion element in our dictionary, so that we can shortcut grafting of duplicate elements

                        copied_scion_structure_elements[new_scion_output_node.shortname] = new_scion_output_node

                        current_output_node = new_scion_output_node
                        trace_log_fn('----Scion grafted.  Current Output node set to scion: '+str(current_output_node.shortname)+' ('+str(n)+')')

                        #Set keep_trying_to_graft to False in order to break out of the while loop, which will try to take us back up the hierarchy until we can graft
                        keep_trying_to_graft = False

                    else:
                        #Attach the scion if the current output node was created from an ancestor of the scion_structure_element
                        for p in scion_structure_element.ancestors:

                            if p is None:
                                break

                            if p.shortname == current_output_node.shortname:

                                new_scion_output_node = StructureElement(element = scion_structure_element.element)
                                trace_log_fn('Scion grafting to ancestor of {}. {}({}) added to {}'.format(scion_structure_element.shortname,new_scion_output_node.shortname,n,current_output_node.shortname))
                                current_output_node._add_child(new_scion_output_node)
                                #record the copied scion element in our dictionary, so that we can shortcut grafting of duplicate elements
                                copied_scion_structure_elements[new_scion_output_node.shortname] = new_scion_output_node
                                trace_log_fn('----Current Output node set to '+str(current_output_node.shortname))

                                current_output_node = new_scion_output_node

                                #Set keep_trying_to_graft to False in order to break out of the while loop, which will try to take us back up the hierarchy until we can graft
                                #By breaking out of the while loop we will start trying to graft the next scion node
                                keep_trying_to_graft = False
                                break

                    if keep_trying_to_graft:
                        #If we got this far without grafting, then we couldn't graft the scion node to this current output node
                        #So go up a level, and try to graft there
                        #Eventually we'll meet an ancestor of the current scion, or the new_rootstock_output_node,
                        # and we'll attach to that
                        #trace_log_fn('Bottom of inner loop current Output Node {} moved up to parent. Is now set to {}'.format(current_output_node.parent.shortname, current_output_node.shortname))
                        current_output_node = current_output_node.parent


        #Return the root node
        return root_output_node


    #def concertina(self, ):

    def filter(self, filter_rule = None,shortcode_list=None,filter_in = True):
        '''Filter out (or filter in) all elements of the subtree that do not (or do) conform to the filter rule or are not (or are) in the shortcode_list.
        filter_in determines whether the elements appearing in the list or conforming to the rule get filtered in or out

        The shortcode list is applied first, followed by the filter rule

        :param filter_rule: a function that takes a StructureElement and returns True if it is to be kept, False, otherwise
        :param shortcode_list: list of shortcodes to be used to filter the tree, alternative to using a filter rule
        :param filter_in:   True if we wish to include shortcodes in the shortcode_list, False if we wish to exclude them from the tree
        '''


        filtered_count = -1
        #Keep filtering the children until there are no filtering events left, before moving onto the children that remain
        while filtered_count != 0:
            #restart the count
            filtered_count = 0
            #Turn .children into a list because we are changing the children as we loop over them
            for ch in list(self.children):

                if shortcode_list is not None:
                    list_result = ch.shortname in shortcode_list
                    if filter_in:
                        do_filter_out =  not list_result
                        #log.info(ch.shortname + ' '+str(do_filter_out)+str(1884))
                    else:
                        do_filter_out =  list_result
                        #log.info(ch.shortname + ' '+str(do_filter_out)+str(1886))

                if filter_rule is not None:
                    rule_result = filter_rule(ch)
                    if filter_in:
                        do_filter_out = not rule_result
                        #log.info(ch.shortname + ' '+str(do_filter_out)+str(1892))
                    else:
                        do_filter_out = rule_result
                        #log.info(ch.shortname + ' '+str(do_filter_out)+str(1896))

                #Filtering the children is done by abdicating them, which means removing them from self (i.e. the child's parent) and putting children in its place
                if do_filter_out:
                    filtered_count+=1
                    #log.info('abdicating '+self.shortname+':'+str(ch.shortname))
                    ch.abdicate()

        #Self.children has been filtered now - so filter the new children's children
        for ch in self.children:
            ch.filter(filter_rule = filter_rule,shortcode_list=shortcode_list,filter_in = filter_in)

        return self

    def bushify(self,bushify_additional_rule=lambda se:True):
        '''Make the tree bushier and less straggly by putting single children in place of their parents

        :param bushify_additional_rule: Extra rule to apply to decide if a StructureElement is eliminated or not
        e.g.

        A
        +-B
        | +-C
        |   +-D
        +-E
          +-F
          +-G

        becomes...

        A
        +-D
        +-E
          +-F
          +-G

        eliminating the unnecessary total elements B and C
        '''

        if self.is_leaf:
            return self

        #make children into a list because we are about to change them
        for ch in list(self.children):
            ch.bushify(bushify_additional_rule=bushify_additional_rule)

        #abdicate (remove self from tree) if you have just one child and have a parent
        if bushify_additional_rule(self) and len(list(self.children)) == 1 and self.parent is not None:
            parent = self.parent
            self.abdicate()
            return parent
        else:
            return self

    #############################################
    #
    # DimensionElement manipulation functions
    #
    #############################################

    def consolidate(self):
        '''Create a consolidation calculation, and set the underlying Element's calculation to the sparse sum of the children
        '''

        for el in self.children:
            if el.physid is None:
                raise ValueError('.consolidate cannot be run until child physids have been set')

        consolidation_calculation_string = ' | '.join([str(el.shortname) for el in self.children])
        #Create a physid calculation - we can't upload this, but we can compare to the Empower version, to stop unnecessary calculation updates
        physid_consolidation_calculation_string = ' | '.join(['@'+str(el.physid) for el in self.children])

        #Set the physid calculation string, which will be the one that Empower exports- this wasy we don't have to trigger an update
        #if the
        self.element._physid_calculation = physid_consolidation_calculation_string
        self.element.calculation = consolidation_calculation_string


    def trickle_down_field(self,fieldname,value):
        '''Set the value of a field on this StructureElement and all its descendents

        :param fieldname: Name of the Element field that we want to set
        :param value: Value we want to set the element field to
        '''
        for ch in self.children:
            ch.element.fields[fieldname] = value
            ch.trickle_down_field(fieldname=fieldname,value=value)

    #Old synonym
    def trickle_down_fields(self,fieldname,value):
        '''Deprecated. Use trickle_down_field() instead'''
        return self.trickle_down_field(fieldname,value)

    def _do_single_slurp(self,fieldname,optimisation_lookup):
        if not self.is_leaf:
            #print('Slurping Children')
            childfields = [ch.slurp_up_field(fieldname=fieldname,optimisation_lookup=optimisation_lookup) for ch in self.children]
            ##Filter fields set to None
            #childfields = [slurp_childfield for slurp_childfield in childfields if slurp_childfield is not None]
            #Return None if field values in children don't match
            if len(set(childfields)) == 1:
                self.fields[fieldname] = childfields[0]
            else:
                self.fields[fieldname] = None

            #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
            #    print('SETTING:  ',self.ancestors_string,self.fields[fieldname])

        #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
        #    print('SET:  ',self.ancestors_string,self.fields[fieldname])


    def slurp_up_field(self,fieldname,optimisation_lookup={}):
        '''From the leaves of a StructureElement to that StructureElement, copy the value in the children's field to the parent StructureElement's field, if and only if all of the fields on the children match.

        :fieldname: The name of the field whos values we want copied up the Structure
        '''
        if optimisation_lookup is not None:

            try:
                #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
                #    print('PATH: ',self.path)
                #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
                #    print('TRY:  ',self.ancestors_string)
                retval = optimisation_lookup[self.path]
                #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
                #    print('LKP:  ',self.ancestors_string,retval)
                return retval

            except KeyError:
                #print('{} isleaf {}'.format(self.shortcode,  self.is_leaf))
                self._do_single_slurp(fieldname,optimisation_lookup)
                #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
                #    print('SLRP: ',self.ancestors_string,self.fields[fieldname])
                optimisation_lookup[self.path] = self.fields[fieldname]
                return self.fields[fieldname]

        else:
            self._do_single_slurp(fieldname,optimisation_lookup)
            #if self.shortcode in ['ONUKC','ONDVA','ONSHBI']:
            #    print('SLRP: ',self.ancestors_string,self.fields[fieldname])
            return self.fields[fieldname]

    #############################################
    #
    # Comparison
    #
    #############################################

    def compare(self,other,shortcode_translations=None,reverse_translations=None):
        '''
        Compare this StructureElement to another, essentially doing a diff
        Also get a list of new, moved and removed elements

        Return a StructureElementComparison object

        :param other: StructureElement to compare self to
        :param shortcode_translations: dictionary for translating shortcodes of "other" structure elements to shortcodes of "self" structure elements, so that similar hierarchies can be compared efficiently
        :param reverse_translations: You shouldn't need to specify this. It exists so that we don't have to calculate the reverse translation for every _recursive_ call of this function
        '''

        if shortcode_translations is None:
            shortcode_translations = {}

        #As an addendum to the diff look for
        # + New Elements (leaf and non-leaf)
        # + moved elements() - we may need the diff to get this right
        # + Removed Elements (leaf and non-leaf)

        self_element_lookup  = {}
        other_element_lookup = {}

        for se in self.walk():
            try:
                self_element_lookup[se.shortcode].append(se)
            except KeyError:
                self_element_lookup[se.shortcode] = [se]

        for se in other.walk():
            try:
                other_element_lookup[se.shortcode].append(se)
            except KeyError:
                other_element_lookup[se.shortcode] = [se]

        new_elements = []
        moved_or_removed_elements = []
        removed_elements = []

        if reverse_translations is None:
            #Look up to see if elements with the shortcode in this StructureElement exist in the other structure element
            for self_shortcode, elements_with_shortcode in self_element_lookup.items():
                try:
                    other_elements = other_element_lookup[self_shortcode]
                except KeyError:
                    removed_elements += elements_with_shortcode
                    continue
                #If they exist, see if they've moved, or if there are more with the same shortcode
                #First create lookups for parent shortcodes
                self_el_parent_sc_se_lookup = {se.parent.shortcode:se for se in elements_with_shortcode if se.parent}
                other_el_parent_sc_se_lookup = {se.parent.shortcode:se for se in other_elements if se.parent}

                #A local_copy_of_moved_or_removed_elements - we'll add these lists to the main list as a tuple
                local_moved_or_removed_elements_self = []
                local_moved_or_removed_elements_other = []

                for k, v in self_el_parent_sc_se_lookup.items():
                    try:
                        other_el_parent_sc_se_lookup[k]
                    except KeyError:
                        local_moved_or_removed_elements_self.append(v)

                for k, v in other_el_parent_sc_se_lookup.items():
                    try:
                        self_el_parent_sc_se_lookup[k]
                    except KeyError:
                        local_moved_or_removed_elements_other.append(v)

                if len(local_moved_or_removed_elements_self)>0 or len(local_moved_or_removed_elements_other)>0:
                    moved_or_removed_elements += [(local_moved_or_removed_elements_self,local_moved_or_removed_elements_other)]

            #Now look the other way - are there elements in other_elements that have are new to this structure?
            for other_shortcode, elements_with_shortcode in other_element_lookup.items():
                try:
                    self_elements = self_element_lookup[other_shortcode]
                except KeyError:
                    new_elements += elements_with_shortcode


        else:
            new_elements = None
            moved_or_removed_elements = None
            removed_elements = None

        #The following will be done in the hierarchy manipulators, since they are at element level, and require a calculation recording at the start
        # + New calculation elements
        # + Calculation changes

        #Now do the diff

        sec = self.diff(other,shortcode_translations=shortcode_translations,reverse_translations=reverse_translations)

        sec.new_elements = new_elements
        sec.moved_or_removed_elements = moved_or_removed_elements
        sec.removed_elements = removed_elements


        return sec

    def diff(self,other,shortcode_translations=None,reverse_translations=None):
        '''
        Compare this StructureElement to another, essentially doing a diff
        If an element is new or has been removed then record this information.
        If an element is in the same position or has been moved, record the information and then proceed to checking the children
        Return a StructureElementComparison object

        :param other: StructureElement to compare self to
        :param shortcode_translations: dictionary for translating shortcodes of "other" structure elements to shortcodes of "self" structure elements, so that similar hierarchies can be compared efficiently
        :param reverse_translations: You shouldn't need to specify this. It exists so that we don't have to calculate the reverse translation for every _recursive_ call of this function
        '''
        if shortcode_translations is None:
            shortcode_translations = {}

        sec = StructureElementComparison(self,other)

        self_children_keys  = {se.shortname:n for n, se in enumerate(self._child_structure_elements)}
        other_children_keys = {}

        for n, se in enumerate(other._child_structure_elements):
            se = se.shortname
            try:
                se = shortcode_translations[se]
            except KeyError:
                pass
            other_children_keys[se] = n

        if reverse_translations is None:
            reverse_translations = {v:k for k,v in shortcode_translations.items()}

            #Fill the reverse translation dict with keys for anything we didn't get in the translation dictionary, to save us trapping KeyErrors all over the place in the following code
            #Note, for an empty translation dictionary, we'll be completely filling this reverse translation dictionary with same shortname:shortname pairs
            for k in other_children_keys.keys():
                try:
                    reverse_translations[k]
                except KeyError:
                    reverse_translations[k] = k

        self_children_pos_lookup  = {n:se for n, se in enumerate( self._child_structure_elements)}
        other_children_pos_lookup = {n:se for n, se in enumerate(other._child_structure_elements)}



        #Now do the diff

        for op, key_list in _diff(list(self_children_keys.keys()),list(other_children_keys.keys())):
            #print(op,key_list)
            for k in key_list:
                comp = None
                transop = op
                if   transop == '-':
                    is_in_self = True
                    is_in_other = False
                    try:
                        this_pos = self_children_keys[k]
                        #print(this_pos)
                    except KeyError:
                        this_pos = None
                    try:
                        other_pos = other_children_keys[k]
                        #print(other_pos)
                    except KeyError:
                        other_pos = None

                    if this_pos is not None and other_pos is not None:
                        if this_pos > other_pos:
                            transop = '^'
                        if this_pos < other_pos:
                            transop = 'v'

                    if transop != '-':
                        #if this is not a true removed item (i.e. it is moved) we will want to diff the children
                        this_se         = self_children_pos_lookup[this_pos]
                        try:
                            other_se        = other_children_pos_lookup[other_pos]
                            is_in_other     = True
                        except KeyError:
                            other_se        = None
                        #print('comparing {} to {}'.format(this_se.shortname,other_se.shortname))
                        comp            = this_se.diff(other_se,shortcode_translations,reverse_translations)

                        comp.is_in_self        = is_in_self
                        comp.is_in_other       = is_in_other
                        branches_match  = comp.same

                        if not branches_match:
                            transop+='>'
                    else:
                        this_se = self_children_pos_lookup[this_pos]
                        comp = StructureElementComparison(this_se,None)

                    #print (k+ '\t'+transop)
                elif transop == '+':
                    is_in_self = False
                    is_in_other = True
                    try:
                        this_pos = self_children_keys[k]
                        #print(this_pos)
                    except KeyError:
                        this_pos = None
                    try:
                        other_pos = other_children_keys[k]
                        #print(other_pos)
                    except KeyError:
                        other_pos = None

                    if this_pos is not None and other_pos is not None:
                        if this_pos > other_pos:
                            transop = 'v'
                        if this_pos < other_pos:
                            transop = '^'

                    if transop != '+':
                        #if this is not a true removed item (i.e. it is moved) we will want to diff the children
                        is_in_self = True
                        is_in_other = True

                        this_se = self_children_pos_lookup[this_pos]
                        other_se = other_children_pos_lookup[other_pos]

                        #Reverse the comparison for moved items
                        comp = other_se.diff(this_se,shortcode_translations,reverse_translations)

                        comp.is_in_self        = is_in_self
                        comp.is_in_other       = is_in_other
                        branches_match = comp.same

                        if not branches_match:
                            transop+='>'
                    else:
                        other_se = other_children_pos_lookup[other_pos]
                        comp = StructureElementComparison(other_se,None)


                    #print ('\t'+transop+' '+k)

                else:
                    #The branches are equal on the face of it - but are the children all the way down the same?
                    #Check the children

                    is_in_self = True
                    is_in_other = True

                    this_pos  = self_children_keys[k]
                    other_pos = other_children_keys[k]

                    this_se   = self_children_pos_lookup[this_pos]
                    other_se  = other_children_pos_lookup[other_pos]
                    #print('comparing {} to {}'.format(this_se.shortname,other_se.shortname))
                    comp = this_se.diff(other_se,shortcode_translations,reverse_translations)

                    comp.is_in_self        = is_in_self
                    comp.is_in_other       = is_in_other
                    branches_match = comp.same

                    if not branches_match:
                        transop='>>'
                    #print(k+ '\t'+transop+' '+k)

                if comp is not None:
                    comp.op =    transop

                    comp.is_in_self        = is_in_self
                    comp.is_in_other       = is_in_other

                    sec.comparison_list.append(comp)





        return sec

class ElementSecurity(object):
    '''Encapsulate Element security, to make viewers, data_viewers and modifiers '''
    def __init__(self
                ,element
                ,viewers = set()
                ,data_viewers = set()
                ,modifiers = set()
                ,initialise_synched = False
                ,initialise_as_default = True
                ):

        self.element        = element
        self._viewers       = _SecurityUsersGetter(element = element, users = viewers, initialise_synched=initialise_synched, initialise_as_default = initialise_as_default)
        self._data_viewers  = _SecurityUsersGetter(element = element, users = data_viewers, initialise_synched=initialise_synched, initialise_as_default = initialise_as_default)
        self._modifiers     = _SecurityUsersGetter(element = element, users = modifiers, initialise_synched=initialise_synched, initialise_as_default = initialise_as_default)

    @property
    def viewers(self):
        return self._viewers

    @property
    def data_viewers(self):
        return self._data_viewers

    @property
    def modifiers(self):
        return self._modifiers

    def _generic_setter(self, attribute, item, attribute_name):
        '''Used for the viewers, data_viewers and modifiers setters'''
        if isinstance(item, _SecurityUsersGetter):
            pass

        else:
            #Can't set to a new string if not empty - this is too unsafe. Insist on calling .clear() first
            if len(attribute) > 0:
                raise AttributeError('Cannot add {} of type {} to {} because {} is not empty. Use {}.clear() to empty or += to add extra items'.format(repr(item),type(item),attribute_name,attribute_name,attribute_name))

            if isinstance(item,str):
                attribute.add(item)
            else:
                inner_error = False
                try:
                    for subitem in item:
                        if isinstance(subitem,str):
                            attribute.add(subitem)
                        else:
                            inner_error = True
                            raise AttributeError('Cannot add {} of type {} to {} from iterable {}. Can only add shortcode strings to an empty {}'.format(repr(subitem),type(subitem),attribute_name,str(item),attribute_name))
                #Type error raised if trying to iterate over a non-iterable
                except TypeError as te:
                    if inner_error:
                        raise te
                    else:
                        raise AttributeError('Cannot add {} of type {} to {}. Can only add shortcode strings to an empty {}'.format(repr(item),type(item),attribute_name,attribute_name))

        return attribute

    @viewers.setter
    def viewers(self,item):
        return self._generic_setter(self._viewers, item, attribute_name='viewers')

    @data_viewers.setter
    def data_viewers(self,item):
        return self._generic_setter(self._data_viewers, item, attribute_name='data_viewers')

    @modifiers.setter
    def modifiers(self,item):
        return self._generic_setter(self._modifiers, item, attribute_name='modifiers')

    @property
    def edited(self):
        return self.viewers.edited or self.data_viewers.edited or self.modifiers.edited


class FieldDefinition(object):
    '''Definition of a Dimension Field. Belongs to a Dimension, not to an Element'''
    def __init__(self, longname , shortname=None,description=None):

        if shortname is not None:
            shortname = str(shortname)

            if len(shortname) == 0:
                raise ValueError("FieldDefinition was created with a shortname with zero characters. Explicit shortnames in a FieldDefinition must not be an empty string")
            if len(shortname) > 10:
                raise ValueError("FieldDefinition was created with a shortname with greater than 10 characters ({}). Explicit shortnames in a FieldDefinition must be less than 10 characters long".format(shortname))

            for character in "'+-*/()@,|^=\r\n\t"+r'" ':
                if character in shortname:
                    raise ValueError("FieldDefinition was created with a shortname ({}) which contained a bad character ({}). FieldDefinition shortnames are restricted to standard characters".format(shortname,character))

        self.shortname   = shortname

        self.longname    = longname
        self.description = description


class Viewpoint(object):
    '''An Empower Viewpoint. A viewpoint specifies a subcube of the entire Empower cube. We read and load data from Viewpoints.
    Viewpoints are a collection of structures, with one structure per dimension.
    '''
    def __init__(self, shortname, structure_0=None, structure_1=None, structure_2=None, structure_3=None, structure_4=None, structure_5=None, structure_6=None, structure_7=None, structure_8=None, structure_9=None, structure_10=None, structure_11=None, structure_12=None, site=None,longname=None,description=None,physid=None):
        self.site         = site
        self.physid       = physid

        self.shortname    = shortname
        self.longname     = longname
        self.description  = description

        self.structures = {}

        #Since we are going to have to define a helper function anyway, may as well define it two different ways - one for if there is a site, a different one otherwise

        self._put_structure_or_string(structure_0 , 0 )
        self._put_structure_or_string(structure_1 , 1 )
        self._put_structure_or_string(structure_2 , 2 )
        self._put_structure_or_string(structure_3 , 3 )
        self._put_structure_or_string(structure_4 , 4 )
        self._put_structure_or_string(structure_5 , 5 )
        self._put_structure_or_string(structure_6 , 6 )
        self._put_structure_or_string(structure_7 , 7 )
        self._put_structure_or_string(structure_8 , 8 )
        self._put_structure_or_string(structure_9 , 9 )
        self._put_structure_or_string(structure_10, 10)
        self._put_structure_or_string(structure_11, 11)
        self._put_structure_or_string(structure_12, 12)


    def _put_structure_or_string(self, src,dimension_number):
        #the inputed structures could be a shortname or an actual Structure() object
        #either create a structure with the shortname or use the Structure()
        
        log.debug('Putting {} into Structure for dimension {} with site {}'.format(repr(src),dimension_number,self.site))


        #the inputed structures could be a shortname or an actual Structure() object
        #either create a structure with the shortname or use the Structure()
        log.debug('Putting {} into Structure for dimension {} with site {} '.format(repr(src),dimension_number, self.site))

        if src is None:
            self.structures[dimension_number] = None
            return

        if isinstance(src,str):
            if self.site is not None:
                try:
                    self.site.dimensions[dimension_number].structures._structures[src]
                except KeyError:
                    # JAT 20210709 - I'm not sure this is so good having looked at it a second time - we could end up accidentally creating structrues
                    self.site.dimensions[dimension_number].structures._structures[src] = Structure(shortname = src,dimension = self.site.dimensions[dimension_number])

                self.structures[dimension_number] = self.site.dimensions[dimension_number].structures._structures[src]                         
            else:
                self.structures[dimension_number]  = Structure(shortname = src,dimension_index = dimension_number)
        elif isinstance(src,Structure):
            self.structures[dimension_number]  = src
        elif isinstance(src,StructureElement):
            self.structures[dimension_number]  = src
        elif isinstance(src,Element):
            self.structures[dimension_number]  = StructureElement(element=src)
        else:
            # ducktype it - if it quacks like a Structure we'll be OK
            self.structures[dimension_number]  = src

        # Try to set our site using the internal site of the structure
        try:
            self.site = src.dimension.site
        except AttributeError:
            pass               

        log.debug('Set target {} for {} with no site'.format(repr(self.structures[dimension_number]),repr(self)))
                
    def load(self, src, mappings = {},safe_load=True,identifier_columns=None,ignore_zero_values=True,clear_focus_before_loading=True):
        if identifier_columns is None:
            identifier_columns=[]
            
        focus = Focus(self)
        focus.load(src=src
                  ,mappings=mappings
                  ,safe_load=safe_load
                  ,identifier_columns=identifier_columns
                  ,ignore_zero_values=ignore_zero_values
                  ,clear_focus_before_loading=clear_focus_before_loading
                  )

    def __len__(self):

        result = 1
        for structure in self.structures.values():
            if structure is not None:
                result *= len(structure)

        return result

class Focus(object):

    def __init__(self, src):
        self._viewpoint = None
        self._structures = _FocusStructuresGetter(focus = self)
            
        if isinstance(src,Viewpoint):
            self._viewpoint = src
            #Copy in the viewpoint structures into the focus
            for k,v in self._viewpoint.structures.items():
                self._structures[k] = v
                
    def load(self, src, mappings = None,safe_load=True,identifier_columns=None,ignore_zero_values=True,clear_focus_before_loading=True):
        if mappings is None:
            mappings = {}

        if identifier_columns is None:
            identifier_columns=[]
                        
        fl = FocusLoader(source=src
                        ,target=self
                        ,mappings=mappings
                        ,safe_load=safe_load
                        ,identifier_columns=identifier_columns
                        ,ignore_zero_values=ignore_zero_values
                        ,clear_focus_before_loading=clear_focus_before_loading
                        ,_defer_mapper_creation=False)

        fl.load()

    @property
    def viewpoint(self):
        return self._viewpoint

    @property
    def structures(self):
        return self._structures

    @property
    def physid(self):
        if self.viewpoint is None:
            return None
        return self.viewpoint.physid

    @property
    def site(self):
        if self.viewpoint is None:
            return None
        return self.viewpoint.site

    def __len__(self):

        result = 1
        for structure in self.structures.values():
            if structure is not None:
                result *= len(structure)

        return result

class _FocusStructuresGetter(object):
    '''Class for ensuring that _setitem_ on structures obeys Focus rules
    It behaves like a dict
    The returned structures are numbered in the same way that .structures in a Viewpoint are
    '''

    def __init__(self,focus):
        self._structures={}

    #Unlike a standard dictionary which returns keys in iter, return values (since that's what we usually want)
    def __iter__(self):
        self._iterator = iter(self.values())
        return self

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self,item):
        try:
            return self._structures[item]
        except KeyError:
            if isinstance(item,int):
                return None
            else:
                raise

    def __setitem__(self,key,item):
        self._structures[key] = item

    ##Define what happens when we call +=
    ##We want to append
    #def __iadd__(self,other):
    #    assert isinstance(other,Structure)
    #    #add the new structure into the dictionary using __setitem__
    #    self[other.shortname] = other
    #    return self

    def values(self):
        return self._structures.values()

    def items(self):
        return self._structures.items()

    def keys(self):
        return self._structures.keys()

    def __len__(self):
        return len(self._structures)


    def __repr__(self):
        return '{} from <{} object at {}>'.format('{' + '\n'.join([ "'{}':{}".format(k,repr(v)) for k,v in self.items()]) + '}',self.__class__.__name__,hex(id(self)))



###################################################################
#
# Mappers
#
###################################################################



class TableEmpowerMapper(object):
    '''Base class for classes mapping tables (so far only pandas DataFrames) to Empower'''
    pass

class Constant(TableEmpowerMapper):
    '''Object for for use with `Loader`s, designed to add a column to a pandas DataFrame containing a single physical identifier for the single Empower Element we want to load against.'''

    def __init__(self,constant=None):
        '''Object for use with `Loader`s,for easily adding the physical identifier of a constant element to the dataframe

        :param constant: A string containing the shortcode of the Empower Element we want to load against
        '''
        self.constant = constant

        #if the constant is a string - it is a shortname
        #if the constant is an int - it is a physid

    def map_dataframe(self,dataframe,dimension,loader):
        '''Transform a pandas DataFrame, adding in a column containing an Empower Element physid (physical identifier) that can be used in an Empower bulk load process.

        Returns a list of the names of the columns that have been created by the mapping process.

        :param dataframe: The pandas dataframe being transformed.
        :param dimension: Dimension being mapped. Since we only know the shortname being mapped we need the dimension to translate the string value
        :param loader: Deprecated
        '''

        column_name='dimension_'+str(dimension.index)+'_physid'

        constant_is_string=False
        try:
            self.constant = self.constant+''
            #looks like the constant is a string - assume it is a shortname
            constant_is_string=True

        except TypeError:
            #assume constant is an integer
            pass

        if constant_is_string:
            physid=dimension.elements[self.constant].physid
            log.verbose('Mapping constant '+str(self.constant)+' to '+str(physid)+' for column ['+str(column_name)+']')
            dataframe[column_name] = physid
        else:
            #Add as a physid
            log.verbose('Setting constant to '+str(self.constant)+' for column ['+str(column_name)+']')
            dataframe[column_name] = self.constant

        #return the columns created in the mapping - i.e. the ones that will be used in the explosion
        return [column_name]

class StructureMapper(TableEmpowerMapper):
    '''Object for use with `Loader`s,for easily mapping and aggregating up structures'''

    def __init__(self,shortname_column=None,subtree=None,longname_column=None,field_shortname=None,field_column=None,path=None):
        '''Object for use with `Loader`s,for easily mapping and aggregating up structures
        A column will be added for each level of hierarchy from the leaf to the StructureElement specified in the constructor (i.e. the __init__ method)

        Maps a DataFrame column holding either, shortname, longname or field value for leaf level translation
        **Only one** of shortname_column, longname_column or a combination of field_column and field_shortname needs to be supplied

        :param shortname_column: The column (series) in the pandas DataFrame that will be mapped which holds the leaf shortname
        :param longname_column:  The column (series) in the pandas DataFrame that will be mapped  which holds the leaf longname
        :param field_column:     The column (series) in the pandas DataFrame that will be mapped  which holds the leaf field
        :param field_shortname:  The shortname of the dimension field holding the translation
        :param subtree:          a tuple of (structure shortname, root element shortname,subtree root shortname). Used for exploding data up a structure hierarchy. For backward compatibility only. Use path instead.
        :param path:             path to a StructureElement e.g. 'MyStruct.Hier/Elemn1/Elemen2' - An alternative to the subtree parameter
        '''
        self.subtree          = subtree
        self.path             = path
        #

        self.field_shortname  = field_shortname

        if shortname_column:
            self.column_type = 'shortname'
            self.column_name = shortname_column
        elif longname_column:
            self.column_type = 'longname'
            self.column_name = longname_column
        elif field_column:
            self.column_type = 'field'
            self.column_name = field_column
            if self.field_shortname is None:
                raise ValueError('When a StructureMapper is initialised with a field_column, a field_shortname must also be present')

    def map_dataframe(self,dataframe,dimension,loader):
        '''Transform a pandas DataFrame, adding in a column containing Empower Element physids (physical identifiers) that can be used in an Empower bulk load process.
        A column will be added for each level of hierarchy from the leaf to the StructureElement specified in the constructor (i.e. the __init__ method)

        Returns a list of the names of the columns that have been created by the mapping process.

        :param dataframe: The pandas dataframe being transformed.
        :param dimension: Dimension being mapped. Since we only know the shortname, longname or field being mapped we need the dimension to translate the string values
        :param loader: Deprecated
        '''

        #TODo - work out the actual column type - assume int = physid, assume string = shortname

        log.verbose('Mapping column '+str(self.column_name)+' to structure ['+str(self.subtree if self.subtree else self.path)+']')

        translation_df   = _get_leaf_translation_df_from_tuple(dimension          = dimension
                                                              ,structure_tuple    = self.subtree
                                                              ,structure_element_path = self.path
                                                              ,field_shortname    = self.field_shortname
                                                              )

        #TODO - ensure we have no duplicates in the translation df

        #Put out a very clear message - we can't load if the translation has duplicates, and the remedial action advised


        columns_for_explosion = _translate_dim(df              = dataframe
                                              ,dim_identifier  = self.column_name
                                              ,dim_type        = self.column_type
                                              ,translate_df    = translation_df
                                              ,field_shortname = self.field_shortname
                                              )

        #return the columns created in the mapping - i.e. the ones that will be used in the explosion
        return columns_for_explosion

class ColumnMapper(TableEmpowerMapper):
    '''Utility object for for use with `Loader`s, designed to map columns in a pandas DataFrame to the physical identifiers of the Empower Elements we want to load against.'''

    def __init__(self,column_name,column_type,field_shortname):
        '''Create a new ColumnMapper, a Utility object for for use with `Loader`s, designed to map columns in a pandas DataFrame to the physical identifiers of the Empower Elements we want to load against.

        Maps a DataFrame column holding either, shortname, longname or field value for leaf level translation

        :param column_name: The name of the column in the pandas DataFrame
        :param column_type: one of 'physid', 'shortname', 'longname' or 'field'
        :param field_shortname: When this is set, the values in the column will be translated from the field in the dimension with that shortname. Use with column_type = 'field'
        '''


        self.column_name = column_name
        self.column_type = column_type
        self.field_shortname = field_shortname

    def map_dataframe(self, dataframe,dimension,loader):
        '''Transform a pandas DataFrame, adding in a column containing Empower Element physids (physical identifiers) that can be used in an Empower bulk load process.

        Returns a list of the names of the columns that have been created by the mapping process.

        :param dataframe: The pandas dataframe being transformed.
        :param dimension: Dimension being mapped. Since we only know the shortname, longname or field being mapped we need the dimension to translate the string values
        :param loader: Deprecated
        '''

        #Work out the column type
        #if it is a string column, then assume it is a shortname
        #If it is an int column, then assume it is a physid (so don't do anything with it at all

        translation_df = dimension._get_simple_translation_df(output_column_name = 'dim_'+str(dimension.index)+'_physid_for_'+self.column_name,field_shortname=self.field_shortname)

        columns_for_explosion = _translate_dim(df              = dataframe
                                              ,dim_identifier  = self.column_name
                                              ,dim_type        = self.column_type
                                              ,translate_df    = translation_df
                                              ,field_shortname = self.field_shortname
                                              )

        #return the columns created in the mapping - i.e. the ones that will be used in the explosion
        return columns_for_explosion


class CubeMapper(object):
    '''Class which maps a table (pandas DataFrame) to a Focus
    Contains the logic for turning dictionaries into more complex mapping objects which are Empower structure aware, and for inferring mapping information
    '''

    def __init__(self,mappings=None,target = None, source = None):

        self._mappers = {}

        self._initial_target = target
        self._initial_source = source

        #Initialise empty mappers
        for n in range(13):
            self._mappers[n] = None

        if mappings is not None:
            #Now put the mappings we've been given into place
            try:
                #If the mappers object is a dict like, then go over the keys (which refer to dimensions we hope)
                for k,v in mappings.items():
                    try:
                        self[k]
                    except KeyError:
                        raise KeyError("mappings[{}] cannot be set because only integer indexed or longname mappings are handled - set each mapping's keys to an integer between 0 and 12 or the longname of the dimension".format(k))

                    self[k] = v

            except AttributeError:
                try:
                    for mapping in mappings:
                        pass
                except TypeError:
                    raise

    def __getitem__(self,item):
        index = None
        if isinstance(item,int):
            index = item
        else:
            for i in range(13):
                try:
                    if self.target.site.dimensions[i].longname == item:
                        index = i
                except (AttributeError,KeyError):
                    pass

        if index is None:
            raise KeyError('Dimension[{}] was not found in site'.format(item) )

        return self._mappers[index]

    def __setitem__(self,item,value):
        index = None
        if isinstance(item,int):
            index = item
        else:
            for i in range(13):
                try:
                    if self.target.site.dimensions[i].longname == item:
                        index = i
                except (AttributeError,KeyError):
                    pass

        if index is None:
            raise KeyError('Dimension[{}] was not found in site'.format(item) )

        self._mappers[index] = value

    @property
    def target(self):
        return self._initial_target
    @property
    def source(self):
        return self._initial_source
    @property
    def site(self):
        return self.target.site

    @property
    def columns(self):
        return [c for c in self.source.columns]



    def _get_implied_shortcode_list_and_mapping_type(self, dimension_index, object_to_check_against, column_list_to_check_against = None):
        '''
        Get a list of shortcodes implied by the this object's mapping for a given dimension_index, given an object that might contain those shortcodes

        e.g. 'v_LONG' could be a constant shortname, or a column holding shortnames
             {'Foo':'Bar'} could be an indicator style metric dictionary - column Foo holds values to go to metric shortname Bar, or a column-field dictionary column Foo goes to field Bar on dimension x
             {'Foo':{'Bar':1,'Guf':1}} is a shortname value mapping - if we find Bar in column Foo, we put 1 against the metric Bar, if we find Guf, we put 1 against that metric shortcode

        If the mapping type is columns to fields, the returned list will instead be a dictionary of the form {(field_value, field_value, ...): shortname, ...}

        :param dimension_index: index of the dimension
        :param object_to_check_against: Empower object to check against - a Site, Dimension, a Structure or a StructureElement
        :param column_list_to_check_against: Optional list of columns that we can check against - useful if we have a large csv file with headers as the source. This parameter is ignored if this Cubemapper has a source

        :return: list_or_dict_of_shortcodes, mapping_type - one of 'constant shortname','column name','columns to fields','columns to shortnames','column to shortname to value', and then column names
        '''

        #convert object_to_check_against to the dimension we wish to check if we have got a Site object, this case will be handled below
        if isinstance(object_to_check_against,Site):
            object_to_check_against = object_to_check_against.dimensions[dimension_index]

        if self.source is not None:
            column_list_to_check_against = [c for c in self.source.columns]
        else:
            column_list_to_check_against = None

        #create a columns_dict for fast lookup
        if column_list_to_check_against is not None:
            columns_dict = {c:c for c in column_list_to_check_against}
        else:
            columns_dict = None

        column_names = None

        #When there is no mapping, the implied shortcode list is None - not [], just None
        try:
            mapping = self[dimension_index]

            if mapping is None:
                return None, None, None
        except KeyError:
            return None, None, None

        #We may need to work out whether we are seeing a
        if   isinstance(object_to_check_against,Dimension):
            elements_dict = object_to_check_against.elements
            fields_dict   = object_to_check_against.fields

        elif isinstance(object_to_check_against,Structure):
            elements_dict = object_to_check_against.dimension.elements
            fields_dict   = object_to_check_against.dimension.fields

        elif isinstance(object_to_check_against,StructureElement):
            elements_dict = object_to_check_against.dimension.elements
            fields_dict   = object_to_check_against.dimension.fields
        else:
            raise TypeError("Cannot map to object {} of type {}".format(object_to_check_against,type(object_to_check_against)))

        is_constant_shortcode_or_column_implied_shortcode_mapping = False
        is_field_or_shortcode_mapping = False
        is_shortcode_value_mapping = False
        is_constant_datetime = False

        if isinstance(mapping,str):
            # If we get a single string we assume that we are looking at a single shortcode OR a single column (with the implication that the column contains shortcodes)
            is_constant_shortcode_or_column_implied_shortcode_mapping = True
        elif isinstance(mapping,datetime.datetime):
            # A single datetime implies that we are doing a date mapping at whatever granularity the supplied hierarchy has
            is_constant_datetime = True

        else:
            if len(mapping) == 1:
                for k, v in mapping.items():
                    try:
                        #If we have a single key with a dictionary mapping, then this is a shortcode - value mapping
                        for k2, v2 in v.items():
                            is_shortcode_value_mapping = True
                            break
                        shortcode_value_mapping = v
                        column_names = [k]
                        break
                    except AttributeError:
                        is_field_or_shortcode_mapping = True
                    break
            else:
                is_field_or_shortcode_mapping = True

        if not is_constant_shortcode_or_column_implied_shortcode_mapping and not is_field_or_shortcode_mapping and not is_shortcode_value_mapping and not is_constant_datetime:
            raise AttributeError('Cannot determine what sort of mapping has been created for dimension[{}]'.format(dimension_index))

        is_constant_shortcode = False
        is_column_implied_shortcode_mapping = False

        if is_constant_shortcode_or_column_implied_shortcode_mapping:
            try:
                elements_dict[mapping]
                is_constant_shortcode = True
                is_column_implied_shortcode_mapping = False
            except KeyError:
                is_constant_shortcode = False
                is_column_implied_shortcode_mapping = True
                column_names = [mapping]

        is_field_mapping = False
        is_shortcode_mapping = False

        if is_field_or_shortcode_mapping:

            found_fields = []
            missing_fields = []
            missing_element_shortcodes = []
            column_names = []
            #Check whether the mapped things are fields or shortcodes
            for k, v in mapping.items():
                column_names.append(k)

                #{'Foo':None} maps a column to a shortname
                if v == None:
                    v = 'Short Name'

                try:
                    fields_dict[v]
                    found_fields.append(v)
                except KeyError:
                    missing_fields.append(v)
                try:
                    elements_dict[v]
                except KeyError:
                    missing_element_shortcodes.append(v)

            if len(missing_fields) == 0 and len(missing_element_shortcodes) == 0:
                raise ValueError('Cannot determine what sort of mapping has been created for dimension[{}] all mapped items {} could be either Fields or Element shortnames'.format(dimension_index,list(mapping.values)))

            if len(missing_fields) == 0:
                is_field_mapping = True

            if len(missing_element_shortcodes) ==  0:
                is_shortcode_mapping = True

            if not is_field_mapping and not is_shortcode_mapping:
                raise ValueError('Cannot determine what sort of mapping has been created for dimension[{}]. {} are not Fields and {} are not Element shortnames '.format(dimension_index,missing_fields,missing_element_shortcodes))

        #Check column names make sense compared to the source
        if column_names is not None and columns_dict is not None:
            for column_name in column_names:
                try:
                    columns_dict[column_name]
                except KeyError:
                    raise KeyError('Column "{}" was implied by mapping {} but was not found in column names {} or in shortcodes of dimension'.format(column_name,mapping,column_list_to_check_against) )

        if column_names is not None and len(column_names) > 0:
            if self.source is None:
                raise mpex.LoaderSetupError('Mapped column names {} in dimension {} could not be resolved because there is no source DataFrame or there are no columns in the source DataFrame'.format(column_names, dimension_index))
            elif self.columns is None:
                raise KeyError('Mapped column names {} in dimension {} could not be resolved because there is no source DataFrame or there are no columns in the source DataFrame'.format(column_names, dimension_index))

        if isinstance(object_to_check_against,Dimension):
            #If we are checking against a dimension, ensure that a single shortcode is one of the elements
            if is_constant_shortcode:
                element = object_to_check_against.elements[mapping]
                return [element.shortname], 'constant shortname',column_names
            elif is_column_implied_shortcode_mapping:
                return None, 'column name',column_names
            elif is_shortcode_mapping:
                #metric_dict style mapping
                return [object_to_check_against.elements[sc].shortname for sc in mapping.values()], 'columns to shortnames',column_names

            elif is_field_mapping:
                fields_element_lookup = {}
                for el in object_to_check_against.elements:
                    fields_element_lookup[tuple(el.fields[field] for field in found_fields)] = el.shortname

                return fields_element_lookup,  'columns to fields',column_names
            elif is_shortcode_value_mapping:
                return [object_to_check_against.elements[sc].shortname for sc in shortcode_value_mapping.keys()], 'column to shortname to value',column_names
            elif is_constant_datetime:
                raise mpex.LoaderSetupError('Cannot map constant datetimes yet')


        elif isinstance(object_to_check_against,Structure) or  isinstance(object_to_check_against,StructureElement):

            #Look through all of the hierarchies for a Structure, for a StructureElement look through that
            if isinstance(object_to_check_against,Structure):
                hierarchies = object_to_check_against.hierarchies
            else:
                hierarchies = [object_to_check_against]

            if is_constant_shortcode:
                for hierarchy in hierarchies:
                    if mapping in [l.shortname for l in hierarchy.get_elements(mapping)]:
                        return [mapping],  'constant shortname',column_names
                #If we didn't return the shortcode, raise an KeyError
                raise KeyError('Shortcode {} is not in the Structure {} in dimension {}'.format(mapping,object_to_check_against.shortname, dimension_index))

            elif is_constant_datetime:
                for hierarchy in hierarchies:
                    for se in hierarchy.walk():
                        try:
                            if se.element.date == mapping:
                                return [se.shortname],  'constant date', column_names
                        except AttributeError:
                            #Not all elements will have a .date attribute - that's OK
                            pass

                #If we didn't return an element with the shortcode, raise an KeyError
                raise KeyError('No element found with datetime {} in the Structure {} in dimension {}'.format(mapping,object_to_check_against.shortname, dimension_index))

            elif is_column_implied_shortcode_mapping:
                return None, 'column name',column_names

            elif is_shortcode_mapping:
                #metric_dict style mapping
                elements = []
                for hierarchy in hierarchies:
                    for sc in mapping.values():
                        if sc in [l.shortname for l in hierarchy.get_elements(sc)]:
                            elements.append(sc)
                return elements, 'columns to shortnames',column_names

            elif is_field_mapping:
                fields_element_lookup = {}
                for hierarchy in hierarchies:
                    for el in hierarchy.leaves:
                        fields_element_lookup[tuple(el.fields[field] for field in found_fields)] = el.shortname
                return fields_element_lookup, 'columns to fields' ,column_names
            elif is_shortcode_value_mapping:
                elements = []
                for sc in shortcode_value_mapping.keys():
                    for hierarchy in hierarchies:
                        if sc in [l.shortname for l in hierarchy.get_elements(sc)]:
                            elements.append(sc)

                return elements, 'column to shortname to value', column_names

            else:
                #We've fallen off the end of the world here - something in the logic of the code is broken
                raise mpex.LoaderSetupError('Could not find mapping type')

    def _create_TableMappers(self):
        if self._initial_target is None:
            raise mpex.LoaderSetupError('Cannot set up a FocusLoader without a target')

        self._dimension_0_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 0)
        self._dimension_1_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 1)
        self._dimension_2_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 2)
        self._dimension_3_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 3)
        self._dimension_4_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 4)
        self._dimension_5_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 5)
        self._dimension_6_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 6)
        self._dimension_7_mapper   = self._get_TableMapper_for_dimensionindex(dimension_index = 7)
        self._metric_mapper        = self._get_TableMapper_for_dimensionindex(dimension_index = 8)
        self._mode_mapper          = self._get_TableMapper_for_dimensionindex(dimension_index = 9)
        self._base_mapper          = self._get_TableMapper_for_dimensionindex(dimension_index = 10)

        time_mapper_tuple          = self._get_TableMapper_for_dimensionindex(dimension_index = 11)

        if time_mapper_tuple is None:
            self._time_mapper         = None
            self._empower_period_type = None
        else:
            self._time_mapper,self._empower_period_type = time_mapper_tuple

    def _get_effective_element_for_structure(self,dimension_index,effective_elements):
        '''
        :param effective_elements: Currently ignores - see comments below
        '''
        #effective_elements may be None.
        #This is what gets returned when we have figured out we are looking at a column
        #It implies that we pass the effective element as computed by self.effective_dimension_elements()

        ##!!!!!!!!
        # for now we are ignoring effective_elements input - it might have some use, but unfortunately it gets the ones at leaf level
        # for comparison with the data coming in
        # we need the rootwise ones, as passed to the Focus String maker.
        # Since we've already calculated these, we have an opportunity for reusing the calculation result (possibly by memoizing the function)
        # For now use the function again

        effective_elements = self.effective_dimension_elements(dimension_index)

        #If still None, raise an error
        if effective_elements is None:
            raise mpex.LoaderSetupError('Could not compute effective elements to create a TableMapper from for dimension index {}, for {}'.format(dimension_index,repr(self.target.structures[dimension_index])))

        if len(effective_elements) > 1:
            #TODO - change this when we have e.g. multiple Comparisons
            raise mpex.LoaderSetupError('Multiple Effective elements {} in dimension {} not coded for StructureMappers yet'.format([repr(el) for el in effective_elements], dimension_index))

        if len(effective_elements) > 1:
            raise mpex.LoaderSetupError('Multiple Effective elements {} in dimension {} not coded for StructureMappers yet'.format([repr(el) for el in effective_elements], dimension_index))

        effective_element = effective_elements[0]

        return effective_element

    def _get_TableMapper_for_dimensionindex(self,dimension_index):

        #Handle the case for empty Unit dimensions
        try:
            if self.site is None:
                return None

            dim = self.site.dimensions[dimension_index]
            if dim is None:
                return None
        except KeyError:
            return None
        
        
        effective_elements, mapping_type,column_names = self._get_implied_shortcode_list_and_mapping_type(dimension_index = dimension_index, object_to_check_against =self.target.structures[dimension_index])


        #Check that a column name really is a column name, and not a mistyped shortname, or a lot of innocent data is going to be destroyed
        if column_names is not None:
            for column_name in column_names:
                if self.source is None or column_name not in self.columns:
                    raise mpex.LoaderSetupError('Mapped column name {} in dimension {} not in column names of source {}'.format(column_name, dimension_index, self.columns))

        #We handle Structures differently to StructureElements
        is_structure = isinstance(self.target.structures[dimension_index],Structure)
        is_structure_element = isinstance(self.target.structures[dimension_index],StructureElement)

        return_value = None

        if mapping_type =='constant shortname':
            return_value = Constant(constant = effective_elements[0])
        elif mapping_type =='column name':


            if is_structure:
                effective_element = self._get_effective_element_for_structure(dimension_index=dimension_index,effective_elements = effective_elements)

                return_value =  StructureMapper(shortname_column=column_name,path = effective_element.path)
            elif is_structure_element:
                structure_element = self.target.structures[dimension_index]

                if structure_element.is_leaf:
                    return_value =  ColumnMapper(column_name=column_name,column_type='shortname',field_shortname=None)
                else:
                    return_value =  StructureMapper(shortname_column=column_name,path = structure_element.path)
            else:
                return_value =  ColumnMapper(column_name=column_name,column_type='shortname',field_shortname=None)


        elif mapping_type =='columns to fields':
            if dimension_index == 11:
                raise mpex.LoaderSetupError('Cannot map fields for the time dimension')

            if is_structure:
                #We have to use logic to figure out, from the structure what the correct effective element is
                effective_element = self._get_effective_element_for_structure(dimension_index=dimension_index,effective_elements = effective_elements)

                return_value =  StructureMapper(field_column=column_name,field_shortname=list(self._mappers[dimension_index].values())[0],path = effective_element.path)

            elif is_structure_element:

                structure_element = self.target.structures[dimension_index]

                field_shortname=list(self._mappers[dimension_index].values())[0]

                if structure_element.is_leaf:
                    return_value = ColumnMapper(column_name=column_name,column_type='field',field_shortname=field_shortname)
                else:
                    return_value = StructureMapper(field_column=column_name,field_shortname=field_shortname,path = structure_element.path)

            else:
                #TODO -extend this to multi field multi column variant
                #column_type: one of 'physid', 'shortname', 'longname' or 'field'
                field_shortname=list(self._mappers[dimension_index].values())[0]

                return_value = ColumnMapper(column_name=column_name,column_type='field',field_shortname=field_shortname)

        elif mapping_type =='columns to shortnames':
            return_value = self._mappers[dimension_index]
        elif mapping_type =='column to shortname to value':
            raise mpex.LoaderSetupError('column:{shortname:value} style mapping (i.e. flag-style mapping) not implemented yet')

        elif mapping_type =='constant date':
            if dimension_index != 11:
                raise mpex.LoaderSetupError('Could not create a focus loader for dimension index {} with a constant date. You can only set a constant data fot the Time dimension (11)'.format(dimension_index))
            else:    
                return_value = Constant(constant = self._mappers[dimension_index]) # JAT 20210309 - put this line in speculatively - it should put the datetime or tuple into the Constant...
        elif mapping_type is None:
            #No mapping was supplied
            #This, this had better be a Structure with a single effective element or single leaf StructureElement
            #Then we can create a single Element to insert into
            if is_structure:
                effective_element = self._get_effective_element_for_structure(dimension_index=dimension_index,effective_elements = effective_elements)
                if not effective_element.is_leaf:
                    raise mpex.LoaderSetupError('Could not create a focus loader for dimension index {} without a supplied mapping, because the StructureElement {} in the relevant Focus was not a leaf element'.format(dimension_index,effective_element.path))

                return_value = Constant(constant = effective_element.physid)
            elif is_structure_element:
                structure_element = self.target.structures[dimension_index]

                if not structure_element.is_leaf:
                    raise mpex.LoaderSetupError('Could not create a focus loader for dimension index {} without a supplied mapping, because the StructureElement {} in the relevant was not a leaf element'.format(dimension_index,effective_element.path))

                return_value = Constant(constant = structure_element.physid)
            else:
                raise mpex.LoaderSetupError('Could not create a focus loader for dimension index {} without a supplied mapping, because found StructureElement in the relevant was of type {} '.format(dimension_index,repr(effective_element)))

        else:
            raise mpex.LoaderSetupError('Got lost deciding TableMapper type for dimension index {} for structure definition {}. Internally, effective_elements = {}, mapping_type = {}, column_names = {}'.format(dimension_index, repr(self.target.structures[dimension_index]), repr(effective_elements), mapping_type,repr(column_names)))


        if dimension_index == 11:
            #Time is handled differently, as it needs to return either a ColumnMapper and an Empower time period
            #or a constant and  an Empower time period

            if isinstance(return_value,Constant):
                found_element = None
                found_date    = None
                found_empower_date_constant = None

                if isinstance(return_value.constant,str):
                    try:
                        found_element = self.site.dimensions[11].elements[return_value.constant]
                    except KeyError:
                        #couldn't find an element - perhaps this is a date string

                        raise mpex.LoaderSetupError('Not Implemented. Time mapping from a string {} is not yet implemented unless that string is a valid shortname of a time element'.format(return_value.constant))

                if isinstance(return_value.constant,datetime.datetime):
                    found_date = return_value.constant

                elif isinstance(return_value.constant,int):
                    #Constant could be an Empower physical id
                    for element in self.site.dimensions[11].elements.values():
                        if element.physid == return_value.constant:
                            found_element = element
                            #TODO handle

                    if found_element is None:
                        #Constant could be a year
                        for element in self.site.dimensions[11].elements.values():
                            if element._start_date  == str(return_value.constant) and element.interval == 'Year' and element.interval_amount == 1 and element.offset is None and element.group_only is None :
                                found_element = element

                elif isinstance(return_value.constant,Element):
                    found_element = return_value.constant

                if found_date is not None:
                    return Constant(found_date), found_empower_date_constant

                if found_element is not None:
                    try:
                        assert found_element.group_only is None
                        assert found_element.interval_amount == 1
                        assert found_element.interval == found_element.resolution
                    except AssertionError:
                        log.error('TimeElement found with incorrect fields for Time Mapping shortname:{}, fields{}'.format(found_element.shortname,found_element.fields))
                        raise

                    if found_element._start_date is None and found_element.offset is not None:
                        #We have a found a Current Month or Current Year element and so on.
                        interval = found_element.interval
                        offset   = found_element.offset
                        #Get the data for the Current Month for the interval, and moev by the offset
                        #TODO
                        raise mpex.LoaderSetupError('Not Implemented. Time mapping from a current month is not yet implemented')
                    else:
                        return Constant(found_element.date),found_element.empower_period_number

            elif isinstance(return_value,ColumnMapper):
                
                # Default is month
                empower_time_constant = llu.EMPOWER_MONTH_CONSTANT
                
                # Try to get the time period from the Time element in the focus
                try:
                    #Get an element from the structure - it should have an Empower date type (week, month, year etc.) and we can use that 
                    empower_time_constant = self.effective_time_elements[0].interval_index
                except AttributeError:
                    # Just go with the default in the case that this is not a standard time element, or if there were no effective elements (although we may never get such a thing in practice because an error would have been raised elsewhere)
                    pass
                    
                return return_value, empower_time_constant
            else:
                raise mpex.LoaderSetupError('Time mapping must be set up with a valid element')

        else:
            return return_value


    @property
    def effective_time_elements(self):

        no_mappings_for_time = self._mappers is None or self._mappers[11] is None

        if self.target is None:
            raise mpex.LoaderSetupError('Cannot compute effective time elements for a FocusLoader which has no target Viewpoint or Focus set')

        #structures[11] is time - we cant' get effective time elements with no time structure set
        if self.target.structures[11] is None:
            raise mpex.LoaderSetupError('Cannot compute effective time elements for a FocusLoader which has no Time structure (.structures[11])')

        dimension_index = 11
        effective_elements, mapping_type,column_names = self._get_implied_shortcode_list_and_mapping_type(dimension_index = dimension_index, object_to_check_against =self.target.structures[dimension_index])

        if isinstance(self.target.structures[11],Structure) and no_mappings_for_time:
            #Check that there is only one hierarchy if we have a Structure and no mappings
            if len(self.target.structures[11].hierarchies) != 1:
                raise mpex.LoaderSetupError('FocusLoader without any mappings cannot handle Time Structures with anything other than 1 hierarchy')

        if isinstance(self.target.structures[11],Structure):

            time_hierarchy = [h for h in self.target.structures[11].hierarchies][0]
        elif isinstance(self.target.structures[11],StructureElement):
            time_hierarchy = self.target.structures[11]

        #Where there are no mappings we are happy to use a single element if one is present in the Time Hierarchy/Structure
        if no_mappings_for_time:

            if len(time_hierarchy.children) == 0:
                return [time_hierarchy]
            else:
                raise mpex.LoaderSetupError('FocusLoader without any mappings cannot handle Time StrucureElements with anything other than a single element')

        if mapping_type == 'constant shortname':
            #Can get the element with the shortcode and turn it into a Structure element
            try:
                leaf_elements = [StructureElement(element=self.site.dimensions[11].elements[effective_elements[0]])]
            except Exception as e:
                print("time_hierarchy")
                print(time_hierarchy)
                print("effective_elements")
                print(effective_elements)                
                raise e
            

        else:

            #time_hierarchy = [h for h in self.target.structures[11].hierarchies][0]
            leaf_elements = [l for l in time_hierarchy.leaves]

        ###Check the leaf elements below for consistency, and for validity against the mapping, before returning them

        #Raise an error if it is a single current month, because we can't handle that yet
        if len(leaf_elements) == 1 and leaf_elements[0]._start_date is None and leaf_elements[0].offset is not None:
            #We have a found a Current Month or Current Year element and so on.
            interval = leaf_elements[0].interval
            offset   = leaf_elements[0].offset
            #Get the data for the Current Month for the interval, and move by the offset
            #TODO
            raise mpex.LoaderSetupError('Not Implemented. Time mapping from a current month is not yet implemented')

        else :
            #Or, check that the leaf elements are of a single Empower time type (e.g. all MONTH)
            #And that the elements are contiguous
            empower_time_type = None
            previous_date = None
            previous_se = None

            dates_to_leaf_elements_lkp = {}

            for se in leaf_elements:

                #Check all fields are populated as we would expect
                if empower_time_type is None:
                    empower_time_type = se.interval

                if empower_time_type != se.interval:
                    raise mpex.LoaderSetupError('Cannot load into a hierarchy of time elements with more than one Interval type. Time element {} in hierarchy {} with Interval {} not same as previous Interval {}'.format(se.shortname,time_hierarchy.path,se.interval,empower_time_type))

                #Check if type or interval is None - if so we are running the loop for the first time

                if se.group_only is not None:
                    raise mpex.LoaderSetupError('Cannot load into Group-Only time element {} in hierarchy {}'.format(se.shortname,time_hierarchy.path))

                if se.interval_amount != 1:
                    raise mpex.LoaderSetupError('Cannot load into time elements with Interval Amounts other than 1. Time element {} in hierarchy {} with Interval Amount {}'.format(se.shortname,time_hierarchy.path,se.interval_amount))

                if se.interval != se.resolution:
                    raise mpex.LoaderSetupError('Cannot load into time elements with Interval Amount not equal to its Resolution. Time element {} in hierarchy {} with Interval Amount {} and Resolution {}'.format(se.shortname,time_hierarchy.path,se.interval_amount,se.resolution))


                date = se.element.date
                if date is not None:
                    dates_to_leaf_elements_lkp[date] = se

                if previous_date is not None:
                    if empower_time_type == 'Month':
                        if previous_date + MONTH != date:
                            raise mpex.LoaderSetupError('Can only load into a Viewpoint with contiguous time elements. Date {} in element {} followed date {} in element in hierarchy {}'.format(date,se.shortname,previous_date,previous_se.shortname,time_hierarchy.path))

                    elif empower_time_type == 'Year':
                        if previous_date + YEAR != date:
                            raise mpex.LoaderSetupError('Can only load into a Viewpoint with contiguous time elements. Date {} in element {} followed date {} in element in hierarchy {}'.format(date,se.shortname,previous_date,previous_se.shortname,time_hierarchy.path))


                previous_time_type = empower_time_type
                previous_date = date
                previous_se = se

            if mapping_type == 'constant date':
                #Since all of the dates in the leaves of the hierarchy are of the same Empower Date Type
                #Then Empower Date Type is unambiguous and the constant date in the mapping must be seen in the context of this date type
                original_date = self._mappers[11]
                assert isinstance(original_date,datetime.datetime)

                #Transform the mappnig to date to one that will look up the correct element
                if empower_time_type == 'Month':
                    lookup_date = datetime.datetime(original_date.year, original_date.month,1)
                elif empower_time_type == 'Year':
                    lookup_date = datetime.datetime(original_date.year, 1,1)
                else:
                    #Other code should have raised the exception if unhandled date type entered
                    assert False
                leaf_element = dates_to_leaf_elements_lkp[lookup_date]
                return [leaf_element]
            else:
                return leaf_elements

        return effective_elements

    @property
    def effective_dim0_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=0)
    @property
    def effective_dim1_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=1)
    @property
    def effective_dim2_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=2)
    @property
    def effective_dim3_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=3)
    @property
    def effective_dim4_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=4)
    @property
    def effective_dim5_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=5)
    @property
    def effective_dim6_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=6)
    @property
    def effective_dim7_elements(self):
        return self.effective_unit_dimension_elements(dimension_index=7)

    def _first_ungrouped_children(self,structure_element):
        if structure_element.group_only == 'Group':
            all_children = []
            for ch in structure_element.children:
                all_children += self._first_ungrouped_children(ch)
            return all_children
        else:
            return [structure_element]

    def effective_dimension_elements(self,dimension_index):
        if dimension_index <= 7:
            if dimension_index < self.site.number_of_unit_dimensions:
                return self.effective_unit_dimension_elements(dimension_index)
            else:
                return None
        elif dimension_index == 8:
            return self.effective_indicator_elements
        elif dimension_index == 9:
            return self.effective_comparison_elements
        elif dimension_index == 10:
            return self.effective_currency_elements
        elif dimension_index == 11:
            return self.effective_time_elements
        elif dimension_index == 12:
            return self.effective_transform_elements


    def effective_unit_dimension_elements(self,dimension_index):

        self._handle_empty_target()

        #Dimension name used for Error messages
        if dimension_index < 8:
            dimension_name = 'Unit '+str(dimension_index)
        if dimension_index==9:
            dimension_name = 'Comparison'
        else:
            dimension_name = 'Dimension '+str(dimension_index)

        if self.target.structures[dimension_index] is None:
            raise mpex.LoaderSetupError('Cannot compute effective unit dimension elements for a FocusLoader which has no structure (.structures[{}])'.format(dimension_index))

        no_mappings_for_this_dimension = False
        if self._mappers is None or len(self._mappers)==0:
            no_mappings_for_this_dimension = True
        else:
            try:
                no_mappings_for_this_dimension = self._mappers[dimension_index] is None
            except KeyError:
                no_mappings_for_this_dimension = True

        #Where there are no mappings we are happy to use a single element if one is available
        if no_mappings_for_this_dimension:

            hierarchy = self._get_hierarchy_direct_or_single_hierarchy_from_structure(dimension_index=dimension_index,dimension_name=dimension_name,enforce_single_element=True)

            first_ungrouped_children = self._first_ungrouped_children(hierarchy)

            #first_ungrouped_children should be a single item list. That item (i.e. that StructureElement) should have no children - i.e. we are loooking at a single element
            if len(first_ungrouped_children) == 1 and len(first_ungrouped_children[0].children) == 0:
                return first_ungrouped_children
            else:
                raise mpex.LoaderSetupError('FocusLoader without any mappings cannot handle {} StructureElements with anything other than a single element. Structure {} has more than one element. Choose another Structure or create mappings for the hierarchy'.format(dimension_name,self.target.structures[dimension_index].longname))
        else:
            #Use _get_implied_shortcode_list_and_mapping_type, because it checks for column existence rather than blithely assuming that column names/shortnames have been typed correctly
            effective_elements, mapping_type,column_names = self._get_implied_shortcode_list_and_mapping_type(dimension_index = dimension_index, object_to_check_against =self.target.structures[dimension_index])

            hierarchy = self._get_hierarchy_direct_or_single_hierarchy_from_structure(dimension_index=dimension_index,dimension_name=dimension_name)

            #first_ungrouped_children = self._first_ungrouped_children(hierarchy)
            ##We are happy to return a Group element here, and then use dottiness of 6
            first_ungrouped_children = [hierarchy]
            ##TODO match the effective elements up with the hierarchy elements
            ##Commented code below is ignorant of the structure of the outputs and isn't working
            #if effective_elements is not None:
            #    for ch in first_ungrouped_children:
            #        assert ch.shortname in effective_elements, "{} not in {}".format(ch.shortname, effective_elements)
            #else:
            #    #maybe should assert that first ungrouped elements is single element list?
            #    pass

            if mapping_type == 'constant shortname':
                for ch in first_ungrouped_children:
                    #this code assumes that a mapping contains a shortcode for a Comparison
                    #It is likely that it'll hold something more sophisticated.
                    #When it does the tests will break - so I've stated this assumption explicitly
                    if ch.shortname == self._mappers[dimension_index]:
                        #Return the first child we find in the hierarchy with the mapped shortcode
                        return [ch]
                #If didn't return a child, then it is possible the first_ungrouped_children is a single grouped element
                #If so, walk it and return the first one found
                if first_ungrouped_children[0].group_only == 'Group':
                    for ch in first_ungrouped_children[0].walk():
                        #this code assumes that a mapping contains a shortcode for a Comparison
                        #It is likely that it'll hold something more sophisticated.
                        #When it does the tests will break - so I've stated this assumption explicitly
                        if ch.shortname == self._mappers[dimension_index]:
                            #Return the first child we find in the hierarchy with the mapped shortcode
                            return [ch]

            else:
                return first_ungrouped_children

    def _handle_no_mapping_single_element(self,dimension_index,dimension_name):
        if isinstance(self.target.structures[dimension_index],Structure):
            #Check that there is only one hierarchy, and that that hierarchy only has a single element
            if len(self.target.structures[dimension_index].hierarchies) == 1 and len([h for h in self.target.structures[dimension_index].hierarchies][0].children) == 0:

                h = list(self.target.structures[dimension_index].hierarchies)[0]
                return self._first_ungrouped_children(h)

            else:
                raise mpex.LoaderSetupError('FocusLoader without any mappings cannot handle {} Structures with anything other than 1 hierarchy with a single element. Structure {} has more than one element. Choose another Structure or create mappings for the hierarchy'.format(dimension_name,self.target.structures[dimension_index].longname))
        elif isinstance(self.target.structures[dimension_index],StructureElement):
            first_ungrouped_children = self._first_ungrouped_children(self.target.structures[dimension_index])

            if len(first_ungrouped_children.children) == 0:
                return first_ungrouped_children
            else:
                raise mpex.LoaderSetupError('FocusLoader without any mappings cannot handle {} StructureElements with anything other than a single element. Structure {} has more than one element. Choose another Structure or create mappings for the hierarchy'.format(dimension_name,self.target.structures[dimension_index].longname))

    def _handle_empty_target(self):
        if self.target is None:
            raise mpex.LoaderSetupError('Cannot compute effective time elements for a FocusLoader which has no target Viewpoint or Focus set')

    def _get_hierarchy_direct_or_single_hierarchy_from_structure(self,dimension_index,dimension_name,enforce_single_element=False):
        '''

        :param enforce_single_element: If set to True, will thrown an error if the returned hierarchy does not have a single element
        '''

        if isinstance(self.target.structures[dimension_index],Structure):
            #Check that there is only one hierarchy
            if len(self.target.structures[dimension_index].hierarchies) == 1:
                if enforce_single_element and not len([h for h in self.target.structures[dimension_index].hierarchies][0].children) == 0:
                    #Some use cases require only single element hierarchies to be present
                    raise mpex.LoaderSetupError('FocusLoader without any mappings cannot handle {} Structures with anything other than 1 hierarchy with a single element. Structure {} has more than one element. Choose another Structure or create mappings for the hierarchy'.format(dimension_name,self.target.structures[dimension_index].shortname))
                else:
                    return list(self.target.structures[dimension_index].hierarchies)[0]
            else:
                raise mpex.LoaderSetupError('FocusLoader cannot handle {} Structures with anything other than 1 hierarchy. Structure {} has multiple hierarchies : {}. Choose another Structure or create mappings for the {} hierarchy'.format(dimension_name,self.target.structures[dimension_index].longname,','.join([h.shortname for h in self.target.structures[dimension_index].hierarchies]),dimension_name))
        elif isinstance(self.target.structures[dimension_index],StructureElement):
            return self.target.structures[dimension_index]

    @property
    def effective_indicator_elements(self):
        #_get_implied_shortcode_list_and_mapping_type
        dimension_index = 8
        self._handle_empty_target()

        #Where there are no mappings we are happy to use a single element if one is available
        if self._mappers is None or self._mappers[dimension_index] is None:
            self._handle_no_mapping_single_element(dimension_index=dimension_index,dimension_name='Indicator')
        else:
            effective_elements, mapping_type,column_names = self._get_implied_shortcode_list_and_mapping_type(dimension_index = dimension_index, object_to_check_against =self.target.structures[dimension_index])

            if mapping_type =='constant shortname':
                return
            elif mapping_type =='column name':
                return
            elif mapping_type =='columns to fields':
                return
            elif mapping_type =='columns to shortnames':

                #return the first Structureelements we find with the
                filtered_elements = []

                #Either get the first hierarchy in a single hierarchy Structure or get the hierarchy passed in - whichever it was
                hierarchy = self._get_hierarchy_direct_or_single_hierarchy_from_structure(dimension_index=dimension_index,dimension_name='Indicator')
                #We've assumed that effective_elements is a list of shortnames
                for shortname in effective_elements:
                    found_elements = hierarchy.get_elements(shortname)
                    #Append the first instance of any elements we find
                    #if we don't find one, doesn't matter (I think)
                    try:
                        filtered_elements.append(found_elements[0] )
                    except IndexError:
                        pass

                return filtered_elements

            elif mapping_type =='column to shortname to value':
                return

    @property
    def effective_comparison_elements(self):
        #Comparison behaves just like a unit dimension, so we should be able to reuse the code
        dimension_index = 9

        if self._mappers[dimension_index] is not None and not isinstance(self._mappers[dimension_index],str):
            raise mpex.LoaderSetupError('Mapping for the Comparison structure of a FocusLoader must be a single shortname string or single column name and not {}'.format(self._mappers[dimension_index]))

        return self.effective_unit_dimension_elements(dimension_index)

    @property
    def effective_currency_elements(self):
        dimension_index = 10
        #self._handle_empty_target()

        ##Where there are no mappings we are happy to use a single element if one is available
        #if self._mappers is None or self._mappers[dimension_index] is None:
        #    hierarchy = self._get_hierarchy_direct_or_single_hierarchy_from_structure(dimension_index=dimension_index,dimension_name='Currency',enforce_single_element=True)
        #    first_ungrouped_children = self._first_ungrouped_children(hierarchy)
        #    return first_ungrouped_children
        #else:
        #    #Either get the first hierarchy in a single hierarchy Structure or get the hierarchy passed in - whichever it was
        #    hierarchy = self._get_hierarchy_direct_or_single_hierarchy_from_structure(dimension_index=dimension_index,dimension_name='Currency')
        #    first_ungrouped_children =  self._first_ungrouped_children(hierarchy)
        #
        #    #Check that each element in first_ungrouped_children is a single element - i.e. has no hierarchy
        #    for h in first_ungrouped_children:
        #        if len(h.children) > 0:
        #            raise mpex.LoaderSetupError('FocusLoader cannot handle Currency StructureElements with anything more than a single flat structure, or a single grouped flat structure. {}'.format(self.target.structures[dimension_index].longname))
        #
        #    return first_ungrouped_children

        return self.effective_unit_dimension_elements(dimension_index)


    @property
    def effective_transform_elements(self):
        '''Get the effective Structure Elements from the Transform dimension
        We just want the first 'Raw' element in the Viewpoint - we don't care how many hierarchies the viewpoint has - since all Raw elements are utterly equivalent
        '''

        dimension_index = 12
        self._handle_empty_target()

        #We are not interested in the mappings

        for se in self.target.structures[dimension_index].walk():
            if se.fields['Calculation Status'] == 'Real' and se.fields['Group Only'] is None:
                return [se]

        raise mpex.LoaderSetupError('FocusLoader cannot handle a Transformation Structure "{}" which does not contain any Real elements.'.format(self.target.structures[dimension_index].longname))


####################################################################

class Loader(object):
    '''Transactional data is loaded into Empower Sites - this object loads it'''

    def __init__(self,source=None,site=None,logging_queue=None,delta=True,identifier_columns=None,name='loader_0',safe_load=True,empower_period_type=llu.EMPOWER_MONTH_CONSTANT,empower_importer_executable=llu.EMPOWER_IMPORTER_EXECUTABLE):
        '''
        If delta is set to True, (which is the default) then this loader will perform delta loads

        :param source: A pandas Dataframe to be used as the source data
        :param identifier_columns: Columns in the source which are useful in debugging
        :param safe_load: only move Data Files after loading at the last moment - this makes the process perfectly restartable
        '''
        if identifier_columns is None:
            identifier_columns=[]

        self._site               = site
        self.logging_queue      = logging_queue
        #TODO - self.validator
        #TODO - maintain dictionary of named dataframes for use in the validator

        self.delta=delta

        self.source=source
        #We may wish to add other sources (e.g. csv, excel) also the df will change over time
        self.df=self.source

        self.identifier_columns = identifier_columns

        self.name = name
        #The load may be broken down into subloads, if we want to reuse a loader
        self.subloads=[]

        self.empower_period_type = empower_period_type
        self.empower_importer_executable = empower_importer_executable

        self.safe_load=safe_load

        self.sharding_queue = None

        #Used for monkey-patching in alpha development status bulk loading functions
        self._single_bulk_load_function =  llu.msgsink__run_single_sql_empower_bulk_load

    def load(self
            ,dimension_0   = None
            ,dimension_1   = None
            ,dimension_2   = None
            ,dimension_3   = None
            ,dimension_4   = None
            ,dimension_5   = None
            ,dimension_6   = None
            ,dimension_7   = None
            ,mode          = None
            ,base          = None
            ,time          = None
            ,metric        = None
            ,empower_period_type = None
            ,value         = None
            ,ignore_zero_values         = True
            ):
        '''

        .load() does .explode(), .shard() and .load_shards()

        :param dimension_0: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_1: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_2: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_3: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_4: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_5: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_6: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_7: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param mode: string, list, pympx.Element, or pympx.Constant
        :param base: string, list, pympx.Element, or pympx.Constant
        :param time: string, list, pympx.Element, or pympx.Constant
        :param metric: Either a string naming the metric column which should contain metric shortnames or physids, or a dictionary of column names to metric shortnames
        :param value: When using a metric column containing metric (indicator) shortcode or physids, then put the values in here. If metrics are in different columns leave this parameter as None
        :param ignore_zero_values: Usually we do not wish to load zero values into Empower in order to save time and space, since most Empower cube implementations display N/As as zero anyway
        '''

        self.explode(dimension_0 = dimension_0
                   ,dimension_1 = dimension_1
                   ,dimension_2 = dimension_2
                   ,dimension_3 = dimension_3
                   ,dimension_4 = dimension_4
                   ,dimension_5 = dimension_5
                   ,dimension_6 = dimension_6
                   ,dimension_7 = dimension_7
                   ,mode        = mode
                   ,base        = base
                   ,time        = time
                   ,metric      = metric
                   #,value         = None
                   ,subload_name= None
                   ,empower_period_type   = empower_period_type
                   ,ignore_zero_values    = ignore_zero_values
                   )

        self.shard()

        self.load_shards()

    def start_sharder(self):

        #Create the queue
        log.verbose('Sharding files on queue')

        self.sharding_queue = mpq.PersistentQueue(pickup_file_prefix='Sharding Queue')

        #Start the message sink
        self.sharder=multiprocessing.Process(target=llu.msgsink__shard_files_by_storage_dim
                                       ,kwargs={'storage_dimension_index':self.site.storage_dimension_index
                                               ,'load_processing_dir':self.site._load_processing_dir
                                               ,'file_mask':'*.tsv'
                                               ,'shard_prefix':'Shard_'
                                               ,'number_of_storage_elements_per_empower_data_file':self.site.elements_per_storage_dimension
                                               ,'separator':'\t'
                                               ,'site_exploded_queue':self.sharding_queue
                                               ,'site_sharded_queue':None
                                               ,'empower_importer_executable':self.empower_importer_executable
                                               ,'logging_queue':self.site.logging_queue
                                               }
                                       ,name='Shard Files')


        #Start the (single threaded) sharder in it's own thread
        #it will wait for exploded files and start sharding them
        self.sharder.start()


    def explode(self
               ,dimension_0         = None
               ,dimension_1         = None
               ,dimension_2         = None
               ,dimension_3         = None
               ,dimension_4         = None
               ,dimension_5         = None
               ,dimension_6         = None
               ,dimension_7         = None
               ,mode                = None
               ,base                = None
               ,time                = None
               ,metric              = None
               ,value_column        = None
               ,subload_name        = None
               ,empower_period_type = None
               ,source_dataframe    = None
               ,ignore_zero_values  = True
               ):
        '''Explode data by the dimension expansions given, and prepare for delta bulk loading

        :param dimension_0: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_1: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_2: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_3: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_4: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_5: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_6: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param dimension_7: string, list, pympx.Element, pympx.Constant or pympx.StructureMapper. String represents a column name, a Constant can be either a physid or shortname, a Structure mapper represents a hierarchy tree. List can be either a list of strings or Constants
        :param mode: string, list, pympx.Element, or pympx.Constant
        :param base: string, pympx.Element, or pympx.Constant
        :param time: string, pympx.Element, or pympx.Constant or datetime
        :param metric: Either a string naming the metric column, or a dictionary of column names to metric shortnames
        :param value_column: When using a metric column containing metric (indicator) shortcode or physids, then put the name of the value column in here. If metrics are in different columns leave this parameter as None
        :param subload_name:
        :param source_dataframe:
        :param ignore_zero_values: Usually we do not wish to load zero values into Empower. This flag prevents the zero values being loaded into Empower
        '''

        #TODO - throw error if base is a list - we can't have more than one non-additive column (since it's non additive we won't aggregate)



        #First, get the type of translation dataframe, and the column names for each dimension

        lookup_metric_shortname_from_column = None
        dynamic_metric_columns              = None

        if subload_name is None:
            subload_name = 'subload_0'


        if empower_period_type is None:
            empower_period_type= self.empower_period_type

        try:
            #Check if metric is a string
            metric=metric+''

            dynamic_metric_columns = [metric]
        except TypeError:
            #metric is not a string - it is a dict
            lookup_metric_shortname_from_column = metric

        if source_dataframe is not None:
            dataframe = source_dataframe.copy()
        else:
            dataframe = self.df.copy()

        def _decide_mapper_type(mapper_input):
            #convert the input to a standard mapper type
            #mapper input may be none if the dimensions is not present
            if mapper_input is None:
                return Constant(-1)
            if isinstance(mapper_input, StructureMapper):
                return mapper_input
            if isinstance(mapper_input, Constant):
                return mapper_input
            if isinstance(mapper_input, ColumnMapper):
                return mapper_input
            if isinstance(mapper_input, str):
                #TODO - differentiate between str and int/float pd.Series, and return shortname or physid mapper accordingly
                return ColumnMapper(column_name     = mapper_input
                                   ,column_type     = 'shortname'
                                   ,field_shortname = None
                                   )

            #TODo - handle lists of columns
            raise ValueError('Cannot map from input '+str(mapper_input))

        dimension_0_mapper = _decide_mapper_type(dimension_0)
        dimension_1_mapper = _decide_mapper_type(dimension_1)
        dimension_2_mapper = _decide_mapper_type(dimension_2)
        dimension_3_mapper = _decide_mapper_type(dimension_3)
        dimension_4_mapper = _decide_mapper_type(dimension_4)
        dimension_5_mapper = _decide_mapper_type(dimension_5)
        dimension_6_mapper = _decide_mapper_type(dimension_6)
        dimension_7_mapper = _decide_mapper_type(dimension_7)
        mode_mapper        = _decide_mapper_type(mode)
        base_mapper        = _decide_mapper_type(base)
        if dynamic_metric_columns is not None:
            metric_mapper = _decide_mapper_type(metric)

        dimension_0_columns = []
        dimension_1_columns = []
        dimension_2_columns = []
        dimension_3_columns = []
        dimension_4_columns = []
        dimension_5_columns = []
        dimension_6_columns = []
        dimension_7_columns = []


        if self.site.number_of_unit_dimensions >=1:
            dimension_0_columns = dimension_0_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[0],loader=self)
        if self.site.number_of_unit_dimensions >=2:
            dimension_1_columns = dimension_1_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[1],loader=self)
        if self.site.number_of_unit_dimensions >=3:
            dimension_2_columns = dimension_2_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[2],loader=self)
        if self.site.number_of_unit_dimensions >=4:
            dimension_3_columns = dimension_3_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[3],loader=self)
        if self.site.number_of_unit_dimensions >=5:
            dimension_4_columns = dimension_4_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[4],loader=self)
        if self.site.number_of_unit_dimensions >=6:
            dimension_5_columns = dimension_5_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[5],loader=self)
        if self.site.number_of_unit_dimensions >=7:
            dimension_6_columns = dimension_6_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[6],loader=self)
        if self.site.number_of_unit_dimensions >=8:
            dimension_7_columns = dimension_7_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[7],loader=self)

        mode_columns        = mode_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[9],loader=self)
        base_columns        = base_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[10],loader=self)
        if dynamic_metric_columns is not None:
            dynamic_metric_columns = metric_mapper.map_dataframe(dataframe=dataframe,dimension=self.site.dimensions[8],loader=self)

        #Map time to empower date tuples
        #needs empower_year etc. columns
        dataframe['empower period type'] = empower_period_type
        if isinstance(time, datetime.datetime):
            dataframe['empower year']        = time.year
            dataframe['empower period']      = time.month
        else:
            #assume the time is a column name
            #Read the time from the column name given
            #turn it into an empower tuple
            dataframe['empower year']        = dataframe[time].dt.year
            dataframe['empower period']      = dataframe[time].dt.month


        for dir in [self.site._bulk_load_intermediate_dir
                   ,self.site._load_processing_dir
                   ,self.site._output_data_files_dir
                   ]:

            try:
                os.makedirs(dir)
            except FileExistsError:
                pass
            except OSError as e:
                if e.winerror == 123:
                    raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                else:
                    raise e

        #Create the file names automatically
        intermediate_file_name = os.path.join(self.site._bulk_load_intermediate_dir,
                                            Loader._get_intermediate_file_name(loader_name  = self.name
                                               ,subload_name = subload_name
                                               ,site_prefix  = self.site.prefix
                                               ,time         = time
                                               ,empower_period_type=empower_period_type
                                               )
                                  )
        target_file_name = os.path.join(self.site._bulk_load_intermediate_dir,
                                            Loader._get_target_file_name(loader_name  = self.name
                                               ,subload_name = subload_name
                                               ,site_prefix  = self.site.prefix
                                               ,time         = time
                                               ,empower_period_type=empower_period_type
                                               )
                                  )

        if value_column is None:
            metric_columns = None
        else:
            metric_columns = [value_column]

        #assert not self.sharding_queue is None

        #explode data for the time period in question
        llu.create_exploded_bulkload_files(dataframe                            = dataframe
                                          ,intermediate_file_name               = intermediate_file_name
                                          ,target_file_name                     = target_file_name
                                          ,lookup_metric_shortname_from_column  = lookup_metric_shortname_from_column
                                          ,lookup_metric_physid_from_column     = {}
                                          ,d1_levels                            = dimension_0_columns
                                          ,d2_levels                            = dimension_1_columns
                                          ,d3_levels                            = dimension_2_columns
                                          ,d4_levels                            = dimension_3_columns
                                          ,d5_levels                            = dimension_4_columns
                                          ,d6_levels                            = dimension_5_columns
                                          ,d7_levels                            = dimension_6_columns
                                          ,d8_levels                            = dimension_7_columns
                                          ,mode_levels                          = mode_columns
                                          ,currency_column_name                 = base_columns[0]
                                          ,empower_date_tuple                   = None
                                          ,exported_metric_physid_df            = self.site.metric.elements.dataframe[['Short Name','ID']]
                                          ,metric_columns                       = metric_columns
                                          ,dynamic_metric_columns               = dynamic_metric_columns
                                          ,identifier_columns                   = self.identifier_columns
                                          ,file_separator                       = '\t'
                                          ,logging_queue                        = self.site.logging_queue
                                          ,completed_metric_queue               = self.sharding_queue
                                          ,ignore_zero_values                   = ignore_zero_values
                                          )

        #Drop the copied dataframe - this will help the Garbage Collector clean up
        dataframe = None

        #store information about where the exploded files are
        self.intermediate_file_name  = intermediate_file_name
        self.target_file_name        = target_file_name


        if self.site.storage_type=="sql":
            if self.delta:
                raise AttributeError("Currently a Loader cannot do delta processing on a SQL file")
            else:
                for dir in [self.site._bulk_load_delta_dir]:

                    try:
                        os.makedirs(dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if e.winerror == 123:
                            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                        else:
                            raise e
                #If we are not doing a delta we don't need to sort the file or create an override file - we just need to move it into place-  this should be quick if it is a simple rename
                shutil.move(target_file_name, os.path.join(self.site._bulk_load_delta_dir, os.path.basename(target_file_name)))

                self.subloads.append((subload_name,os.path.basename(target_file_name),))

        else:

            if self.delta:
                target_file_name_no_ext, ext = os.path.splitext(os.path.basename(target_file_name))

                #Create the delta
                #history file will be in 'Data Files\last_successful_bulk_load'
                #currently loading files (which will be written into 'Data Files\last_successful_bulk_load' after a successful load are in 'Data Files\currently_processing_bulk_load'
                #Make the directory if it doesn't exist
                try:
                    os.mkdir(os.path.join(self.site._data_files_dir,'currently_processing_bulk_load'))
                except FileExistsError:
                    #If the directory does exist, then it holds data from a failed load - remove the failed data
                    log.warn('Found leftover data from a previously failed load in '+str(os.path.join(self.site._data_files_dir,'currently_processing_bulk_load')))
                    for f in os.listdir(os.path.join(self.site._data_files_dir,'currently_processing_bulk_load')):
                        os.remove(os.path.join(self.site._data_files_dir,'currently_processing_bulk_load',f))

                target_file_name_sorted=os.path.join(self.site._data_files_dir,'currently_processing_bulk_load', target_file_name_no_ext+'_sorted'+ext)


                #Sort the exploded bulk load file - so that we can delta it
                llu.sort_file(source_file_name=target_file_name,target_file_name=target_file_name_sorted)

                #Make the directory if it doesn't exist
                #Move any sorted.tsv files in, as they would have been created by a previous incarnation of this code
                try:
                    os.mkdir(os.path.join(self.site._data_files_dir,'last_successful_bulk_load'))
                    for f in os.listdir(os.path.join(self.site._data_files_dir)):
                        if fnmatch.fnmatch(f,'*_sorted.tsv'):
                            shutil.move(os.path.join(self.site._data_files_dir,f), os.path.join(self.site._data_files_dir,'last_successful_bulk_load'))

                except FileExistsError:
                    pass

                target_file_name_sorted_previous=os.path.join(self.site._data_files_dir,'last_successful_bulk_load', target_file_name_no_ext+'_sorted'+ext)
                delta_file_name=os.path.join(self.site._bulk_load_delta_dir, target_file_name_no_ext+'_sorted'+ext)

                for dir in [self._bulk_load_delta_dir]:

                    try:
                        os.makedirs(dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if e.winerror == 123:
                            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                        else:
                            raise e
                #Attempt to create a delta bulk load file
                llu.create_overwrite_bulk_load_file(old_source_bulk_load_ready_file_sorted = target_file_name_sorted_previous
                                                   ,new_source_bulk_load_ready_file_sorted = target_file_name_sorted
                                                   ,target_bulk_load_ready_file            = delta_file_name
                                                   ,target_bulk_load_reversion_file        = os.devnull
                                                   ,create_true_delta                      = True
                                                   ,number_of_unit_dimensions              = self.site.number_of_unit_dimensions
                                                   ,ignore_missing_old                     = True
                                                   )

                self.subloads.append((subload_name,target_file_name_sorted))

            else:
                try:
                    os.mkdir(os.path.join(self.site._data_files_dir,'currently_processing_bulk_load'))
                except FileExistsError:
                    pass

                for dir in [self.site._bulk_load_delta_dir]:

                    try:
                        os.makedirs(dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if e.winerror == 123:
                            raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                        else:
                            raise e
                #If we are not doing a delta we don't need to sort the file or create an override file - we just need to move it into place-  this should be quick if it is a simple rename
                shutil.move(target_file_name, os.path.join(self.site._bulk_load_delta_dir, os.path.basename(target_file_name)))

                self.subloads.append((subload_name,os.path.basename(target_file_name)))


        #Make the list unique - in case we are running this in Jupyter notebook, and the same loader is being run multiple times (e.g. during development)
        self.subloads=list(set( self.subloads))

        #if not self.sharding_queue is None:
        #    delta_file_name = os.path.join(self.site._bulk_load_delta_dir,os.path.basename(target_file_name))
        #
        #    try:
        #        #put the message on the queue
        #        self.sharding_queue.put(delta_file_name)
        #        log.verbose('Queuing file for sharding:'+delta_file_name)
        #
        #
        #    except Exception:
        #        log.error('Failing sharding queue...')
        #        self.sharding_queue.fail()
        #        log.error('Failed  sharding queue')
        #        raise


    def shard(self,files_to_shard=None):
        '''Shard all of the delta files for all of the subloads to create files ready to be loaded'''

        if files_to_shard is None and self.sharding_queue is None:
            files_to_shard=[]
            #Go through all of the files to shard from subloads and shard them together
            for subload_name,target_file_name_sorted in self.subloads:
                delta_file_name = os.path.join(self.site._bulk_load_delta_dir,os.path.basename(target_file_name_sorted))

                files_to_shard.append(delta_file_name)



        #Shard the intermediate files so we can load them in parallel
        llu.shard_files_in_list_by_storage_dim(files_to_shard=files_to_shard
                                              ,storage_dimension_index=self.site.storage_dimension_index
                                              ,number_of_storage_elements_per_empower_data_file=self.site.elements_per_storage_dimension
                                              ,load_processing_dir=self.site._load_processing_dir
                                              ,shard_prefix='Shard_'
                                              ,separator='\t'
                                              ,logging_queue = self.site.logging_queue
                                              )

    def load_shards(self,subloads=None):
        '''
        '''

        if not self.sharding_queue is None:
            log.verbose('Disposing sharding queue...')
            self.sharding_queue.dispose()
            log.verbose('Sharding queue disposed')

            log.verbose('Joining sharder')
            self.sharder.join()

            if self.sharder.exitcode != 0:
                log.error('{}.exitcode = {}'.format(self.sharder.self.sharder, self.sharder.exitcode))
                raise mpex.CompletelyLoggedError('Sharder Job:'+self.sharder.name+' failed with exit code '+str(self.sharder.exitcode))
            else:
                log.verbose('{}.exitcode = {}'.format(self.sharder.name, self.sharder.exitcode))

        if self.site.storage_type=="sql":

            llu.load_sql_empower_from_shards( empower_site=self.site._site_locator
                                             ,encrypted_empower_user=self.site._encrypted_user
                                             ,encrypted_empower_pwd=self.site._encrypted_pwd
                                             ,shard_file_prefix='Shard_'
                                             ,number_of_workers=multiprocessing.cpu_count()-1
                                             ,load_processing_dir=self.site._load_processing_dir
                                             ,logging_queue=self.site.logging_queue
                                             ,_single_bulk_load_function = self._single_bulk_load_function
                                             )
        else:
            log.verbose('Calling low level utility load_empower_from_shards...')

            if self.site.prefix is None:
                raise ValueError('Cannot begin bulk loading until the site.prefix has been set. Set site.prefix to the filename prefix of the data files (the bit before the last 3 letters before.000). Then call loader.load() again')

            #Should we create a SubLoad object, to hold the subload and period together, just in case?
            llu.load_empower_from_shards(empower_site = self.site._site_locator
                                        ,empower_user = self.site._user
                                        ,empower_pwd  = self.site._pwd
                                        ,load_method='bulk'
                                        ,shard_file_prefix='Shard_'
                                        ,empower_data_file_prefix=self.site.prefix
                                        ,main_site_output_data_files_dir=self.site._output_data_files_dir
                                        ,load_processing_dir=self.site._load_processing_dir
                                        ,logging_queue = self.site.logging_queue
                                        ,safe_load=self.safe_load
                                        ,encrypted_empower_user=self.site._encrypted_user
                                        ,encrypted_empower_pwd=self.site._encrypted_pwd
                                        )

    def _replace_bad_chars(string):
        for char in r'<>:"/\|?*':
            string=string.replace(char,'#')
        return string

    def _get_bulkload_file_time_prefix(time,empower_period_type):
        try:
            time_prefix=datetime.datetime.strftime(time,'%Y_%m_%d_')+str(empower_period_type)
        except TypeError:
            #We got passed in a Column Name (with Multiple times)
            time_prefix = time.replace(' ','_')+'_'+str(empower_period_type)

        return time_prefix

    def _get_bulkload_file_prefix(loader_name, subload_name, site_prefix, time,empower_period_type):
        time_prefix             = Loader._get_bulkload_file_time_prefix(time,empower_period_type)
        file_prefix             = Loader._replace_bad_chars(site_prefix) + '_' + Loader._replace_bad_chars(loader_name) + '_' + Loader._replace_bad_chars(subload_name)+'_'+time_prefix
        return file_prefix

    def _get_intermediate_file_name(loader_name, subload_name, site_prefix, time,empower_period_type):
        return Loader._get_bulkload_file_prefix(loader_name, subload_name, site_prefix, time,empower_period_type) + '_intermediate.tsv'

    def _get_target_file_name(loader_name, subload_name, site_prefix, time,empower_period_type):
        return Loader._get_bulkload_file_prefix(loader_name, subload_name, site_prefix, time,empower_period_type) + '_exploded.tsv'

    def _get_delta_file_name(loader_name, subload_name, site_prefix, time,empower_period_type):
        return Loader._get_bulkload_file_prefix(loader_name, subload_name, site_prefix, time,empower_period_type) + '_delta.tsv'

    def _get_delta_reversion_file_name(loader_name, subload_name, site_prefix, time,empower_period_type):
        return Loader._get_bulkload_file_prefix(loader_name, subload_name, site_prefix, time,empower_period_type) + '_delta_reversion.tsv'

    def _get_sorted_file_name(loader_name, subload_name, site_prefix, time,empower_period_type):
        return Loader._get_bulkload_file_prefix(loader_name, subload_name, site_prefix, time,empower_period_type) + '_exploded_sorted.tsv'

    @property
    def site(self):
        return self._site

class FocusLoader(Loader):
    '''Loads transactions into an Empower focus'''

    #A FocusLoader is a Loader which can take a Focus as target, and fill in the super class Loader object accordingly
    #This means that calls to load need little application programmer input, and thus a call such as df.to_empower(Focus) or even df.to_empower(Viewpoint) becomes possible

    def __init__(self,source=None,target=None,mappings=None,safe_load=True,identifier_columns=None,ignore_zero_values=True,clear_focus_before_loading=True,_defer_mapper_creation=False):
        ''' Create a new FocusLoader

        :param source:
        :param target:
        :param mappings:
        :param safe_load:
        :param identifier_columns:
        :param ignore_zero_values: Don't load Zero values into the cube - leave N/As in place
        :param clear_focus_before_loading:

        '''
        if identifier_columns is None:
            identifier_columns=[]

        self._initial_target = target

        self._initial_source = source

        #TODO - carefully set up mappings to transform dictionaries or use CubeMapper as is
        if isinstance(mappings,CubeMapper):
            self._mappings = mappings
        else:
            self._mappings = CubeMapper(mappings = mappings, target = self._initial_target, source = self._initial_source)

        self._ignore_zero_values = ignore_zero_values

        #Override the old Loader name with this rather generic 'FocusLoader'

        if self.site is not None:
            logging_queue = self.site.logging_queue
            empower_importer_executable = self.site.empower_importer_executable
        else:
            logging_queue = None
            empower_importer_executable = llu.EMPOWER_IMPORTER_EXECUTABLE

        super(FocusLoader, self).__init__(source=self._initial_source
                                         ,site=self.site
                                         ,logging_queue=logging_queue
                                         ,delta=False
                                         ,identifier_columns=identifier_columns
                                         ,name='FocusLoader'
                                         ,safe_load=safe_load
                                         ,empower_period_type=llu.EMPOWER_MONTH_CONSTANT # This will be overridden by the inferred empower_period_type
                                         ,empower_importer_executable=empower_importer_executable)

        #check that everything with a mapping has the necessary prerequisites, or raise a LoaderSetupError
        #This will catch unimplemented use cases nice and early


            
        self._defer_mapper_creation = _defer_mapper_creation
        if not self._defer_mapper_creation:
            self._mappings._create_TableMappers()


    def load(self):
        '''
        .load() does .delete_target_data(), .explode(), .shard() and .load_shards()
        '''

        if self._defer_mapper_creation:
            self._mappings._create_TableMappers()

        self.delete_target_data()

        if isinstance(self._mappings._time_mapper, Constant):
            time_mapping = self._mappings._time_mapper.constant
        else:
            time_mapping = self._mappings._time_mapper

        #TODO - defer this to base and have this class do the work of setting the parameters in a simple .explode() call under the covers
        self.explode(dimension_0         = self._mappings._dimension_0_mapper
                    ,dimension_1         = self._mappings._dimension_1_mapper
                    ,dimension_2         = self._mappings._dimension_2_mapper
                    ,dimension_3         = self._mappings._dimension_3_mapper
                    ,dimension_4         = self._mappings._dimension_4_mapper
                    ,dimension_5         = self._mappings._dimension_5_mapper
                    ,dimension_6         = self._mappings._dimension_6_mapper
                    ,dimension_7         = self._mappings._dimension_7_mapper
                    ,mode                = self._mappings._mode_mapper
                    ,base                = self._mappings._base_mapper
                    ,time                = time_mapping
                    ,metric              = self._mappings._metric_mapper
                    #,value                 = None
                    ,subload_name        = self.target.viewpoint.shortname
                    ,empower_period_type = self._mappings._empower_period_type
                    ,ignore_zero_values  = self._ignore_zero_values
                    ,source_dataframe    = self._initial_source
                    )

        self.shard()

        self.load_shards()


    @property
    def mappings(self):
        return self._mappings


    @property
    def site(self):
        if self.target is None:
            return None
        else:
            return self.target.viewpoint.site

    #@property
    #def site(self):
    #    self._initial_target.site

    @property
    #TODO - manipulate Focus to include filters before returning it
    def target(self):
        if self._initial_target is None:
            return None
        elif isinstance(self._initial_target,Viewpoint):
            return Focus(self._initial_target)
        elif isinstance(self._initial_target,Focus):
            return self._initial_target
        else:
            raise TypeError('FocusLoader.target should be a Viewpoint or Focus, but was in fact: {}'.format(repr(self._initial_target)))

    def _single_dimension_focus_stringlet(self,dimension_index):

        r'1=#7##1#2;'


        #4 dottiness is custom, elements are separated by spaces
        #e.g.
        #12=#4##1#178 179 180;
        #JAN11 178
        #FEB11 179
        #MAR11 180
        if dimension_index <= 7:

            effective_elements = self._mappings.effective_unit_dimension_elements(dimension_index=dimension_index)
        elif dimension_index == 8:
            effective_elements = self._mappings.effective_indicator_elements
        elif dimension_index == 9:
            effective_elements = self._mappings.effective_comparison_elements
        elif dimension_index == 10:
            effective_elements = self._mappings.effective_currency_elements
        elif dimension_index == 11:
            effective_elements = self._mappings.effective_time_elements
        elif dimension_index == 12:
            effective_elements = self._mappings.effective_transform_elements

        #We need the position relative to the initial target in the Structure
        structure = self._initial_target.structures[dimension_index]

        first_effective_element = effective_elements[0]

        if len(effective_elements) > 1:
            #Pretty blunt - but I think it works - if there is more than 1 effective element, then must be 4 'custom' (?)
            dottiness_number = 4
        else:
            if len(first_effective_element.children) > 0:

                if first_effective_element.group_only == 'Group':
                    #Dottiness 6 is all children
                    dottiness_number = 6

                else:
                    #Dottiness 7 is self and all children
                    dottiness_number = 7



            else:
                #Single elements get a dottiness of 1 - i.e. just self
                dottiness_number = 1

        instance_number = 0
        for se in structure.walk():
            #Keep incrementing the effective element until (and including) when we find the matching element. Then stop
            if first_effective_element.shortname == se.shortname:
                instance_number += 1

            if first_effective_element == se:
                break

        physid_string = ' '.join([str(el.physid) for el in effective_elements])

        #dimension_index + 1
        # =
        #Dottiness
        #Instance Number
        #Physid
        output_string = '{}=#{}##{}#{};'.format(dimension_index+1,dottiness_number,instance_number,physid_string)

        return output_string

    @property
    def _focus_string(self):
        focus_string = "Focus = "

        for n, structure in enumerate(self._initial_target.structures.values()):
            #Empty structures (because of empty Unit dimensions) do not get a focus stringlet
            if structure is not None:
                focus_string += self._single_dimension_focus_stringlet(dimension_index = n)

        return focus_string

    @property
    def _focus_blockset_string(self):
        '''A string for clearing down the data in the focus - it'll go into a BlockSet command'''
        focus_blockset_string = 'block-set Viewpoint = {}, '.format(self._initial_target.physid) + self._focus_string + ', Value = N/A'
        return focus_blockset_string

    def delete_target_data(self):
        '''BlockSet the Focus to N/A. This is a mighty powerful command, to be used with caution'''
        log.verbose('Deleting all {} data points in {}. '.format(len(self),self._focus_string))
        self.site.importer.run_commands([self._focus_blockset_string])

    def __len__(self):

        def _len_effective_elements(effective_elements):
            if effective_elements is None:
                return 1
            first_effective_element = effective_elements[0]
            if len(effective_elements) > 1:
                return len(effective_elements)
            else:
                if len(first_effective_element.children) > 0:
                    #Dottiness 7 is self and all children
                    count = 0
                    for ch in first_effective_element.walk():
                        if ch.group_only is None or ch.group_only != 'Group':
                            count+=1
                    if count ==0:
                        return 1
                    else:
                        return count
                else:
                    #Single elements get a dottiness of 1 - i.e. just self
                    return 1

        result = 1
        for n in range(self.site.number_of_unit_dimensions):
            result *=  _len_effective_elements(self._mappings.effective_unit_dimension_elements(dimension_index=n))

        result *= _len_effective_elements(self._mappings.effective_indicator_elements )
        result *= _len_effective_elements(self._mappings.effective_comparison_elements)
        result *= _len_effective_elements(self._mappings.effective_currency_elements  )
        result *= _len_effective_elements(self._mappings.effective_transform_elements )
        result *= _len_effective_elements(self._mappings.effective_time_elements      )
        return result


###################################################################
#
# Structure Comparison
#
###################################################################

class StructureElementComparison(object):
    '''Created by a StructureElement during a comparison with another StructureElement with helpful '''

    #Must easily show up differences, and create nicely formatted messages

    #Essentially the only possible differences are added, removed or reordered children
    #Anything which is the same should says so quickly, and then we can drill down to the children and so on...

    def __init__(self,structure_element,other_structure_element):
        self.structure_element = structure_element
        self.other_structure_element = other_structure_element
        self.comparison_list   = []
        self.is_in_self        = None
        self.is_in_other       = None
        self.op = None

    @property
    def same(self):
        '''Return True if there is no difference between the structure elements'''
        if not (self.is_in_self and self.is_in_other):
            return False

        for c in self.comparison_list:
            if not c.same:
                return False
        return True

    def new_leaf_strings(self):
        for se in self.new_elements:
            if se.is_leaf:
                yield '{:40} :: {}'.format(se.longname, se.string_to_root)

    def new_nonleaf_strings(self):
        for se in self.new_elements:
            if not se.is_leaf:
                yield '{:50} :: {}'.format(se.longname, se.string_to_root)

    def removed_leaf_strings(self):
        for se in self.removed_elements:
            if se.is_leaf:
                yield '{:40} :: {}'.format(se.longname, se.string_to_root)

    def removed_nonleaf_strings(self):
        for se in self.removed_elements:
            if not se.is_leaf:
                yield '{:50} :: {}'.format(se.longname, se.string_to_root)

    def diff_strings(self,indent = 0,trim_equal = False):

        print_string = ''

        if self.is_in_self is None and self.is_in_other is None:
            #First element - top level
            print_string = '{:10} X  {:10}'.format(self.structure_element.shortname, self.other_structure_element.shortname)
        elif self.is_in_self and self.is_in_other:
            if self.structure_element.longname == self.other_structure_element.longname:
                print_string = indent*'  '+'{:10} {} {:10}              {}'.format(self.structure_element.shortname,self.op,self.other_structure_element.shortname,self.structure_element.longname)
            else:
                print_string = indent*'  '+'{:10} {} {:10}              {} / {}'.format(self.structure_element.shortname,self.op,self.other_structure_element.shortname,self.structure_element.longname, self.other_structure_element.longname)

        elif self.is_in_self:
            print_string = indent*'  '+'{:10} {}                         {}'.format(self.structure_element.shortname,self.op,self.structure_element.longname)

        elif self.is_in_other:
            print_string = indent*'  '+'           {} {:10}              {}'.format(self.op,self.structure_element.shortname,self.structure_element.longname)

        else:
            print(indent*'  ','????',self.op,self.structure_element.shortname)
            assert False

        yield print_string

        if not (trim_equal and self.op == '='):
            for sec in self.comparison_list:
                yield from sec.diff_strings(indent + 1,trim_equal=trim_equal)

        #print (k+ '\t'+comp.transop)


    def print_comparison(self,indent = 0,trim_equal = False):

        print_string = ''

        if self.is_in_self is None and self.is_in_other is None:
            #First element - top level
            print_string = '{:10} X  {:10}'.format(self.structure_element.shortname, self.other_structure_element.shortname)
        elif self.is_in_self and self.is_in_other:
            if self.structure_element.longname == self.other_structure_element.longname:
                print_string = indent*'  '+'{:10} {} {:10}              {}'.format(self.structure_element.shortname,self.op,self.other_structure_element.shortname,self.structure_element.longname)
            else:
                print_string = indent*'  '+'{:10} {} {:10}              {} / {}'.format(self.structure_element.shortname,self.op,self.other_structure_element.shortname,self.structure_element.longname, self.other_structure_element.longname)

        elif self.is_in_self:
            print_string = indent*'  '+'{:10} {}                         {}'.format(self.structure_element.shortname,self.op,self.structure_element.longname)

        elif self.is_in_other:
            print_string = indent*'  '+'           {} {:10}              {}'.format(self.op,self.structure_element.shortname,self.structure_element.longname)

        else:
            print(indent*'  ','????',self.op,self.structure_element.shortname)
            assert False

        print(print_string)

        if not (trim_equal and self.op == '='):
            for sec in self.comparison_list:
                sec.print_comparison(indent + 1,trim_equal=trim_equal)

        #print (k+ '\t'+comp.transop)

    def count_equal_and_total(self):
        if self.is_in_self and self.is_in_other:
            count_equal = 1
        else:
            count_equal = 0

        count_total = 1

        for comp in self.comparison_list:
            child_count_equal, child_count_total = comp.count_equal_and_total()
            count_equal += child_count_equal
            count_total += child_count_total

        return count_equal, count_total

    def add_calculation_comparison(self, previous_calculation_lookup):
        '''
        Create a comparison between previous calculations and final calculations

        Returns a dictionary of {shortcode: (old_calculation, new_calculation)}
        '''

        changed_calculations = {}

        #Note - other structure element is usually the built structure element, since we are comparing previous to new with previous.compare(new)
        for se in self.other_structure_element.walk():
            try:
                old_calculation = previous_calculation_lookup[se.shortcode]
            except KeyError:
                if se.calculation is not None:
                    #There is no old calculation - so put in the new calculation only
                    changed_calculations[se.shortcode] = (None,se.calculation)
                continue

            #Calculations may have been created (as a string) or be in the original physid form exported from Empower
            #We need to check against both
            new_calculation = se.element.calculation
            new_physid_calculation = se.element._physid_calculation
            #If the calculations match, do nothing
            if (old_calculation is None and new_calculation is None) or  old_calculation == new_calculation or old_calculation == new_physid_calculation:
                pass
            else:
                #Otherwise, record the changed calculation
                changed_calculations[se.shortcode] = (old_calculation,new_calculation)

        self.changed_calculations = changed_calculations

def _get_leaf_translation_df_from_tuple(dimension,structure_tuple,field_shortname,structure_element_path):

    '''
    :param: structure_tuple. The old way of specifying a structure element. A tuple of (structure shortcode, hierarchy shortcode, first element in sub-tree shortcode)

    '''

    #TODO - do this through the object model, to ensure clean synchronisation
    dimension_index=dimension.index
    site=dimension.site

    #Don't double up field shortnames when a canonical field is put in
    if field_shortname in ['ID','Short Name','Long Name']:
        field_shortname = None

    if structure_tuple is not None:
        try:
            #if structure is a string then we need to look up the structure from the shortname
            _structure_shortname,_root_shortname,_subtree_shortname = structure_tuple

        except IndexError:
            raise TypeError('parameter structure must be a tuple of shortnames (structure,root_tree_start,subtree_start) or a mpxu.StructureElement object')

        #TODO - this should really come directly from the site object (or subobjects) so that the site can return data that is definitely up to date
        _structure = dimension.structures[_structure_shortname]

        _hierarchy = _structure.get_root_element(_root_shortname)

        if _hierarchy is None:
            msg = 'Could not read Hierarchy "' + _structure_shortname + '.'+_root_shortname+' from zero based Dimension[' + str(dimension_index) + '] in site "' + site._site_locator + '"'
            log.error(msg)
            raise mpex.CompletelyLoggedError(msg)

        #get a DataFrame which will translate the leaf shortnames to level 0- and up physids, for use during data explosion
        column_prefix='dim '+str(dimension_index)+' '+_subtree_shortname+' '
        leaf_translation_df = _hierarchy.get_subtree_translation_df(subtree_shortname=_subtree_shortname,column_prefix=column_prefix,field_shortname=field_shortname)

    elif structure_element_path is not None:
        #When a path has been passed in as a parameter, we know the exact StructureElement we are getting the tree for

        structure_element = dimension.get(structure_element_path)
        #get a DataFrame which will translate the leaf shortnames to level 0- and up physids, for use during data explosion
        column_prefix='dim '+str(dimension_index)+' '+structure_element.shortname+' '
        leaf_translation_df = structure_element.get_subtree_translation_df(subtree_shortname=structure_element.shortname,column_prefix=column_prefix,field_shortname=field_shortname)


    #Change the field shortname to a nonsense string for the dataframe rename - the code below won't accept a None
    if field_shortname is None:
        field_shortname = '#############'
    leaf_translation_df.rename(columns={column_prefix+'ID':'LKUP ID',column_prefix+'Short Name':'LKUP Short Name',column_prefix+'Long Name':'LKUP Long Name',column_prefix+field_shortname:'LKUP '+field_shortname},inplace=True)

    return leaf_translation_df

def _translate_dim(df,dim_identifier,dim_type,translate_df,field_shortname=None):
    #Lookup either on shortname, longname or physid (or field)
    #Lookup either a single or multiple columns

    #If a singular item, convert it to a list
    if isinstance(dim_identifier,str) or isinstance(dim_identifier,int) or isinstance(dim_identifier,float):
        dim_identifier=[dim_identifier]

    left_on=None
    right_on=None


    ################################
    ##TODO
    ################################

    #Are all dim identifiers column in df?

    #Otherwise they are literals
    #Literal physids don't need looking up
    #Literal shortnames need a lookup, but not a merge as such

    ################################

    columns_for_explosion=[]

    if dim_type=='physid':
        right_on='LKUP ID'
    if dim_type=='shortname':
        right_on='LKUP Short Name'
    if dim_type=='longname':
        right_on='LKUP Long Name'
    if dim_type=='field':
        right_on='LKUP '+field_shortname

    #Copy the translation dataframe to avoid corrupting it
    translate_df=translate_df.drop_duplicates(subset=right_on,keep='last').copy()


    #For every column that needs translating, translate it
    #TODO - optimise this so we are not unnecessarily translating single physids to physids
    for column in dim_identifier:

        left_on=column

        try:
            #It is important to keep the new dataframe's index the same as the old one, in case we are merging to a slice
            #Otherwise when we put the columns back we end up with the joined data going in the wrong place
            newdf = pd.merge(how='left',left=df.reset_index(),right=translate_df,left_on=left_on,right_on=right_on).set_index('index')
            #print('newdf')
            #print(newdf.info())
        except KeyError:
            print(df.head())
            print('left_on='+str(left_on))
            print('right_on='+str(right_on))
            print(translate_df.head())
            raise

        #Get the columns for the explode call
        #Change the field shortname to a nonsense string for the dataframe rename - the code below won't accept a None
        if field_shortname is None:
            field_shortname = '#############'
        columns_for_explosion+=[c for c in translate_df.columns if c not in ['LKUP Long Name','LKUP Short Name','LKUP ID','LKUP '+field_shortname]]

    #Add the new columns into the original dataframe
    for column in columns_for_explosion:
        df[column]=newdf[column]

    #Set translate_df to None - to help the Garbage Collector
    translate_df = None


    #print('df')
    #print(df.info())

    return columns_for_explosion

def _time_dimension_import_elements(dimension, elements,imported_dimension_filepath,imported_time_dimension_filepath ):
    dimension_index = 11
    debug = dimension.site._debug

    def _yield_time_dimension_strings(elements):
        #time dimension element stuff
        for output_element in elements:
            #longnames, year, month, day and interval index (year = 0, day = 5).
            #Put the shortname into the longname field - the shortname will be defaulted to the longname.
            #Then the standard dimension code will be run to correct the longname and add the description
            if output_element.longname is not None:
                yield output_element.longname
            else:
                yield output_element.shortname
            yield '\t'
            if output_element.shortname is not None:
                yield output_element.shortname
            yield '\t'
            if output_element.year is not None:
                yield str(int(output_element.year))
            yield '\t'
            if output_element.month is not None:
                yield str(int(output_element.month))
            yield '\t'
            if output_element.day is not None:
                yield str(int(output_element.day))
            yield '\t'
            yield str(int(output_element.interval_index))
            yield '\n'

    #Import the elements in the working file into Empower
    #Export the structure to working_directory

    command_list = dimension.site._logon_parameter_importer_commands + \
                   ['load-file-tsv "' + imported_time_dimension_filepath + '"'
                   ,'empower-import-time-elements "${site}" "${user}" "${password}"'
                   ]

    #In debug mode write the data into a tsv file and read it with Importer, putting the elements into Empower
    if debug:
        #Non time dimensions may have fields - write the standard and non standard fields to file and import them
        with open(imported_time_dimension_filepath,'w') as imported_time_dimension_file:

            #Write empty calculation elements for all changed calculations to help prevent circular calculations
            #These will be overwritten immediately
            for s in _yield_time_dimension_strings(elements):
                imported_time_dimension_file.write(s)

        llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)

    else:
        #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
        #imported_time_dimension_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
        #The merry dance means starting empower, referencing the pipe, opening the pipe before empower is properly started
        #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
        #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
        #before we have created it. But we will block on our side until Importer has connected
        proc = None
        try:
            proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)
            with llu.outbound_pipe(imported_time_dimension_filepath) as pipe:
                #win32file.WriteFile(pipe,"".encode("utf-8"));
                #Write empty calculation elements for all changed calculations to help prevent circular calculations
                #These will be overwritten immediately
                for s in _yield_time_dimension_strings(elements):
                     win32file.WriteFile(pipe, str.encode(s))

                log.debug("Pipe {} finished writing".format(imported_time_dimension_filepath))
        finally:

            #Check if Importer returned an error and raise it as a python if it did
            llu.complete_no_output_importer_process(proc)



    #def _yield_time_dimension_field_strings(elements):
    #
    #    for output_element in elements:
    #
    #        yield output_element.longname
    #        yield '\t'
    #        if output_element.shortname is not None:
    #            yield output_element.shortname
    #
    #        yield '\t'
    #        if output_element.description is not None:
    #            yield output_element.description
    #        yield '\n'
    #
    #command_list = dimension.site._logon_parameter_importer_commands + \
    #               ['set-parameter dimension_index='    + str(dimension_index)
    #               ,'load-file-tsv "'                   + imported_dimension_filepath + '"'
    #               ,'empower-import-field-values "${site}" "${user}" "${password}" ${dimension_index}'
    #               ]
    #
    ##Both time dimensions and standard dimensions will need the longname
    ##In debug mode write the data into a tsv file and read it with Importer, putting the elements into Empower
    #if debug:
    #    #Non time dimensions may have fields - write the standard and non standard fields to file and import them
    #    with open(imported_dimension_filepath,'w') as imported_dimension_file:
    #
    #        #Write empty calculation elements for all changed calculations to help prevent circular calculations
    #        #These will be overwritten immediately
    #        for s in _yield_time_dimension_field_strings(elements):
    #            imported_dimension_file.write(s)
    #
    #    llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)
    #
    #else:
    #    #In 'normal' mode do a merry dance with Windows named pipes. This avoids writing the data to file for security and practicality reasons
    #    #imported_dimension_filepath is the name of the named pipe e.g. \\.\pipe\9dccfa08-40c1-45f5-8e0e-f64c18502bcd
    #    #The merry dance means starting empower, referencing the pipe, opening the pipe before empower is properly started
    #    #setting up the named pipe on this thread, and writing to it (as soon as Importer connects at its end)
    #    #The difficulty, is that we have to pass the name of the pipe to Importer, and rely on the fact that it won't have time to open it
    #    #before we have created it. But we will block on our side until Importer has connected
    #    proc = None
    #    try:
    #        proc = llu.start_no_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)
    #        with llu.outbound_pipe(imported_dimension_filepath) as pipe:
    #
    #            #Write empty calculation elements for all changed calculations to help prevent circular calculations
    #            #These will be overwritten immediately
    #            for s in _yield_time_dimension_field_strings(elements):
    #                win32file.WriteFile(pipe, str.encode(s))
    #
    #            log.debug("Pipe {} finished writing".format(imported_dimension_filepath))
    #
    #    finally:
    #
    #        #Check if Importer returned an error and raise it as a python if it did
    #        llu.complete_no_output_importer_process(proc)

    log.verbose('Time Elements created for dimension '+str(dimension_index))

def _read_structure_from_site(dimension,shortname,encoding='cp1252',old_structure=None):
    '''Read a structure for a given dimension, by specifying the structure shortname
    Return a Structure class

    :param dimension: the Empower dimension we are reading a structure for
    :param shortnam: Short Name of theStructure
    :param dimension_data_dict: A dictionary of dimension data - from the Empower exported dimension. If this is empty, then the dimension will be reexported and read in to the dictionary
    '''
    working_directory           = dimension.site._empower_export_data_dir
    old_structure               = old_structure
    debug                       = dimension.site._debug

    if old_structure is not None:
        structure=old_structure
        #structure.shortname=shortname
        structure.dimension_index = dimension.index
    else:
        structure=Structure(dimension_index=dimension.index,shortname=shortname)

    if debug:
        try:
            os.makedirs(working_directory)
        except FileExistsError:
            pass

    exported_structure_filepath=os.path.join(working_directory,'Exported_Structure_'+str(dimension.index)+'_'+str(shortname)+'.tsv')

    export_structure_importer_script=pkg_resources.resource_filename('pympx','importer_scripts/ExportDimensionStructure.eimp')

    command_list = dimension.site._logon_parameter_importer_commands + \
                       ['set-parameter dimension_index='     + str(dimension.index)
                       ,'set-parameter structure_shortname=' + shortname
                       ,'empower-export-structure "${site}" "${user}" "${password}" ${dimension_index} ${structure_shortname}'
                       ,'tsv-encode'
                       ]

    if debug:
        command_list += ['save-file "{}"'.format(os.path.abspath(exported_structure_filepath))]
        llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)
    else:
        command_list += ['output']
        output = llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)

    def _read_exported_structure_data(exported_structure_data):

        #Note parents always exist before children, and the tree is always written from root to leaf
        #We find the parent element by keeping track of the level, and essentially popping elements when the level decreases
        #The easiest way to do this is to have a level dict, and use the Level number to look up the previous level parent

        #The reason we must use the structure in the file in this way is that SHORTNAMES MAY BE REPEATED.
        #This means that you can't just look up the parent element from the structure. A parent may appear many times in the same structure

        #Note: levels must always be one greater than the previous level, or they may be smaller (up to any amount smaller)

        #e.g.
        #0
        #1
        #2
        #3
        #1
        #2
        #2

        #is fine

        #A dictionary of the Structure elements in the level above
        level_dict={}

        reader=csv.DictReader(exported_structure_data,delimiter='\t')
        record_num = 0

        try:
            for record in reader:

                record_num+=1

                level=          int(record['Level'])
                is_root=        level==0

                shortname=record['Short Name']

                try:
                    #Look up the shortname in the shortname_element_dict, so that we can create the StructureElement from an Element with full information
                    #An Element will be looked up - we muist always create new StructureElements from each line in the structure file.
                    element=dimension.elements[shortname]
                except KeyError:
                    #There is no issue if we have reached the root element, which holds the Structure shortname (and is not a real element anyway)
                    if shortname==structure.shortname and is_root:
                        continue
                    else:
                        raise

                #The parent is the element with a level one less than the current level
                if level > 0:
                    parent_element=level_dict[level-1]
                else:
                    parent_element=None

                structure_element=StructureElement(element=element
                                                  ,structure=structure
                                                  ,parent_structure_element=parent_element
                                                  ,is_root=is_root)

                #Set the current structure element as the StructureElement for this level.
                #As we go down the hierarchy we set new elements. We will only be looking up Strcuture Elements above us, so stale ones below us don't actually matter
                level_dict[level]=structure_element
        except:

            print('Record Number =',record_num)
            raise

        structure._hierarchies_read = True
        structure._exists_in_empower = True
        return structure

    if debug:
        #Read the exported structure file
        with open(exported_structure_filepath,mode='r',encoding=encoding) as exported_structure_data:

            #The element list that will be retutned - we'll add elements to this list
            structure = _read_exported_structure_data(exported_structure_data)
    else:
        import io
        #Do a funky Glagolytic replacement to fix quoting issues - I chose the one that looks like a lamp
        #If there are real Glagolytic characters in your data (highly unlikely - it's a very, very dead language) this code will fail
        #The element list that will be retutned - we'll add elements to this list
        structure = _read_exported_structure_data(io.StringIO(output.replace('""','Ⱖ').replace('"','').replace('Ⱖ','"')))

    #TODO set the structure longname
    return structure


def _create_empower_dimension_shortname_structure_dict( dimension
                                                      , old_structures = None
                                                      ):
    return_dict={}

    if old_structures is None:
        old_structures = []

    #Helper function to convert strings correctly
    def convert_string(s):
        if s == '':
            return None
        else:
            return s

    debug = dimension.site._debug

    if debug:
        try:
            os.makedirs(dimension.site._empower_export_data_dir)
        except FileExistsError:
            pass

    exported_structures_list_filepath=os.path.join(dimension.site._empower_export_data_dir, 'Structures_'+str(dimension.index)+'.tsv')

    ##Export the structures list from Empower if we need to
    log.verbose( "Exporting Structure List from the Empower Site dimension "+str(dimension.index)+" from "+dimension.site._site_locator)

    command_list = dimension.site._logon_parameter_importer_commands + \
                   ['set-parameter dimension_index='   +str(dimension.index)
                   ,'empower-export-structures "${site}" "${user}" "${password}" ${dimension_index}'
                   ,'tsv-encode'
                   ]

    if debug:
        command_list += ['save-file "{}"'.format(os.path.abspath(exported_structures_list_filepath))]
        llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)
    else:
        command_list += ['output']
        output = llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)

    def _read_exported_structures_data(exported_structures_data):
        reader=csv.DictReader(exported_structures_data,delimiter='\t')
        dimension_longname=None
        structure_list=[]
        try:
            for record in reader:

                dimension_longname = convert_string(record['Dimension'])
                shortname          = convert_string(record['Shortname'])
                longname           = convert_string(record['Longname'])
                description        = convert_string(record['Description'])

                #TODO - correct parameters
                structure= Structure(shortname=shortname
                                    ,longname=longname
                                    ,dimension_index = dimension.index
                                    ,dimension=dimension
                                    )
                structure.description = description
                structure._exists_in_empower = True
                structure_list.append(structure)


        except Exception:
            print('Line no: '+str(reader.line_num))
            raise

        #This is an opportunity to set the dimension longname, which isn't available via an explicit empower command
        dimension.longname = dimension_longname

        return structure_list

    major_version, minor_version, release, release_number = dimension.site.importer_version
    encoding='ansi'
    if (major_version == 9 and (minor_version >= 8)) or major_version > 9:
        encoding="utf-8-sig"
        
    if debug:
        #Read the data from file
        with open(exported_structures_list_filepath,mode='r',encoding=encoding) as exported_structures_data:
            #The element list that will be retutned - we'll add elements to this list
            structure_list = _read_exported_structures_data(exported_structures_data)
            
    else:
        import io
        #Do a funky Glagolytic replacement to fix quoting issues - I chose the one that looks like a lamp
        #If there are real Glagolytic characters in your data (highly unlikely - it's a very, very dead language) this code will fail
        #The element list that will be retutned - we'll add elements to this list
        structure_list = _read_exported_structures_data(io.StringIO(output.replace('""','Ⱖ').replace('"','').replace('Ⱖ','"')))

    #Attempt to keep the same object references for previously used elements
    if old_structures is not None:
        for structure in old_structures:
            return_dict[structure.shortname]=structure

    for structure in structure_list:
        try:
            #If the structure already exists, set the structures internals to be the same as the new structure, but make sure we keep the
            return_dict[structure.shortname].longname    = structure.longname
            return_dict[structure.shortname].description = structure.description

        except KeyError:
            return_dict[structure.shortname]=structure

    return return_dict


def _create_empower_dimension_element_list(dimension,debug=False):
    '''Create a list of Empower elements, for a given dimension
    The elements will be of type Element, a class in this module.

    :param dimension: A pympx Dimension object
    :param debug: Write elements to file, to aid with debugging
    '''

    #Helper function to convert strings correctly
    def convert_string(s):
        #print('converting string',s)
        if s == '':
            return None
        else:
            return s

    #The element list that will be returned - we'll add elements to this list
    element_list=[]

    #Export the dimension from Empower
    #Make the directories if in debug mode
    if debug:
        try:
            os.makedirs(dimension.site._empower_export_data_dir)
        except FileExistsError:
            pass

    dim_index =int(dimension.index)

    log.verbose( "Running IMPORTER: from <stdin> to export the Empower Site dimension {} from {}".format(dim_index, dimension.site._site_locator))

    command_list = dimension.site._logon_parameter_importer_commands + \
                   ['set-parameter target='            +os.path.abspath(dimension.site._empower_export_data_dir)
                   ,'set-parameter dimension_index='   +str(dim_index)
                   ,'empower-export-elements "${site}" "${user}" "${password}" ${dimension_index}'
                   ,'tsv-encode'
                   ]

    if debug:
        command_list += ['save-file "${target}\Dimension_${dimension_index}.tsv"']
        llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)
    else:
        command_list += ['output']

        output = llu.run_single_output_importer_commands(command_list,empower_importer_executable=dimension.site.empower_importer_executable)

    def _read_exported_dimension_data(exported_dimension_data):
        reader=csv.DictReader(exported_dimension_data,delimiter='\t')

        for field_name in reader.fieldnames:
            if field_name != 'ID' and dimension is not None:
                dimension.fields._add_field_name(field_name,from_empower=True)

        try:
            prev_record = []
            for record in reader:
                fields={}

                #This is an odd way to deal with a dictionary - basicly we want to put the leftovers into fields,
                #after we've scraped out the parts of the element that are always present
                #So we iterate over the dictionary, seeing if the entry is something that is going into the Element constructor (i.e. the __init__ function)
                #Or if the dictionary entry is going to end up in Element.fields

                physid=None
                shortname=None
                longname=None
                description=None
                group_only=None
                calculation_status=None
                calculation=None
                colour=None
                measure=None
                start_date=None
                interval=None
                interval_amount=None
                offset=None
                resolution=None

                for key, value in record.items():

                    if   key=='ID':
                        physid=int(value)
                        #print('ID',key,value)
                    elif key=='Short Name':
                        shortname=convert_string(value)
                        #if '~TE#MP~' in shortname:
                        #    shortname=shortname[7:]
                        #print('Short-Name',key,value,shortname)
                    elif key=='Long Name':
                        longname=convert_string(value)                        
                        #print('Long-Name',key,value,longname)
                    elif key=='Description':
                        description =convert_string(value)
                        #print('Description',key,value)
                    elif key=='Group Only':
                        group_only=convert_string(value)
                        #print('Group Only',key,value)
                    elif key=='Calculation Status':
                        calculation_status=convert_string(value)
                        #print('Calculation Status',key,value)
                    elif key=='Calculation':
                        calculation=convert_string(value)
                        #print('Calculation',key,value)
                    elif key=='Colour':
                        colour=convert_string(value)
                        #print('Colour',key,value)
                    elif key=='Measure Element':
                        measure=convert_string(value)
                    elif dimension.index==11 and key=='Start Date':
                        start_date=convert_string(value)
                    elif dimension.index==11 and key=='Interval':
                        interval=convert_string(value)
                    elif dimension.index==11 and key=='Interval Amount':
                        interval_amount=convert_string(value)
                    elif dimension.index==11 and key=='Offset':
                        offset=convert_string(value)
                    elif dimension.index==11 and key=='Resolution':
                        resolution=convert_string(value)


                    else:
                        fields[key]=convert_string(value)
                        #print('fields[key]=value',key,value)
                  
                if shortname is None:
                    print('shortName is None')
                    
                    print('record')
                    print(record)
                    print('prev_record')
                    print(prev_record)

                    assert  shortname is not None
                prev_record=record

                if dimension.index != 11 or start_date is None:

                    element= Element(shortname=shortname
                                    ,longname=longname
                                    ,description=description
                                    ,physid=physid
                                    ,group_only=group_only
                                    ,calculation_status=calculation_status
                                    ,calculation=calculation
                                    ,colour=colour
                                    ,measure=measure
                                    ,fields=fields
                                    ,dimension=dimension
                                    )
                    #print('elem-shortname',element.shortname)
                else:
                    try:
                        interval_index = {'Year':     llu.EMPOWER_YEAR_CONSTANT
                                         ,'Half-year':llu.EMPOWER_HALFYEAR_CONSTANT
                                         ,'Quarter':  llu.EMPOWER_QUARTER_CONSTANT
                                         ,'Month':llu.EMPOWER_MONTH_CONSTANT
                                         ,'Week':llu.EMPOWER_WEEK_CONSTANT
                                         ,'Day':llu.EMPOWER_DAY_CONSTANT}[interval]
                    except KeyError:
                        raise ValueError("Could not create a TimeElement reading data from Empower with unexpected Interval '{}'. Expecting one of 'Year','Half-year','Quarter','Month','Week','Day'".format(interval))

                    #Decipher start date into Year, Month, Day

                    _date = _calc_date_info(start_date_str=start_date,interval_index=interval_index,offset=offset)
                    if _date is None:
                        raise ValueError('Date is None for start_date {},interval_index {},offset {}'.format(start_date,interval_index,offset))

                    assert physid is not None
                    element= TimeElement(interval_index=interval_index
                                        ,shortname=shortname
                                        ,year=_date.year
                                        ,month=_date.month
                                        ,day=_date.day
                                        ,description=description
                                        ,longname=longname
                                        ,physid=physid
                                        ,dimension=dimension
                                        )
                    assert element.physid is not None
                    element._interval_amount = int(interval_amount)
                    element._resolution      = resolution
                    element._start_date      = start_date
                    if offset is None:
                        element._offset          = None
                    else:
                        element._offset          = int(offset)

                    #print('elem-shortname2',element.shortname)
                element_list.append(element)

        except Exception as e:
            print('Line no: '+str(reader.line_num))
            try:
                print(record)
            except Exception:
                pass

            raise e
        return element_list

    if debug:
        for dir in [dimension.site._empower_export_data_dir]:

            try:
                os.makedirs(dir)
            except FileExistsError:
                pass
            except OSError as e:
                if e.winerror == 123:
                    raise ValueError('Directory "{}" has an invalid name. Did you pass a site_locator path "{}" without double-escaping backslashes or prefixing the string with an "r" for raw?'.format(dir,repr(site_locator)))
                else:
                    raise e
       #Read the
        exported_dimension_filepath=os.path.join(dimension.site._empower_export_data_dir, 'Dimension_'+str(dimension.index)+'.tsv')
        
        major_version, minor_version, release, release_number = dimension.site.importer_version
        encoding='ansi'
        if (major_version == 9 and (minor_version >= 8)) or major_version > 9:
            encoding="utf-8-sig"
            
        with open(exported_dimension_filepath,mode='r',encoding=encoding) as exported_dimension_data:
            return _read_exported_dimension_data(exported_dimension_data)
        
    else:
        import io
        #Do a funky Glagolytic replacement to fix quoting issues - I chose the one that looks like a lamp
        #If there are real Glagolytic characters in your data (highly unlikely - it's a very, very dead language) this code will fail
        return _read_exported_dimension_data(io.StringIO(output.replace('""','Ⱖ').replace('"','').replace('Ⱖ','"')))

def _create_empower_dimension_shortname_element_dict(dimension,old_elements=None,debug=False):
    '''Create a dictionary of shortnames to Empower elements, for a given zero based dimension
    The elements will be of type Element, a class in this module.

    :param dimension: A pympx Dimension object
    :param old_elements: previous set of elements, this allows us to merge in the elements as they are created
    '''

    element_list= _create_empower_dimension_element_list(dimension= dimension,debug=debug)

    return_dict={}

    #Attempt to keep the same object references for previously used elements
    if old_elements is not None:
        try:
            for element in old_elements.values():
                return_dict[element.shortname]=element
        except AttributeError:
            for element in old_elements:
                return_dict[element.shortname]=element

    for element in element_list:
        try:
            return_dict[element.shortname].merge(element)
        except KeyError:
            return_dict[element.shortname]=element

    return return_dict

def _dataframe_as_elements(dataframe,longname_shortname_rule=None,dimension=None):
    '''Take a pandas.Dataframe and yield Elements'''

    #check the columns are correct
    long_name_column_is_found   = False
    short_name_column_is_found  = False
    description_column_is_found = False
    group_only_column_is_found  = False
    calc_status_column_is_found = False
    calculation_column_is_found = False
    colour_column_is_found      = False
    measure_column_is_found     = False
    field_shortnames=[]

    for c in dataframe.columns:
        if c == 'Long Name':
            long_name_column_is_found=True
        elif c == 'Short Name':
            short_name_column_is_found  = True
        elif c == 'Description':
            description_column_is_found = True
        elif c == 'Group Only':
            group_only_column_is_found  = True
        elif c == 'Calculation Status':
            calc_status_column_is_found = True
        elif c == 'Calculation':
            calculation_column_is_found = True
        elif c == 'Colour':
            colour_column_is_found      = True
        elif c == 'Measure Element':
            measure_column_is_found     = True
        else:
            field_shortnames.append(c)

    if not long_name_column_is_found and not short_name_column_is_found:
        raise ValueError('_dataframe_as_elements(): The dataframe parameter must contain a dataframe with either a "Long Name" column or a "Short Name" column or both. Columns in the dataframe are: '+str(dataframe.columns))

    for d in dataframe.itertuples(index=False):
        #For some reason itertuples isn't coming back with the column names - create a dictionary using the original column names of the dictionary
        element_as_dictionary = {}
        for i, v in enumerate(d):
            try:
                if np.isnan(v):
                    v = None
            except TypeError:
                pass
            element_as_dictionary[dataframe.columns[i]] = v

        shortname=None
        longname=None
        description=None
        physid=None
        group_only=None
        calculation_status=None
        calculation=None
        colour=None
        measure=None
        fields={}

        try:
            if short_name_column_is_found:
                shortname = element_as_dictionary['Short Name']
            else:
                if longname_shortname_rule:
                    shortname = longname_shortname_rule(element_as_dictionary['Long Name'])
                else:
                    #Just set no shortname and let Empower sort it out
                    shortname = None #element_as_dictionary['Long Name']
                    needs_resync = True

            if long_name_column_is_found:
                longname = element_as_dictionary['Long Name']
            if description_column_is_found:
                description = element_as_dictionary['Description']
            if group_only_column_is_found:
                group_only = element_as_dictionary['Group Only']
            if calc_status_column_is_found:
               calculation_status = element_as_dictionary['Calculation Status']
            if calculation_column_is_found :
               calculation = element_as_dictionary['Calculation']
            if measure_column_is_found :
               measure = element_as_dictionary['Measure Element']
            if colour_column_is_found:
                colour = element_as_dictionary['Colour']

            for f_sn in field_shortnames:
                fields[f_sn] = element_as_dictionary[f_sn]

        except KeyError:
            log.error(str(element_as_dictionary))
            raise

        yield Element(shortname          = shortname
                     ,longname           = longname
                     ,description        = description
                     ,physid             = physid
                     ,group_only         = group_only
                     ,calculation_status = calculation_status
                     ,calculation        = calculation
                     ,colour             = colour
                     ,fields             = fields
                     ,override_shortname_length_rule = True
                     ,dimension          = dimension
                     )

#This function takes about a second to run, and is called multiple times during testing
#By making it a non-member function, we can monkeypatch a memoized version during testing, thus speeding up testing, but preserving integration testing
#The _inner version of the function is to prevent a recursion error when monkeypatching the memoized version
def _inner_get_site_details(_logon_parameter_importer_commands,empower_importer_executable):
    site_details={}
    command_list = list(_logon_parameter_importer_commands) + \
                   ['empower-export-site-details "${site}" "${user}" "${password}"'
                   ,'tsv-encode'
                   ,'output'
                   ]
    output = llu.run_single_output_importer_commands(command_list,empower_importer_executable=empower_importer_executable)

    #TODO this does not work for Lock Dimensions which are tab separated already
    for kv in output.split('\r\n'):
        kv_split = kv.split('\t')
        if len(kv_split) > 1:
            site_details[kv_split[0][1:]] = kv_split[1][:-1]
    return site_details

def _get_site_details(_logon_parameter_importer_commands,empower_importer_executable):
    return _inner_get_site_details(_logon_parameter_importer_commands,empower_importer_executable)

def _calc_date_info(start_date_str,interval_index,offset):
    _start_date_str =  start_date_str
    _interval = interval_index
    _offset = offset

    if _start_date_str is None:
        _date = None
    else:
        if _interval == llu.EMPOWER_DAY_CONSTANT:

            #_start_date_str will be of the form '2011' for Jan 2011, '1.2011' for Feb 2011

            day = None
            try:
                year = int(_start_date_str.split('.')[1])
            except IndexError:
                day = 1
                year = int(_start_date_str)

            if day is None:
                day = int(_start_date_str.split('.')[0]) +1

            #Return 1st of month - this isn't correct
            _date =  datetime.datetime(year,1,1) + (day * DAY)
            #_date = None
        elif _interval == llu.EMPOWER_WEEK_CONSTANT:

            #self._start_date_str will be of the form '2011' for Q1 2011, '5.2011' for Q3 2011
            day = None
            try:
                year = int(_start_date_str.split('.')[1])
            except IndexError:
                day = 1
                year = int(_start_date_str)

            if day is None:
                day = int(_start_date_str.split('.')[0]) +1

            #Return 1st of month - this isn't correct
            _date =  datetime.datetime(year,1,1) + (day * DAY)
            #_date = None

        elif _interval == llu.EMPOWER_MONTH_CONSTANT:

            #_start_date_str will be of the form '2011' for Jan 2011, '1.2011' for Feb 2011

            month = None
            try:
                year = int(_start_date_str.split('.')[1])
            except IndexError:
                month = 1
                year = int(_start_date_str)

            if month is None:
                month = int(_start_date_str.split('.')[0]) +1

            #Return 1st of month
            _date =  datetime.datetime(year,month,1)

        elif _interval == llu.EMPOWER_QUARTER_CONSTANT:

            #self._start_date_str will be of the form '2011' for Q1 2011, '5.2011' for Q3 2011
            month = None
            try:
                year = int(_start_date_str.split('.')[1])
            except IndexError:
                month = 1
                year = int(_start_date_str)

            if month is None:
                month = int(_start_date_str.split('.')[0]) +1

            #Return 1st date of quarter
            #quarter * 3 - 2 gives first month of quarter
            _date =  datetime.datetime(year,month,1)

        elif _interval == llu.EMPOWER_HALFYEAR_CONSTANT:

            #self._start_date_str will be of the form '2011' for H1 2011, '5.2011' for H2 2011
            month = None
            try:
                year = int(_start_date_str.split('.')[1])
            except IndexError:
                month = 1
                year = int(_start_date_str)

            if month is None:
                month = 6

            #Return 1st date of half
            _date =  datetime.datetime(year,month,1)


        elif _interval == llu.EMPOWER_YEAR_CONSTANT:

            try:
                year = int(_start_date_str.split('.')[1])
            except IndexError:
                month = 1
                year = int(_start_date_str)
            #Return January 1st of year
            _date =  datetime.datetime(year,1,1)
        else:
            raise ValueError('Not Implemented. Date mapping from Elements are only implemented for day, week, month, quarter, half-year and year intervals, got {} interval_index'.format(interval_index))

    return _date

#This function takes about a 0.2 seconds to run, and is called multiple times during testing
#By making it a non-member function, we can monkeypatch a memoized version during testing, thus speeding up testing, but preserving integration testing
#The _inner version of the function is to prevent a recursion error when monkeypatching the memoized version
def _inner_get_importer_version(empower_importer_executable):

    importer_script=pkg_resources.resource_filename('pympx','importer_scripts/Version.eimp')
    output = llu.run_empower_importer_script(script=importer_script
                        ,empower_importer_executable=empower_importer_executable
                        )

    return [int(s) for s in output.strip().split('.')]

def _get_importer_version(empower_importer_executable):
    return _inner_get_importer_version(empower_importer_executable)

def _diff(old, new):
    '''
    Find the differences between two lists. Returns a list of pairs, where the
    first value is in ['+','-','='] and represents an insertion, deletion, or
    no change for that list. The second value of the pair is the list
    of elements.
    Params:
        old     the old list of immutable, comparable values (ie. a list
                of strings)
        new     the new list of immutable, comparable values

    Returns:
        A list of pairs, with the first part of the pair being one of three
        strings ('-', '+', '=') and the second part being a list of values from
        the original old and/or new lists. The first part of the pair
        corresponds to whether the list of values is a deletion, insertion, or
        unchanged, respectively.
    Examples:
        >>> _diff([1,2,3,4],[1,3,4])
        [('=', [1]), ('-', [2]), ('=', [3, 4])]
        >>> _diff([1,2,3,4],[2,3,4,1])
        [('-', [1]), ('=', [2, 3, 4]), ('+', [1])]
        >>> _diff('The quick brown fox jumps over the lazy dog'.split(),
        ...      'The slow blue cheese drips over the lazy carrot'.split())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('=', ['The']),
         ('-', ['quick', 'brown', 'fox', 'jumps']),
         ('+', ['slow', 'blue', 'cheese', 'drips']),
         ('=', ['over', 'the', 'lazy']),
         ('-', ['dog']),
         ('+', ['carrot'])]
    '''

    # Create a map from old values to their indices
    old_index_map = dict()
    for i, val in enumerate(old):
        old_index_map.setdefault(val,list()).append(i)

    # Find the largest substring common to old and new.
    # We use a dynamic programming approach here.
    #
    # We iterate over each value in the `new` list, calling the
    # index `inew`. At each iteration, `overlap[i]` is the
    # length of the largest suffix of `old[:i]` equal to a suffix
    # of `new[:inew]` (or unset when `old[i]` != `new[inew]`).
    #
    # At each stage of iteration, the new `overlap` (called
    # `_overlap` until the original `overlap` is no longer needed)
    # is built from the old one.
    #
    # If the length of overlap exceeds the largest substring
    # seen so far (`sub_length`), we update the largest substring
    # to the overlapping strings.

    overlap = dict()
    # `sub_start_old` is the index of the beginning of the largest overlapping
    # substring in the old list. `sub_start_new` is the index of the beginning
    # of the same substring in the new list. `sub_length` is the length that
    # overlaps in both.
    # These track the largest overlapping substring seen so far, so naturally
    # we start with a 0-length substring.
    sub_start_old = 0
    sub_start_new = 0
    sub_length = 0

    for inew, val in enumerate(new):
        _overlap = dict()
        for iold in old_index_map.get(val,list()):
            # now we are considering all values of iold such that
            # `old[iold] == new[inew]`.
            _overlap[iold] = (iold and overlap.get(iold - 1, 0)) + 1
            if(_overlap[iold] > sub_length):
                # this is the largest substring seen so far, so store its
                # indices
                sub_length = _overlap[iold]
                sub_start_old = iold - sub_length + 1
                sub_start_new = inew - sub_length + 1
        overlap = _overlap

    if sub_length == 0:
        # If no common substring is found, we return an insert and delete...
        return (old and [('-', old)] or []) + (new and [('+', new)] or [])
    else:
        # ...otherwise, the common substring is unchanged and we recursively
        # diff the text before and after that substring
        return _diff(old[ : sub_start_old], new[ : sub_start_new]) + \
               [('=', new[sub_start_new : sub_start_new + sub_length])] + \
               _diff(old[sub_start_old + sub_length : ],
                       new[sub_start_new + sub_length : ])

#mutable counter - integers will keep resetting when we count
class _Counter(object):
    def __init__(self):
        self.counter = 0
    def __str__(self):
        self.counter+=1
        return '('+str(self.counter-1)+')'
