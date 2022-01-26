###
### casashell configuration file for casatools. This file is loaded by the casatools
### package when it is first imported
###
import os as _os
from casashell import flags as _flags

#----------------------------------------------------------------------------------------------------
#-- first, set default values for configuration parameters                                          --
#----------------------------------------------------------------------------------------------------
#
# directories to add to the data search path
#
datapath=[ ]

if not _flags.norc:
    if _flags.rcdir is None:
        _home = _os.curdir                        # Default
        if 'HOME' in _os.environ:
            _home = _os.environ['HOME']
        elif _os.name == 'posix':
            _home = _os.path.expanduser("~/")
        elif _os.name == 'nt':                   # Contributed by Jeff Bauer
            if 'HOMEPATH' in _os.environ:
                if 'HOMEDRIVE' in _os.environ:
                    _home = _os.environ['HOMEDRIVE'] + _os.environ['HOMEPATH']
                else:
                    _home = _os.environ['HOMEPATH']

        _config = _os.path.join(_home, ".casa/config.py")
        
    else:
        _config = _os.path.join(_os.path.expanduser(_flags.rcdir),"config.py")

    #----------------------------------------------------------------------------------------------------
    #-- next, exec user's configuration file if it exists                                              --
    #----------------------------------------------------------------------------------------------------
    try:
        _f = open(_config)
    except IOError:
        pass
    else:
        _f.close()
        try:
            exec(open(_config).read( ))
        except:
            import sys
            sys.stderr.write("error: evaluation of %s failed\n" % _config)
