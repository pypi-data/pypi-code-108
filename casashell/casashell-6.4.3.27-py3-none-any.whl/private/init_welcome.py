
###
### misc remaining builtins
###
register_builtin( [ "inp", "go", "casalog", "casatools", "casatasks" ] )
from casashell.private.builtin_mgr import unregister_builtin
unregister_builtin( [ "display" ] )

###
### cleanup global namespace
###
del register_builtin
del unregister_builtin

###
### Include the casatools/casatasks module version number at the end of the startup prompt
### If they are equal, just include one copy otherwise include both version numbers
###
try:
    import casalith as __casalith
    print("CASA %s -- Common Astronomy Software Applications [%s]" % (__casalith.version_string( ),casatasks.version_string( )))
    del __casalith
except:
    import casashell as __casashell
    print("CASA %s -- Common Astronomy Software Applications" % __casashell.version_string( ))
    del __casashell

###
### post any startup log messages
###

try:
    for logTup in config.startup_log:
        casalog.post(logTup[0],logTup[1])
except:
    pass

###
### Verify geodetic Measures tables
###

checkgeodetic()
