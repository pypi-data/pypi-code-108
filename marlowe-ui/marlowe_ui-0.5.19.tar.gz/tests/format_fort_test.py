import sys
import os
sys.path.insert(0, os.path.join(__file__, '..', '..'))

import nose

import io

from marlowe_ui import format_fort

def test():
    strs = []
    for i in range(30):
        strs.append('x'*i)

    buf = io.StringIO()
    buf.write('_&TEST_')
    buf.write(format_fort.format_fort(strs))
    buf.write('/')

    ans = """\
_&TEST_,x,xx,xxx,xxxx,xxxxx,xxxxxx,xxxxxxx,xxxxxxxx,xxxxxxxxx,xxxxxxxxxx,
       xxxxxxxxxxx,xxxxxxxxxxxx,xxxxxxxxxxxxx,xxxxxxxxxxxxxx,xxxxxxxxxxxxxxx,
       xxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxx,
       xxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxx,
       xxxxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxxxx,
       xxxxxxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxxxxxx,
       xxxxxxxxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxxxxxxxx,
       xxxxxxxxxxxxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxxxxxxxxxxxxx/"""

    nose.tools.eq_(buf.getvalue(), ans)
