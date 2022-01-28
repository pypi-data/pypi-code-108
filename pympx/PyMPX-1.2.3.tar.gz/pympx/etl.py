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
General ETL methods
'''

from pympx import exceptions as mpex
from pympx import logconfig
import os

log=logconfig.get_logger()
CompletelyLoggedError=mpex.CompletelyLoggedError

class WelcomePrompt():
    '''Prompt users about the service they are about to run, and allow them to stop it
    '''
        
    def __init__(self,message=None,message_file=None):
        '''
        Use either a message (string) or a file containing the message. If both are supplied the message parameter will be used.
        :param message: A string containing the message prompt to show the user
        :param message_file: A file containing the message prompt to show the user
        '''
        
        self.message=""
        
        if message_file and not message:
            self.message=self._read_message_from_file_path(message_file)
            
        #Message takes priority over file    
        if message:    
            self.message=message
        
        # Get the user to validate that they are happy to proceed
        self.current_user = self._get_current_user()
    
    def _display_welcome(self):
        print(self.message)
    
    def _get_current_user(self):
    # Get the user to validate that they are happy to proceed
        log.debug('Checking the current user in the os environment variables')
        current_user = os.environ['USERNAME']
        return current_user
        
    def _get_confirmation_input(self):
        return input('Enter "Y" to confirm you would like to proceed, or "N" to abort: ')
    
    def _break_on_disconfirmation(self,response,current_user):
        if response.lower()[0] == 'y':
            log.info('Confirmation provided; current user is "{}"'.format(current_user))
        else:
            log.info('Confirmation not provided; processed will be halted')
            raise KeyboardInterrupt('This process has been halted')
    
    def _read_message_from_file_path(self,path):
        # Display the prompt to screen
        log.debug('Opening welcome prompt: {}'.format(prompt_file))
        message=""
        with open(os.path.join(self.cwd, prompt_file), 'r') as f:
            message=self._read_message_from_open_file(f)
        
        # Log that the prompt file is being used
        log.verbose('Welcome prompt read from file: {}'.format(prompt_file))
        
        return message
        
    def _read_message_from_open_file(self,open_file):
        message=""
        for line in open_file:
            message += line
        
        return message
        
    def display(self):
        
        self._display_welcome()
        try:
            response = self._get_confirmation_input()
        except KeyboardInterrupt:
            raise KeyboardInterrupt('This process has been halted')    
            
        self._break_on_disconfirmation(response,self._get_current_user())
    
        return response;
    