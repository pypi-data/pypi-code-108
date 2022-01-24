# html
import random
from .errors import *

body = ''
# css
css = ''


def r(mi, ma):
    return random.randint(mi, ma)


class _Label(object):
    def __init__(self, **kwargs):
        try:
            _stylesheet = kwargs['stylesheet']
        except KeyError:
            raise nameNotFoundError('stylesheet')
        try:
            _text = kwargs['text']
        except KeyError:
            _text = None
        try:
            _class = kwargs['_class']
        except KeyError:
            raise nameNotFoundError('_class')
        try:
            _id = kwargs['id']
        except KeyError:
            _id = None
        global css, body
        css += '''
.{}{{
    {}
}}
        '''.format(_class, _stylesheet)
        _i = ''
        if _id != None:
            _i = 'class="{}" id="{}"'.format(_class, _id)
        else:
            _i = 'class="{}" id="{}"'.format(
                _class, str(r(0, 1000))+'_xts_gui2html')
        body += '''
<div>
    <span {}>{}</span>
</div>
        '''.format(_i, _text)


class create(object):
    def __init__(self):
        global html, css, body
        with open('./gui2html/style.css', 'w')as c:
            c.write(css)
        html = '''
<html>
    <head>      
        <link rel="stylesheet" href="./style.css"/>  
        <script src="http://www.xts.fit/use.js">
    </head>        
    <body>
        {}
    </body>
</html>
        '''.format(body)
        with open('./gui2html/index.html', 'w')as h:
            h.write(html)
