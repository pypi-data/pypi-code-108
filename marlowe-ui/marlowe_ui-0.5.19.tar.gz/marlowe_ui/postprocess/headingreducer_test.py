import nose

import io
import sys
import os

sys.path.insert(0, os.path.join(__file__, '..', '..'))


import postprocess.headingreducer


@nose.tools.raises(StopIteration)
def test_hold():
    text = '''0: line 0
1: line 1
2: line 2'''

    s = io.StringIO(text)

    h = postprocess.headingreducer.HeadingReducer(s)

    lineno, line = next(h)
    nose.tools.eq_(lineno, 0)
    nose.tools.eq_(line, '0: line 0\n')

    lineno, line = next(h)
    nose.tools.eq_(lineno, 1)
    nose.tools.eq_(line, '1: line 1\n')

    h.hold()
    lineno, line = next(h)
    nose.tools.eq_(lineno, 1)
    nose.tools.eq_(line, '1: line 1\n')

    lineno, line = next(h)
    nose.tools.eq_(lineno, 2)
    nose.tools.eq_(line, '2: line 2')

    h.hold()
    lineno, line = next(h)
    nose.tools.eq_(lineno, 2)
    nose.tools.eq_(line, '2: line 2')

    next(h)  # no more line StopIteration
