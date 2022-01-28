#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation

'''Log configuration for use with the Metapraxis utilities.

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

WRITING CLI CODE    
-------------------

When writing Command Line Interface processes (i.e. the ones that use argparse or click)
Use the code in: 
if __name__=='__main__'
as a template. Note that the calls to:
    get_logger() and add_file_handler(log)
must have logconfig appended to them:
    logconfig.get_logger() and logconfig.add_file_handler(log)
and we must also run the import statement:
    from pympx import logconfig

WRITING MODULE CODE    
-------------------    
When writing standard module code use:

    from pympx import logconfig
    log=logconfig.get_logger()

...at the module level - this will ensure that calls to log.info() etc. from inside functions will be routed correctly without any other log setup.

WRITING MULTIPROCESSING CODE    
----------------------------
When writing multiprocessing code, ensure that the Process(es) have the queue sent to them which was created by:
    logging_queue,listener=logconfig.add_file_handler(log) 
See the call to _test_worker_process in the test code below for an example.
Ensure that the overarching function which is invoked by multiprocessing.Process (i.e. _test_worker_process in the example below), calls:
    logconfig.add_queue_handler(logging_queue)
Immediately, to ensure that logs are directed to file.    

   
'''


import logging
import logging.config
import os
import datetime
import multiprocessing

#Create a verbose level - lower than INFO (20), higher than DEBUG (10)
logging.VERBOSE = 15 
logging.addLevelName(logging.VERBOSE, "VERBOSE")
def verbose(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(logging.VERBOSE):
        self._log(logging.VERBOSE, message, args, **kws) 
        
'''Monkey patch in the verbose function - so we can use it like .info() and .error()       
https://stackoverflow.com/questions/5626193/what-is-a-monkey-patch''' 
logging.Logger.verbose = verbose

#Create copies of the logging levels, so that we can set them when using this module, without having to call logging
DEBUG   = logging.DEBUG
VERBOSE = logging.VERBOSE
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR

from pympx import exceptions as mpex
CompletelyLoggedError = mpex.CompletelyLoggedError


def add_rotating_file_handler(log,log_filepath='log.txt',max_bytes_per_file=1000000, backup_file_count=5, verbosity=logging.DEBUG):
    
    file_handler= logging.handlers.RotatingFileHandler(filename=log_filepath
                                                      ,maxBytes=max_bytes_per_file
                                                      ,backupCount=backup_file_count
                                                      )
                                                      
    formatter=logging.Formatter(fmt='%(asctime)s %(levelname)-8s : %(processName)-10s: %(process)-5s: %(message)s'
                               ,datefmt='%Y-%m-%d %H:%M:%S'
                               )
    
    file_handler.setLevel(verbosity)
    file_handler.setFormatter(formatter) 
    
    log.addHandler(file_handler)
    
def add_file_handler(log,log_directory='.', verbosity=logging.VERBOSE, process_date_str_format='%Y%m%d_%H%M%S_%f', log_msg_fmt = '%(asctime)s %(levelname)-8s : %(process)-5s : %(processName)-10s: %(message)s'):
    '''
    
    :param process_date_str_format: By controlling the format of the process date string, we can control the granularity of the files this file handler produces
    :param log_msg_fmt: control the format of the log messages
    '''

    process_date_str=datetime.datetime.strftime(datetime.datetime.now(), process_date_str_format)
    log_file=os.path.join(log_directory,'log_'+process_date_str+'.txt') 
        
    file_handler= logging.FileHandler(filename=log_file)
                                                      
    formatter=logging.Formatter(fmt=log_msg_fmt
                               ,datefmt='%Y-%m-%d %H:%M:%S'
                               )
    
    file_handler.setLevel(verbosity)
    file_handler.setFormatter(formatter) 
    
    queue=multiprocessing.Queue(-1)
    
    listener=logging.handlers.QueueListener(queue,file_handler)
    
    log.addHandler(file_handler)
    
    listener.start()
    
    return queue, listener

def add_console_handler(log, verbosity=logging.VERBOSE, log_msg_fmt = '%(asctime)s %(levelname)-8s : %(process)-5s : %(processName)-10s: %(message)s'):
    '''
    
    :param process_date_str_format: By controlling the format of the process date string, we can control the granularity of the files this file handler produces
    :param log_msg_fmt: control the format of the log messages
    '''

    console_handler= logging.StreamHandler()
                                                      
    formatter=logging.Formatter(fmt=log_msg_fmt
                               ,datefmt='%Y-%m-%d %H:%M:%S'
                               )
    
    console_handler.setLevel(verbosity)
    console_handler.setFormatter(formatter) 
    
    queue=multiprocessing.Queue(-1)
    
    listener=logging.handlers.QueueListener(queue,console_handler)
    
    log.addHandler(console_handler)
    
    listener.start()
    
    return queue, listener
    
def add_queue_handler(queue,log):    
    queue_handler= logging.handlers.QueueHandler(queue)
    log.addHandler(queue_handler)
    
def get_logger(config=None,name='pympx_log'):
    
    if not config:
    
        config={
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                        'detailed': {
                            'class': 'logging.Formatter',
                            'format': '%(asctime)s %(levelname)-8s : %(process)-5s : %(module)-17s@%(lineno)-5s: %(message)s',
                            'datefmt':'%Y-%m-%d %H:%M:%S'
                        },
                        'simple': {
                            'class': 'logging.Formatter',
                            'format': '%(asctime)s %(levelname)-8s : %(message)s',
                            'datefmt':'%Y-%m-%d %H:%M:%S'
                        }
                },
                'handlers': {'console': {
                         'class': 'logging.StreamHandler',
                         'formatter': 'simple',
                         'level': 'INFO',
                     }
                     }
                ,
                'root': {
                    'handlers': ['console'],
                    'level': 'VERBOSE',
                },
            }
    else:
        config=config
    
    logging.config.dictConfig(config)
    pid=os.getpid()    
    logger = logging.getLogger(str(pid))
    return logger    
 
    
def get_verbose_logger(name='pympx_log'):
    

    config={
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                    'detailed': {
                        'class': 'logging.Formatter',
                        'format': '%(asctime)s %(levelname)-8s : %(process)-5s : %(module)-17s@%(lineno)-5s: %(message)s',
                        'datefmt':'%Y-%m-%d %H:%M:%S'
                    },
                    'simple': {
                        'class': 'logging.Formatter',
                        'format': '%(asctime)s %(levelname)-8s : %(message)s',
                        'datefmt':'%Y-%m-%d %H:%M:%S'
                    }
            },
            'handlers': {'console': {
                     'class': 'logging.StreamHandler',
                     'formatter': 'simple',
                     'level': 'VERBOSE',
                 }
                 }
            ,
            'root': {
                'handlers': ['console'],
                'level': 'VERBOSE',
            },
        }

    
    logging.config.dictConfig(config)
    pid=os.getpid()    
    logger = logging.getLogger(str(pid))
    return logger  
def _test_worker_process(logging_queue):
    '''A function to test multithreading is working correctly'''
    
    '''In worker jobs, we need to direct the log (for the worker pid) to the logging_queue'''
    add_queue_handler(logging_queue)
    
    log.warning('Inside job')
    log.info('Inside job')
    log.verbose('Inside job')
    
    
def _test_multithreading(logging_queue):
    '''A function to test multithreading is working correctly'''
        
    #multiprocessing is used as a 'threading' tool
    import multiprocessing 
           
    jobs=[]
    for n in range(3):
        inner_job= multiprocessing.Process(target=_test_worker_process,name='Inner Job',kwargs={'logging_queue':logging_queue})
        jobs.append(inner_job)
    
    for j in jobs:
        log.verbose('Starting job  '+str(j.name))
        j.start()
        log.info('Started job   '+str(j.name)+' with pid '+str(j.pid))

    for n,j in enumerate(jobs):
        j.join()        
        log.info('Completed job '+str(j.name))

   
def banner(product_name='Empower Automated Publication'):
    '''Create a string that shows a process banner, incorporating the product_name
    Use this banner at the start of an command process
    '''
    
    lnlgth = 100
    padlgth = 5
    indentlgth = 2
    lndec =  '#'
    lnspace = ' '
    indentln = lnspace*indentlgth
    padln = lnspace*padlgth

    def divider(prev=''):
        new = indentln + (lndec*lnlgth)
        return '{}\n{}'.format(prev,new)
    def addln(prev='',new=''):
        new = indentln + lndec + padln + new + (lnspace*(lnlgth-2-len(new)-len(padln))) + lndec
        return '{}\n{}'.format(prev,new)
    def addblankln(prev=''):
        new = indentln + (lnspace*lnlgth)
        return '{}\n{}'.format(prev,new)
        
    s = divider()
    s = addln(s)
    s = addln(s,'Metapraxis (c) 2017')
    s = addln(s,'http://www.metapraxis.com | support@metapraxis.com')
    s = addln(s)
    s = addln(s,product_name)
    s = addln(s)
    s = divider(s)
    s = addblankln(s)
    return s
        
        
if __name__=='__main__':
    #Test code - also can be used as an example
    
    #Create a logger - this simulates what happens outside of the calling code - i.e. we should be setting up the file handlers at CLI level
    log=get_logger()
    #Add a file handler, which will listen for log mesages on the logging_queue
    logging_queue,listener=add_file_handler(log)
    log.info('Created file handler queue: '+str(logging_queue))
    try:
        _test_multithreading(logging_queue)
    finally:
        #Stop listening for new log messages
        listener.stop()
    
else:
    log=get_logger()
        
    