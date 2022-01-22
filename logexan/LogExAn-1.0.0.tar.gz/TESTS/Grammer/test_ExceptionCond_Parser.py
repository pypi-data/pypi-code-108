from LogExAn.Grammer.SyntaxParser import LA_Grammer, LA_Parser
from lark import Lark, Transformer, v_args
import pytest

##########################################################################################################
## Exception condition based tests for Parser 
##########################################################################################################

def test_ExceptionCondition():

    LA_Template = Lark(LA_Grammer, parser='lalr', transformer=LA_Parser())
    Logan_Parser = LA_Template.parse
    print("Exception Condition with out braces with logic && and || ")
    Cond = "( Var_new_1 == 1 || Var_new_4 == 7 && Var_new_9 == 12 )";
    print(Cond)
    try:
        Cond_Map = Logan_Parser(Cond)
    except AssertionError as err:
        assert(isinstance(err, AssertionError));
        assert("Only One operator to be present within a single ()" in str(err));
    Ref_File = None;
