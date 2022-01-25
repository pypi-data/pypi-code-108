from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Awaitable, Iterator
import sys
import daiquiri
import urllib.request
import urllib.error
from datetime import datetime
import argparse
import logging
import os

import dbnomics_fetcher_toolbox.arguments as ta
from dbnomics_fetcher_toolbox.resources import Resource, process_resources
from dbnomics_fetcher_toolbox.status import load_events, open_status_writer


class Downloader(ABC):
    '''a abstract downloader class to be implemented in specific downloaders''' 
        
    @abstractmethod
    def extend_arguments(self):
       print(' call this function to add additional arguments and call it before the init arguments method ')
        
    @abstractmethod
    def init_arguments_and_logging(self):
        ''' define then launch this to initialise the argument parser and logger  '''

    @abstractmethod
    def prepare_resources(self) -> Iterator[Resource]:
        print('Create an iterator of resources - can be a similar function outside of a subclass')
    
    @abstractmethod
    async def process_single_resource(self, res: Resource):
        print('Consume one resource - and perform a dowload step based on it - can be a similar function outside of a subclass')

    @abstractmethod
    async def download_resources(self, prepare_resources: Iterator[Resource], process_single_resource: Callable[[Resource], Awaitable[None]] ):
        print('downloading resources - this is best implemented in a subclass')  


class SimpleDownloader(Downloader):
    ''' A simple yet fairly complete downloader  - additional arguments can be set in a subclass, and initiated afterwards'''
    parser: argparse.ArgumentParser 
    args: argparse.Namespace
    target_dir: Path
    logger: logging.Logger

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        ta.add_arguments_for_download(self.parser)
        # list arguments (--debug, --limit, --only, )
        # add optional parser arguments in the implementing class (http-debug log level, proxy setting for running contexts)
        self.args = None
        self.target_dir = None


    def init_arguments_and_logging(self):
        ''' execute this after having set custom arguments and logging in the implementing class'''
        self.args = self.parser.parse_args()
                
        self.target_dir = self.args.target_dir
        level = logging.DEBUG if self.args.debug else logging.INFO
        daiquiri.setup(level=level,
                 outputs=(daiquiri.output.Stream(sys.stdout), daiquiri.output.File(self.target_dir / "debug.log", formatter=daiquiri.formatter.TEXT_FORMATTER)))
        self.logger = daiquiri.getLogger(__name__)

    async def download_resources(self, prepare_resources: Iterator[Resource], process_single_resource: Callable[[Resource], Awaitable[None]]):
        '''orchestrate the download of all needed resources'''
        resources = list(prepare_resources)
        events = load_events(self.target_dir)

        self.logger.info('start downloading resources') 
        with open_status_writer(self.args) as append_event:
            await process_resources(
                resources=resources,
                args=self.args,
                process_resource=process_single_resource,
                on_event=append_event,
                events=events,
            )
    
    def extend_arguments(self):
       print(' call this function to add additional arguments and call it before the init arguments method ')
    
    
    def prepare_resources(self) -> Iterator[Resource]:
        print('Create an iterator of resources - can be a similar function outside of a subclass')
    
    def process_single_resource(self, res: Resource):
        print('Consume one resource - and perform a dowload step based on it - can be a similar function outside of a subclass')

# ----------------------
# HELPER FUNCTIONS
# ----------------------
    
def downloadIfNewerThanLocal(sourceURL: str, targetPath: str):
    logger = daiquiri.getLogger(__name__)
    
    if Path(targetPath).exists():
        target_timestamp = datetime.fromtimestamp(os.path.getmtime(targetPath))
    else:
        target_timestamp = datetime(1900, 1, 1)

    target_timestamp_str = target_timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')
    req = urllib.request.Request(url=sourceURL, headers={"If-Modified-Since": target_timestamp_str})

    try:
        u = urllib.request.urlopen(req)

    except urllib.error.HTTPError as e:
        if e.code == 304:
            logger.info('no updates for: {}; download aborted'.format(targetPath))
        else:
            logger.error('http error for: {}; code: {}; {}'.format(targetPath, e.code, e.info))

    else:
        f = open(targetPath, 'wb')
        f.write(u.read())
        f.close()
    

        

