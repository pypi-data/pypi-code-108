from abc import ABC, abstractmethod
import argparse
from pathlib import Path
from typing import Callable, Awaitable, Optional, Iterator
import logging
import daiquiri
import sys
import ujson as json
from slugify import slugify
from iso3166 import countries

import dbnomics_fetcher_toolbox.arguments as ta
from dbnomics_fetcher_toolbox.resources import Resource, process_resources
from dbnomics_fetcher_toolbox.status import load_events, open_status_writer

class Converter(ABC):
    '''An abstract converter class''' 
        
    @abstractmethod
    def extend_arguments(self):
       '''Call this function to add additional arguments and call it before the init arguments method '''

    @abstractmethod
    def update_provider_metadata(self, metadata: dict):
       '''Call this function to update provider metadata'''
        
    @abstractmethod
    def init_arguments_and_logging(self):
        '''Define then launch this to initialise the argument parser and logger  '''

    @abstractmethod
    def prepare_resources(self) -> Iterator[Resource]:
        '''Create an iterator of resources - can be a similar function outside of a subclass'''
    
    @abstractmethod
    async def process_single_resource(self, res: Resource):
        '''Consume one resource - and perform a dowload step based on it - can be a similar function outside of a subclass'''

    @abstractmethod
    async def convert_resources(self, prepare_resources: Iterator[Resource], process_single_resource: Callable[[Resource], Awaitable[None]] ):
        '''convert resources - this is best implemented in a subclass'''  

class SimpleConverter(Converter):
    ''' A simple yet fairly complete converter  - additional arguments can be set in a subclass, and initiated afterwards'''
    parser: argparse.ArgumentParser 
    args: argparse.Namespace
    target_dir: Path
    source_dir: Path
    logger: logging.Logger

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        ta.add_arguments_for_convert(self.parser)
        # list arguments (--debug, --limit, --only, )
        # add optional parser arguments in the implementing class
        self.args = None
        self.target_dir = None
        self.source_dir = None


    def init_arguments_and_logging(self):
        ''' execute this after having set custom arguments and logging in the implementing class'''
        self.args = self.parser.parse_args()
                
        self.target_dir = self.args.target_dir
        self.source_dir = self.args.source_dir
        level = logging.DEBUG if self.args.debug else logging.INFO
        daiquiri.setup(level=level,
                 outputs=(daiquiri.output.Stream(sys.stdout), daiquiri.output.File(self.target_dir / "debug.log", formatter=daiquiri.formatter.TEXT_FORMATTER)))
        self.logger = daiquiri.getLogger(__name__)

    async def convert_resources(self, prepare_resources: Iterator[Resource], process_single_resource: Callable[[Resource], Awaitable[None]]):
        '''orchestrate the conversion of all needed resources'''
        resources = list(prepare_resources)
        events = load_events(self.target_dir)

        self.logger.info('start converting resources') 
        with open_status_writer(self.args) as append_event:
            await process_resources(
                resources=resources,
                args=self.args,
                process_resource=process_single_resource,
                on_event=append_event,
                events=events,
            )

    def extend_arguments(self):
       print('Call this function to add additional arguments and call it before the init arguments method ')
    
    
    def prepare_resources(self) -> Iterator[Resource]:
        print('Create an iterator of resources - can be a similar function outside of a subclass')
    
    def process_single_resource(self, res: Resource):
        print('Consume one resource - and convert it - can be a similar function outside of a subclass')

    def update_provider_metadata(self, dict):
        write_json_file(Path(self.target_dir / 'provider.json'), dict)


#region --- Helper functions for converters -----------

#----------------------labels from iso_codes----------------------
def labels_from_isocodes(country_set : set) -> dict:
    """In case ISO codes are provided and labels are needed.
    Pass in a set with ISO-codes.
    """
         
    return {k: countries.get(k).name for k in country_set}


#----------------------isocodes from country labels----------------------
def isocodes_from_labels(country_set : set) -> dict:
    """In case lables are provided and alpha-3 ISO-codes are needed.
    Pass in a set of labels  
    """
       
    return {countries.get(v).alpha3: v  for v in country_set}


#----------------------create a dimenson values dictionary----------------------
def create_dimension_dict(df_code: list, df_label: list, replacements: Optional[list]=[]) -> dict:
    """Two lists are packaged into a code-value dictionary.
    If codes are missing they are generated from labels. Custom replacements are possible.
    If labels are missing codes are duplicated.
    """

    if (not df_code) and (not df_label):
        raise ValueError('Please provide either a non empty list of code or non empty list of label.')
    
    if not df_code:
        df_code = [slugify(l, replacements=replacements) for l in df_label]

    if not df_label:
        df_label = df_code

    if len(df_code) != len(df_label):
        raise ValueError('Please provide lists of equal length for codes and labels, or an empty list for one of them.')

    df_dict = dict(zip(df_code, df_label))

    return df_dict


#----------------------create a series label----------------------
def create_series_label(ts_dimensions: dict, dimensions_values_labels: dict) -> str:  
    """Create a series label"""
    return ' - '.join([dimensions_values_labels[k][ts_dimensions[k]] for k in ts_dimensions.keys() if k != 'FREQ'])


#----------------------create a series code----------------------
def create_series_code(ts_dimensions: dict) -> str:  
    """Create a series code"""
    return '.'.join([ts_dimensions[k] for k in ts_dimensions.keys()]) 


#----------------------write a json file----------------------
def write_json_file(file_path: Path, data: dict):
    """Write data the JSON way to file_path."""
    with file_path.open('w', encoding='UTF-8') as json_fd:
        json.dump(data, json_fd, ensure_ascii=False, indent=2, sort_keys=True)  

#----------------------write_series_jsonl----------------------
def write_series_jsonl(series_filepath: Path, prep_df_list: list):
    """Write series list to series.jsonl file at once."""
    with series_filepath.open('wt', encoding='UTF-8') as fd:
        fd.write('\n'.join(map(lambda dict_:json.dumps(dict_, ensure_ascii=False, sort_keys=True), prep_df_list)))             
#endregion
