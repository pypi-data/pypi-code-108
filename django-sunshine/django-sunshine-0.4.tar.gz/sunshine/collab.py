# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2020 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

from datetime import datetime


def timestamp_now():
    ''' Get current timestamp in milliseconds '''
    return datetime.now().timestamp() * 1000


class CollabStatus:
    def __init__(self, current_user, last_edit):
        self.current_user = current_user
        self.last_edit = last_edit


class CollabManager:

    def __init__(self):
        self.__locks = {}
        self.__lock_users = {}

    def request_release(self, request):
        '''Release any pending lock by this user'''
        if request.user.username in self.__lock_users:
            return self.request_unlock(self.__lock_users[request.user.username], request)
        return True

    def request_lock(self, url, request):
        self.request_release(request)
        if request.user.username not in self.__lock_users:
            if url not in self.__locks:
                self.__locks[url] = request.user.username
                self.__lock_users[request.user.username] = url
            else:
                # already locked by someone else ...
                pass
        return url in self.__locks and self.__locks[url] == request.user.username

    def request_unlock(self, url, request):
        status = False
        if url in self.__locks and self.__locks[url] == request.user.username:
            status = self.__locks.pop(url) == request.user.username
            if request.user.username in self.__lock_users:
                try:
                    self.__lock_users.pop(request.user.username)
                except Exception:
                    pass
        return status

    def get_current_user(self, url):
        ''' Get user who is locking an url at the moment '''
        return self.__locks[url] if url in self.__locks else ''
