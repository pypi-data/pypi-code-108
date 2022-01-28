# -*- coding: utf-8 -*-

import pickle
import os
from . import Domain

class SSHProfileDumper:
    def save(self, sshp):
        file_path = os.path.expanduser('~') + os.sep + '.sshman.pkl'

        with open(file_path, 'wb') as file_to_save:
            pickle.dump(sshp, file_to_save)

    def load(self):
        file_path = os.path.expanduser('~') + os.sep + '.sshman.pkl'
        sshp = None

        if not os.path.exists(file_path):
            open(file_path, 'w').close() 

        with open(file_path, 'rb') as file_to_load:
            if os.path.getsize(file_path) == 0 or not os.path.exists(file_path):
                return None
            else:
                try:
                    sshp = pickle.load(file_to_load)
                    return sshp
                except:
                    raise