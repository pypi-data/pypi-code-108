from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.parsing.op.action import op_ACTION, op_EACTION
from aasm.parsing.op.agent import op_AGENT, op_EAGENT
from aasm.parsing.op.behav import op_BEHAV, op_EBEHAV
from aasm.parsing.op.clr import op_CLR
from aasm.parsing.op.conditional import (
    handle_ordered_conditional_statement,
    handle_unordered_conditional_statement)
from aasm.parsing.op.decl import op_DECL
from aasm.parsing.op.defg import op_DEFG
from aasm.parsing.op.eblock import op_EBLOCK
from aasm.parsing.op.graph import op_EGRAPH, op_GRAPH
from aasm.parsing.op.len import op_LEN
from aasm.parsing.op.list import (handle_list_inclusion,
                                  handle_list_modification)
from aasm.parsing.op.math import handle_math_statement
from aasm.parsing.op.message import op_EMESSAGE, op_MESSAGE
from aasm.parsing.op.prm import op_agent_PRM, op_message_PRM
from aasm.parsing.op.rand import op_RAND
from aasm.parsing.op.remen import op_REMEN
from aasm.parsing.op.round import op_ROUND
from aasm.parsing.op.send import op_SEND
from aasm.parsing.op.set import op_SET
from aasm.parsing.op.size import op_SIZE
from aasm.parsing.op.subs import op_SUBS
from aasm.parsing.state import State

if TYPE_CHECKING:
    from aasm.parsing.state import ParsedData


def parse_lines(lines: List[str], debug: bool) -> ParsedData:
    state = State(lines, debug)
    for tokens in state.tokens_from_lines():
        match tokens:                                        
            case [ 'AGENT', name ]:
                op_AGENT(state, name)
            
            case [ 'EAGENT' ]:
                op_EAGENT(state)
                
            case [ 'MESSAGE', name, performative ]:
                op_MESSAGE(state, name, performative)
            
            case [ 'EMESSAGE' ]:
                op_EMESSAGE(state)
                
            case [ 'PRM', name, category ]:
                op_message_PRM(state, name, category)
                
            case [ 'PRM', name, category, *args ]:
                op_agent_PRM(state, name, category, args)
                
            case [ 'BEHAV', name, category, *args ]:
                op_BEHAV(state, name, category, args)
                
            case [ 'EBEHAV' ]:
                op_EBEHAV(state)
                
            case [ 'ACTION', name, category, *args ]:
                op_ACTION(state, name, category, args)
                
            case [ 'EACTION' ]:
                op_EACTION(state)
                
            case [ 'DECL', name, value ]:
                op_DECL(state, name, value)
                
            case [ 'EBLOCK' ]:
                op_EBLOCK(state)
                
            case [ 'IEQ' | 'INEQ' | 'WEQ' | 'WNEQ' as op, arg1, arg2 ]:
                handle_unordered_conditional_statement(state, op, arg1, arg2)
                
            case [ 'IGT' | 'IGTEQ' | 'ILT' | 'ILTEQ' | 'WGT' | 'WGTEQ' | 'WLT' | 'WLTEQ' as op, arg1, arg2 ]:
                handle_ordered_conditional_statement(state, op, arg1, arg2)
                
            case [ 'ADD' | 'SUBT' | 'MULT' | 'DIV' as op, arg1, arg2 ]:
                handle_math_statement(state, op, arg1, arg2)
                
            case [ 'ADDE' | 'REME' as op, list_, element ]:
                handle_list_modification(state, op, list_, element)
                
            case [ 'LEN', result, list_ ]:
                op_LEN(state, result, list_)
                
            case [ 'CLR', list_ ]:
                op_CLR(state, list_)
                
            case [ 'IN' | 'NIN' as op, list_, element ]:
                handle_list_inclusion(state, op, list_, element)
                
            case [ 'SEND', rcv_list ]:
                op_SEND(state, rcv_list)
                
            case [ 'SUBS', dst_list, src_list, num ]:
                op_SUBS(state, dst_list, src_list, num)
                
            case [ 'SET', arg1, arg2 ]:
                op_SET(state, arg1, arg2)
                
            case [ 'REMEN', list_, num ]:
                op_REMEN(state, list_, num)

            case [ 'RAND', result, cast_to, dist, *args ]:
                op_RAND(state, result, cast_to, dist, args)

            case [ 'ROUND', num ]:
                op_ROUND(state, num)
                
            case [ 'SET', arg1, arg2 ]:
                op_SET(state, arg1, arg2)

            case [ 'GRAPH', category ]:
                op_GRAPH(state, category)

            case [ 'EGRAPH' ]:
                op_EGRAPH(state)

            case [ 'SIZE', size ]:
                op_SIZE(state, size)

            case [ 'DEFG',  agent_name, amount, *args ]:
                op_DEFG(state, agent_name, amount, args)
                
            case _:
                state.panic(f'Unknown tokens: {tokens}')

    return state.get_parsed_data()
