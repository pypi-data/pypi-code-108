# -*- coding: UTF-8 -*-
# !/usr/bin/python
class Search:
    def __init__(self, path):
        super(Search, self).__init__()
        self.Answer = None
        with open(path) as data:
            self.Data = eval(data.read())

    def find(self, data=None, things=None):
        if data is None:
            data = self.Data
        answer = None
        try:
            answer = data[things[0]]
        except KeyError:
            print(things + ' not find')
        if type(answer) == dict:
            return self.find(answer, things[1:])
        else:
            return answer
