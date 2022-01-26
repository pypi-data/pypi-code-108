from casashell.private.stack_manip import find_local as __sf__

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


@static_var("state", __sf__('casa_inp_go_state'))
def inp(obj=None):
    if obj is not None:
        if type(obj) == str:
            try:
                new_obj = eval(obj)
                inp(new_obj)
                return
            except:
                print("ERROR %s does not seem to be a CASA task" % obj)
                return
        if 'inp' in dir(obj):
            inp.state['last'] = obj
            obj.inp( )
        else:
            print("ERROR %s does not seem to be a CASA task" % obj)
    elif 'last' in inp.state and inp.state['last'] is not None:
        inp.state['last'].inp( )
    else:
        print("ERROR task not specified and no active task")

@static_var("state", __sf__('casa_inp_go_state'))
def go(obj=None):
    if obj is not None:
        if type(obj) == str:
            try:
                new_obj = eval(obj)
                go(new_obj)
                return
            except:
                print("ERROR %s does not seem to be a CASA task" % obj)
                return
        if 'inp' in dir(obj):
            go.state['last'] = obj
            return obj( )
        else:
            print("ERROR %s does not seem to be a CASA task" % obj)
            return None
    elif 'last' in go.state and go.state['last'] is not None:
        return go.state['last']( )
    else:
        print("ERROR task not specified and no active task")
        return None

@static_var("state", __sf__('casa_inp_go_state'))
def default(obj=None):
    if obj is not None:
        if type(obj) == str:
            try:
                new_obj = eval(obj)
                default(new_obj)
                return
            except:
                print("ERROR %s does not seem to be a CASA task" % obj)
                return
        if 'set_global_defaults' in dir(obj):
            default.state['last'] = obj
            obj.set_global_defaults( )
            return
        else:
            print("ERROR argument does not appear to be a task")
            return
    elif 'last' in default.state and default.state['last'] is not None:
        return go.state['last'].set_global_defaults( )
    else:
        print("ERROR task not specified and no active task")
        return None

@static_var("state", __sf__('casa_inp_go_state'))
def tget(obj=None,savefile=None):
    if obj is not None:
        if type(obj) == str:
            try:
                new_obj = eval(obj)
                tget(new_obj,savefile)
                return
            except:
                print("ERROR %s does not seem to be a CASA task" % obj)
                return
        if 'tget' in dir(obj):
            tget.state['last'] = obj
            obj.tget(savefile)
            return
        else:
            print("ERROR 'obj' argument does not appear to be a task")
            return
    elif 'last' in tget.state and tget.state['last'] is not None:
        tget.state['last'].tget(savefile)
    else:
        print("ERROR task not specified and no active task")
        return

@static_var("state", __sf__('casa_inp_go_state'))
def tput(obj=None, outfile=None):
    if obj is not None:
        if type(obj) == str:
            try:
                new_obj = eval(obj)
                tput(new_obj,outfile)
                return
            except:
                print("ERROR %s does not seem to be a CASA task" % obj)
                return
        if 'tput' in dir(obj):
            tput.state['last'] = obj
            obj.tput(outfile)
            return
        else:
            print("ERROR 'obj' argument does not appear to be a task")
            return
    elif 'last' in tput.state and tput.state['last'] is not None:
        tput.state['last'].tput(outfile)
    else:
        print("ERROR task not specified and no active task")
        return

saveinputs = tput
        
del __sf__
del static_var
