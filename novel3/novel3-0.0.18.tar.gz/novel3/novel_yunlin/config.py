import json
from os.path import abspath


class Config:
    def __init__(self):
        self.novel_config = self.read_config()

    @classmethod
    def read_config(cls):
        with open('%s/../config/novel.json' % abspath(__file__), 'r', encoding='utf-8') as fp:
            return json.load(fp)
