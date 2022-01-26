import ast
import traceback
from IPython.core.error import InputRejected
from casashell.private.stack_manip import find_local as __sf__

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

@static_var("builtins", __sf__('casa_builtin_state'))
def register_builtin(obj):
    if isinstance(obj,str):
        register_builtin.builtins[obj] = True
    elif isinstance(obj, list) and all(isinstance(elem, str) for elem in obj):
        for b in obj: register_builtin.builtins[b] = True
    else:
        raise RuntimeError("parameter is not a string or list of strings")

@static_var("nonbuiltins", __sf__('casa_nonbuiltin_state'))
def unregister_builtin(obj):
    if isinstance(obj,str):
        unregister_builtin.nonbuiltins[obj] = True
    elif isinstance(obj, list) and all(isinstance(elem, str) for elem in obj):
        for b in obj: unregister_builtin.nonbuiltins[b] = True
    else:
        raise RuntimeError("parameter is not a string or list of strings")

@static_var("names", __sf__('casa_builtin_state'))
@static_var("nonnames", __sf__('casa_nonbuiltin_state'))
def builtins( ):
    return [ n for n in builtins.names if n not in nonnames ]

class __check_builtin(ast.NodeTransformer):
    """prevent assignment to builtin values"""
    def __init__(self):
        self.casa_builtins = __sf__('casa_builtin_state')
        self.casa_nonbuiltins = __sf__('casa_nonbuiltin_state')
    def visit_FunctionDef(self, node):
        return node
    def visit_Module(self, node):
        try:
            for body in node.body:
                for name in body.names:
                    if name.asname is not None:
                        if name.asname in __builtins__:
                            raise InputRejected("attempt to modify a python builtin value")
                        if name.asname in self.casa_builtins:
                            raise InputRejected("attempt to modify a casa builtin value")
                    else:
                        if name.name in __builtins__:
                            raise InputRejected("attempt to modify a python builtin value")
                        if name.name in self.casa_builtins:
                            raise InputRejected("attempt to modify a casa builtin value")

        except InputRejected as ir:
            raise ir
        except: pass
        return node
    def visit_Assign(self, node):
        try:
            for n in node.targets:
                # CASA <1>: def foobar( ): return (1,2,3)
                # CASA <2>: True,b,c = foobar( )
                #
                #           generates a [<ast.Tuple>] for 'node'
                #           and tuple.elts provides access to the
                #           strings/names within the ast.Tuple
                #
                tgts = n.elts if isinstance(n,ast.Tuple) else [n]
                for t in tgts:
                    if not isinstance(t,ast.Attribute) and \
                       not isinstance(t,ast.Subscript):
                        if t.id in self.casa_nonbuiltins:
                            continue
                        if t.id in __builtins__:
                            raise InputRejected("attempt to modify a python builtin value")
                        if t.id in self.casa_builtins:
                            raise InputRejected("attempt to modify a casa builtin value")
        except InputRejected as ir:
            raise ir
        except:
            print("-----------------------------------------------------------------")
            print("internal error in CASA assignment filter...")
            print(traceback.format_exc())
            print("-----------------------------------------------------------------")
        return node
    def visit_Lambda(self, node):
        return node

#@static_var("ip",get_ipython( ))
#def enable_builtin_protection( ):
#    enable_builtin_protection.ip.ast_transformers.append(__check_builtin( ))

get_ipython( ).ast_transformers.append(__check_builtin( ))
