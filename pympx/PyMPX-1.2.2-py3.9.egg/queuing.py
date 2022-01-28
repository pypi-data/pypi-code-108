############################################################################
# Metapraxis Limited                                                       #
#                                                                          #
# Copyright (©) Metapraxis Ltd, 1991 - 2019, all rights reserved.          #
############################################################################
# NOTICE:  All information contained herein is, and remains the property   #
# of Metapraxis Limited and its suppliers, if any.                         #
# The intellectual and technical concepts contained herein are proprietary #
# to Metapraxis Limited and its suppliers and may be covered by UK and     #
# Foreign Patents, patents in process, and are protected by trade secret   #
# or copyright law.  Dissemination of this information or reproduction of  #
# this material is strictly forbidden unless prior written permission is   #
# obtained from Metapraxis Limited.                                        #
#                                                                          #
# This file is subject to the terms and conditions defined in              #
# file "license.txt", which is part of this source code package.           #
############################################################################

'''
Queuing - a solution to an ETL problem
=======================================

Extract Transform and Load (ETL) processes can take a long time to run. 
Because the data that ETL processes receive can have subtle inconsistencies, and because the servers that ETL processes run on can be capricious, ETL code can and does fail. 
Thus there is a real need for tools for writing quick, robust ETL code.

One such method is processing data in parallel, and one of the best ways of running code in parallel, is to put work on a queue for multiple processors to pick up and run.
Unfortunately, queues are usually designed to run fast, and in memory, and if a process or entire server fails, our only option is to go back and start again.

So there is a requirement for robust queues, that can pick up work part way through, after a failure has occurred.

This module contains various Queues we've used at Metapraxis (https://www.metapraxis.com) to overcome some of the ETL challenges we have faced, when loading data into Empower.
'''

#The done message is set as a constant
DONE=0
FAILED=-1

import os
import shutil

#multiprocessing is used as a 'threading' tool
import multiprocessing
import queue as qq
#unix style wildcard matching
import fnmatch

import uuid
import datetime
from dateutil import relativedelta

#For getting fully qualified domain name
import socket

import time #for sleeping

import json

from pympx import exceptions as mpex
from pympx import logconfig

log=logconfig.get_logger()
CompletelyLoggedError=mpex.CompletelyLoggedError

import multiprocessing
CTX=multiprocessing.get_context()
    
class PersistentQueue(object):
    '''The PersistentQueue behaves like a normal multiprocessing queue, only it records the messages passed to it, so that it can requeue work after a failure.
    
    By maintaining a list of messages in files we can pick up unprocessed work when the processing fails mid way through.
    The files are kept as a pair, the put_file and the done_file that are kept in a new directory for each procesing in run.
    The put file records work put on to the queue and the done file records work which has been done. After a failure the difference between the files shows outstanding work, and there are methods in this class to requeue that work.
    '''
    
    #use in place of a lambda, since lambdas are not picklable
    #PersistentQueue is pickled (saved to a string) when sending to another process - so all of the parts need to be picklable. Google 'python picklable' for more info.
    def return_same(x):
        '''Default message formatter, used instead of lambda x:x because queues need to be pickled, and lambdas cannot be pickled'''
        return x
    
    def __init__(self,pickup_file_prefix=None,current_pickup_dir=None,previous_pickup_dir=None, formatter_list=[return_same], converter_list=[return_same],number_of_workers=1, use_queue=True):
        '''
        Create a multiprocessing Queue, and also create files which record work that has been requested and completed
        
        The pickups directories hold files that allow us to requeue work if there is a failure.
        The files are groups of _requested and _completed files, which, when read in total, can tell us how much work remains outstanding.
        
        By calling requeue_unprocessed_work() on this queue, unfinished work can be re-queued when a failed process is restarted.
        
        :param current_pickup_dir: The directory that will hold pickup files from this run of the process
        :param previous_pickup_dir: The directory that will hold pickup files from the previous run of this process
        :param pickup_file_prefix: The common prefix for pickup requested and completed files
        :param formatter_list: list of functions which will format the objects which are in a message into a string for writing to the pickups file
        :param converter_list: list of functions which will convert the strings in the pickups file into an object for a message
        :param number_of_workers: how many workers will be pulling work off the queue - we need to know this so we can put the correct number of done messages on the queue
        :param use_queue: If set to false we requeue using only the pickups files and not actual queue - this queue can't be used for multiple simultaneous processes. All work must be written before any work is done
        '''

        #Work out where we are recording current work, for use by the next pickups process
        self.put_file_path=None
        self.done_file_path=None
        self.use_queue=use_queue
        self._current_pickup_dir = current_pickup_dir
        
        if current_pickup_dir is not None and pickup_file_prefix is not None:
            put_file_path=os.path.join(current_pickup_dir,pickup_file_prefix+'_requested_PID*.tsv')
            done_file_path=os.path.join(current_pickup_dir,pickup_file_prefix+'_completed_PID*.tsv')
            self.put_file_path=put_file_path
            self.done_file_path=done_file_path
        
        #Get previously requested and completed work, so that we can work out what work is outstanding
        previous_put_file_paths=[]
        previous_done_file_paths=[]
        if previous_pickup_dir is not None:
            for f in os.listdir(previous_pickup_dir):
                full_filepath=os.path.join(previous_pickup_dir,f)
                
                if fnmatch.fnmatch(f,pickup_file_prefix+'_requested_PID*.tsv'):
                    previous_put_file_paths.append(full_filepath)
                    continue

                if fnmatch.fnmatch(f,pickup_file_prefix+'_completed_PID*.tsv'):
                    previous_done_file_paths.append(full_filepath)
                    continue
        
        
        self.pickup_file_prefix=pickup_file_prefix
        
        if self.pickup_file_prefix is None:
            self.pickup_file_prefix = 'unlabeled_queue'
        
        self.previous_put_file_paths=previous_put_file_paths
        self.previous_done_file_paths=previous_done_file_paths
        self.formatter_list=formatter_list
        self.converter_list=converter_list
        self.number_of_workers=number_of_workers
    
        if self.use_queue:
            #initialise the multiprocessing.Queue
            self.joinable_queue=multiprocessing.JoinableQueue()
            #pass
        self.requeued_work=[]
    
        #If we are not recording requested work set a flag
        self._recording_requested_work= self.put_file_path is not None
        self._recording_completed_work= self.done_file_path is not None
        
        self._put_file=None
        self._done_file=None

    @property
    def put_file(self):
        '''The put_file is the open file that records work put() on the queue'''
        
        if self.put_file_path:
    
            if self._put_file is None:
                self._put_file=open(self.put_file_path.replace('PID*','PID'+str(os.getpid())),'w')
                
            return self._put_file
        else:
            return None
        
    @property
    def done_file(self):
        '''done_file is the open file that records work on the queue which has had task_done() called on it'''
        if self.done_file_path:
            if self._done_file is None:
                self._done_file=open(self.done_file_path.replace('PID*','PID'+str(os.getpid())),'w')
                
            return self._done_file
        else:
            return None
    
    def _make_string_from_object(self,obj):
        #If the object is a string then return it as is
        if str(obj)==obj:
            return obj
        else:
            #if the object is a tuple or list, use the formatter list to format the object into a string
            return '\t'.join([str(self.formatter_list[n](sub_obj)) for n, sub_obj in enumerate(obj)])
                
    def _make_object_from_string(self,string_from_file):
        
        strings=string_from_file.strip().split('\t')
        #Return only the string if we have only one item per line
        if len(strings)==1:
            return self.converter_list[0](strings[0])
        #return a tuple of objects if there were multiple tabe separated items on the line
        else:
            return tuple([str(self.converter_list[n](s)) for n, s in enumerate(strings)])
             
    def _test_serialization(self,obj):
        #Serialise and deserialise a test object
        #Check that one method applied after the other results in the original object
        assert obj==self._make_object_from_string(self._make_string_from_object(obj))
    
    def _compute_outstanding_work(self):
        #read in the files each queue's requested/completed work and populate the relevant list
        previously_requested_work=[]
        previously_completed_work=[]
        
        #open the file and read each line into the list
        for file_path in self.previous_put_file_paths:
            with open(file_path,'r') as qfile:
                for line in qfile:
                    previously_requested_work.append(self._make_object_from_string(line))
    
        #open the file and read each line into the list
        for file_path in self.previous_done_file_paths:
            with open(file_path,'r') as qfile:
                for line in qfile:
                    previously_completed_work.append((self._make_object_from_string(line)))            

        #Outstanding work is requested work that has not been completed
        self.list_of_outstanding_work=list(set(previously_requested_work)-set(previously_completed_work))
        
    def requeue_unprocessed_work(self):
        '''Requeue any work that was not processed during the previous (failed) load.
        Only do this after this queue has been sent to child processes'''
        self._compute_outstanding_work()
        
        for msg in self.list_of_outstanding_work:
            log.verbose('Requeuing uncompleted message: '+self._make_string_from_object(msg).strip())
            #JAT. Ideally we'd put the messages on the queue - only that is not going to work in a multiprocessing environment, because we should only be pickling empty queues
            #We need to record requeued work anyway (to stop us putting work onto a queue twice) so we will use the requeud_work list to silently .put() the work on the queue in the child processes
            #JAT - there is nothing for it, but to restrict requeuing of work until after the queue has been sent to child processes
            self.put(msg)
            self.requeued_work.append(msg)
        
        
    def get_list_of_outstanding_work(self):
        '''Return a list of items on the queue which had not been completed when this queue was last created.
        The queue uses the files in previous_pickup_dir to compute work that needs to be redone.
        '''
    
        try:
            return self.list_of_outstanding_work
        except NameError:
            self._compute_outstanding_work()
            return self.list_of_outstanding_work
    
    def _record_work_requested(self,obj):
        if self._recording_requested_work:
            self.put_file.write(self._make_string_from_object(obj)+'\n')
            self.put_file.flush()
        
        
    def _record_work_completed(self,obj):
        if self._recording_completed_work:
            self.done_file.write(self._make_string_from_object(obj)+'\n')
            self.done_file.flush()
        
    def put(self,obj,block=True,timeout=None):
        '''Put item into the queue. 
        If optional args `block` is true and `timeout` is `None (the default), block if necessary until a free slot is available. 
        If `timeout` is a positive number, it blocks at most timeout seconds and raises the Full exception if no free slot was available within that time. 
        Otherwise (block is false), put an item on the queue if a free slot is immediately available, else raise the `Full` exception (timeout is ignored in that case).'''
    
    
        if obj in self.requeued_work:
            log.verbose('Requested item not put on queue as it has previously been requeued')
            return None
        else:
            if obj != DONE and obj != FAILED:
                #Write to pickups file
                self._record_work_requested(obj)
            #put the object on the underlying queue
            if self.use_queue:
                self.joinable_queue.put(obj,block,timeout)
   
    def put_nowait(self,obj):
        '''Equivalent to put(item, False).'''
        
        self._record_work_requested(obj)
        if self.use_queue:
            self.joinable_queue.put_nowait(obj)
    
         
    def get(self,block=True,timeout=None):
        '''Remove and return an item from the queue. If optional args `block` is true and `timeout` is None (the default), block if necessary until an item is available. 
        If timeout is a positive number, it blocks at most timeout seconds and raises the `Empty` exception if no item was available within that time. 
        Otherwise (block is false), return an item if one is immediately available, else raise the Empty exception (timeout is ignored in that case).

        Prior to 3.0 on POSIX systems, and for all versions on Windows, if block is true and timeout is None, this operation goes into an uninterruptible wait on an underlying lock. 
        This means that no exceptions can occur, and in particular a SIGINT will not trigger a KeyboardInterrupt.
        '''

        log.debug('get has self.use_queue=='+str(self.use_queue))
        if self.use_queue==False:
            #The code must only call get, for a file only process, once all of the tasks have been queued
            #But we can't test for this, becuase we are on a different process
            
            #The internal list of work must be read at the first get if we are using a file (possible across separate processes that run consecutively)
            try: 
                self._internal_list_of_work=self._internal_list_of_work
            except AttributeError:
                #Find the current 'put' pickup files. They should have been closed by this point
                #And read the work in from them
                self._current_pickup_dir
                
                
                #Get currently requested and completed work, so that we can read it into the queue
                current_put_file_paths=[]
                if self._current_pickup_dir is not None:
                    for f in os.listdir(self._current_pickup_dir):
                        full_filepath=os.path.join(self._current_pickup_dir,f)
                        
                        if fnmatch.fnmatch(f,self.pickup_file_prefix+'_requested_PID*.tsv'):
                            current_put_file_paths.append(full_filepath)
                            
            
                #open the files and read each line into the list of outstanding work
                self._internal_list_of_work=[]
                for path in current_put_file_paths:
                    with open(path,'r') as qfile:
                        for line in qfile:
                            self._internal_list_of_work.append(self._make_object_from_string(line))                
            
                #Put DONE messages on the queue
                for _ in range(self.number_of_workers):
                    log.debug('Putting DONE message on _internal_list_of_work of '+self.pickup_file_prefix)
                    self._internal_list_of_work.append(DONE)
                
            try:
                next_item=self._internal_list_of_work[0]
                self._internal_list_of_work=self._internal_list_of_work[1:]
                log.debug('get return next_item: '+str(next_item) + ' on '+self.pickup_file_prefix)
                return next_item
            except IndexError:
                log.debug('get raising qq.Empty() on '+self.pickup_file_prefix)
                #The empty queue error serves as a signal, and will be caught appropriately
                raise qq.Empty()
            
        else:      
            return self.joinable_queue.get(block,timeout)
            
            
    def get_nowait(self):
        '''Equivalent to get(False).'''
        return self.get(block=False)
        
    def task_done(self,obj):
        '''Write the object to the pickups complete file, then call task_done() on the underlying queue.
        This will indicate that a formerly enqueued task is complete. Used by queue consumer threads. For each get() used to fetch a task, a subsequent call to task_done() tells the queue that the processing on the task is complete.
        
        If a join() is currently blocking, it will resume when all items have been processed (meaning that a task_done() call was received for every item that had been put() into the queue).

        Raises a ValueError if called more times than there were items placed in the queue.
        '''

        #Write to pickups file
        self._record_work_completed(obj)
        #record work as done on the underlying queue
        if self.use_queue:
            self.joinable_queue.task_done()
    
    def mark_all_work_done(self):
        '''Mark all of the work in the queue as done, for the purposes of picking up from a failed laod.
        
        We need to mark all the work as done at once if it is done as a logical whole.
        This function calls task_done() on all of the messages left in the queue. 
        '''
        
        #Get all of the messages left in the queue and mark them as done
        for msg in self:
            self.task_done(msg)
        
    
    def close(self):
        '''As a producer, close the queue for new inputs, and place appropriate DONE messages on the queue, so that consumers know that all work has been done, and they can stop.'''
        
        if self.put_file:
            #Close the files 
            self.put_file.close()
        
        #Put DONE messages on the queue
        for _ in range(self.number_of_workers):
            log.debug('Putting DONE message on Queue '+self.pickup_file_prefix)
            self.put(DONE)
        if self.use_queue:
            log.debug('Closing Queue '+self.pickup_file_prefix)
            try:
                self.joinable_queue.close()
            except Exception:
                log.error('Exception raised when closing queue')
                raise
        
    def fail(self):
        '''Close the queue for new inputs, and place appropriate FAILED messages on the queue, so that consumers know that an upstream process has failed, and they can stop.'''
        
        if self.put_file:
            #Close the put file - catching code should close the done file, since work may be being done while another stream is failing
            self.put_file.close()
            
        #Put FAILED messages on the queue
        for _ in range(self.number_of_workers):
            log.error('Putting FAILED message on PersistentQueue '+self.pickup_file_prefix)
            self.put(FAILED)
        if self.use_queue:
            log.error('Closing PersistentQueue '+self.pickup_file_prefix)
            self.joinable_queue.close()
    
    def dispose(self):
        '''As a consumer, stop using the queue, and crucially, close the done_file, which records successful work completion'''
        if self.done_file_path and self.done_file:
            try:
                log.debug('Closing Done File: '+str(self.done_file_path))
                self.done_file.close()
            except Exception:
                pass
                
                
    #Some cunning code to allow the queue to be used like an iterable (i.e. in a for loop)
    #The class handles the DONE and FAILURE messages internally which reduces boilerplate calling code
    
    def __iter__(self):
        return self

    def __next__(self): # Python 3 only
    
        log.debug('__next__ Getting message')
        msg=self.get()
        
        if  msg==FAILED:
            log.error('Got FAILED message on PersistentQueue '+self.pickup_file_prefix)
            self.dispose()  
            raise mpex.UpstreamFailureError('Upstream process failed. FAILED message received via Queue')
            
        #When DONE (0) stop
        if  msg==DONE:
            log.debug('Got DONE message on PersistentQueue '+self.pickup_file_prefix)
            self.dispose()  
            raise StopIteration    
        else:
            log.debug('__next__ Got message '+str(msg))
        
            return msg

    #Pickling code. Override the default pickling code to remove the opened files which are recording our work. We don't need to pass them around anyway, since each file will have its own PID
    #and that file should only be updated by the process with that PID
    def __getstate__(self):
        #copy the dictionary of attributes and methods, so that we don't alter the original PersistentQueue object when pickling
        d = dict(self.__dict__)
        #Don't pickle open work requested or work completed files
        #not all queues will have these files open, as they only get opened when we put work on the queue
        try:
            del d['_done_file']
        except KeyError:
            pass
            
        try:
            del d['_put_file']
        except KeyError:
            pass
        
        return d
        
    def __setstate__(self,d):
        self.__dict__.update(d)
        #Start with None in the attributes for the work requested and completed files. When we call put() or task_done() the files will be created and opened
        self._done_file=None
        self._put_file=None

class RobustQueue(object):
    '''An abstraction over a folder that is being used for work passing between processes.
    
    Unlike a PersistentQueue, it is assumed that the queue is cross server, and has relatively slow response times, and can have large messages and data written to it
    
    This queue is designed for robust single producer, single consumer processes rather than multiple worker processes.
    
    On top of data passing we add distributed heartbeat monitoring.
    The queue is designed for a single Producer, single Consumer, and multiple Monitors
    
    Producer - produces work and puts it into the message box
    Consumer - consumes work and takes it from the message box
    Monitor  - checks that work is going through the message box
    
    Each of these participators should send an emergency email should they suspect that the queue is not working, though they should not be the primary emailing-responsibility.
    In normal Emails should go on to a queue 
    '''
    
    def __init__(self,path,number_of_workers=1, email_sender=None,email_receivers=None,smtp_host=None, heartbeat_cleanup_wait_ms=1000*60*60*24*7):
        '''
        
        :param heartbeat_cleanup_wait_ms: How long to wait after a heartbeat created by another process has expired before cleaning it up - default is a week
        '''
        #set email details of who to alert if Consumer, Producer or Monitor of the queue is unresponsive
        
        self.email_sender               = email_sender
        if email_receivers is None:
            email_receivers = []
        else:
            self.email_receivers            = email_receivers
            
        self.smtp_host                  = smtp_host
        self.path                       = path
        self.number_of_workers          = number_of_workers
        self.heartbeat_cleanup_wait_ms  = heartbeat_cleanup_wait_ms
        
        self._timeformat                = '%Y-%m-%d %H:%M:%S.%f'
        self._hostname                  = socket.gethostname()
        self._fqdn                      = socket.getfqdn()
        import hashlib
        self._fqdn_hash                 = str(int(hashlib.sha256(self._fqdn.encode('utf-8')).hexdigest(), 16) % 10**10).zfill(10)
        self._pid                       = str(os.getpid()).zfill(6)
        self._login                     = os.getlogin()
        
        
        self._heartbeats_path           = os.path.join(self.path,'heartbeats')
        
        try:
            os.makedirs(self.path)
        except FileExistsError:
            pass
        
        try:
            os.mkdir(self._heartbeats_path)
        except FileExistsError:
            pass
    

    def _uuid_string_to_uuid_file_string(self,uuid_string):
        return uuid_string.replace('-','_')
    
    def _filepath(self,datetime_string,uuid_string,extension):
        '''Returns a message  filename
        '''
        return os.path.join(self.path,datetime_string.replace('-','').replace('.','_').replace(':','').replace(' ','_')+'_'+self._uuid_string_to_uuid_file_string(uuid_string)+'.'+extension)
    
    
    def _heartbeat_filepath(self,datetime_string,uuid_string,extension):
        '''Returns a heartbeat filename
        '''
        return os.path.join(self._heartbeats_path,datetime_string.replace('-','').replace('.','_').replace(':','').replace(' ','_')+'_'+self._uuid_string_to_uuid_file_string(uuid_string)+'.'+extension)
    
    
    def _datetime_string(self):
        return datetime.datetime.utcnow().strftime(self._timeformat)
    def _uuid_string(self):
        return str(uuid.uuid1())
    
    def get(self,timeout=None):
    
        message = self.get_cautiously(timeout=timeout)
        
        if message == DONE or message == FAILED:
            return message
        
        #TODO - remove wip file from the queue
        for f in os.listdir(self.path):
            #filter to message files only
            if fnmatch.fnmatch(f,'*_{}_{}_{}_{}.wip'.format(message['header']['pid']
                                                            ,message['header']['machineFQDN']
                                                            ,message['header']['createdUTCTimestamp'].replace('-','').replace(':','').replace(' ','_').replace('.','_')
                                                            ,self._uuid_string_to_uuid_file_string(message['header']['uuid']))):
                wip_file_path = os.path.join(self.path,f)
                
                os.remove(wip_file_path)
                
        return message['data']
        
        
    
    def get_cautiously(self,timeout=None,usebydate=None):
        '''Getting data will return a message, including the header that this Queue has added to the message when it was put on the queue
        The ['data'] will contain the dictionary originally put on to the queue
        it will also put a special Consumer heartbeat message on the queue
        
        The message file will be renamed and remain on the queue until task_done(message) is called or release(message) is called
        '''
        start_polling_datetime = datetime.datetime.utcnow()
        
        _extension = 'message'
        
        #TODO
        #Check for files which are work in progress on them. If the wip has timed out (after 1000 ms)
        #then set it back the way it was in a use it or lose it fashion
        #This stops unprocessed messages hanging when a process which has taken dibs on a file dies before it can process it
        
        if timeout is None:
            #Timeout after 10 years - or so
            timeout = 1000*60*60*24*365*10
        
        if timeout < 1000:
            #Don't sleep longer than the timeout - convert timeout into seconds and divide by 10
            sleep_seconds = timeout/10000
        else:
            #Poll every second
            sleep_seconds = 1
        
        end_polling_datetime = start_polling_datetime + datetime.timedelta(milliseconds = timeout)

        while True:
            #Get the earliest message on the queue
            for f in sorted(list(os.listdir(self.path))):
                #filter to message files only
                if fnmatch.fnmatch(f,'*.{}'.format(_extension)):
                    message_file_path = os.path.join(self.path,f)
        
                    if usebydate is None:
                        #Default usebydate is 1 second from now
                        usebydate = datetime.datetime.utcnow() + datetime.timedelta(milliseconds = 1000)
                    
                    #Put out a heartbeat expecting another heartbeat after we estimate the message will be used 
                    delta = usebydate - datetime.datetime.utcnow()
                    milliseconds_difference = delta.days*24*60*60*1000 + delta.seconds * 1000 + delta.microseconds / 1000
                    self.heartbeat(type='consumer', next_ms= milliseconds_difference + 1000)
        
        
                    #put dibs on the message by renaming file with own unique fqdn and pid before using it
                    wip_file_path = os.path.join(self.path,usebydate.strftime('%Y%m%d%H%M%S%f')+'_'+str(self._pid)+'_'+self._fqdn_hash+'_'+f.replace(_extension,'wip'))
                    try:
                        shutil.move(message_file_path,wip_file_path)
                    except FileNotFoundError:
                        #If we couldn't put dibs on the file it may have been grabbed by another process - look for the next message
                        continue
                    except PermissionError:
                        log.error('Access Denied on message file "{}"'.format(message_file_path))
                        continue
        
                    #the message should contain data
                    #links to files are handled by the data containing the filepath 
                    
                    #Open the file and check the header
                    with open(wip_file_path,'r') as msgf:
                        message_dict = json.load(msgf)
                        return message_dict
            
                #filter to done files to see if there is no more work to do
                if fnmatch.fnmatch(f,'*.done'):
                    os.remove(os.path.join(self.path,f))
                    
                    #TODO - put out a heartbeat, saying we are about to turn off until...?
                    
                    return DONE
                
                #filter to done files to see if there is no more work to do
                if fnmatch.fnmatch(f,'*.failed'):
                    os.remove(os.path.join(self.path,f))
                    return FAILED
                
            #If there are no messages, sleep, and then poll again until the timeout
            
            if datetime.datetime.utcnow() < end_polling_datetime:
                #log.info("Didn't find a message, sleeping")            
        
                #TODO 
                #Monitor heartbeats from the producer
                
                #If producer is not in rude health instigate emergency action
                
                
        
                #put a heartbeat out so the consumer and monitor know that we WILL be polling again, and when
                self.heartbeat(type='consumer', next_ms=sleep_seconds*1000+1000)
        
                #Sleep for a second, then do the next loop
                time.sleep(sleep_seconds)
            else:
                #Raise Queue.Empty if there is a timeout - this is standard behaviour for a queue
        
                raise qq.Empty('RobustQueue on path {} had no messages within the timeout period {} milliseconds'.format(self.path,timeout))
                
    
    
    def estimate(self,msg,ms,debug_string=''):
        '''Put out an estimate for how long the consumer process thinks it will take to process a message
        A consumer process may not know how long a given message may take to process until it has read the message
        By adding a later estimate file, it can signal to the producer that it will take a certain amount of time
        
        :param debug_string: String to help us figure out from logs which heartbeat failed
        '''
        #Write the message to the folder
        if isinstance(msg,dict):
            _temp_extension  = 'tempestimate'
            _extension       = 'estimate'
            
            _datetime_string = self._datetime_string()
        
            _uuid_string = msg['header']['uuid']
        
            #Create the file with a temporary extension, then move (rename) to make the file write transactional
            with open(self._filepath(_datetime_string,_uuid_string,_temp_extension),'w') as f:
                json.dump(obj={'header':{
                                         'type':'estimate'
                                        ,'createdUTCTimestamp':_datetime_string
                                        ,'uuid':_uuid_string
                                        ,'nextMessageUTCOffset':ms
                                        ,'createdBy':self._login
                                        ,'hostName':self._hostname
                                        ,'machineFQDN':self._fqdn
                                        ,'pid':self._pid
                                        ,'debugString':debug_string
                                        }
                            ,'data':None}
                            ,fp=f,indent=2)
        
            shutil.move(self._filepath(_datetime_string,_uuid_string,_temp_extension),self._filepath(_datetime_string,_uuid_string,_extension))
    
        else:
            pass        
        
        
    def put(self,msg,next_ms=24*60*60*1000,debug_string=''):
        '''
        :param msg: A file object, or a dictionary. If a file object the file will be written to the queue folder, along with a message. If a dictionary then the dictionary will be used as the data argument and json dumped to a msg file
        :param next_ms: Time we expect to put the next message on the queue. This helps the monitor process and consumer process check on the health of the producer process
        '''
        self.heartbeat(type='producer', next_ms=next_ms+60000,debug_string=debug_string)
        
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        
        #Write the message to the folder
        if isinstance(msg,dict):
            _temp_extension  = 'temp'
            _extension       = 'message'
            
            #Create the file with a temporary extension, then move (rename) to make the file write transactional
            with open(self._filepath(_datetime_string,_uuid_string,_temp_extension),'w') as f:
                json.dump(obj={'header':{
                                         'type':'message'
                                        ,'createdUTCTimestamp':_datetime_string
                                        ,'uuid':_uuid_string
                                        ,'nextMessageUTCOffset':next_ms
                                        ,'createdBy':self._login
                                        ,'hostName':self._hostname
                                        ,'machineFQDN':self._fqdn
                                        ,'pid':self._pid
                                        ,'debugString':debug_string
                                        }
                            ,'data':msg}
                            ,fp=f,indent=2, default=str)
        
            shutil.move(self._filepath(_datetime_string,_uuid_string,_temp_extension),self._filepath(_datetime_string,_uuid_string,_extension))
    
        else:
            pass

    def _put_done(self):
        '''
        '''
        self.heartbeat(type='producer', next_ms=None)
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        
        _temp_extension  = 'temp'
        _extension       = 'done'
        
        #Create the file with a temporary extension, then move (rename) to make the file write transactional
        with open(self._filepath(_datetime_string,_uuid_string,_temp_extension),'w') as f:
            json.dump(obj={'header':{
                                     'type':'done'
                                    ,'createdUTCTimestamp':_datetime_string
                                    ,'uuid':_uuid_string
                                    ,'nextMessageUTCOffset':None
                                    ,'createdBy':self._login
                                    ,'hostName':self._hostname
                                    ,'machineFQDN':self._fqdn
                                    ,'pid':self._pid
                                    }}
                        ,fp=f
                        ,indent=2)
    
        shutil.move(self._filepath(_datetime_string,_uuid_string,_temp_extension),self._filepath(_datetime_string,_uuid_string,_extension))

    
    def _put_failed(self):
        '''
        '''
        self.heartbeat(type='producer', next_ms=None)
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        
        _temp_extension  = 'temp'
        _extension       = 'failed'
        
        #Create the file with a temporary extension, then move (rename) to make the file write transactional
        with open(self._filepath(_datetime_string,_uuid_string,_temp_extension),'w') as f:
            json.dump(obj={'header':{
                                     'type':'failed'
                                    ,'createdUTCTimestamp':_datetime_string
                                    ,'uuid':_uuid_string
                                    ,'nextMessageUTCOffset':None
                                    ,'createdBy':self._login
                                    ,'hostName':self._hostname
                                    ,'machineFQDN':self._fqdn
                                    ,'pid':self._pid
                                    }}
                        ,fp=f
                        ,indent=2)
    
        shutil.move(self._filepath(_datetime_string,_uuid_string,_temp_extension),self._filepath(_datetime_string,_uuid_string,_extension))

    def _message_expiry_datetime(self,message_header):
        
        _datetime        = self._message_created_datetime(message_header)
        next_ms          = message_header['nextMessageUTCOffset']
        
        if next_ms is None:
            return None
        else:    
            return _datetime + datetime.timedelta(milliseconds = next_ms)
    
    def _message_created_datetime(self,message_header):
        
        _datetime_string = message_header['createdUTCTimestamp']
        return datetime.datetime.strptime(_datetime_string,self._timeformat)
        
            
    def _timeout_is_expired(self,message_header):
        
        expiry_datetime  = self._message_expiry_datetime(message_header)
    
        if expiry_datetime is None:
            return False
    
        now = datetime.datetime.utcnow()
        
        return now > expiry_datetime
    
    def _message_is_mine(self,message_header):
        #Return whether the message was created by this process
        #We can delete our own heartbeats with more confidence than deleting other's since we know we are still creating new ones
        return message_header['pid'] == self._pid and message_header['machineFQDN'] == self._fqdn
    
    def heartbeat(self,type=None, next_ms=60000,debug_string=''):
        '''Put a heartbeat message on the queue
        
        :param type: Type of heartbeat. One of 'producer', 'consumer', 'monitor' - this allows Producers, Consumers and Monitors to tell who's heartbeats are on the queue
        :param next_ms: Number of milliseconds before we expect to put another heartbeat on the queue
        '''
        _type = 'generic'
        if type is not None:
            _type = str(type)
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        _temp_extension  = 'temp'
        
        _extension       = 'heartbeat'
        
        #Create the file with a temporary extension, then move (rename) to make the file write transactional
        with open(self._heartbeat_filepath(_datetime_string,_uuid_string,_temp_extension),'w') as f:
            json.dump(obj={'header':{
                                     'type':'heartbeat'
                                    ,'heartbeatType':_type
                                    ,'createdUTCTimestamp':_datetime_string
                                    ,'uuid':_uuid_string
                                    ,'nextMessageUTCOffset':next_ms
                                    ,'createdBy':self._login
                                    ,'hostName':self._hostname
                                    ,'machineFQDN':self._fqdn
                                    ,'pid':self._pid
                                    ,'debugString':debug_string
                                    }
                          ,'data':{}
                          }
                          ,fp=f
                          ,indent=2)
        
        shutil.move(self._heartbeat_filepath(_datetime_string,_uuid_string,_temp_extension),self._heartbeat_filepath(_datetime_string,_uuid_string,_extension))
    
        #Eat old heartbeats if they belong to self, or are a week past their expiry date
        #Expiry date is utc + next milliseconds
        for f in os.listdir(self._heartbeats_path):
            #filter to heartbeat files only
            if fnmatch.fnmatch(f,'*.{}'.format(_extension)):
                heartbeat_file_path = os.path.join(self._heartbeats_path,f)
                #Open the file and check the header
                try:
                    with open(heartbeat_file_path,'r') as hbf:
                        heartbeat_dict = json.load(hbf)
                except (FileNotFoundError,PermissionError):
                    #Heartbeat file was removed by another process - it must have been old, or it is currently being renamed or deleted
                    continue
                except json.decoder.JSONDecodeError as e:
                    log.error('Failed to read corrupt heartbeat file {}'.format(heartbeat_file_path))
                        
                    log.exception(e)
                    #Try to delete it (something else might be deleting it, it might be locked etc.)
                    try:
                        os.remove(heartbeat_file_path)
                        log.warning('Removed corrupt heartbeat file {}'.format(heartbeat_file_path))
            
                    except Exception as e:
                        log.warning('Failed to remove corrupt heartbeat file {}'.format(heartbeat_file_path))
                        log.exception(e)
                    continue
                    
                #get expiry
                #self.heartbeat_cleanup_wait_ms
                
                heartbeat_header = heartbeat_dict['header']
                
                
                #print(heartbeat_header['heartbeatType'],self._message_expiry_datetime(heartbeat_header),self._timeout_is_expired(heartbeat_header) )
                
                if self._timeout_is_expired(heartbeat_header) and heartbeat_header['heartbeatType']==_type:
                    if self._message_is_mine(heartbeat_header) or self._message_expiry_datetime(heartbeat_header) + datetime.timedelta(weeks=1) < datetime.datetime.utcnow():
                        #Try to delete it (something else might be deleting it, it might be locked etc.)
                        try:
                            os.remove(heartbeat_file_path)
                            log.debug('Removed heartbeat file {}'.format(heartbeat_file_path))
                
                        except Exception:
                            log.warning('Failed to remove heartbeat file {}'.format(heartbeat_file_path))
                    
    
    def _get_latest_heartbeat(self,heartbeat_type):
    
        _extension = 'heartbeat'
    
        _latest_created_datetime = None
        
        _latest_heartbeat = None
    
    
        for f in os.listdir(self._heartbeats_path):
            #filter to heartbeat files only
            if fnmatch.fnmatch(f,'*.{}'.format(_extension)):
                
                heartbeat_file_path = os.path.join(self._heartbeats_path,f)
                
                try:
                    #Open the file and check the header
                    with open(heartbeat_file_path,'r') as hbf:
                        heartbeat_dict = json.load(hbf)
                except (FileNotFoundError,PermissionError):
                    log.info('Heartbeat file {} eaten by another process, before it could be checked'.format(heartbeat_file_path))
                    continue
                        
                #get expiry
                #self.heartbeat_cleanup_wait_ms
                
                heartbeat_header = heartbeat_dict['header']
                
                if heartbeat_header['heartbeatType'] == heartbeat_type:
                    
                    _created_datetime = self._message_created_datetime(heartbeat_header)
                    
                    if _latest_created_datetime is None or _latest_created_datetime < _created_datetime:
                        _latest_created_datetime = _created_datetime
                        _latest_heartbeat        = heartbeat_dict
                
        return _latest_heartbeat
    
    
    def _get_latest_work_in_progress(self):
        '''This one is a bit different.
        it looks up work in progress, but if it finds an estimate, it adjusts the expiry date of the wip 
        '''
        
        _latest_wip_created_datetime = None
        _latest_wip_estimated_end_datetime = None
        
        _latest_wip = None
        _latest_estimate = None
        
        #Look for work in progress
        for f in sorted(list(os.listdir(self.path))):
            #filter to message files only
            if fnmatch.fnmatch(f,'*.wip'):
                
                wip_file_path = os.path.join(self.path,f)
                
                with open(wip_file_path,'r') as hbf:
                    message_dict = json.load(hbf)
                    
                message_header = message_dict['header']
                
                _created_datetime = self._message_created_datetime(message_header)
                
                if _latest_wip_created_datetime is None or _latest_wip_created_datetime < _created_datetime:
                    _latest_wip_created_datetime = _created_datetime
                    _latest_wip              = message_dict
                                
        if _latest_wip is not None: 
        
            #See if we can get an estimate for the work in progress
            #Then tinker with the wip header to incorporate this information
            for f in sorted(list(os.listdir(self.path))):
                #filter to the matching estimate file only
                if fnmatch.fnmatch(f,'*_{}.estimate'.format(self._uuid_string_to_uuid_file_string(_latest_wip['header']['uuid']))) :
                    estimate_file_path = os.path.join(self.path,f)

                    with open(estimate_file_path,'r') as hbf:
                        _latest_estimate = json.load(hbf)
                        
                    _latest_wip['header']['createdUTCTimestamp']  = _latest_estimate['header']['createdUTCTimestamp'] 
                    _latest_wip['header']['nextMessageUTCOffset'] = _latest_estimate['header']['nextMessageUTCOffset'] 
        
        return _latest_wip
    
    
    def monitor_producer(self,next_ms=600000):
        '''
        Check that the producer is in good health
        Send an emergency email and call the associated hooks
        
        '''
        
        #Check that the producer is in good health
        
        #Are there heartbeats? 
        latest_heartbeat = self._get_latest_heartbeat(heartbeat_type='producer')
        #latest_work_produced = self._get_latest_work_produced()
        
        if latest_heartbeat is None:
            log.warning('Producer is dead - no heartbeat found')
            raise mpex.MonitoringError('Producer is dead - no heartbeat found')
            
        elif self._timeout_is_expired(latest_heartbeat['header']):
            try:
                debug_string = latest_heartbeat['header']['debugString']
            except KeyError:
                debug_string = ''
            
            log.warning('Producer is dead - heart stopped beating at {} ({})'.format(self._message_expiry_datetime(latest_heartbeat['header']),debug_string))
            raise mpex.MonitoringError('Producer is dead - heart stopped beating at {}'.format(self._message_expiry_datetime(latest_heartbeat['header'])))
            
        else:    
            log.info('Producer is well - heart beat expiry is {}'.format(self._message_expiry_datetime(latest_heartbeat['header'])))
            pass
            
        #Is Producer expecting to produce work?
        
        
        #Get the latest work - check that it hasn't timed out
        
        pass
    
    def monitor_consumer(self,next_ms=600000,allowable_backlog_length=None):
        '''Check that the consumer is in good health
        
        Send an emergency email and call the associated hooks
        
        '''
        
        #Check that the consumer is in good health
        #Are there heartbeats? 
        latest_heartbeat        = self._get_latest_heartbeat(heartbeat_type='consumer')
        latest_work_in_progress = self._get_latest_work_in_progress()
        #backlog_number          = self._get_total_backlog_count()
        #backlog_time            = self._get_total_backlog_time()
        
        
        heart_is_beating = latest_heartbeat is not None and not self._timeout_is_expired(latest_heartbeat['header'])
            
        work_is_progressing = latest_work_in_progress is not None and not self._timeout_is_expired(latest_work_in_progress['header'])
        
        if latest_heartbeat is None and latest_work_in_progress is None:
            log.warning('Consumer is dead - no heartbeat or wip found')
                
        elif not (heart_is_beating or work_is_progressing):
            if not heart_is_beating and latest_heartbeat is not None:
                try:
                    debug_string = latest_heartbeat['header']['debugString']
                except KeyError:
                    debug_string = ''
                    
                log.warning('Consumer is dead - heart stopped beating at {} ({})'.format(self._message_expiry_datetime(latest_heartbeat['header']),debug_string))
            if not work_is_progressing and latest_work_in_progress is not None:
                log.warning('Consumer is dead - wip overran at {}'.format(self._message_expiry_datetime(latest_work_in_progress['header'])))
            
        else:    
            if not latest_heartbeat is None:
                log.info('Consumer is well - heart beat expiry is {}'.format(self._message_expiry_datetime(latest_heartbeat['header'])))
            if not latest_work_in_progress is None:
                log.info('Consumer is well - wip expiry is {}'.format(self._message_expiry_datetime(latest_work_in_progress['header'])))
        
        #Is consumer expecting to produce work?

    def peek(self,msg_id):
        '''Peeking at each message allows a monitor to determine the state of the queue, so that it can decide whether to take emergency action
        '''
    
        pass
 
    def task_done(self,obj):
    
        uuid_string = None
        try:
            uuid_string = obj['uuid']
            
        except KeyError:    
            uuid_string = obj['header']['uuid']
            
        except (AttributeError,TypeError):
            uuid_string = obj
        
        if uuid_string is None:
            raise ValueError('obj parameter in task_done must be a dictionary containing a header, or uuid key, or a uuid.uuid1() instance or string representing a uuid1')
        
        uuid_string = self._uuid_string_to_uuid_file_string(uuid_string)
            
    
        #When a task is done
        for f in sorted(list(os.listdir(self.path))):
            #filter to message files only
            if fnmatch.fnmatch(f,'*_{}.wip'.format(uuid_string)) or fnmatch.fnmatch(f,'*_{}.estimate'.format(uuid_string)) :
                wip_file_path = os.path.join(self.path,f)
    
                try:
                    os.remove(wip_file_path)
                except FileNotFoundError:
                    continue
                    
                    
        #Do a heartbeat
        self.heartbeat(type='consumer', next_ms=None)
        
        
    def mark_all_work_done(self):
        '''Mark all of the work in the queue as done, for the purposes of pickups
        
        We would need to mark all the work as done at once if it is done as a logical whole
        This function calls task_done() on all of the messages left in the queue 
        '''
        
        #Get all of the messages left in the queue and mark them as done
        for msg in self:
            self.task_done(msg)
        
    
    def close(self):
        '''As a producer, close the queue for new inputs, and place appropriate DONE messages on the queue, so that consumers know that all work has been done, and they can stop.'''
            
        ##Put DONE messages on the queue
        for _ in range(self.number_of_workers):
            log.debug('Putting DONE message on RobustQueue '+self.path)
            self._put_done()
        
        pass
        
    def fail(self):
        '''Close the queue for new inputs, and place appropriate FAILED messages on the queue, so that consumers know that an upstream process has failed, and they can stop.'''
        
        #Put FAILED messages on the queue
        for _ in range(self.number_of_workers):
            log.error('Putting FAILED message on RobustQueue '+self.path)
            self._put_failed()
            
        pass
    
    def dispose(self):
        '''As a consumer, stop using the queue. Currently this method does nothing, and merely keeps the queue interface aligned, but may be implemented in future if it is needed for orderly queue shut down.'''
        
        #if self.done_file_path and self.done_file:
        #    try:
        #        log.debug('Closing Done File: '+str(self.done_file_path))
        #        self.done_file.close()
        #    except Exception:
        #        pass
        pass
        
                
    #Some cunning code to allow the queue to be used like an iterable (i.e. in a for loop)
    #The class handles the DONE and FAILURE messages internally which reduces boilerplate calling code
    
    def __iter__(self):
        return self

    def __next__(self): # Python 3 only
    
        log.debug('__next__ Getting message')
        msg=self.get()
        
        if  msg==FAILED:
            #log.error('Got FAILED message on PersistentQueue '+self.pickup_file_prefix)
            self.dispose()  
            raise mpex.UpstreamFailureError('Upstream process failed. FAILED message received via Queue')
            
        #When DONE (0) stop
        if  msg==DONE:
            #log.debug('Got DONE message on PersistentQueue '+self.pickup_file_prefix)
            self.dispose()  
            raise StopIteration    
        else:
            log.debug('__next__ Got message '+str(msg))
        
            return msg
        
        return None

    #Pickling code. Override the default pickling code to remove the opened files which are recording our work. We don't need to pass them around anyway, since each file will have its own PID
    #and that file should only be updated by the process with that PID
    def __getstate__(self):
        ##copy the dictionary of attributes and methods, so that we don't alter the original PersistentQueue object when pickling
        #d = dict(self.__dict__)
        ##Don't pickle open work requested or work completed files
        ##not all queues will have these files open, as they only get opened when we put work on the queue
        #try:
        #    del d['_done_file']
        #except KeyError:
        #    pass
        #    
        #try:
        #    del d['_put_file']
        #except KeyError:
        #    pass
        #
        #return d
        
        pass
        
    def __setstate__(self,d):
        #self.__dict__.update(d)
        ##Start with None in the attributes for the work requested and completed files. When we call put() or task_done() the files will be created and opened
        #self._done_file=None
        #self._put_file=None
        
        pass

class _FolderQueue(object):
    '''Base class for an abstraction over a folder that is being used for work passing between processes.
    
    Unlike a PersistentQueue, it is assumed that the queue is cross server, and has relatively slow response times, and can have large messages and data written to it
    Unlike a RobustQueue, this queue passes data files directly and not specially formatted messages in files. A strict renaming mechanism is used to ensure queuelike behaviour

    Get returns a file name (of the renamed file - ready for use) or DONE or FAILED
    '''
    
    def __init__(self,path,message_extension='.tsv',task_done_directory=None,sorting_function=lambda x:x):
        '''
        :param path: Directory which files for this process get put into
        :param message_extension: Files with this extension will be treated as messages
        :param task_done_directory: Completed files will be moved to his directory when task_done is called on the message (i.e. called with the file_path returned by .get())
        :param sorting_function: function used sorting the file names of the files in the queue. This function will be applied to each file on the queue and must return a string. The strings will then be sorted in order to determine which file is processed first. Remember that files not on the queue yet will not be involved in the sort. The sorting function must catch errors and return None if there has been an error. The default is to return the same filename that was passed in, resulting in files being processed in name order.
        '''
        self.path                       = path
        
        self._timeformat                = '%Y%m%d_%H%M%S_%f'
        self._hostname                  = socket.gethostname()
        self._fqdn                      = socket.getfqdn()
        import hashlib
        self._fqdn_hash                 = str(int(hashlib.sha256(self._fqdn.encode('utf-8')).hexdigest(), 16) % 10**10).zfill(10)
        self._pid                       = str(os.getpid()).zfill(6)
        self._login                     = os.getlogin()
        self._uuid                      = uuid.uuid1()
         
        self.message_extension          = message_extension.replace('.','')
        
        self._sorting_function           = sorting_function
        try:
            os.makedirs(self.path)
        except FileExistsError:
            pass
        
        #Keep track of what producers exist, so that when all producers are finished we can stop
        self.producers = {}
        
        self.have_put_a_helo_file_before = False

        self.files_already_dealt_with = {}

    #def _uuid_string_to_uuid_file_string(self,uuid_string):
    #    return uuid_string.replace('-','_')
    
    def sorting_function(self, filename):
        '''Apply this queue's sorting function to the filename, returning the string that will be sorted in order to determine which file is processed first'''
        try:
            return self._sorting_function(filename)
        except Exception:
            return ""
    
    def _datetime_string(self):
        return datetime.datetime.utcnow().strftime(self._timeformat)
    
    def _filepath(self, msg,extension=None):
        if extension:
            return os.path.join(self.path,os.path.basename(msg))+'.'+extension
        else:
            return os.path.join(self.path,os.path.basename(msg))
    
    def _uuid_string(self):
        return str(self._uuid)
        
    def original_filename_from_wip(self,msg):
        '''The original name of a work-in-progress file for a given file name on this queue. I.e. The name of the file before it was picked up for processing.
        
        :param msg: File name or file path of the message file, after it was renamed to a work-in-progress file
        '''
        _filename, _extension = os.path.splitext(os.path.basename(msg))
        length_of_prefix_info = len(self._wip_info_prefix)
        return  os.path.join(self.path,_filename[length_of_prefix_info:]+'.'+self.message_extension)
        
    def wip_filename(self,msg):
        '''The path to a work-in-progress file for a given file name on the queue. 
        
        :param msg: Original file name or file path of the message file, before it is renamed to a work-in-progress file
        '''
        _filename, _extension = os.path.splitext(os.path.basename(msg))
        return os.path.join(self.path,self._wip_info_prefix+_filename+'.wip')
    
    @property
    def _wip_info_prefix(self):
        return str(self._pid)+'_'+self._fqdn_hash+'_'
    def dispose(self):
        '''As a consumer, stop using the queue. Currently this method does nothing, and merely keeps the queue interface aligned, but may be implemented in future if it is needed for orderly queue shut down.'''
        
        #if self.done_file_path and self.done_file:
        #    try:
        #        log.debug('Closing Done File: '+str(self.done_file_path))
        #        self.done_file.close()
        #    except Exception:
        #        pass
        pass
        
    #Some cunning code to allow the queue to be used like an iterable (i.e. in a for loop)
    #The class handles the DONE and FAILURE messages internally which reduces boilerplate calling code
    
    def __iter__(self):
        return self

    def __next__(self): # Python 3 only
    
        log.debug('__next__ Getting message')
        msg=self.get()
        
        if  msg==FAILED:
            #log.error('Got FAILED message on PersistentQueue '+self.pickup_file_prefix)
            self.dispose()  
            raise mpex.UpstreamFailureError('Upstream process failed. FAILED message received via Queue')
            
        #When DONE (0) stop
        if  msg==DONE:
            #log.debug('Got DONE message on PersistentQueue '+self.pickup_file_prefix)
            self.dispose()  
            raise StopIteration    
        else:
            log.debug('__next__ Got message '+str(msg))
        
            return msg
        
        return None

    #Pickling code. Override the default pickling code to remove the opened files which are recording our work. We don't need to pass them around anyway, since each file will have its own PID
    #and that file should only be updated by the process with that PID
    def __getstate__(self):
        ##copy the dictionary of attributes and methods, so that we don't alter the original DirectoryQueue object when pickling
        #d = dict(self.__dict__)
        ##Don't pickle open work requested or work completed files
        ##not all queues will have these files open, as they only get opened when we put work on the queue
        #try:
        #    del d['_done_file']
        #except KeyError:
        #    pass
        #    
        #try:
        #    del d['_put_file']
        #except KeyError:
        #    pass
        #
        #return d
        
        pass
        
    def __setstate__(self,d):
        #self.__dict__.update(d)
        ##Start with None in the attributes for the work requested and completed files. When we call put() or task_done() the files will be created and opened
        #self._done_file=None
        #self._put_file=None
        
        pass

class WritableFolderQueue(_FolderQueue):
    '''A queue which uses a folder (directory) to store its messages.
    This queue is designed to be used in conjunction with a ReadableFolderQueue or ReadableGroupedFileFolderQueue.
    This version of the queue is used by the process putting work on to the queue.
    During processing, or after a failure, it is possible to inspect the directories that the data files reside in, to determine the state of a process which uses the queues.
    Messages are the data files that need to be processed.
    Queue like behaviour is maintained by renaming of files when getting them off of the queue.
    '''
    def __init__(self,path,message_extension='.tsv',task_done_directory=None):
        '''
        Create an instance of a WritableFolderQueue 
        
        :param path: Directory where files put onto the queue, and control messages will be stored. Must match the directory specified in related ReadableFolderQueue objects
        :param message_extension: Files with this extension placed into the queue will be considered messages to be processed
        :param task_done_directory: A directory where files are moved to when task_done() is called on a processed file. If this directory is not set, then processed files must be moved by teh calling process.
        '''
    
    
        #call the base class initialiser       
        super().__init__( path = path
                        ,message_extension=message_extension
                        ,task_done_directory=task_done_directory
                       )

        self._put_helo()
        
    def purge(self):
        '''Remove all messages and files from the queue. Files and directories in the queue folder will be deleted. Permanently.'''
        for f in os.listdir(self.path):
            if os.path.isfile(os.path.join(self.path,f)):
                os.remove(os.path.join(self.path,f))
            else:
                os.rmdir(os.path.join(self.path,f))

        log.info("Purged queue {}".format(self.path))
            
            
    def purge_control_messages(self):
        '''Remove old control messages from previous runs'''
        for f in os.listdir(self.path):
            #filter to helo files to see if there are producers 
            if fnmatch.fnmatch(f,'*.helo') or fnmatch.fnmatch(f,'*.done') or fnmatch.fnmatch(f,'*.failed'):
                os.remove(os.path.join(self.path,f))
    
    def reset_processing_files(self):
        '''Reset partially processed files to their original names'''
        for f in os.listdir(self.path):
            if fnmatch.fnmatch(f,"*.wip"):
                #Rename the file back to its original name
                os.rename(os.path.join(self.path,f),self.original_filename_from_wip(f))
    
    def reset(self):
        '''Remove old control messages from previous runs, reset partially processed files to their original names'''
        self.purge_control_messages()
        self.reset_processing_files()
        #self._put_helo()

        log.info("Reset queue {}".format(self.path))

        
    def put(self,msg,copy=False):
        '''Put a message on the queue. The message should be a valid path to file. The file will be renamed and moved or copied into the queue folder.
        
        :param msg: The source file path. The file will be put onto the queue with some added metadata in the filename
        :param copy: the default behaviour is to move the file into the directory queue. If copy is True, then the file will be copied in, and the original left in place.
        '''
        
        #Announce producer's existence first time a message is put on the queue
        if not self.have_put_a_helo_file_before:
            self._put_helo()
        
        _datetime_string = self._datetime_string()
        
        if os.path.exists(self._filepath(msg)):
            raise FileExistsError('Cannot put file {} into queue folder because a file with the target name {} exists already'.format(msg,self._filepath(msg)))
        
        if copy:
            os.rename(msg,msg+'.'+str(self._pid)+'copying1')
            shutil.copy(msg+'.'+str(self._pid)+'copying1',self._filepath(msg)+'.'+str(self._pid)+'copying2')
            os.rename(msg+'.'+str(self._pid)+'copying1',msg)
        else:
            os.rename(msg,msg+'.'+str(self._pid)+'copying1')
            shutil.move(msg+'.'+str(self._pid)+'copying1',self._filepath(msg)+'.'+str(self._pid)+'copying2')

        if os.path.exists(self._filepath(msg)):
            raise FileExistsError('Cannot put file {} into queue folder because a file with the target name {} exists already'.format(msg,self._filepath(msg)))
        
        os.rename(self._filepath(msg)+'.'+str(self._pid)+'copying2',self._filepath(msg))
        #if we couldn't do the final rename log an error and raise an appropriate error

    def _put_helo(self):
        '''
        '''
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        
        _temp_extension  = 'temphelo'
        _extension       = 'helo'
        
        helo_filepath = self._filepath(_datetime_string+'__'+str(self._pid),extension=_temp_extension) 
        #Create the file with a temporary extension, then move (rename) to make the file write transactional
        with open(helo_filepath,'w') as f:
            json.dump(obj={'header':{
                                     'type':'helo'
                                    ,'createdUTCTimestamp':_datetime_string
                                    ,'uuid':_uuid_string
                                    ,'createdBy':self._login
                                    ,'hostName':self._hostname
                                    ,'machineFQDN':self._fqdn
                                    ,'pid':self._pid
                                    }}
                        ,fp=f
                        ,indent=2)
    
        shutil.move(self._filepath(_datetime_string+'__'+str(self._pid),extension=_temp_extension),self._filepath(_datetime_string+'__'+str(self._pid),extension=_extension))

        self.have_put_a_helo_file_before = True

        log.info("Put helo message on queue {}".format(self._filepath(_datetime_string+'__'+str(self._pid),extension=_extension)))

    def _put_done(self):
        '''
        '''
        #Announce producer's existence first time a message is put on the queue
        if not self.have_put_a_helo_file_before:
            self._put_helo()
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        
        _temp_extension  = 'tempdone'
        _extension       = 'done'
        
        done_filepath = self._filepath(_datetime_string+'__'+str(self._pid),extension=_temp_extension) 
        #Create the file with a temporary extension, then move (rename) to make the file write transactional
        with open(done_filepath,'w') as f:
            json.dump(obj={'header':{
                                     'type':'done'
                                    ,'createdUTCTimestamp':_datetime_string
                                    ,'uuid':_uuid_string
                                    ,'createdBy':self._login
                                    ,'hostName':self._hostname
                                    ,'machineFQDN':self._fqdn
                                    ,'pid':self._pid
                                    }}
                        ,fp=f
                        ,indent=2)
    
        shutil.move(self._filepath(_datetime_string+'__'+str(self._pid),extension=_temp_extension),self._filepath(_datetime_string+'__'+str(self._pid),extension=_extension))

        log.info("Put done message on queue {}".format(self._filepath(_datetime_string+'__'+str(self._pid),extension=_extension)))
    
    def _put_failed(self):
        '''
        '''
        
        _datetime_string = self._datetime_string()
        _uuid_string     = self._uuid_string()    
        
        _temp_extension  = 'tempfail'
        _extension       = 'failed'
        print()
        failed_filepath = self._filepath(_datetime_string+'__'+str(self._pid),_temp_extension) 
        
        #Create the file with a temporary extension, then move (rename) to make the file write transactional
        with open(failed_filepath,'w') as f:
            json.dump(obj={'header':{
                                     'type':'failed'
                                    ,'createdUTCTimestamp':_datetime_string
                                    ,'uuid':_uuid_string
                                    ,'hostName':self._hostname
                                    ,'machineFQDN':self._fqdn
                                    ,'pid':self._pid
                                    }}
                        ,fp=f
                        ,indent=2)
    
        shutil.move(self._filepath(_datetime_string+'__'+str(self._pid),_temp_extension),self._filepath(_datetime_string+'__'+str(self._pid),_extension))

        log.info("Put fail message on queue {}".format(self._filepath(_datetime_string+'__'+str(self._pid),extension=_extension)))


    
    def close(self):
        '''As a producer, close the queue for new inputs, and place appropriate DONE messages on the queue, so that consumers know that all work has been done, and they can stop.'''
            
        ##Put DONE messages on the queue
        log.debug('Putting DONE message on FolderQueue '+self.path)
        self._put_done()
        
        pass
        
    def fail(self):
        '''Close the queue for new inputs, and place appropriate FAILED messages on the queue, so that consumers know that an upstream process has failed, and they can stop.'''
        
        #Put FAILED messages on the queue
        log.error('Putting FAILED message on FolderQueue '+self.path)
        self._put_failed()
            
        pass
    
class ReadableFolderQueue(_FolderQueue):
    '''A queue which uses a folder (directory) to store its messages.
    This queue is designed to be used in conjunction with a WritableFolderQueue.
    This version of the queue is used by the process getting work off of the queue.
    During processing, or after a failure, it is possible to inspect the directories that the data files reside in, to determine the state of a process which uses the queues.
    Messages are the data files that need to be processed.
    Queue like behaviour is maintained by renaming of files when getting them off of the queue.
    '''
    
    def get(self,timeout=None):
        '''
        Return the file name of the next file to process.
        The message file will be renamed and remain in the folder, and the new name will be returned.
        
        :param timeout: Time in milliseconds to wait for a message on an empty queue before raising an Empty exception.
        '''
        start_polling_datetime = datetime.datetime.utcnow()
        
        _extension = self.message_extension
        
        #TODO
        #Check for files which are work in progress on them. If the wip has timed out (after 1000 ms)
        #then set it back the way it was in a use it or lose it fashion
        #This stops unprocessed messages hanging when a process which has taken dibs on a file dies before it can process it
        
        if timeout is None:
            #Timeout after 10 years - or so
            timeout = 1000*60*60*24*365*10
        
        if timeout < 1000:
            #Don't sleep longer than the timeout - convert timeout into seconds and divide by 10
            sleep_seconds = timeout/10000
        else:
            #Poll every second
            sleep_seconds = 1
        
        end_polling_datetime = start_polling_datetime + datetime.timedelta(milliseconds = timeout)

        while True:
            
            
            for f in os.listdir(self.path):
        
                #filter to helo files to see if there are producers 
                if fnmatch.fnmatch(f,'*.helo'):
                    
                    #Just move on to the next file if we've dealt with this file before
                    try:
                        self.files_already_dealt_with[f]
                        continue
                    except KeyError:
                        pass
                        
                    try:
                        #Read the whole of the helo file, and work out who the producer is
                        
                        try:
                            with open(os.path.join(self.path,f),'r') as openfile:
                                helo_contents = json.load(openfile)
                            #print('Read json for {}'.format(f))
                                
                        except json.decoder.JSONDecodeError:
                            #not a standard helo file - possibly handmade or corrupt
                            #remove it and return done
                            #os.remove(os.path.join(self.path,f))
                            return FAILED
                        
                        try:
                            
                            machineFQDN = helo_contents['header']['machineFQDN']
                            pid = helo_contents['header']['pid']
                            uuid = helo_contents['header']['uuid']
                        except KeyError:
                            #corrupt Helo file
                            #remove it and return FAILED
                            #os.remove(os.path.join(self.path,f))
                            return FAILED
                        
                        try:
                            self.producers[(machineFQDN,pid,uuid)]
                        except KeyError:    
                            self.producers[(machineFQDN,pid,uuid)] = True
                            
                        self.files_already_dealt_with[f] = f
                        continue

                    except FileNotFoundError:
                        continue        
                
                #filter to failed files to see if there has been a problem with the queue
                if fnmatch.fnmatch(f,'*.failed'):
                    return FAILED
                        
            for f in sorted(list(os.listdir(self.path)),key = self.sorting_function):
                
                #log.info('Found file {}'.format(f))
                #filter to message files only
                _matchstring = '*.{}'.format(_extension).replace('..','.')
                #log.info('Matching on pattern {}'.format(_matchstring))
                
                if fnmatch.fnmatch(f,_matchstring):
                    #log.info('Matched file {}'.format(f))
                    message_file_path = os.path.join(self.path,f)
        
                    #put dibs on the message by renaming file with own unique fqdn and pid before using it
                    wip_file_path = self.wip_filename(message_file_path)
                    try:
                        os.rename(message_file_path,wip_file_path)
                    except Exception:
                    #    #If we couldn't put dibs on the file it may have been grabbed by another process - look for the next message
                        continue
        
                    #Sleep for 10 milliseconds
                    time.sleep(0.01)
                    
                    #It seems that sometimes the rename doesn't fail, if another process is moving the file simultaneously
                    #Double check the moved file exists
                    if not os.path.isfile(wip_file_path):
                        #If moved file doesn't exist, then something grabbed it - look for another file
                        continue
                    
                    #log.info('Returning {}'.format(wip_file_path))
                    
                    return wip_file_path
            
            for f in os.listdir(self.path):
            
                try:
                    self.files_already_dealt_with[f]
                    continue
                except KeyError:
                    pass
            
                
                
                #filter to done files to see if there is no more work to do
                if fnmatch.fnmatch(f,'*.done'):
                    #print('found done {}'.format(f))
                    try:
                        #Remove the equivalent helo file:
                        #find out who produced the done file by checking self.producers
                        #remove their helo file, to signal they are now offline, to anyone who has been watching (i.e. parallel queues to this one)
                        try:
                            with open(os.path.join(self.path,f),'r') as openfile:
                                done_contents = json.load(openfile)
                        except json.decoder.JSONDecodeError:
                            #not a standard done file - possibly handmade or corrupt
                            #remove it and return done
                            #os.remove(os.path.join(self.path,f))
                            return DONE
                        
                        try:
                            machineFQDN = done_contents['header']['machineFQDN']
                            pid = done_contents['header']['pid']
                            uuid = done_contents['header']['uuid']
                        except KeyError:
                            #corrupt Done file
                            #remove it and return done
                            #os.remove(os.path.join(self.path,f))
                            return DONE
                        
                        #lookup the equivalent helo file
                        try:
                            #print('looking for helo {},{},{}'.format(machineFQDN,pid,uuid))
                    
                            self.producers[(machineFQDN,pid,uuid)] = False
                            #print('found helo {},{},{}'.format(machineFQDN,pid,uuid))
                    
                        except KeyError:
                            self.files_already_dealt_with[f] = f
                            continue
                        
                        
                        #print('Removing helo file {}'.format(helo_file_path))
                    
                        #Remove the helo file
                        #Now consumers will know that a producer they have seen before is done
                        #os.remove(helo_file_path)
                        #print('Removed helo file {}'.format(f))
                        self.files_already_dealt_with[f] = f
                            
                        continue
                    except FileNotFoundError:
                        continue
                        

            
            #if there are no producers, and there have been producers in the past, then return DONE
            #otherwise carry on (i.e. sleep)
            #If files have been put in place manually, then there will be no helo files
            if len(self.producers) > 0 and not any(self.producers.values()) :
                return DONE
            
            #If there are no messages, sleep, and then poll again until the timeout
            
            if datetime.datetime.utcnow() < end_polling_datetime:
                #log.info("Didn't find a message, sleeping")            
        
                #Sleep for a second, then do the next loop
                time.sleep(sleep_seconds)
            else:
                #Raise Queue.Empty if there is a timeout - this is standard behaviour for a queue
        
                raise qq.Empty('DirectoryQueue on path {} had no messages within the timeout period {} milliseconds'.format(self.path,timeout))
    
    #def peek(self):
    #    '''Peeking at each message allows a monitor to determine the state of the queue, so that it can decide whether to take emergency action
    #    '''
    # 
    #    pass
 
    def task_done(self,obj):
        '''Mark a completed task as done, by removing the work in progress file
        
        :param obj: a dictionary containing a header, or uuid key, or a uuid.uuid1() instance or string representing a uuid1, refering to a message on the queue
        '''    
        uuid_string = None
        try:
            uuid_string = obj['uuid']
            
        except KeyError:    
            uuid_string = obj['header']['uuid']
            
        except (AttributeError,TypeError):
            uuid_string = obj
        
        if uuid_string is None:
            raise ValueError('obj parameter in task_done must be a dictionary containing a header, or uuid key, or a uuid.uuid1() instance or string representing a uuid1')
        
        uuid_string = self._uuid_string_to_uuid_file_string(uuid_string)
            
    
        #When a task is done
        for f in sorted(list(os.listdir(self.path))):
            #filter to message files only
            if fnmatch.fnmatch(f,'*_{}.wip'.format(uuid_string)) or fnmatch.fnmatch(f,'*_{}.estimate'.format(uuid_string)) :
                wip_file_path = os.path.join(self.path,f)
    
                try:
                    os.remove(wip_file_path)
                except FileNotFoundError:
                    continue
        
    def mark_all_work_done(self):
        '''Mark all of the work in the queue as done, for the purposes of pickups
        
        We would need to mark all the work as done at once if the work should be done as a logical whole.
        This function calls task_done() on all of the messages left in the queue 
        '''
        
        #Get all of the messages left in the queue and mark them as done
        for msg in self:
            self.task_done(msg)
        
class ReadableGroupedFileFolderQueue(ReadableFolderQueue):
    '''An abstraction over a folder that is being used for work passing between processes.
    
    The functionality it has beyond that of a ReadableFolderQueue is that it returns sets of files.
    Sometimes the logical unit of work is a set of files (for instance covering all of the units of a business) and our process will need to wait until all of the files have been created before processing that list of files at once.
    
    Get returns a list of file names (i.e. of the renamed files - ready for use) or DONE or FAILED
    '''
    
    def __init__(self,path,message_extension='.tsv',task_done_directory=None,grouping_function=lambda x:x, item_function = lambda x:x,list_of_items_in_group=None):
        '''
        Create an instance of a ReadableGroupedFileFolderQueue
        
        :param path: Directory which files for this process get put into
        :param message_extension: Files with this extension will be treated as messages
        :param number_of_workers: The number of workers who will be taking messages off of this queue. By knowing the number of workers we can put enough DONE messages on the queue for them all 
        :param grouping_function: A function, that when applied to a filename will get the string that represents the group of files
        :param item_function: A function, that when applied to a filename will get the string that represents the item in the group. This item must be present in the list of items that is parameter list_of_items_in_set
        :param list_of_items_in_group: a list of strings with all of the items that make up a complete group of files. When get() is called the Queue will be searched for a full set of files (that return the same string from the grouping function and the fulle set of strings using the item function)
        :param task_done_directory: Completed files will be moved to his directory when task_done is called on the message (i.e. called with the file_path returned by .get())
        '''
        #call the base class initialiser       
        super().__init__( path = path
                        ,message_extension=message_extension
                        ,task_done_directory=task_done_directory
                       )
        
        if list_of_items_in_group is None:
            list_of_items_in_group = []
            
        self.grouping_function      = grouping_function
        self.item_function          = item_function
        self.set_of_items_in_group = set(list_of_items_in_group)
        
        #Dictionary holding group string as key, and list of files as 
        self.groups = {}
        #Files that have been shuffled into groups. Having a dictionary allows us to avoid constantly reprocessing the same files
        self.considered_files = {}
        
    def get(self,timeout=None):
        '''Return the file names of the next group of files to process in a list.
        The message files will be renamed and remain in the folder, and the new names will be returned in the list.
        
        :param timeout: Time in milliseconds to wait for a message on an empty queue before raising an Empty exception.
        
        '''
        start_polling_datetime = datetime.datetime.utcnow()
        
        _extension = self.message_extension
        
        #TODO
        #Check for files which are work in progress on them. If the wip has timed out (after 1000 ms)
        #then set it back the way it was in a use it or lose it fashion
        #This stops unprocessed messages hanging when a process which has taken dibs on a file dies before it can process it
        
        if timeout is None:
            #Timeout after 10 years - or so
            timeout = 1000*60*60*24*365*10
        
        if timeout < 1000:
            #Don't sleep longer than the timeout - convert timeout into seconds and divide by 10
            sleep_seconds = timeout/10000
        else:
            #Poll every second
            sleep_seconds = 1
        
        end_polling_datetime = start_polling_datetime + datetime.timedelta(milliseconds = timeout)

        while True:
        
            
            for f in os.listdir(self.path):
        
                #filter to helo files to see if there are producers 
                if fnmatch.fnmatch(f,'*.helo'):
                    
                    #Just move on to the next file if we've dealt with this file before
                    try:
                        self.files_already_dealt_with[f]
                        continue
                    except KeyError:
                        pass
                        
                    try:
                        #Read the whole of the helo file, and work out who the producer is
                        
                        try:
                            with open(os.path.join(self.path,f),'r') as openfile:
                                helo_contents = json.load(openfile)
                            #print('Read json for {}'.format(f))
                                
                        except json.decoder.JSONDecodeError:
                            #not a standard helo file - possibly handmade or corrupt
                            #remove it and return done
                            #os.remove(os.path.join(self.path,f))
                            return FAILED
                        
                        try:
                            
                            machineFQDN = helo_contents['header']['machineFQDN']
                            pid = helo_contents['header']['pid']
                            uuid = helo_contents['header']['uuid']
                        except KeyError:
                            #corrupt Helo file
                            #remove it and return FAILED
                            #os.remove(os.path.join(self.path,f))
                            return FAILED
                        
                        try:
                            self.producers[(machineFQDN,pid,uuid)]
                        except KeyError:    
                            self.producers[(machineFQDN,pid,uuid)] = True
                            
                        self.files_already_dealt_with[f] = f
                        continue

                    except FileNotFoundError:
                        continue        
                
                #filter to failed files to see if there has been a problem with the queue
                if fnmatch.fnmatch(f,'*.failed'):
                    return FAILED
                        
            #Get the earliest message on the queue
            for f in sorted(list(os.listdir(self.path))):
            
                #First, check if we've considered this file before - if so carry on, we don't need to process it again
                
                try:
                    self.considered_files[f]
                    #If we find the file, continue on to the next file
                    continue
                except KeyError:
                    #We are considering the file now, so add it to our dictionary
                    self.considered_files[f] = f
    
                #log.info('Found file {}'.format(f))
                #filter to message files only
                _matchstring = '*.{}'.format(_extension).replace('..','.')
                #log.info('Matching on pattern {}'.format(_matchstring))
                
                if fnmatch.fnmatch(f,_matchstring):
                    #log.info('Matched file {}'.format(f))
                    message_file_path = os.path.join(self.path,f)
        
                    #get the group that the file belongs to
                    group = self.grouping_function(f)
                    item  = self.item_function(f)
                    if item in self.set_of_items_in_group:
                        #Lookup or create the group that this file belongs to
                        #Typically the group would be a given business date - so we would be loading a number of items (e.g. business units) 
                        #against each group (i.e. business date)
                        try:
                            files_in_group = self.groups[group]
                            files_in_group.append(f)
                        except KeyError:
                            files_in_group = [f]
                            self.groups[group] = files_in_group
                        
                        
                        
                        #Check if we have all items in the group. If not continue on to the next file
                        if not len(self.set_of_items_in_group) == len(files_in_group):
                            continue

                    #If we have got this far we have found a whole group of files 
                    #So put dibs on the messages in order (we must sort the files so that another process will attempt to put dibs on the same file we are trying to put dibs on)
                    #If we fail to put dibs on the first message then another process has grabbed this group of files. 
                    #If so, skip the rest of the files.
                    all_wip_file_paths = []
                    
                    for f in sorted(files_in_group):
                        message_file_path = os.path.join(self.path,f)
                        #put dibs on the message by renaming file with own unique fqdn and pid before using it
                        wip_file_path = self.wip_filename(message_file_path)
                        all_wip_file_paths.append(wip_file_path)
                        try:
                            os.rename(message_file_path,wip_file_path)
                        except Exception:
                            #If we couldn't put dibs on the file it may have been grabbed by another process 
                            break
                        
                        #Sleep for 10 milliseconds
                        time.sleep(0.01)
                        
                        #It seems that sometimes the rename doesn't fail, if another process is renaming the file simultaneously
                        #Double check the moved file exists
                        if not os.path.isfile(wip_file_path):
                            #If moved file doesn't exist, then another process grabbed it - give up
                            break
                            
                    if len(all_wip_file_paths) == len(self.set_of_items_in_group):
                        #Return a list of all of the file paths
                        return all_wip_file_paths
            
            for f in os.listdir(self.path):
            
                try:
                    self.files_already_dealt_with[f]
                    continue
                except KeyError:
                    pass
            
                #filter to done files to see if there is no more work to do
                if fnmatch.fnmatch(f,'*.done'):
                    #print('found done {}'.format(f))
                    try:
                        #Remove the equivalent helo file:
                        #find out who produced the done file by checking self.producers
                        #remove their helo file, to signal they are now offline, to anyone who has been watching (i.e. parallel queues to this one)
                        try:
                            with open(os.path.join(self.path,f),'r') as openfile:
                                done_contents = json.load(openfile)
                        except json.decoder.JSONDecodeError:
                            #not a standard done file - possibly handmade or corrupt
                            #remove it and return done
                            #os.remove(os.path.join(self.path,f))
                            return DONE
                        
                        try:
                            machineFQDN = done_contents['header']['machineFQDN']
                            pid = done_contents['header']['pid']
                            uuid = done_contents['header']['uuid']
                        except KeyError:
                            #corrupt Done file
                            #remove it and return done
                            #os.remove(os.path.join(self.path,f))
                            return DONE
                        
                        #lookup the producer file, and set the producer to False - i,e, done
                        self.producers[(machineFQDN,pid,uuid)] = False
                        self.files_already_dealt_with[f] = f
                            
                        continue
                    except FileNotFoundError:
                        continue
            
            #if there are no active producers, and there have been producers in the past, then return DONE
            #otherwise carry on (i.e. sleep)
            #If files have been put in place manually, then there will be no helo files
            #any(producers.values()) checks for active producers
            if len(self.producers) > 0 and not any(self.producers.values()) :
                return DONE
                
            #If there are no messages, sleep, and then poll again until the timeout
            
            if datetime.datetime.utcnow() < end_polling_datetime:
                #log.info("Didn't find a message, sleeping")            
        
                #Sleep for a second, then do the next loop
                time.sleep(sleep_seconds)
            else:
                #Raise Queue.Empty if there is a timeout - this is standard behaviour for a queue
        
                raise qq.Empty('DirectoryQueue on path {} had no messages within the timeout period {} milliseconds'.format(self.path,timeout))
    
     


#class _FolderQueueOperator(object):
#    '''Monitors a FolderQueue, to check that work is being produced and consumed on it, and that the processes using it are alive and well
#    
#    
#    '''
#
#
#    def __init__(self,monitor_inbox,email_outbox):
#        
#        pass
#
#    def on_no_pulse(self):
#        pass
#        
#    def _parse_message(self,msg):
#        pass
#        
#    def start():
#        pass
#        
#    def stop():
#        pass
#
#        
#class MonitorMixin(_FolderQueueOperator):
#    '''Monitors a FolderQueue, to check that work is being produced and consumed on it, and that the processes using it are alive and well
#    
#    Does no initialisation, so can be used as a mixin
#    
#    Must set 
#    
#    '''
#    
#    def __init__(self):
#        
#        pass
#
#    def set_queue(queue):
#        self._queue = queue
#    
#    def set_email_outbox(queue):
#        self._email_outbox = queue
#        
#    def on_no_pulse(self):
#        '''Hook for behaviour when there is no pulse on the monitored queue'''
#        pass
#        
#    def _parse_message(self,msg):
#        pass
#        
#    def start():
#        pass
#        
#    def stop():
#        pass
#
#class ProducerMixin(MonitorMixin):
#    '''Produces work for a queue, and monitors whether work is being consumed from it
#    '''
#
#    def __init__(self):
#        
#        pass 
#        
#    def start():
#        pass
#        
#    def stop():
#        pass    
#
#
#class ConsumerMixin(MonitorMixin):
#    '''Consumes work off a Folder queue
#    '''
#
#    def __init__(self,queue):
#        
#        pass
#        
#    def start():
#        pass
#        
#    def stop():
#        pass