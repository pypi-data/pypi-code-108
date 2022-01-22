from setux.main import banner


doc = f'''{banner}

setux [Module | Manager | Command] [*args | **kwargs] [Target]

Deploy Module, Call Manager or Execute Command on Target


Module, Manager or Command:
    - Deploy Module ( see the "modules" command )
    - Call Manager ( see the "managers" command)
        Manager may be dotted
        ex :
            pip.installed
    - Set or Get Manager's Property
        ex :
            system.hostname
            system.hostname=server
    - Execute Command ( see the "help" command )
    - if not specified : enter REPL on Target

Target:
    - May be passed on command line
    - Set in environement as "setux_target"
    - defaults to "Local"
'''


def usage(*args):
    print(doc)
