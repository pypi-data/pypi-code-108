from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error, start_interceptor, end_interceptor
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil
import re

def parseServiceName(graphql_doc):
    try:
        op_def = [
            i for i in graphql_doc.definitions
            if type(i).__name__ == "OperationDefinition"
        ][0]
    except KeyError:
        return "GraphQL unknown operation"

    op = op_def.operation
    name = op_def.name
    fields = op_def.selection_set.selections
    if not fields:
        fields = []
    return "/GraphQL %s %s" % (op.upper(), name.value if name else "+".join([f.name.value for f in fields]))  

def intercept_execute(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        ctx = TraceContext()
        is_transaction_started = False
    else:
        is_transaction_started = not ctx.is_ignored
    if not is_transaction_started:
        if len(args) > 1 and hasattr(args[1],"definitions"):
            name = parseServiceName(args[1])
            if name:    
                ctx.service_name =  name
        start_interceptor(ctx)
    start_time = DateUtil.nowSystem()
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        if not is_transaction_started:
            end_interceptor()
        else:
            text = "graphql.execute"
            payloads = [text, '']
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.TX_METHOD, ctx, payloads)

def parseDocumentName(op_def):
    op = op_def.operation
    name = op_def.name
    fields = op_def.selection_set.selections
    if not fields:
        fields = []
    return "GraphQL %s %s" % (op.upper(), name if name else "+".join([f.name.value for f in fields]))  


def parseSelectionSet(gnode, tokens = [], indent=0):
    nameFound = False
    
    if hasattr(gnode, "selection_set"):
        if hasattr(gnode, "name") and hasattr(gnode, "selection_set"): 
            if gnode.selection_set:
                tokens.append("  "*indent+gnode.name.value+"{")
                nameFound = True
            else:
                tokens.append("  "*indent+gnode.name.value)

    if hasattr(gnode, "selection_set"):
        if gnode.selection_set:
            if gnode.selection_set.selections:
                for sel in gnode.selection_set.selections:
                    parseSelectionSet(sel, tokens, indent = indent+1)
    if nameFound:
        tokens.append("  "*indent+"}")

def parseDocument(defi):
    tokens = []
    if hasattr(defi, "name"):
        tokens.append(defi.name.value+"{")
    
    if hasattr(defi, "selection_set"):
        if defi.selection_set:
            if defi.selection_set.selections:
                for sel in defi.selection_set.selections:
                    if sel:
                        parseSelectionSet(sel, tokens, 1)

    if hasattr(defi, "name"):
        tokens.append("}")
    tokens.reverse()
    return "\n".join(tokens)

def intercept_execute_method( fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    start_time = DateUtil.nowSystem()
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        if ctx:
            interceptor_step_error(e)
    finally:
        if ctx and len(args) > 4 and not args[4] and args[3]:
            operation_definition = args[3][0]
            text = operation_definition.name.value
            arg = parseDocument(operation_definition)
            
            payloads = [text, arg]
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.TX_METHOD, ctx, payloads)
        
def instrument_graphql(module):
    def wrapper(fn):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            callback = intercept_execute(fn, *args, **kwargs)
            return callback

        return trace
    if hasattr(module, 'execute'):
        module.execute = wrapper(module.execute)

    def wrapper( fn):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            callback = intercept_execute_method( fn, *args, **kwargs)
            return callback
        return trace

    # if hasattr(module, 'execute_operation'):
    #    module.execute_operation = wrapper(module.execute_operation)
        
    if hasattr(module, 'resolve_field'):
       module.resolve_field = wrapper(module.resolve_field)